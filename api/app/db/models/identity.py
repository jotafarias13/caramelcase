"""Identity: users, how they sign in, and their preferences."""

import uuid
from datetime import datetime, time

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import AuthProvider, Locale, PushPlatform, Theme, UserRole


class User(Base):
    """A student or a staff member.

    A guest is a real row: signing in upgrades it and keeps its history.
    """

    __tablename__ = "users"

    # Lower case. Null for a guest.
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(80))
    locale: Mapped[Locale] = mapped_column(default=Locale.PT_BR)
    # IANA name such as "America/Sao_Paulo". The student's days, daily goal
    # and streak follow it.
    timezone: Mapped[str] = mapped_column(String(64))
    is_guest: Mapped[bool] = mapped_column(default=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    # Onboarding step 2: optional free text.
    university: Mapped[str | None] = mapped_column(String(120))
    course: Mapped[str | None] = mapped_column(String(120))
    # The subject Home shows.
    current_subject_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subjects.id")
    )
    # The code in the student's invite link (V3, behind referral).
    referral_code: Mapped[str | None] = mapped_column(String(16), unique=True)


class AuthIdentity(Base):
    """One way a user signs in: a Google account or an email address."""

    __tablename__ = "auth_identities"
    __table_args__ = (UniqueConstraint("provider", "provider_subject"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[AuthProvider]
    # Google's "sub" claim, or the address for an email magic link.
    provider_subject: Mapped[str] = mapped_column(String(320))


class AuthSession(Base):
    """A signed-in browser or device.

    The token is a random 256-bit value; only its SHA-256 hash is stored.
    """

    __tablename__ = "sessions_auth"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime]


class MagicLink(Base):
    """A single-use sign-in link sent by email."""

    __tablename__ = "magic_links"

    email: Mapped[str] = mapped_column(String(320), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime]
    used_at: Mapped[datetime | None]


class UserSettings(Base):
    """A user's preferences. One row per user."""

    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    # Questions a day: one of settings.daily_goal_options.
    daily_goal: Mapped[int]
    theme: Mapped[Theme] = mapped_column(default=Theme.SYSTEM)
    show_option_reasons: Mapped[bool] = mapped_column(default=True)
    # Notification preferences (V2, behind reminders). Both are opt-in.
    daily_reminder: Mapped[bool] = mapped_column(default=False)
    weekly_email: Mapped[bool] = mapped_column(default=False)
    # Local time of the daily reminder; null means the default hour.
    reminder_time: Mapped[time | None]


class UserSubject(Base):
    """A subject the student chose to study."""

    __tablename__ = "user_subjects"
    __table_args__ = (UniqueConstraint("user_id", "subject_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))


class PushSubscription(Base):
    """Where to send a user's push notifications (V2, behind reminders)."""

    __tablename__ = "push_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    platform: Mapped[PushPlatform]
    # The Web Push endpoint URL, or the device token on Android and iOS.
    endpoint: Mapped[str] = mapped_column(Text, unique=True)
    # Web Push encryption keys; null on Android and iOS.
    p256dh: Mapped[str | None] = mapped_column(String(255))
    auth: Mapped[str | None] = mapped_column(String(255))
