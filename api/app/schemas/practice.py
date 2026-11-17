"""Practice: sessions, answers and the summary of a finished session.

SessionQuestion is what a student sees before answering, so it has no
field for the correct key, the reasons or the explanation. Those leave
the API only in AnswerResponse, after the student commits.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.question_doc import OptionKey
from app.enums import Locale, QuestionType, SessionMode
from app.schemas.common import (
    GoalModel,
    LevelModel,
    RatingChangeModel,
    StreakModel,
    SubjectRef,
    TopicRef,
)


class SessionCreate(BaseModel):
    subject: str = Field(description="A published subject's slug.")
    mode: Literal["practice"] = "practice"


class OptionModel(BaseModel):
    key: OptionKey
    text: str


class GivenAnswer(BaseModel):
    """What the student answered to a question of the session."""

    selected_key: OptionKey
    is_correct: bool
    xp_earned: int


class SessionQuestion(BaseModel):
    id: uuid.UUID
    topic: TopicRef
    type: QuestionType
    difficulty: int = Field(description="1 (easiest) to 5.")
    locale: Locale
    stem: str
    code: str | None
    code_language: str | None
    # In the order to show them. The order is shuffled per session and
    # stays the same when the session is loaded again.
    options: list[OptionModel]
    # Null until the student answers.
    answer: GivenAnswer | None


class TopicToReview(TopicRef):
    wrong_count: int


class SessionSummary(BaseModel):
    """A finished session, for the summary screen."""

    correct_count: int
    total: int
    xp_earned: int
    rating: RatingChangeModel
    streak: StreakModel
    goal: GoalModel
    level_before: LevelModel
    level_after: LevelModel
    # Topics with a wrong answer in this session, most errors first.
    topics_to_review: list[TopicToReview]
    # Sessions the user has finished, this one included. 1 is the cue to
    # offer a guest to save their progress.
    sessions_finished: int


class SessionResponse(BaseModel):
    id: uuid.UUID
    mode: SessionMode
    subject: SubjectRef
    started_at: datetime
    finished_at: datetime | None
    questions: list[SessionQuestion]
    answered_count: int
    correct_count: int
    xp_earned: int
    # Null until the session is finished.
    summary: SessionSummary | None


class AnswerRequest(BaseModel):
    question_id: uuid.UUID
    key: OptionKey
    time_ms: int = Field(ge=0, le=86_400_000)


class OptionReason(BaseModel):
    key: OptionKey
    reason: str


class AnswerRating(BaseModel):
    """The student's rating in the subject around this answer. Only a
    first attempt at a question moves it.
    """

    before: float
    after: float
    delta: float


class AnswerResponse(BaseModel):
    is_correct: bool
    correct_key: OptionKey
    # One per option, whatever the user's show_option_reasons says.
    reasons: list[OptionReason]
    explanation: str
    rating: AnswerRating
    xp_earned: int
    session_complete: bool
