"""What the alembic command line runs: it connects the migrations to the
app's settings (the database URL) and models (what the tables should be).
"""

import asyncio
from logging.config import fileConfig
from typing import Literal

import sqlalchemy as sa
from alembic import context
from alembic.autogenerate.api import AutogenContext
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.db import models  # noqa: F401  registers every table on Base
from app.db.base import Base
from app.settings import get_settings

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

target_metadata = Base.metadata


def render_item(
    type_: str, item: object, autogen: AutogenContext
) -> str | Literal[False]:
    """Write two column types into a new migration as the database sees
    them, without the options that only matter to Python.

    An enum column is a VARCHAR: the migration would otherwise list the
    enum's values of that day, which the database knows nothing about.
    """
    if type_ != "type":
        return False
    if isinstance(item, sa.Enum) and not item.native_enum:
        return f"sa.String(length={item.length})"
    if isinstance(item, postgresql.JSONB):
        autogen.imports.add("from sqlalchemy.dialects import postgresql")
        return "postgresql.JSONB()"
    return False


def run_migrations_offline() -> None:
    """Print the SQL instead of running it: alembic upgrade head --sql."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_server_default=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(
        get_settings().database_url, poolclass=NullPool
    )
    async with engine.connect() as connection:
        await connection.run_sync(_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
