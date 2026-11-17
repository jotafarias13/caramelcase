"""Stats and activity: the numbers on Home and on the profile."""

from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    DailyActivity,
    PracticeSession,
    Subject,
    User,
    UserTopicMastery,
)
from app.domain.local_time import local_date
from app.domain.mastery import accuracy
from app.errors import AppError
from app.schemas.common import GoalModel, RatingChangeModel, StreakModel
from app.schemas.stats import (
    ActivityDay,
    ActivityResponse,
    StatsResponse,
    SubjectRating,
)
from app.services.catalog import published_subjects, ratings_of
from app.services.progress import (
    goal_today,
    level_model,
    rating_change_in,
    sessions_finished_by,
    streak_of,
    subject_ref,
    total_xp_of,
)
from app.settings import Settings


async def user_stats(
    session: AsyncSession, user: User, *, settings: Settings, now: datetime
) -> StatsResponse:
    today = local_date(now, user.timezone)
    total, correct = (
        await session.execute(
            select(
                func.coalesce(func.sum(UserTopicMastery.total), 0),
                func.coalesce(func.sum(UserTopicMastery.correct), 0),
            ).where(UserTopicMastery.user_id == user.id)
        )
    ).one()
    ratings = await ratings_of(session, user.id)
    subjects = []
    for subject in await published_subjects(session):
        row = ratings.get(subject.id)
        answers = row.answers_count if row else 0
        subjects.append(
            SubjectRating(
                **subject_ref(subject).model_dump(),
                rating=row.rating if row and answers else None,
                answers_count=answers,
            )
        )
    return StatsResponse(
        today=today,
        level=level_model(await total_xp_of(session, user.id), settings),
        streak=StreakModel.of(await streak_of(session, user.id, today)),
        goal=GoalModel.of(await goal_today(session, user.id, today)),
        questions_answered=int(total),
        correct_answers=int(correct),
        accuracy=accuracy(int(correct), int(total)),
        sessions_finished=await sessions_finished_by(session, user.id),
        subjects=subjects,
        last_rating_change=await _last_rating_change(session, user),
    )


async def _last_rating_change(
    session: AsyncSession, user: User
) -> RatingChangeModel | None:
    """The rating change of the last session the user finished."""
    last = await session.scalar(
        select(PracticeSession)
        .where(
            PracticeSession.user_id == user.id,
            PracticeSession.finished_at.is_not(None),
            PracticeSession.subject_id.is_not(None),
        )
        .order_by(PracticeSession.finished_at.desc())
        .limit(1)
    )
    if last is None:
        return None
    subject = await session.get(Subject, last.subject_id)
    assert subject is not None
    return await rating_change_in(session, last, subject)


async def user_activity(  # noqa: PLR0913
    session: AsyncSession,
    user: User,
    *,
    start: date | None,
    end: date | None,
    settings: Settings,
    now: datetime,
) -> ActivityResponse:
    """The user's days with activity between two dates, both included.

    Without dates: the current month of the user's own calendar, which
    is what the profile shows. Without an end: to the end of the month
    that start is in.
    """
    today = local_date(now, user.timezone)
    start = start or today.replace(day=1)
    end = end or _last_day_of_month(start)
    if end < start:
        raise AppError(422, "validation_error", "end is before start.")
    if (end - start).days >= settings.activity_max_days:
        raise AppError(
            422,
            "validation_error",
            f"At most {settings.activity_max_days} days at a time.",
        )
    rows = await session.scalars(
        select(DailyActivity)
        .where(
            DailyActivity.user_id == user.id,
            DailyActivity.local_date >= start,
            DailyActivity.local_date <= end,
        )
        .order_by(DailyActivity.local_date)
    )
    days = [
        ActivityDay(
            date=row.local_date,
            xp=row.xp,
            questions=row.questions,
            sessions_finished=row.sessions_finished,
            goal_met=row.goal_met,
        )
        for row in rows
    ]
    return ActivityResponse(today=today, start=start, end=end, days=days)


def _last_day_of_month(day: date) -> date:
    next_month = (day.replace(day=28) + timedelta(days=4)).replace(day=1)
    return next_month - timedelta(days=1)
