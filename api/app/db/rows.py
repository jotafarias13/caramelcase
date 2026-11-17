"""Get-or-create for the tables that hold one row per user and something:
a day's activity, a subject's rating, a topic's mastery, the streak.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


async def ensure_row[Model: Base](
    session: AsyncSession,
    model: type[Model],
    keys: dict[str, Any],
    defaults: dict[str, Any] | None = None,
) -> Model:
    """Return the row with these key columns, creating it if needed.

    The row comes back locked until the transaction ends, so two requests
    of one user cannot both add to the same counter and lose one of the
    additions. keys must be the columns of a unique constraint: INSERT
    ... ON CONFLICT DO NOTHING is what makes a simultaneous first write
    safe.
    """
    values = {**keys, **(defaults or {})}
    await session.execute(
        insert(model)
        .values(**values)
        .on_conflict_do_nothing(index_elements=list(keys))
    )
    row = await session.scalar(
        select(model)
        .filter_by(**keys)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    assert row is not None
    return row
