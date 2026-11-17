"""Account: the user's own data and preferences."""

from fastapi import APIRouter, Response

from app.db.session import SessionDep
from app.routes.dependencies import (
    CurrentUser,
    Now,
    SettingsDep,
    clear_session_cookie,
)
from app.schemas.account import ExportResponse, MeResponse, SettingsPatch
from app.services.account import (
    change_settings,
    delete_user,
    export_user,
    me_response,
)

router = APIRouter(prefix="/me", tags=["account"])


@router.get("")
async def get_me(session: SessionDep, user: CurrentUser) -> MeResponse:
    return await me_response(session, user)


@router.patch("/settings")
async def patch_settings(
    body: SettingsPatch,
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
    now: Now,
) -> MeResponse:
    """Change preferences and profile fields. Only the fields sent
    change.
    """
    await change_settings(session, user, body, settings=settings, now=now)
    me = await me_response(session, user)
    await session.commit()
    return me


@router.get("/export")
async def export_me(
    session: SessionDep, user: CurrentUser, now: Now
) -> ExportResponse:
    """Everything stored about the user."""
    return await export_user(session, user, now)


@router.delete("", status_code=204)
async def delete_me(
    response: Response,
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
) -> None:
    """Erase the account and everything that belongs to it."""
    await delete_user(session, user)
    await session.commit()
    clear_session_cookie(response, settings)
