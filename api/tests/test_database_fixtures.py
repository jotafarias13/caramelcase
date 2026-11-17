"""The database fixtures themselves: rollback, and requests in the test's
transaction.
"""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FeatureFlag
from app.db.session import SessionDep, engine
from app.enums import FlagState
from tests.support.database import rollback_session


async def _count_flags(session: AsyncSession) -> int:
    count = await session.scalar(select(func.count()).select_from(FeatureFlag))
    return count or 0


@pytest.mark.usefixtures("database")
async def test_what_a_test_commits_is_gone_when_it_ends() -> None:
    async with rollback_session(engine) as first:
        first.add(FeatureFlag(key="probe"))
        await first.commit()
        assert await _count_flags(first) == 1

    async with rollback_session(engine) as second:
        assert await _count_flags(second) == 0


async def test_a_request_and_the_test_see_each_others_rows(
    client: AsyncClient, app: FastAPI, session: AsyncSession
) -> None:
    @app.post("/test-only/flags/switch-on")
    async def switch_every_flag_on(db: SessionDep) -> int:
        flags = list(await db.scalars(select(FeatureFlag)))
        for flag in flags:
            flag.state = FlagState.ON
        db.add(FeatureFlag(key="added_by_the_request"))
        await db.commit()
        return len(flags)

    flag = FeatureFlag(key="added_by_the_test")
    session.add(flag)

    response = await client.post("/test-only/flags/switch-on")

    assert response.json() == 1
    await session.refresh(flag)
    assert flag.state is FlagState.ON
    assert await _count_flags(session) == 2
