"""Auth: guests, Google sign-in, email links, sign-out."""

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from loguru import logger

from app.db.models import User
from app.db.session import SessionDep
from app.enums import AuthProvider, Locale
from app.errors import AppError
from app.providers.email import EmailSender, get_email_sender
from app.providers.google import (
    GoogleError,
    GoogleProvider,
    get_google_provider,
)
from app.routes.dependencies import (
    Now,
    OptionalUser,
    SettingsDep,
    clear_session_cookie,
    session_token,
    set_session_cookie,
)
from app.schemas.account import (
    GuestRequest,
    MagicLinkRequest,
    MagicLinkVerifyRequest,
    MeResponse,
)
from app.services.account import me_response
from app.services.auth_sessions import end_session, start_session
from app.services.magic_links import send_magic_link, use_magic_link
from app.services.sign_in import sign_in
from app.services.users import create_user
from app.settings import Settings

router = APIRouter(prefix="/auth", tags=["auth"])

GoogleDep = Annotated[GoogleProvider | None, Depends(get_google_provider)]
EmailDep = Annotated[EmailSender, Depends(get_email_sender)]

_STATE_COOKIE = "cc_oauth_state"
_GOOGLE_PATH = "/api/v1/auth/google"


@router.post("/guest")
async def create_guest(
    body: GuestRequest,
    response: Response,
    session: SessionDep,
    settings: SettingsDep,
    now: Now,
    user: OptionalUser,
) -> MeResponse:
    """Start playing without an account.

    The web app calls this on a first visit. Someone already signed in
    gets their own user back, so calling it twice makes one guest.
    """
    if user is None:
        user = await create_user(
            session, settings, locale=body.locale, timezone=body.timezone
        )
        token = await start_session(session, user.id, now, settings)
        set_session_cookie(response, token, settings)
    me = await me_response(session, user)
    await session.commit()
    return me


@router.post("/magic-link", status_code=202)
async def request_magic_link(
    body: MagicLinkRequest,
    session: SessionDep,
    settings: SettingsDep,
    now: Now,
    user: OptionalUser,
    sender: EmailDep,
) -> None:
    """Email a sign-in link. The answer is the same for any address."""
    locale = body.locale or (user.locale if user else Locale.PT_BR)
    await send_magic_link(
        session, sender, settings, email=body.email, locale=locale, now=now
    )
    await session.commit()


@router.post("/magic-link/verify")
async def verify_magic_link(
    body: MagicLinkVerifyRequest,
    request: Request,
    response: Response,
    session: SessionDep,
    settings: SettingsDep,
    now: Now,
    user: OptionalUser,
) -> MeResponse:
    """Sign in with the token of an emailed link.

    A guest playing in this browser becomes the account, or is merged
    into the account that already has the address.
    """
    email = await use_magic_link(session, body.token, now)
    account = await sign_in(
        session,
        settings,
        current_user=user,
        provider=AuthProvider.EMAIL,
        provider_subject=email,
        email=email,
    )
    await _replace_session(request, response, session, account, settings, now)
    me = await me_response(session, account)
    await session.commit()
    return me


@router.get("/google/start", status_code=307)
async def google_start(
    google: GoogleDep, settings: SettingsDep
) -> RedirectResponse:
    """Send the browser to Google's consent screen."""
    if google is None:
        raise AppError(404, "not_found", "Not Found")
    state = secrets.token_urlsafe(32)
    url = google.authorization_url(state, _google_redirect_uri(settings))
    redirect = RedirectResponse(url, status_code=307)
    # The state comes back in the callback's query; this cookie proves
    # that the same browser started the flow.
    redirect.set_cookie(
        _STATE_COOKIE,
        state,
        max_age=settings.oauth_state_expire_minutes * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path=_GOOGLE_PATH,
    )
    return redirect


@router.get("/google/callback", status_code=307)
async def google_callback(
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
    now: Now,
    user: OptionalUser,
    google: GoogleDep,
    code: str = "",
    state: str = "",
) -> RedirectResponse:
    """Where Google sends the browser back. Signs in and goes on to the
    web app, which shows an error when the address says so.
    """
    if google is None:
        raise AppError(404, "not_found", "Not Found")
    expected = request.cookies.get(_STATE_COOKIE, "")
    # As bytes: compare_digest refuses text that is not ASCII.
    state_is_ours = bool(state) and secrets.compare_digest(
        state.encode(), expected.encode()
    )
    if not code or not state_is_ours:
        return _back_to_app(settings, error="google_sign_in_failed")
    try:
        profile = await google.fetch_profile(
            code, _google_redirect_uri(settings)
        )
    except GoogleError as error:
        logger.opt(exception=error).warning("google sign-in failed")
        return _back_to_app(settings, error="google_sign_in_failed")
    if not profile.email_verified:
        return _back_to_app(settings, error="google_email_not_verified")

    account = await sign_in(
        session,
        settings,
        current_user=user,
        provider=AuthProvider.GOOGLE,
        provider_subject=profile.subject,
        email=profile.email.lower(),
        display_name=profile.name,
    )
    redirect = _back_to_app(settings)
    await _replace_session(request, redirect, session, account, settings, now)
    await session.commit()
    return redirect


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    session: SessionDep,
    settings: SettingsDep,
) -> None:
    """Sign out this browser or device."""
    token = session_token(request, settings)
    if token is not None:
        await end_session(session, token)
        await session.commit()
    clear_session_cookie(response, settings)


async def _replace_session(
    request: Request,
    response: Response,
    session: SessionDep,
    account: User,
    settings: Settings,
    now: Now,
) -> None:
    """End the session the request came with and start one for the
    account: a token from before the sign-in is never one after it.
    """
    old_token = session_token(request, settings)
    if old_token is not None:
        await end_session(session, old_token)
    token = await start_session(session, account.id, now, settings)
    set_session_cookie(response, token, settings)


def _google_redirect_uri(settings: Settings) -> str:
    return f"{settings.app_base_url}{_GOOGLE_PATH}/callback"


def _back_to_app(
    settings: Settings, error: str | None = None
) -> RedirectResponse:
    url = f"{settings.app_base_url}/auth/callback"
    if error:
        url += f"?error={error}"
    redirect = RedirectResponse(url, status_code=307)
    redirect.delete_cookie(_STATE_COOKIE, path=_GOOGLE_PATH)
    return redirect
