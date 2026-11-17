"""The demo user of a development database: an account with three weeks
of history, so that Home, the profile and the calendar have something
to show.

The history is not written by hand: the demo user plays real sessions
through the practice service, on past dates. It ends with a streak of
seven days.
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Subject, User, UserSubject
from app.enums import AuthProvider
from app.services.catalog import playable_subjects
from app.services.practice import (
    answer_question,
    correct_key_of,
    finish_session,
    start_session,
)
from app.services.sign_in import sign_in
from app.settings import Settings

_STREAK_DAYS = 7
# Before the streak, the demo user practiced on about this share of days.
_EARLIER_DAY_CHANCE = 0.5
_SECOND_SESSION_CHANCE = 0.4
_OTHER_SUBJECT_CHANCE = 0.3
_CORRECT_CHANCE = 0.78
_SECONDS_PER_ANSWER = 40
_KEYS = ("a", "b", "c", "d")


class NoPublishedSubjectError(Exception):
    """The demo user has nothing to practice."""


@dataclass(frozen=True)
class DemoUser:
    user: User
    created: bool  # False when the demo user was already there
    sessions: int


async def create_demo_user(
    session: AsyncSession,
    settings: Settings,
    now: datetime,
    rng: random.Random,
) -> DemoUser:
    """Create the demo user and its history, unless it exists."""
    existing = await session.scalar(
        select(User).where(User.email == settings.demo_user_email)
    )
    if existing is not None:
        return DemoUser(user=existing, created=False, sessions=0)
    subjects = await playable_subjects(session)
    if not subjects:
        raise NoPublishedSubjectError("no published subject has questions")

    user = await sign_in(
        session,
        settings,
        current_user=None,
        provider=AuthProvider.EMAIL,
        provider_subject=settings.demo_user_email,
        email=settings.demo_user_email,
        display_name=settings.demo_user_name,
    )
    user.course = "Ciência da Computação"
    user.current_subject_id = subjects[min(1, len(subjects) - 1)].id
    for subject in subjects:
        session.add(UserSubject(user_id=user.id, subject_id=subject.id))
    await session.flush()

    played = 0
    for days_ago in reversed(range(settings.demo_history_days)):
        in_streak = days_ago < _STREAK_DAYS
        # The day before the streak is a gap, or the streak is longer.
        gap = days_ago == _STREAK_DAYS
        if gap or not (in_streak or rng.random() < _EARLIER_DAY_CHANCE):
            continue
        start = now - timedelta(days=days_ago, hours=1)
        starts = [start]
        if rng.random() < _SECOND_SESSION_CHANCE:
            starts.append(start + timedelta(minutes=20))
        for moment in starts:
            await _play(
                session, user, subjects, moment, settings=settings, rng=rng
            )
            played += 1
    return DemoUser(user=user, created=True, sessions=played)


async def _play(  # noqa: PLR0913
    session: AsyncSession,
    user: User,
    subjects: list[Subject],
    start: datetime,
    *,
    settings: Settings,
    rng: random.Random,
) -> None:
    """Play one session from start to finish."""
    current = next(s for s in subjects if s.id == user.current_subject_id)
    subject = current
    if rng.random() < _OTHER_SUBJECT_CHANCE:
        subject = rng.choice(subjects)
    practice = await start_session(
        session, user, subject.slug, settings=settings, now=start, rng=rng
    )
    moment = start
    for question_id in practice.question_ids:
        moment += timedelta(seconds=_SECONDS_PER_ANSWER)
        correct = await correct_key_of(session, question_id)
        key = correct
        if rng.random() > _CORRECT_CHANCE:
            key = rng.choice([k for k in _KEYS if k != correct])
        await answer_question(
            session,
            user,
            practice.id,
            question_id=question_id,
            key=key,
            time_ms=rng.randint(8_000, 45_000),
            settings=settings,
            now=moment,
        )
    await finish_session(
        session, user, practice.id, settings=settings, now=moment
    )
