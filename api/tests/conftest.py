"""Fixtures for the API tests.

Tests that need Postgres ask for one of the database fixtures. Postgres 16
runs in one container for the whole run, started on first use, so unit
tests run without Docker. Set TEST_DATABASE_URL to use a server that is
already running instead: everything in that database is dropped first.

- database: the URL of the test database, migrated to head by the alembic
  command line.
- session: a database session whose writes are rolled back after the test.
  While a test holds it, the app's requests run in the same transaction,
  each with its own session: a request sees what the test flushed, and the
  test sees what a request committed.
- scratch_database: the URL of an empty database of the test's own, for a
  test that runs migrations or commits for real.
- client: an HTTP client of the app, as a browser with no cookies yet. It
  does not start Postgres. other_client is a second browser.
- clock: the time the API believes it is, fixed and movable.
- outbox: the emails the API sent, instead of sending them.
- rate_limiter: used by every test, so that rate-limit counts start at
  zero in each.

The environment is exported before anything from app is imported: the
settings are cached and the engine reads DATABASE_URL at import.
"""

import os
import socket


def _free_port() -> int:
    """Return a host port nothing listens on, for the container to bind."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port: int = probe.getsockname()[1]
        return port


_DB_USER = "caramel"
_DB_PASSWORD = "caramel"
_DB_NAME = "caramelcase_test"
_EXTERNAL_URL = os.environ.get("TEST_DATABASE_URL")
_CONTAINER_PORT = None if _EXTERNAL_URL else _free_port()
DATABASE_URL = _EXTERNAL_URL or (
    f"postgresql+asyncpg://{_DB_USER}:{_DB_PASSWORD}"
    f"@localhost:{_CONTAINER_PORT}/{_DB_NAME}"
)

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = DATABASE_URL
os.environ["LOG_JSON"] = "false"

# testcontainers mounts the Docker socket into its reaper container. The
# client may reach Docker through another path (Docker Desktop's is under
# ~/.docker), but inside Docker's VM or host the socket is this one.
os.environ.setdefault(
    "TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "/var/run/docker.sock"
)

# Everything below reads the environment exported above.
import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import ExitStack
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.community.postgres import PostgresContainer

from app.db.base import utc_now
from app.db.session import engine, get_session
from app.main import app as fastapi_app
from app.providers.email import get_email_sender
from app.services.rate_limits import RateLimiter, get_rate_limiter
from tests.support import commands
from tests.support import database as db
from tests.support.outbox import Outbox


@pytest_asyncio.fixture(scope="session")
async def database() -> AsyncIterator[str]:
    """Make Postgres available, migrate it to head and yield its URL."""
    with ExitStack() as stack:
        if _CONTAINER_PORT is not None:
            container = PostgresContainer(
                "postgres:16-alpine",
                username=_DB_USER,
                password=_DB_PASSWORD,
                dbname=_DB_NAME,
                driver=None,
            ).with_bind_ports(5432, _CONTAINER_PORT)
            stack.enter_context(container)

        await db.empty_the_database(DATABASE_URL)
        upgrade = commands.alembic(
            "upgrade", "head", database_url=DATABASE_URL
        )
        if upgrade.returncode != 0:
            # Every database test would fail the same way: stop the run.
            pytest.exit(
                f"alembic upgrade head failed:\n{commands.output_of(upgrade)}",
                returncode=1,
            )
        yield DATABASE_URL
        await engine.dispose()


@pytest_asyncio.fixture
async def session(
    database: str,  # noqa: ARG001  it must be up before the engine connects
    app: FastAPI,
) -> AsyncIterator[AsyncSession]:
    """A database session whose writes are rolled back after the test."""
    async with db.rollback_session(engine) as session:

        async def use_request_session() -> AsyncIterator[AsyncSession]:
            # As in production, each request has its own session. This one
            # joins the test's transaction, so flush what the test added.
            await session.flush()
            async with db.open_session(db.connection_of(session)) as request:
                yield request

        app.dependency_overrides[get_session] = use_request_session
        try:
            yield session
        finally:
            app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture
async def scratch_database(database: str) -> AsyncIterator[str]:
    """The URL of an empty database of the test's own, dropped afterwards."""
    name = f"scratch_{uuid.uuid4().hex[:12]}"
    async with db.scratch_database(database, name) as url:
        yield url


@pytest.fixture
def app() -> FastAPI:
    return fastapi_app


@pytest.fixture(autouse=True)
def rate_limiter(app: FastAPI) -> Iterator[RateLimiter]:
    """A rate limiter of the test's own: counts never carry over from
    another test.
    """
    limiter = RateLimiter()
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    yield limiter
    app.dependency_overrides.pop(get_rate_limiter, None)


# Requests go to https, because the session cookie is Secure, and carry
# the CSRF header, as the web app's do.
_BASE_URL = "https://test"
CSRF_HEADERS = {"X-Requested-With": "test"}


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """An HTTP client of the app, as a browser with no cookies yet. It
    does not start Postgres.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url=_BASE_URL, headers=CSRF_HEADERS
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def other_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """A second browser, with cookies of its own."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url=_BASE_URL, headers=CSRF_HEADERS
    ) as c:
        yield c


class Clock:
    """The time the API believes it is. Tests read it and move it.

    Every request moves it one millisecond, so no two requests of a test
    happen at the same instant, as none do in production.
    """

    def __init__(self) -> None:
        # A Monday, at noon in São Paulo.
        self.now = datetime(2026, 11, 16, 15, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.now += timedelta(milliseconds=1)
        return self.now

    def advance(self, **amount: float) -> None:
        self.now += timedelta(**amount)


@pytest.fixture
def clock(app: FastAPI) -> Iterator[Clock]:
    """Fix the API's clock, for every request of the test."""
    clock = Clock()
    app.dependency_overrides[utc_now] = clock
    yield clock
    app.dependency_overrides.pop(utc_now, None)


@pytest.fixture
def outbox(app: FastAPI) -> Iterator[Outbox]:
    """Keep the emails the API sends instead of sending them."""
    outbox = Outbox()
    app.dependency_overrides[get_email_sender] = lambda: outbox
    yield outbox
    app.dependency_overrides.pop(get_email_sender, None)
