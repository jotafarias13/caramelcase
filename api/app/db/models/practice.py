"""Practice: sessions, answers, and the progress worked out from them."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import ForeignKey, Index, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import Locale, SessionMode


class PracticeSession(Base):
    """One run of questions. The list is fixed when the session starts."""

    __tablename__ = "practice_sessions"
    __table_args__ = (Index(None, "user_id", "started_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    # Null when the session mixes subjects, as a review or an exam track can.
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subjects.id")
    )
    mode: Mapped[SessionMode] = mapped_column(default=SessionMode.PRACTICE)
    # In the order the questions are served.
    question_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(Uuid))
    started_at: Mapped[datetime]
    finished_at: Mapped[datetime | None]
    correct_count: Mapped[int] = mapped_column(default=0)
    xp_earned: Mapped[int] = mapped_column(default=0)


class Attempt(Base):
    """One answer to one question.

    This is the raw history: ratings, mastery, activity and streaks can be
    rebuilt from it.
    """

    __tablename__ = "attempts"
    __table_args__ = (
        # A question is answered once in a session, so a repeated request
        # cannot count twice.
        UniqueConstraint("session_id", "question_id"),
        Index(None, "user_id", "question_id"),
        Index(None, "user_id", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"))
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("practice_sessions.id", ondelete="CASCADE")
    )
    # What the student answered. For multiple choice: {"key": "b"}.
    answer: Mapped[dict[str, Any]]
    is_correct: Mapped[bool]
    time_ms: Mapped[int]
    # The two ratings around this answer. Only a student's first attempt
    # at a question moves them; otherwise before and after are equal.
    user_rating_before: Mapped[float]
    user_rating_after: Mapped[float]
    question_rating_before: Mapped[float]
    question_rating_after: Mapped[float]
    # The language the student read the question in.
    locale: Mapped[Locale]


class UserSubjectRating(Base):
    """A student's rating in one subject."""

    __tablename__ = "user_subject_ratings"
    __table_args__ = (UniqueConstraint("user_id", "subject_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))
    rating: Mapped[float]
    answers_count: Mapped[int] = mapped_column(default=0)


class UserTopicMastery(Base):
    """A student's correct and total answers in one topic."""

    __tablename__ = "user_topic_mastery"
    __table_args__ = (UniqueConstraint("user_id", "topic_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"))
    correct: Mapped[int] = mapped_column(default=0)
    total: Mapped[int] = mapped_column(default=0)
    last_seen_at: Mapped[datetime]


class DailyActivity(Base):
    """What a student did on one day of their own calendar.

    It drives the daily goal, the streak and the profile calendar.
    """

    __tablename__ = "daily_activity"
    __table_args__ = (UniqueConstraint("user_id", "local_date"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    # The date in the student's timezone.
    local_date: Mapped[date]
    xp: Mapped[int] = mapped_column(default=0)
    questions: Mapped[int] = mapped_column(default=0)
    # One finished session makes the day count toward the streak.
    sessions_finished: Mapped[int] = mapped_column(default=0)
    goal_met: Mapped[bool] = mapped_column(default=False)


class Streak(Base):
    """A student's streak of days. One row per user."""

    __tablename__ = "streaks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    current: Mapped[int] = mapped_column(default=0)
    longest: Mapped[int] = mapped_column(default=0)
    last_active_date: Mapped[date | None]
    # Freezes held (V2, behind streak_freeze).
    freezes: Mapped[int] = mapped_column(default=0)
    # The streak that was lost and when, while it can still be repaired
    # (V3, behind streak_repair). Null when there is nothing to repair.
    lost_length: Mapped[int | None]
    lost_at: Mapped[datetime | None]


class ReviewItem(Base):
    """A question the student missed, waiting to be reviewed.

    Written from V1 on every wrong answer, so V2 starts with data.
    """

    __tablename__ = "review_items"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id"),
        Index(None, "user_id", "due_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"))
    due_at: Mapped[datetime]
    interval_days: Mapped[int]
    # Times the student got it wrong again in a review.
    lapses: Mapped[int] = mapped_column(default=0)


class Lives(Base):
    """A student's lives (V2, behind lives). One row per user."""

    __tablename__ = "lives"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    remaining: Mapped[int]
    # When the countdown to the next life started; null with every life.
    refill_started_at: Mapped[datetime | None]
