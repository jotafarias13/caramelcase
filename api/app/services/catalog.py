"""The catalog: published subjects and their topics, with the user's
rating and mastery.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Question,
    Subject,
    Topic,
    User,
    UserSubjectRating,
    UserTopicMastery,
)
from app.domain.mastery import MasteryLevel, accuracy, mastery_level
from app.enums import QuestionStatus, SubjectStatus
from app.schemas.catalog import (
    SubjectDetail,
    SubjectSummary,
    TopicWithMastery,
)
from app.services.practice import published_subject
from app.services.progress import subject_ref
from app.settings import Settings


async def published_subjects(session: AsyncSession) -> list[Subject]:
    """In catalog order."""
    rows = await session.scalars(
        select(Subject)
        .where(Subject.status == SubjectStatus.PUBLISHED)
        .order_by(Subject.sort_order)
    )
    return list(rows)


async def playable_subjects(session: AsyncSession) -> list[Subject]:
    """The published subjects that have at least one published question."""
    counts = await _question_counts(session)
    return [s for s in await published_subjects(session) if s.id in counts]


async def ratings_of(
    session: AsyncSession, user_id: uuid.UUID
) -> dict[uuid.UUID, UserSubjectRating]:
    """Subject id -> the user's rating row."""
    rows = await session.scalars(
        select(UserSubjectRating).where(UserSubjectRating.user_id == user_id)
    )
    return {row.subject_id: row for row in rows}


async def _question_counts(
    session: AsyncSession,
) -> dict[uuid.UUID, dict[uuid.UUID, int]]:
    """Subject id -> topic id -> published questions."""
    rows = await session.execute(
        select(Question.subject_id, Question.topic_id, func.count())
        .where(Question.status == QuestionStatus.PUBLISHED)
        .group_by(Question.subject_id, Question.topic_id)
    )
    counts: dict[uuid.UUID, dict[uuid.UUID, int]] = {}
    for subject_id, topic_id, count in rows:
        counts.setdefault(subject_id, {})[topic_id] = count
    return counts


def _summary(
    subject: Subject,
    user: User,
    rating: UserSubjectRating | None,
    per_topic: dict[uuid.UUID, int],
) -> SubjectSummary:
    # A rating row exists from the first answer on.
    answers = rating.answers_count if rating else 0
    return SubjectSummary(
        **subject_ref(subject).model_dump(),
        topics_count=len(per_topic),
        questions_count=sum(per_topic.values()),
        rating=rating.rating if rating and answers else None,
        answers_count=answers,
        is_current=subject.id == user.current_subject_id,
    )


async def list_subjects(
    session: AsyncSession, user: User
) -> list[SubjectSummary]:
    ratings = await ratings_of(session, user.id)
    counts = await _question_counts(session)
    return [
        _summary(
            subject, user, ratings.get(subject.id), counts.get(subject.id, {})
        )
        for subject in await published_subjects(session)
    ]


async def subject_detail(
    session: AsyncSession, user: User, slug: str, settings: Settings
) -> SubjectDetail:
    """A subject with its topics, in order, and the user's mastery of
    each. A topic without published questions is left out: it could
    never be practiced.
    """
    subject = await published_subject(session, slug)
    ratings = await ratings_of(session, user.id)
    per_topic = (await _question_counts(session)).get(subject.id, {})
    topics = await session.scalars(
        select(Topic)
        .where(Topic.subject_id == subject.id, Topic.id.in_(per_topic))
        .order_by(Topic.sort_order)
    )
    mastery = {
        row.topic_id: row
        for row in await session.scalars(
            select(UserTopicMastery).where(
                UserTopicMastery.user_id == user.id,
                UserTopicMastery.topic_id.in_(per_topic),
            )
        )
    }

    shown = []
    for topic in topics:
        row = mastery.get(topic.id)
        correct = row.correct if row else 0
        total = row.total if row else 0
        shown.append(
            TopicWithMastery(
                slug=topic.slug,
                name_pt=topic.name_pt,
                name_en=topic.name_en,
                mastery=mastery_level(correct, total, settings),
                correct=correct,
                total=total,
                accuracy=accuracy(correct, total),
            )
        )
    summary = _summary(subject, user, ratings.get(subject.id), per_topic)
    not_mastered = [
        t.slug for t in shown if t.mastery is not MasteryLevel.MASTERED
    ]
    return SubjectDetail(
        **summary.model_dump(),
        topics=shown,
        next_topic=not_mastered[0] if not_mastered else None,
    )
