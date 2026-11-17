"""Reading a user's progress: today, the goal, the streak, XP, levels.

Shared by the practice, stats and account services. Nothing here writes.
"""

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    DailyActivity,
    PracticeSession,
    Streak,
    Subject,
    UserSettings,
)
from app.domain.daily_goal import GoalProgress, goal_progress
from app.domain.streak import StreakState, StreakToday, streak_today
from app.domain.xp import level_progress
from app.schemas.common import LevelModel, RatingChangeModel, SubjectRef
from app.settings import Settings


def subject_ref(subject: Subject) -> SubjectRef:
    return SubjectRef(
        slug=subject.slug,
        name_pt=subject.name_pt,
        name_en=subject.name_en,
        short_pt=subject.short_pt,
        short_en=subject.short_en,
    )


async def daily_goal_of(session: AsyncSession, user_id: uuid.UUID) -> int:
    goal = await session.scalar(
        select(UserSettings.daily_goal).where(UserSettings.user_id == user_id)
    )
    assert goal is not None  # every user has a settings row
    return goal


async def goal_today(
    session: AsyncSession, user_id: uuid.UUID, today: date
) -> GoalProgress:
    questions = await session.scalar(
        select(DailyActivity.questions).where(
            DailyActivity.user_id == user_id,
            DailyActivity.local_date == today,
        )
    )
    goal = await daily_goal_of(session, user_id)
    return goal_progress(questions or 0, goal)


def streak_state(row: Streak | None) -> StreakState:
    if row is None:
        return StreakState()
    return StreakState(row.current, row.longest, row.last_active_date)


async def streak_of(
    session: AsyncSession, user_id: uuid.UUID, today: date
) -> StreakToday:
    row = await session.scalar(select(Streak).where(Streak.user_id == user_id))
    return streak_today(streak_state(row), today)


async def total_xp_of(session: AsyncSession, user_id: uuid.UUID) -> int:
    total = await session.scalar(
        select(func.coalesce(func.sum(DailyActivity.xp), 0)).where(
            DailyActivity.user_id == user_id
        )
    )
    return int(total or 0)


def level_model(total_xp: int, settings: Settings) -> LevelModel:
    return LevelModel.of(total_xp, level_progress(total_xp, settings))


async def sessions_finished_by(
    session: AsyncSession, user_id: uuid.UUID
) -> int:
    count = await session.scalar(
        select(func.count())
        .select_from(PracticeSession)
        .where(
            PracticeSession.user_id == user_id,
            PracticeSession.finished_at.is_not(None),
        )
    )
    return count or 0


async def rating_change_in(
    session: AsyncSession, practice: PracticeSession, subject: Subject
) -> RatingChangeModel | None:
    """The student's rating before the first and after the last answer
    of a session. None for a session without answers.
    """
    attempts = (
        select(Attempt)
        .where(Attempt.session_id == practice.id)
        .order_by(Attempt.created_at, Attempt.id)
    )
    first = await session.scalar(attempts.limit(1))
    last = await session.scalar(
        select(Attempt)
        .where(Attempt.session_id == practice.id)
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
        .limit(1)
    )
    if first is None or last is None:
        return None
    return RatingChangeModel(
        subject=subject_ref(subject),
        before=first.user_rating_before,
        after=last.user_rating_after,
        delta=last.user_rating_after - first.user_rating_before,
    )
