"""Practice sessions: starting one, answering, finishing.

Everything an answer changes is written here, in one transaction: the
attempt, both ratings, the topic's mastery, the day's activity, the
session's counts and, for a wrong answer, the review item. The rules
themselves are the pure functions in app/domain/. The caller commits.
"""

import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    DailyActivity,
    PracticeSession,
    Question,
    QuestionTranslation,
    ReviewItem,
    Streak,
    Subject,
    User,
    UserSubjectRating,
    UserTopicMastery,
)
from app.db.rows import ensure_row
from app.domain.local_time import local_date
from app.domain.rating import RatingChange, rate_answer, unrated_answer
from app.domain.review import first_review
from app.domain.selection import Candidate, select_questions
from app.domain.streak import streak_after_session
from app.domain.xp import xp_for_answer, xp_for_finishing
from app.enums import QuestionStatus, SessionMode, SubjectStatus
from app.errors import AppError
from app.services.progress import daily_goal_of, streak_state
from app.settings import Settings


@dataclass(frozen=True)
class AnswerResult:
    """What an answer did. The route adds the text of the feedback."""

    question_id: uuid.UUID
    selected_key: str
    is_correct: bool
    rating: RatingChange
    xp_earned: int
    session_complete: bool


# ---- starting ----


async def published_subject(session: AsyncSession, slug: str) -> Subject:
    subject = await session.scalar(
        select(Subject).where(
            Subject.slug == slug, Subject.status == SubjectStatus.PUBLISHED
        )
    )
    if subject is None:
        raise AppError(404, "subject_not_found", "No such subject.")
    return subject


async def start_session(  # noqa: PLR0913
    session: AsyncSession,
    user: User,
    subject_slug: str,
    *,
    settings: Settings,
    now: datetime,
    rng: random.Random,
) -> PracticeSession:
    """Start a practice session in a subject, or return the one the
    student left unfinished there.
    """
    subject = await published_subject(session, subject_slug)
    sessions_here = select(PracticeSession).where(
        PracticeSession.user_id == user.id,
        PracticeSession.subject_id == subject.id,
        PracticeSession.mode == SessionMode.PRACTICE,
    )
    unfinished = await session.scalar(
        sessions_here.where(PracticeSession.finished_at.is_(None))
        .order_by(PracticeSession.started_at.desc())
        .limit(1)
    )
    if unfinished is not None:
        return unfinished

    earlier = await session.scalar(sessions_here.limit(1))
    user_rating = await session.scalar(
        select(UserSubjectRating.rating).where(
            UserSubjectRating.user_id == user.id,
            UserSubjectRating.subject_id == subject.id,
        )
    )
    question_ids = select_questions(
        await _candidates(session, user, subject.id, settings, now),
        user_rating=user_rating or settings.user_rating_start,
        first_session=earlier is None,
        settings=settings,
        rng=rng,
    )
    if not question_ids:
        raise AppError(
            409, "no_questions", "This subject has no questions yet."
        )
    practice = PracticeSession(
        user_id=user.id,
        subject_id=subject.id,
        mode=SessionMode.PRACTICE,
        question_ids=question_ids,
        started_at=now,
    )
    session.add(practice)
    await session.flush()
    return practice


async def _candidates(
    session: AsyncSession,
    user: User,
    subject_id: uuid.UUID,
    settings: Settings,
    now: datetime,
) -> list[Candidate]:
    """The published questions of a subject that have text in the
    student's language, each with whether they answered it recently.
    """
    last_answered = (
        select(func.max(Attempt.created_at))
        .where(Attempt.user_id == user.id, Attempt.question_id == Question.id)
        .correlate(Question)
        .scalar_subquery()
    )
    in_their_language = exists().where(
        QuestionTranslation.question_id == Question.id,
        QuestionTranslation.locale == user.locale,
    )
    rows = await session.execute(
        select(
            Question.id,
            Question.topic_id,
            Question.rating,
            Question.difficulty_prior,
            last_answered,
        ).where(
            Question.subject_id == subject_id,
            Question.status == QuestionStatus.PUBLISHED,
            in_their_language,
        )
    )
    recent_from = now - timedelta(days=settings.selection_recent_days)
    return [
        Candidate(
            question_id=question_id,
            topic_id=topic_id,
            rating=rating,
            difficulty_prior=prior,
            answered_recently=answered is not None and answered > recent_from,
        )
        for question_id, topic_id, rating, prior, answered in rows
    ]


# ---- answering ----


async def own_session(
    session: AsyncSession,
    user: User,
    session_id: uuid.UUID,
    *,
    lock: bool = False,
) -> PracticeSession:
    """The user's session with this id. Someone else's is a 404, the
    same as one that does not exist.

    lock makes other requests for the same session wait until this
    transaction ends, so two answers are never counted at once.
    """
    statement = select(PracticeSession).where(
        PracticeSession.id == session_id, PracticeSession.user_id == user.id
    )
    if lock:
        statement = statement.with_for_update()
    practice = await session.scalar(statement)
    if practice is None:
        raise AppError(404, "session_not_found", "No such session.")
    return practice


async def answer_question(  # noqa: PLR0913
    session: AsyncSession,
    user: User,
    session_id: uuid.UUID,
    *,
    question_id: uuid.UUID,
    key: str,
    time_ms: int,
    settings: Settings,
    now: datetime,
) -> AnswerResult:
    """Grade one answer and record everything that follows from it.

    Sending the same question again changes nothing and returns what the
    first answer did: a client that lost the response can ask again.
    """
    practice = await own_session(session, user, session_id, lock=True)
    if question_id not in practice.question_ids:
        raise AppError(
            404, "question_not_in_session", "No such question in the session."
        )
    earlier = await session.scalar(
        select(Attempt).where(
            Attempt.session_id == practice.id,
            Attempt.question_id == question_id,
        )
    )
    if earlier is not None:
        return await _result_of(session, earlier, practice, settings)

    question = await session.scalar(
        select(Question).where(Question.id == question_id).with_for_update()
    )
    assert question is not None  # a session's questions are never deleted
    is_correct = key == await correct_key_of(session, question_id)

    rating = await ensure_row(
        session,
        UserSubjectRating,
        {"user_id": user.id, "subject_id": question.subject_id},
        {"rating": settings.user_rating_start},
    )
    seen_before = await session.scalar(
        select(Attempt.id)
        .where(Attempt.user_id == user.id, Attempt.question_id == question_id)
        .limit(1)
    )
    if seen_before is None:
        change = rate_answer(
            user_rating=rating.rating,
            user_answers=rating.answers_count,
            question_rating=question.rating,
            question_answers=question.answers_count,
            is_correct=is_correct,
            settings=settings,
        )
        rating.rating = change.user_after
        rating.answers_count += 1
        question.rating = change.question_after
        question.answers_count += 1
        question.correct_count += int(is_correct)
    else:
        change = unrated_answer(rating.rating, question.rating)

    attempt = Attempt(
        user_id=user.id,
        question_id=question_id,
        session_id=practice.id,
        answer={"key": key},
        is_correct=is_correct,
        time_ms=time_ms,
        user_rating_before=change.user_before,
        user_rating_after=change.user_after,
        question_rating_before=change.question_before,
        question_rating_after=change.question_after,
        locale=user.locale,
        created_at=now,
    )
    session.add(attempt)
    xp = xp_of_attempt(attempt, settings)

    practice.correct_count += int(is_correct)
    practice.xp_earned += xp
    await _count_in_topic(session, user, question.topic_id, is_correct, now)
    await _count_in_day(session, user, now, xp=xp, questions=1)
    if not is_correct:
        await _schedule_review(session, user, question_id, now, settings)
    await session.flush()
    return await _result_of(session, attempt, practice, settings)


async def correct_key_of(session: AsyncSession, question_id: uuid.UUID) -> str:
    """The key of a question's correct option. It is the same in every
    language, so any translation tells.
    """
    payload = await session.scalar(
        select(QuestionTranslation.payload)
        .where(QuestionTranslation.question_id == question_id)
        .limit(1)
    )
    assert payload is not None  # every question has text
    correct = [o["key"] for o in payload["options"] if o["is_correct"]]
    assert len(correct) == 1
    return str(correct[0])


def xp_of_attempt(attempt: Attempt, settings: Settings) -> int:
    """The XP an answer earned, worked out from its row."""
    return xp_for_answer(
        is_correct=attempt.is_correct,
        question_rating=attempt.question_rating_before,
        user_rating=attempt.user_rating_before,
        settings=settings,
    )


async def _result_of(
    session: AsyncSession,
    attempt: Attempt,
    practice: PracticeSession,
    settings: Settings,
) -> AnswerResult:
    answered = await answered_count(session, practice.id)
    return AnswerResult(
        question_id=attempt.question_id,
        selected_key=str(attempt.answer["key"]),
        is_correct=attempt.is_correct,
        rating=RatingChange(
            user_before=attempt.user_rating_before,
            user_after=attempt.user_rating_after,
            question_before=attempt.question_rating_before,
            question_after=attempt.question_rating_after,
        ),
        xp_earned=xp_of_attempt(attempt, settings),
        session_complete=answered >= len(practice.question_ids),
    )


async def answered_count(session: AsyncSession, session_id: uuid.UUID) -> int:
    count = await session.scalar(
        select(func.count())
        .select_from(Attempt)
        .where(Attempt.session_id == session_id)
    )
    return count or 0


async def _count_in_topic(
    session: AsyncSession,
    user: User,
    topic_id: uuid.UUID,
    is_correct: bool,
    now: datetime,
) -> None:
    mastery = await ensure_row(
        session,
        UserTopicMastery,
        {"user_id": user.id, "topic_id": topic_id},
        {"last_seen_at": now},
    )
    mastery.total += 1
    mastery.correct += int(is_correct)
    mastery.last_seen_at = now


async def _count_in_day(  # noqa: PLR0913
    session: AsyncSession,
    user: User,
    now: datetime,
    *,
    xp: int = 0,
    questions: int = 0,
    sessions_finished: int = 0,
) -> None:
    """Add to the student's own calendar day that `now` falls on."""
    day = await ensure_row(
        session,
        DailyActivity,
        {"user_id": user.id, "local_date": local_date(now, user.timezone)},
    )
    day.xp += xp
    day.questions += questions
    day.sessions_finished += sessions_finished
    # Once met, a day stays met, even if the goal is raised later.
    goal = await daily_goal_of(session, user.id)
    day.goal_met = day.goal_met or day.questions >= goal


async def _schedule_review(
    session: AsyncSession,
    user: User,
    question_id: uuid.UUID,
    now: datetime,
    settings: Settings,
) -> None:
    """A wrong answer puts the question in the review queue, due on the
    first interval. If it was already there, it starts over.
    """
    schedule = first_review(now, settings)
    item = await ensure_row(
        session,
        ReviewItem,
        {"user_id": user.id, "question_id": question_id},
        {"due_at": schedule.due_at, "interval_days": schedule.interval_days},
    )
    item.due_at = schedule.due_at
    item.interval_days = schedule.interval_days


# ---- finishing ----


async def finish_session(
    session: AsyncSession,
    user: User,
    session_id: uuid.UUID,
    *,
    settings: Settings,
    now: datetime,
) -> PracticeSession:
    """Finish a session whose questions are all answered: the finishing
    XP, the day's finished session and the streak.

    Finishing again changes nothing.
    """
    practice = await own_session(session, user, session_id, lock=True)
    if practice.finished_at is not None:
        return practice
    answered = await answered_count(session, practice.id)
    if answered < len(practice.question_ids):
        raise AppError(
            409,
            "session_incomplete",
            "Answer every question before finishing the session.",
        )
    bonus = xp_for_finishing(settings)
    practice.finished_at = now
    practice.xp_earned += bonus
    await _count_in_day(session, user, now, xp=bonus, sessions_finished=1)

    streak = await ensure_row(session, Streak, {"user_id": user.id})
    after = streak_after_session(
        streak_state(streak), local_date(now, user.timezone)
    )
    streak.current = after.current
    streak.longest = after.longest
    streak.last_active_date = after.last_active_date
    await session.flush()
    return practice
