"""GET /health: is the API up and can it reach the database?"""

from typing import Literal

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionDep
from app.errors import AppError, ErrorResponse

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]


@router.get("/health", responses={503: {"model": ErrorResponse}})
async def health(session: SessionDep) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError) as error:
        logger.opt(exception=error).error("health check failed")
        raise AppError(
            503, "database_unavailable", "The database is not reachable."
        ) from error
    return HealthResponse(status="ok", database="ok")
