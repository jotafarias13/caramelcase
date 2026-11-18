"""Reports about a question, and the web app's product events."""

import uuid

from fastapi import APIRouter, Depends

from app.db.session import SessionDep
from app.routes.dependencies import (
    CurrentUser,
    Now,
    OptionalUser,
    SettingsDep,
    limit_reports,
)
from app.schemas.stats import (
    EventsRequest,
    EventsResponse,
    ReportRequest,
    ReportResponse,
)
from app.services.feedback import record_events, report_question

router = APIRouter()


@router.post(
    "/questions/{question_id}/report",
    status_code=201,
    tags=["reports"],
    dependencies=[Depends(limit_reports)],
)
async def post_report(
    question_id: uuid.UUID,
    body: ReportRequest,
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
) -> ReportResponse:
    """Say that something is wrong with a question the user was served."""
    report = await report_question(
        session,
        user,
        question_id,
        reason=body.reason,
        comment=body.comment,
        settings=settings,
    )
    await session.commit()
    return ReportResponse(id=report.id, created_at=report.created_at)


@router.post("/events", status_code=202, tags=["events"])
async def post_events(
    body: EventsRequest,
    session: SessionDep,
    user: OptionalUser,
    settings: SettingsDep,
    now: Now,
) -> EventsResponse:
    """A batch of product events. Open to visitors: the landing page
    sends events before there is a guest.
    """
    accepted = await record_events(session, user, body.events, settings, now)
    await session.commit()
    return EventsResponse(accepted=accepted)
