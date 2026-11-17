"""Email sign-in links: single use, valid for 15 minutes.

The link carries a random token; the database holds only its hash. The
link does not remember who asked for it: whoever opens it is signed in,
and the guest playing in that browser is the one that is upgraded.
"""

from datetime import datetime, timedelta

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MagicLink
from app.enums import Locale
from app.errors import AppError
from app.providers.email import Email, EmailSender
from app.services.auth_sessions import hash_token, new_token
from app.settings import Settings

_SUBJECT = {
    Locale.PT_BR: "Seu link pra entrar no CaramelCase",
    Locale.EN: "Your CaramelCase sign-in link",
}
_TEXT = {
    Locale.PT_BR: (
        "Oi!\n\n"
        "Abra este link pra entrar no CaramelCase:\n\n"
        "{link}\n\n"
        "Ele vale por {minutes} minutos e só funciona uma vez. Abra no "
        "mesmo aparelho em que você estava praticando, pra manter seu "
        "progresso.\n\n"
        "Se não foi você que pediu, é só ignorar este e-mail.\n"
    ),
    Locale.EN: (
        "Hi!\n\n"
        "Open this link to sign in to CaramelCase:\n\n"
        "{link}\n\n"
        "It is valid for {minutes} minutes and works only once. Open it "
        "on the device you were practicing on, to keep your progress.\n\n"
        "If you did not ask for it, just ignore this email.\n"
    ),
}


def link_url(token: str, settings: Settings) -> str:
    return f"{settings.app_base_url}/auth/callback?token={token}"


async def create_magic_link(
    session: AsyncSession, email: str, now: datetime, settings: Settings
) -> str:
    """Store a new link for an email address and return its token."""
    token = new_token(settings)
    session.add(
        MagicLink(
            email=email,
            token_hash=hash_token(token),
            expires_at=now
            + timedelta(minutes=settings.magic_link_expire_minutes),
        )
    )
    await session.flush()
    return token


async def send_magic_link(  # noqa: PLR0913
    session: AsyncSession,
    sender: EmailSender,
    settings: Settings,
    *,
    email: str,
    locale: Locale,
    now: datetime,
) -> None:
    token = await create_magic_link(session, email, now, settings)
    text = _TEXT[locale].format(
        link=link_url(token, settings),
        minutes=settings.magic_link_expire_minutes,
    )
    await sender.send(Email(to=email, subject=_SUBJECT[locale], text=text))


async def use_magic_link(
    session: AsyncSession, token: str, now: datetime
) -> str:
    """Spend a link and return the email address it proves.

    One UPDATE checks and marks it, so two requests with the same token
    cannot both pass.
    """
    email: str | None = await session.scalar(
        update(MagicLink)
        .where(
            MagicLink.token_hash == hash_token(token),
            MagicLink.used_at.is_(None),
            MagicLink.expires_at > now,
        )
        .values(used_at=now)
        .returning(MagicLink.email)
    )
    if email is None:
        raise AppError(
            400,
            "invalid_magic_link",
            "This link was already used or has expired.",
        )
    return email
