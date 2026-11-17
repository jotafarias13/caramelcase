"""The user's own account: reading it, changing preferences, exporting
and deleting it.
"""

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.models import (
    Attempt,
    AuthIdentity,
    DailyActivity,
    Event,
    MagicLink,
    PracticeSession,
    QuestionReport,
    ReviewItem,
    Streak,
    Subject,
    User,
    UserSettings,
    UserSubject,
    UserSubjectRating,
    UserTopicMastery,
)
from app.db.rows import ensure_row
from app.domain.daily_goal import is_goal_option
from app.domain.local_time import local_date
from app.errors import AppError
from app.schemas.account import (
    ExportResponse,
    MeResponse,
    SettingsModel,
    SettingsPatch,
)
from app.services.practice import published_subject
from app.settings import Settings

# The user's rows that GET /me/export returns, by table. Session tokens
# and sign-in links are left out: they are credentials, not data.
_EXPORTED: tuple[type[Base], ...] = (
    UserSettings,
    AuthIdentity,
    UserSubject,
    PracticeSession,
    Attempt,
    UserSubjectRating,
    UserTopicMastery,
    DailyActivity,
    Streak,
    ReviewItem,
    QuestionReport,
    Event,
)

_USER_FIELDS = ("locale", "timezone", "display_name", "university", "course")
_SETTINGS_FIELDS = (
    "theme",
    "show_option_reasons",
    "daily_reminder",
    "weekly_email",
)
# Fields that null clears. For the others null means "leave as it is".
_CLEARABLE = ("display_name", "university", "course")


async def settings_of(session: AsyncSession, user: User) -> UserSettings:
    row = await session.scalar(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    assert row is not None  # every user has a settings row
    return row


async def me_response(session: AsyncSession, user: User) -> MeResponse:
    preferences = await settings_of(session, user)
    current = None
    if user.current_subject_id is not None:
        current = await session.scalar(
            select(Subject.slug).where(Subject.id == user.current_subject_id)
        )
    return MeResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        locale=user.locale,
        timezone=user.timezone,
        is_guest=user.is_guest,
        role=user.role,
        university=user.university,
        course=user.course,
        current_subject=current,
        settings=SettingsModel(
            daily_goal=preferences.daily_goal,
            theme=preferences.theme,
            show_option_reasons=preferences.show_option_reasons,
            daily_reminder=preferences.daily_reminder,
            weekly_email=preferences.weekly_email,
        ),
    )


async def change_settings(
    session: AsyncSession,
    user: User,
    patch: SettingsPatch,
    *,
    settings: Settings,
    now: datetime,
) -> None:
    """Apply the fields the client sent, and only those."""
    sent = patch.model_fields_set
    preferences = await settings_of(session, user)

    for field in _USER_FIELDS:
        value = getattr(patch, field)
        if field in sent and (value is not None or field in _CLEARABLE):
            # An empty text clears the field, like null.
            setattr(user, field, value or None)
    for field in _SETTINGS_FIELDS:
        value = getattr(patch, field)
        if field in sent and value is not None:
            setattr(preferences, field, value)

    if patch.current_subject is not None:
        subject = await published_subject(session, patch.current_subject)
        user.current_subject_id = subject.id
        await ensure_row(
            session,
            UserSubject,
            {"user_id": user.id, "subject_id": subject.id},
        )
    if patch.daily_goal is not None:
        await _change_daily_goal(
            session,
            user,
            preferences,
            goal=patch.daily_goal,
            settings=settings,
            now=now,
        )
    await session.flush()


async def _change_daily_goal(  # noqa: PLR0913
    session: AsyncSession,
    user: User,
    preferences: UserSettings,
    *,
    goal: int,
    settings: Settings,
    now: datetime,
) -> None:
    if not is_goal_option(goal, settings):
        options = ", ".join(str(n) for n in settings.daily_goal_options)
        raise AppError(
            422, "validation_error", f"daily_goal: must be one of {options}"
        )
    preferences.daily_goal = goal
    # A lower goal may already be met today.
    today = await session.scalar(
        select(DailyActivity).where(
            DailyActivity.user_id == user.id,
            DailyActivity.local_date == local_date(now, user.timezone),
        )
    )
    if today is not None and today.questions >= goal:
        today.goal_met = True


async def export_user(
    session: AsyncSession, user: User, now: datetime
) -> ExportResponse:
    tables: dict[str, list[dict[str, Any]]] = {}
    for model in _EXPORTED:
        rows = await session.scalars(
            select(model)
            .where(model.user_id == user.id)  # type: ignore[attr-defined]
            .order_by(model.created_at, model.id)
        )
        tables[model.__tablename__] = [_as_json(row) for row in rows]
    return ExportResponse(exported_at=now, user=_as_json(user), tables=tables)


def _as_json(row: Base) -> dict[str, Any]:
    """A row as a JSON object: every column, by name."""
    return {
        column.name: _json_value(getattr(row, column.key))
        for column in row.__table__.columns
    }


def _json_value(value: object) -> object:
    if isinstance(value, uuid.UUID | Decimal):
        return str(value)
    if isinstance(value, datetime | date | time):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


async def delete_user(session: AsyncSession, user: User) -> None:
    """Erase the user and everything that belongs to them.

    Their rows in other tables go with the users row (ON DELETE
    CASCADE). Sign-in links are tied to the address, not to the user.
    """
    if user.email is not None:
        await session.execute(
            delete(MagicLink).where(MagicLink.email == user.email)
        )
    await session.delete(user)
    await session.flush()
