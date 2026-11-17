"""Stats and activity: the numbers on Home and on the profile."""

from datetime import date

from fastapi import APIRouter

from app.db.session import SessionDep
from app.routes.dependencies import CurrentUser, Now, SettingsDep
from app.schemas.stats import ActivityResponse, StatsResponse
from app.services.stats import user_activity, user_stats

router = APIRouter(prefix="/me", tags=["stats"])


@router.get("/stats")
async def get_stats(
    session: SessionDep, user: CurrentUser, settings: SettingsDep, now: Now
) -> StatsResponse:
    return await user_stats(session, user, settings=settings, now=now)


@router.get("/activity")
async def get_activity(
    session: SessionDep,
    user: CurrentUser,
    settings: SettingsDep,
    now: Now,
    start: date | None = None,
    end: date | None = None,
) -> ActivityResponse:
    """The days with activity from start to end, both included. Without
    them: the current month of the user's calendar.
    """
    return await user_activity(
        session, user, start=start, end=end, settings=settings, now=now
    )
