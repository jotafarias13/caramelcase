"""V3 behind flags: plans, subscriptions, limits, ads, the tutor, referrals."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import AdEventKind, SubscriptionStatus, TutorRole


class Plan(Base):
    """A plan, its prices and what it allows.

    The rows mirror settings.plans: seeding writes them from there.
    """

    __tablename__ = "plans"

    # One of app.enums.PlanKey.
    key: Mapped[str] = mapped_column(String(32), unique=True)
    price_month_brl: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    # Null until the price of the yearly and of the semester pass is set.
    price_year_brl: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    price_semester_brl: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    # The fields of app.settings.PlanLimits.
    limits: Mapped[dict[str, Any]]


class Subscription(Base):
    """What a user has paid for. The only source of truth for it."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        # A provider's webhook finds its row by this pair, so a repeated
        # webhook updates the same row.
        UniqueConstraint("provider", "provider_ref"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    plan_key: Mapped[str] = mapped_column(String(32), ForeignKey("plans.key"))
    status: Mapped[SubscriptionStatus]
    # The billing provider: "mock", "stripe", or "manual" for a plan
    # granted by hand.
    provider: Mapped[str] = mapped_column(String(32))
    # The provider's id for the subscription or payment; null for a
    # manual grant.
    provider_ref: Mapped[str | None] = mapped_column(String(255))
    # The plan is held until then. Null before the first payment.
    current_period_end: Mapped[datetime | None]


class UsageCounter(Base):
    """What a user consumed on one day of their own calendar.

    The daily limits of a plan are enforced against it.
    """

    __tablename__ = "usage_counters"
    __table_args__ = (UniqueConstraint("user_id", "local_date"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    local_date: Mapped[date]
    questions_answered: Mapped[int] = mapped_column(default=0)
    tutor_messages: Mapped[int] = mapped_column(default=0)


class AdEvent(Base):
    """One step of an ad break or of a Beat the ad challenge."""

    __tablename__ = "ad_events"
    __table_args__ = (Index(None, "user_id", "created_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    kind: Mapped[AdEventKind]
    meta: Mapped[dict[str, Any]] = mapped_column(default=dict)


class TutorThread(Base):
    """A conversation with the tutor, about a question or about a topic."""

    __tablename__ = "tutor_threads"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.id")
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id"))


class TutorMessage(Base):
    __tablename__ = "tutor_messages"
    __table_args__ = (Index(None, "thread_id", "created_at"),)

    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tutor_threads.id", ondelete="CASCADE")
    )
    role: Mapped[TutorRole]
    content: Mapped[str] = mapped_column(Text)


class Referral(Base):
    """One student invited by another."""

    __tablename__ = "referrals"

    referrer_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # A student is invited once.
    referred_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    # When the invited student finished their first session.
    completed_at: Mapped[datetime | None]
    # When both students got the reward.
    rewarded_at: Mapped[datetime | None]
