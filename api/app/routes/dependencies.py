"""What routes depend on: who is asking, the CSRF header, feature flags,
rate limits.

A session token arrives as the session cookie (the web app) or as a
bearer header (the native wrapper). Either way the token is looked up by
its hash.
"""

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Annotated

from fastapi import Depends, Request, Response

from app.client_ip import client_ip
from app.db.base import utc_now
from app.db.models import User
from app.db.session import SessionDep
from app.domain.rate_limit import is_over_limit, retry_after_seconds
from app.enums import FlagKey
from app.errors import AppError
from app.services.auth_sessions import (
    find_session,
    renew_if_due,
    session_lifetime,
)
from app.services.flags import flag_is_on_for
from app.services.rate_limits import RateLimiter, get_rate_limiter
from app.settings import RateLimit, Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
Now = Annotated[datetime, Depends(utc_now)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter)]

_SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
_BEARER = "bearer "


def session_token(request: Request, settings: Settings) -> str | None:
    """The token the request carries: the bearer header, else the cookie."""
    header = request.headers.get("authorization", "")
    if header.lower().startswith(_BEARER):
        return header[len(_BEARER) :].strip() or None
    return request.cookies.get(settings.session_cookie_name)


def set_session_cookie(
    response: Response, token: str, settings: Settings
) -> None:
    response.set_cookie(
        settings.session_cookie_name,
        token,
        max_age=int(session_lifetime(settings).total_seconds()),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        settings.session_cookie_name,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


async def optional_user(
    request: Request,
    response: Response,
    session: SessionDep,
    settings: SettingsDep,
    now: Now,
) -> User | None:
    """The signed-in user, or None for a visitor.

    A session past half of its lifetime is renewed here. The commit is
    its own, so the renewal holds whatever the route does next.
    """
    token = session_token(request, settings)
    if token is None:
        return None
    auth_session = await find_session(session, token, now)
    if auth_session is None:
        return None
    user = await session.get(User, auth_session.user_id)
    if user is not None and renew_if_due(auth_session, now, settings):
        await session.commit()
        if settings.session_cookie_name in request.cookies:
            set_session_cookie(response, token, settings)
    return user


OptionalUser = Annotated[User | None, Depends(optional_user)]


async def current_user(user: OptionalUser) -> User:
    if user is None:
        raise AppError(401, "unauthenticated", "Sign in first.")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


async def require_csrf_header(request: Request, settings: SettingsDep) -> None:
    """Refuse a state-changing request without the custom header.

    A form or a script on another site can make a browser send our
    cookie, but not a header of its own, so the header shows that the
    request comes from our app. It applies to every route of the API.
    """
    if request.method in _SAFE_METHODS:
        return
    if settings.csrf_header_name not in request.headers:
        raise AppError(
            403,
            "csrf_header_missing",
            f"Send the {settings.csrf_header_name} header.",
        )


def require_flag(key: FlagKey) -> Callable[..., Awaitable[None]]:
    """A dependency for the routes of a flagged feature.

    While the flag is off for whoever is asking, the route answers 404,
    exactly as a route that does not exist.
    """

    async def flag_must_be_on(session: SessionDep, user: OptionalUser) -> None:
        if not await flag_is_on_for(session, key, user):
            raise AppError(404, "not_found", "Not Found")

    return flag_must_be_on


def enforce_rate_limit(
    limiter: RateLimiter,
    rule: str,
    caller: str,
    limit: RateLimit,
    now: datetime,
) -> None:
    """Count the request; over the limit, refuse it with a 429 that says
    in Retry-After how many seconds are left in the window.
    """
    count = limiter.count(rule, caller, limit, now)
    if is_over_limit(count, limit):
        wait = retry_after_seconds(now, limit)
        raise AppError(
            429,
            "rate_limited",
            f"Too many requests. Try again in {wait} seconds.",
            headers={"Retry-After": str(wait)},
        )


async def limit_auth(
    request: Request,
    limiter: RateLimiterDep,
    settings: SettingsDep,
    now: Now,
) -> None:
    """Guests, sign-in links and the Google flow, per network address."""
    enforce_rate_limit(
        limiter, "auth", client_ip(request), settings.rate_limit_auth, now
    )


async def limit_answers(
    user: CurrentUser,
    limiter: RateLimiterDep,
    settings: SettingsDep,
    now: Now,
) -> None:
    enforce_rate_limit(
        limiter, "answers", str(user.id), settings.rate_limit_answers, now
    )


async def limit_reports(
    user: CurrentUser,
    limiter: RateLimiterDep,
    settings: SettingsDep,
    now: Now,
) -> None:
    enforce_rate_limit(
        limiter, "reports", str(user.id), settings.rate_limit_reports, now
    )
