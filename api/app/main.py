"""The FastAPI app: middleware, error handlers and router registration."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.db.session import engine
from app.errors import ErrorResponse, add_error_handlers
from app.logger import log_request, setup_logging
from app.routes import (
    account,
    auth,
    catalog,
    config,
    feedback,
    health,
    practice,
    stats,
)
from app.routes.dependencies import require_csrf_header
from app.settings import get_settings

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    yield
    await engine.dispose()


def _operation_id(route: APIRoute) -> str:
    """Name an operation after its function: "get_me", not FastAPI's
    "get_me_api_v1_me_get". The web app's generated types use the name.
    """
    return route.name


_DESCRIPTION = """
Every route is under `/api/v1` and answers JSON. An error is always
`{"error": {"code": "...", "message": "..."}}`.

**Who is asking.** `POST /auth/guest` starts a session and sets it as an
httpOnly cookie; a native client sends the same token as
`Authorization: Bearer`. Routes that need a user answer 401 without one.

**CSRF.** Every POST, PATCH, PUT and DELETE must carry the
`X-Requested-With` header, with any value, or it is a 403.
"""

app = FastAPI(
    title="CaramelCase API",
    description=_DESCRIPTION,
    lifespan=lifespan,
    generate_unique_id_function=_operation_id,
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=None,
)

app.middleware("http")(log_request)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_error_handlers(app)

# Every state-changing route of the API requires the CSRF header.
api = APIRouter(
    prefix=API_PREFIX,
    dependencies=[Depends(require_csrf_header)],
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
for area in (
    health,
    auth,
    account,
    stats,
    config,
    catalog,
    practice,
    feedback,
):
    api.include_router(area.router)
app.include_router(api)
