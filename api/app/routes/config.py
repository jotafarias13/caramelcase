"""Config: flags, plans, entitlements. Open to visitors."""

from fastapi import APIRouter

from app.db.session import SessionDep
from app.routes.dependencies import Now, OptionalUser, SettingsDep
from app.schemas.config import ConfigResponse
from app.services.config import config_response

router = APIRouter(tags=["config"])


@router.get("/config")
async def get_config(
    session: SessionDep, user: OptionalUser, settings: SettingsDep, now: Now
) -> ConfigResponse:
    return await config_response(session, user, settings=settings, now=now)
