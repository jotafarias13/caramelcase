import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.db.session import get_session


@pytest.mark.usefixtures("database")
async def test_health_is_ok_when_the_database_answers(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    assert response.headers["X-Request-ID"]


class _UnreachableSession:
    async def execute(self, _: object) -> None:
        raise OSError("connection refused")


async def test_health_is_503_when_the_database_is_unreachable(
    client: AsyncClient, app: FastAPI
) -> None:
    app.dependency_overrides[get_session] = _UnreachableSession

    response = await client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "database_unavailable",
            "message": "The database is not reachable.",
        }
    }
