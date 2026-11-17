from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel

from app.errors import AppError


async def test_unknown_route_uses_the_error_shape(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Not Found"}
    }


class _Body(BaseModel):
    count: int


async def test_app_error_and_invalid_body_use_the_error_shape(
    client: AsyncClient, app: FastAPI
) -> None:
    @app.post("/test-only/echo")
    async def echo(body: _Body) -> _Body:
        if body.count < 0:
            raise AppError(409, "negative_count", "Count is negative.")
        return body

    conflict = await client.post("/test-only/echo", json={"count": -1})
    invalid = await client.post("/test-only/echo", json={"count": "many"})

    assert conflict.status_code == 409
    assert conflict.json() == {
        "error": {"code": "negative_count", "message": "Count is negative."}
    }
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"
    assert invalid.json()["error"]["message"].startswith("body.count:")
