"""Fixtures for the API tests.

Tests that need Postgres ask for the `database` fixture. It starts one
Postgres 16 container for the whole run, on first use, so unit tests run
without Docker. Set TEST_DATABASE_URL to use a server that is already
running instead (its data may be wiped by later test fixtures).

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
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from testcontainers.community.postgres import PostgresContainer

from app.db.session import engine
from app.main import app as fastapi_app


@pytest_asyncio.fixture(scope="session")
async def database() -> AsyncIterator[str]:
    """Make Postgres available and yield its URL."""
    if _CONTAINER_PORT is None:
        yield DATABASE_URL
        await engine.dispose()
        return
    container = PostgresContainer(
        "postgres:16-alpine",
        username=_DB_USER,
        password=_DB_PASSWORD,
        dbname=_DB_NAME,
        driver=None,
    ).with_bind_ports(5432, _CONTAINER_PORT)
    with container:
        yield DATABASE_URL
        await engine.dispose()


@pytest.fixture
def app() -> FastAPI:
    return fastapi_app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """An anonymous HTTP client of the app. It does not start Postgres."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
