"""Stats, activity, reports and events."""

import uuid
from datetime import date, datetime
from typing import Annotated, Any

from pydantic import AwareDatetime, BaseModel, StringConstraints

from app.enums import ReportReason
from app.schemas.common import (
    GoalModel,
    LevelModel,
    RatingChangeModel,
    StreakModel,
    SubjectRef,
)


class SubjectRating(SubjectRef):
    rating: float | None  # null before the first answer
    answers_count: int


class StatsResponse(BaseModel):
    # Today in the user's timezone.
    today: date
    level: LevelModel
    streak: StreakModel
    goal: GoalModel
    questions_answered: int
    correct_answers: int
    accuracy: float  # 0 to 1
    sessions_finished: int
    # Every published subject, in catalog order.
    subjects: list[SubjectRating]
    # From the last finished session; null before the first.
    last_rating_change: RatingChangeModel | None


class ActivityDay(BaseModel):
    date: date
    xp: int
    questions: int
    sessions_finished: int
    goal_met: bool


class ActivityResponse(BaseModel):
    today: date
    start: date
    end: date
    # Only the days with activity, oldest first.
    days: list[ActivityDay]


class ReportRequest(BaseModel):
    reason: ReportReason
    comment: (
        Annotated[str, StringConstraints(strip_whitespace=True)] | None
    ) = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime


class EventIn(BaseModel):
    name: Annotated[
        str, StringConstraints(pattern=r"^[a-z0-9_.]+$", max_length=64)
    ]
    props: dict[str, Any] = {}
    occurred_at: AwareDatetime


class EventsRequest(BaseModel):
    events: list[EventIn]


class EventsResponse(BaseModel):
    accepted: int
