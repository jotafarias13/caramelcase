"""Feature flags, as stored: read them, and decide for a user."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FeatureFlag, User
from app.domain.flags import flag_is_on
from app.enums import FlagKey, FlagState


async def flag_states(session: AsyncSession) -> dict[str, FlagState]:
    """Every known flag and its state. A flag with no row is off."""
    stored = {
        key: state
        for key, state in await session.execute(
            select(FeatureFlag.key, FeatureFlag.state)
        )
    }
    return {key.value: stored.get(key.value, FlagState.OFF) for key in FlagKey}


async def flags_for(
    session: AsyncSession, user: User | None
) -> dict[str, bool]:
    """Flag key -> is it on for this user (None: a visitor)."""
    role = user.role if user else None
    states = await flag_states(session)
    return {key: flag_is_on(state, role) for key, state in states.items()}


async def flag_is_on_for(
    session: AsyncSession, key: FlagKey, user: User | None
) -> bool:
    state = await session.scalar(
        select(FeatureFlag.state).where(FeatureFlag.key == key.value)
    )
    return flag_is_on(state or FlagState.OFF, user.role if user else None)
