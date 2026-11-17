"""Signed-in browsers and devices: opaque session tokens.

A token is a random 256-bit value. The client holds the token; the
database holds only its SHA-256 hash, so a copy of the table signs
nobody in.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuthSession
from app.settings import Settings


def new_token(settings: Settings) -> str:
    return secrets.token_urlsafe(settings.session_token_bytes)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def session_lifetime(settings: Settings) -> timedelta:
    return timedelta(days=settings.session_lifetime_days)


async def start_session(
    session: AsyncSession,
    user_id: uuid.UUID,
    now: datetime,
    settings: Settings,
) -> str:
    """Sign a user in. Returns the token, which is not stored anywhere."""
    token = new_token(settings)
    session.add(
        AuthSession(
            user_id=user_id,
            token_hash=hash_token(token),
            expires_at=now + session_lifetime(settings),
        )
    )
    await session.flush()
    return token


async def find_session(
    session: AsyncSession, token: str, now: datetime
) -> AuthSession | None:
    """The session a token belongs to, unless it has expired."""
    return await session.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hash_token(token),
            AuthSession.expires_at > now,
        )
    )


def renew_if_due(
    auth_session: AuthSession, now: datetime, settings: Settings
) -> bool:
    """Give a session its full lifetime again once half of it is gone.

    Returns whether it did, in which case the cookie is sent again.
    """
    lifetime = session_lifetime(settings)
    if auth_session.expires_at - now > lifetime / 2:
        return False
    auth_session.expires_at = now + lifetime
    return True


async def end_session(session: AsyncSession, token: str) -> None:
    """Sign out the one browser or device that holds this token."""
    await session.execute(
        delete(AuthSession).where(AuthSession.token_hash == hash_token(token))
    )
