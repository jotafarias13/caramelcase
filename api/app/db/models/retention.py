"""V2 behind flags: leagues, achievements and mock exams."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import LeagueOutcome


class LeagueWeek(Base):
    """One week of the leagues."""

    __tablename__ = "league_weeks"

    # The week's first day.
    week_start: Mapped[date] = mapped_column(unique=True)
    # When promotions and relegations were worked out; null while the
    # week is still open.
    closed_at: Mapped[datetime | None]


class LeagueMembership(Base):
    """A student's league in one week, and the XP they earned in it."""

    __tablename__ = "league_memberships"
    __table_args__ = (
        UniqueConstraint("league_week_id", "user_id"),
        Index(None, "league_week_id", "tier", "cohort"),
    )

    league_week_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("league_weeks.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # One of settings.league_tiers.
    tier: Mapped[str] = mapped_column(String(32))
    # Which league of that tier: a tier is split into leagues of
    # settings.league_size students.
    cohort: Mapped[int]
    xp: Mapped[int] = mapped_column(default=0)
    # Both are set when the week closes.
    final_rank: Mapped[int | None]
    outcome: Mapped[LeagueOutcome | None]


class Achievement(Base):
    """A badge a student can unlock. Its name is in the interface copy."""

    __tablename__ = "achievements"

    key: Mapped[str] = mapped_column(String(64), unique=True)
    sort_order: Mapped[int]


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("achievements.id")
    )
    unlocked_at: Mapped[datetime]
    # When the student saw the unlock; until then the badge shows as new.
    seen_at: Mapped[datetime | None]


class ExamTemplate(Base):
    """The recipe of a timed mock exam."""

    __tablename__ = "exam_templates"

    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name_pt: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str] = mapped_column(String(120))
    # The exam track it belongs to (V3, behind exam_tracks); null outside
    # a track.
    track: Mapped[str | None] = mapped_column(String(64), index=True)
    # Null when the exam covers several subjects.
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subjects.id")
    )
    duration_min: Mapped[int]
    # How many questions come from each subject and topic.
    composition: Mapped[dict[str, Any]]


class ExamAttempt(Base):
    """One sitting of a mock exam.

    Its questions and answers are in the practice session of mode "exam".
    """

    __tablename__ = "exam_attempts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exam_template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exam_templates.id"), index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("practice_sessions.id", ondelete="CASCADE"), unique=True
    )
    # The three below are null until the exam is submitted.
    submitted_at: Mapped[datetime | None]
    # Correct answers.
    score: Mapped[int | None]
    # Correct and total answers per topic.
    results: Mapped[dict[str, Any] | None]
