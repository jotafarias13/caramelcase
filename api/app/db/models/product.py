"""Feature flags and first-party product analytics."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import FlagState


class FeatureFlag(Base):
    """The switch of a V2 or V3 feature: off, staff only, or on."""

    __tablename__ = "feature_flags"

    # One of app.enums.FlagKey.
    key: Mapped[str] = mapped_column(String(64), unique=True)
    state: Mapped[FlagState] = mapped_column(default=FlagState.OFF)


class Event(Base):
    """Something that happened in the product.

    The web app sends these in batches. The API also records its own here,
    such as a streak freeze earned or used and a streak repair.
    """

    __tablename__ = "events"
    __table_args__ = (
        Index(None, "user_id", "occurred_at"),
        Index(None, "name", "occurred_at"),
    )

    # Null for an event sent before the visitor has a guest account.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(64))
    props: Mapped[dict[str, Any]] = mapped_column(default=dict)
    # When it happened. created_at is when the API received it, which is
    # later for an event that waited in a batch.
    occurred_at: Mapped[datetime]
