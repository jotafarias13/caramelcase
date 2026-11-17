"""What students send back: reports about a question, and the web app's
product events.
"""

import json
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event, PracticeSession, QuestionReport, User
from app.enums import ReportReason
from app.errors import AppError
from app.schemas.stats import EventIn
from app.settings import Settings


async def report_question(  # noqa: PLR0913
    session: AsyncSession,
    user: User,
    question_id: uuid.UUID,
    *,
    reason: ReportReason,
    comment: str | None,
    settings: Settings,
) -> QuestionReport:
    """Record a report about a question the user was served.

    A question that was never in one of their sessions is a 404, like
    one that does not exist: reports do not tell which ids are real.
    """
    if comment and len(comment) > settings.report_comment_max_chars:
        raise AppError(
            422,
            "validation_error",
            f"comment: at most {settings.report_comment_max_chars} characters",
        )
    was_served = await session.scalar(
        select(PracticeSession.id)
        .where(
            PracticeSession.user_id == user.id,
            PracticeSession.question_ids.contains([question_id]),
        )
        .limit(1)
    )
    if was_served is None:
        raise AppError(404, "question_not_found", "No such question.")
    report = QuestionReport(
        question_id=question_id,
        user_id=user.id,
        locale=user.locale,
        reason=reason,
        comment=comment or None,
    )
    session.add(report)
    await session.flush()
    return report


async def record_events(
    session: AsyncSession,
    user: User | None,
    events: list[EventIn],
    settings: Settings,
    now: datetime,
) -> int:
    """Store a batch of the web app's events. All or nothing."""
    if len(events) > settings.events_max_batch:
        raise AppError(
            422,
            "validation_error",
            f"events: at most {settings.events_max_batch} at a time",
        )
    for event in events:
        size = len(json.dumps(event.props, default=str))
        if size > settings.event_props_max_bytes:
            raise AppError(
                422,
                "validation_error",
                f"events: the props of {event.name} are too large",
            )
    for event in events:
        session.add(
            Event(
                user_id=user.id if user else None,
                name=event.name,
                props=event.props,
                # A client's clock can be ahead; an event is never later
                # than its arrival.
                occurred_at=min(event.occurred_at, now),
            )
        )
    await session.flush()
    return len(events)
