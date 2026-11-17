"""Creating users. Every user has a user_settings row from the start."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserSettings
from app.enums import Locale
from app.settings import Settings


async def create_user(  # noqa: PLR0913  one keyword per column
    session: AsyncSession,
    settings: Settings,
    *,
    locale: Locale | None = None,
    timezone: str | None = None,
    email: str | None = None,
    display_name: str | None = None,
) -> User:
    """Create a guest, or an account when an email is given."""
    user = User(
        email=email,
        display_name=display_name,
        locale=locale or Locale.PT_BR,
        timezone=timezone or settings.default_timezone,
        is_guest=email is None,
    )
    session.add(user)
    await session.flush()
    session.add(
        UserSettings(user_id=user.id, daily_goal=settings.daily_goal_default)
    )
    await session.flush()
    return user
