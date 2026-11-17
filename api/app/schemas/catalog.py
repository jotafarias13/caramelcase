"""Catalog: subjects and their topics, with the user's progress."""

from pydantic import BaseModel

from app.domain.mastery import MasteryLevel
from app.schemas.common import SubjectRef, TopicRef


class SubjectSummary(SubjectRef):
    topics_count: int
    questions_count: int
    # The user's rating in the subject; null before the first answer.
    rating: float | None
    answers_count: int
    is_current: bool


class SubjectsResponse(BaseModel):
    subjects: list[SubjectSummary]


class TopicWithMastery(TopicRef):
    mastery: MasteryLevel
    correct: int
    total: int
    accuracy: float  # 0 to 1


class SubjectDetail(SubjectSummary):
    # In the order they are shown. Only topics that have questions.
    topics: list[TopicWithMastery]
    # The first topic not yet mastered; null when all are.
    next_topic: str | None
