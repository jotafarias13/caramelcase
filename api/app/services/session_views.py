"""What the API says about a practice session: the questions as the
student may see them, the feedback after an answer, and the summary.

The correct key, the reasons and the explanation are read only in
answer_feedback, which runs after the answer is recorded.
"""

import uuid
from collections import Counter
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    PracticeSession,
    Question,
    QuestionTranslation,
    Subject,
    Topic,
    User,
)
from app.domain.local_time import local_date
from app.domain.selection import shuffled_option_keys
from app.enums import Locale
from app.schemas.common import GoalModel, StreakModel, TopicRef
from app.schemas.practice import (
    AnswerRating,
    AnswerResponse,
    GivenAnswer,
    OptionModel,
    OptionReason,
    SessionQuestion,
    SessionResponse,
    SessionSummary,
    TopicToReview,
)
from app.services.practice import AnswerResult, xp_of_attempt
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


def topic_ref(topic: Topic) -> TopicRef:
    return TopicRef(
        slug=topic.slug, name_pt=topic.name_pt, name_en=topic.name_en
    )


async def translations_of(
    session: AsyncSession, question_ids: list[uuid.UUID], locale: Locale
) -> dict[uuid.UUID, QuestionTranslation]:
    """Each question's text in the locale, or in another language when
    it has none in that one.
    """
    rows = await session.scalars(
        select(QuestionTranslation).where(
            QuestionTranslation.question_id.in_(question_ids)
        )
    )
    chosen: dict[uuid.UUID, QuestionTranslation] = {}
    for row in rows:
        if row.locale == locale or row.question_id not in chosen:
            chosen[row.question_id] = row
    return chosen


async def session_response(
    session: AsyncSession,
    user: User,
    practice: PracticeSession,
    *,
    settings: Settings,
    now: datetime,
) -> SessionResponse:
    ids = list(practice.question_ids)
    questions = {
        q.id: q
        for q in await session.scalars(
            select(Question).where(Question.id.in_(ids))
        )
    }
    topics = {
        t.id: t
        for t in await session.scalars(
            select(Topic).where(
                Topic.id.in_({q.topic_id for q in questions.values()})
            )
        )
    }
    texts = await translations_of(session, ids, user.locale)
    attempts = {
        a.question_id: a
        for a in await session.scalars(
            select(Attempt).where(Attempt.session_id == practice.id)
        )
    }
    subject = await _subject_of(session, practice)

    shown = []
    for question_id in ids:
        question, text = questions[question_id], texts[question_id]
        attempt = attempts.get(question_id)
        shown.append(
            SessionQuestion(
                id=question_id,
                topic=topic_ref(topics[question.topic_id]),
                type=question.type,
                difficulty=question.difficulty_prior,
                locale=text.locale,
                stem=text.stem,
                code=text.code,
                code_language=text.code_language,
                options=_options_as_shown(text, practice.id),
                answer=_given(attempt, settings) if attempt else None,
            )
        )

    summary = None
    if practice.finished_at is not None:
        summary = await session_summary(
            session, user, practice, settings=settings, now=now
        )
    return SessionResponse(
        id=practice.id,
        mode=practice.mode,
        subject=subject_ref(subject),
        started_at=practice.started_at,
        finished_at=practice.finished_at,
        questions=shown,
        answered_count=len(attempts),
        correct_count=practice.correct_count,
        xp_earned=practice.xp_earned,
        summary=summary,
    )


def _options_as_shown(
    text: QuestionTranslation, session_id: uuid.UUID
) -> list[OptionModel]:
    """The options with their key and text only, in this session's order."""
    by_key = {o["key"]: o["text"] for o in text.payload["options"]}
    order = shuffled_option_keys(sorted(by_key), session_id, text.question_id)
    return [OptionModel(key=key, text=by_key[key]) for key in order]


def _given(attempt: Attempt, settings: Settings) -> GivenAnswer:
    return GivenAnswer(
        selected_key=attempt.answer["key"],
        is_correct=attempt.is_correct,
        xp_earned=xp_of_attempt(attempt, settings),
    )


async def _subject_of(
    session: AsyncSession, practice: PracticeSession
) -> Subject:
    subject = await session.get(Subject, practice.subject_id)
    assert subject is not None  # every V1 session has a subject
    return subject


async def answer_feedback(
    session: AsyncSession, user: User, result: AnswerResult
) -> AnswerResponse:
    """The response to an answer: now the student may see the key, the
    reason of every option and the explanation, in their language.
    """
    texts = await translations_of(session, [result.question_id], user.locale)
    text = texts[result.question_id]
    options = sorted(text.payload["options"], key=lambda o: o["key"])
    correct_key = next(o["key"] for o in options if o["is_correct"])
    return AnswerResponse(
        is_correct=result.is_correct,
        correct_key=correct_key,
        reasons=[
            OptionReason(key=o["key"], reason=o["reason"]) for o in options
        ],
        explanation=text.explanation,
        rating=AnswerRating(
            before=result.rating.user_before,
            after=result.rating.user_after,
            delta=result.rating.user_delta,
        ),
        xp_earned=result.xp_earned,
        session_complete=result.session_complete,
    )


async def session_summary(
    session: AsyncSession,
    user: User,
    practice: PracticeSession,
    *,
    settings: Settings,
    now: datetime,
) -> SessionSummary:
    """The summary of a finished session.

    The session's own numbers are stored. The streak, the goal and the
    level are the student's as of now, which is the moment of finishing
    when the summary is first shown.
    """
    subject = await _subject_of(session, practice)
    rating = await rating_change_in(session, practice, subject)
    assert rating is not None  # a finished session has answers
    today = local_date(now, user.timezone)
    total_xp = await total_xp_of(session, user.id)
    return SessionSummary(
        correct_count=practice.correct_count,
        total=len(practice.question_ids),
        xp_earned=practice.xp_earned,
        rating=rating,
        streak=StreakModel.of(await streak_of(session, user.id, today)),
        goal=GoalModel.of(await goal_today(session, user.id, today)),
        level_before=level_model(total_xp - practice.xp_earned, settings),
        level_after=level_model(total_xp, settings),
        topics_to_review=await _topics_to_review(session, practice.id),
        sessions_finished=await sessions_finished_by(session, user.id),
    )


async def _topics_to_review(
    session: AsyncSession, session_id: uuid.UUID
) -> list[TopicToReview]:
    """Topics with a wrong answer in the session, most errors first,
    then in the subject's order.
    """
    topics = list(
        await session.scalars(
            select(Topic)
            .join(Question, Question.topic_id == Topic.id)
            .join(Attempt, Attempt.question_id == Question.id)
            .where(
                Attempt.session_id == session_id,
                Attempt.is_correct.is_(False),
            )
        )
    )
    wrong = Counter(topic.id for topic in topics)
    unique = {topic.id: topic for topic in topics}.values()
    ordered = sorted(unique, key=lambda t: (-wrong[t.id], t.sort_order))
    return [
        TopicToReview(
            slug=t.slug,
            name_pt=t.name_pt,
            name_en=t.name_en,
            wrong_count=wrong[t.id],
        )
        for t in ordered
    ]
