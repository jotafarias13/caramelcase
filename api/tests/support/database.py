"""Database helpers: sessions that roll back, and scratch databases.

A test that asks for the `session` fixture runs inside one transaction on
one connection, and that transaction is never committed. The test's
session and the session of each request join it with savepoints: their
commit() only releases a savepoint, so nothing reaches the next test.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


@asynccontextmanager
async def rollback_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Open a session whose writes are all rolled back on exit."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = open_session(connection)
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


def open_session(connection: AsyncConnection) -> AsyncSession:
    """A session like the app's that joins the connection's transaction."""
    return AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


def connection_of(session: AsyncSession) -> AsyncConnection:
    """The connection a session from rollback_session is bound to."""
    assert isinstance(session.bind, AsyncConnection)
    return session.bind


async def run_sql(database_url: str, sql: str) -> list[tuple[object, ...]]:
    """Run one statement on its own connection, outside any transaction."""
    engine = create_async_engine(
        database_url, isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text(sql))
            if not result.returns_rows:
                return []
            return [tuple(row) for row in result]
    finally:
        await engine.dispose()


async def table_names(database_url: str) -> set[str]:
    rows = await run_sql(
        database_url,
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public'",
    )
    return {str(row[0]) for row in rows}


async def empty_the_database(database_url: str) -> None:
    """Drop everything in the database, as if it had just been created."""
    await run_sql(database_url, "DROP SCHEMA IF EXISTS public CASCADE")
    await run_sql(database_url, "CREATE SCHEMA public")


@asynccontextmanager
async def scratch_database(server_url: str, name: str) -> AsyncIterator[str]:
    """Create an empty database next to server_url's; drop it on exit.

    Yields the new database's URL.
    """
    await run_sql(server_url, f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
    await run_sql(server_url, f'CREATE DATABASE "{name}"')
    url = make_url(server_url).set(database=name)
    try:
        yield url.render_as_string(hide_password=False)
    finally:
        await run_sql(server_url, f'DROP DATABASE "{name}" WITH (FORCE)')
