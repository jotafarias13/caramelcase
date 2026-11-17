"""Practice: start a session, answer its questions, finish it.

The server grades. GET and POST /sessions return the questions without
their answers; the correct key, the reasons and the explanation come
back from the answer route, one question at a time.
"""

import random
import uuid

from fastapi import APIRouter

from app.db.session import SessionDep
from app.routes.dependencies import CurrentUser, Now, SettingsDep
from app.schemas.practice import (
    AnswerRequest,
    AnswerResponse,
    SessionCreate,
    SessionResponse,
    SessionSummary,
)
from app.services.practice import (
    answer_question,
    finish_session,
    own_session,
    start_session,
)
from app.services.session_views import (
    answer_feedback,
    session_response,
    session_summary,
)

router = APIRouter(prefix="/sessions", tags=["practice"])


@router.post("")
async def create_session(
    body: SessionCreate,
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
    now: Now,
) -> SessionResponse:
    """Start a session in a subject. If the user left one unfinished
    there, that one comes back instead.
    """
    practice = await start_session(
        session,
        user,
        body.subject,
        settings=settings,
        now=now,
        rng=random.Random(),
    )
    view = await session_response(
        session, user, practice, settings=settings, now=now
    )
    await session.commit()
    return view


@router.get("/{session_id}")
async def get_session(
    session_id: uuid.UUID,
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
    now: Now,
) -> SessionResponse:
    """A session as it stands, to resume it or to show its summary."""
    practice = await own_session(session, user, session_id)
    return await session_response(
        session, user, practice, settings=settings, now=now
    )


@router.post("/{session_id}/answers")
async def post_answer(
    session_id: uuid.UUID,
    body: AnswerRequest,
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
    now: Now,
) -> AnswerResponse:
    """Answer one question. Answering it again returns the first result."""
    result = await answer_question(
        session,
        user,
        session_id,
        question_id=body.question_id,
        key=body.key,
        time_ms=body.time_ms,
        settings=settings,
        now=now,
    )
    feedback = await answer_feedback(session, user, result)
    await session.commit()
    return feedback


@router.post("/{session_id}/finish")
async def post_finish(
    session_id: uuid.UUID,
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
    now: Now,
) -> SessionSummary:
    """Finish a session whose questions are all answered."""
    practice = await finish_session(
        session, user, session_id, settings=settings, now=now
    )
    summary = await session_summary(
        session, user, practice, settings=settings, now=now
    )
    await session.commit()
    return summary
