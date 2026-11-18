"""Logging: one JSON object per line, or readable lines for development.

Call sites use loguru directly: `logger.info("message", key=value)`. The
keyword arguments become fields of the JSON line. Inside a request every
line also carries its request_id (see log_request).
"""

import json
import sys
import time
import traceback
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC
from typing import TYPE_CHECKING

from fastapi import Request, Response
from loguru import logger

from app.client_ip import client_ip
from app.settings import get_settings

if TYPE_CHECKING:
    import loguru

_READABLE_FORMAT = (
    "<level>{level: <8}</level> <cyan>{time:HH:mm:ss.SSS}</cyan> "
    "<bold>{message}</bold> {extra}"
)


def _write_json_line(message: "loguru.Message") -> None:
    record = message.record
    line: dict[str, object] = {
        "time": record["time"].astimezone(UTC).isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        **record["extra"],
    }
    if record["exception"] is not None:
        line["exception"] = "".join(
            traceback.format_exception(*record["exception"])
        )
    sys.stdout.write(json.dumps(line, default=str) + "\n")
    sys.stdout.flush()


def setup_logging() -> None:
    settings = get_settings()
    logger.remove()
    if settings.log_json:
        logger.add(_write_json_line, level=settings.log_level)
    else:
        logger.add(
            sys.stdout, level=settings.log_level, format=_READABLE_FORMAT
        )


async def log_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Log one line per request and return its id in X-Request-ID."""
    request_id = uuid.uuid4().hex
    start = time.perf_counter()
    fields: dict[str, object] = {
        "method": request.method,
        "path": request.url.path,
        "ip": client_ip(request),
    }
    with logger.contextualize(request_id=request_id):
        try:
            response = await call_next(request)
        except Exception:
            fields["status"] = 500
            fields["duration_ms"] = _elapsed_ms(start)
            logger.exception("request failed", **fields)
            raise
        fields["status"] = response.status_code
        fields["duration_ms"] = _elapsed_ms(start)
        level = "WARNING" if response.status_code >= 400 else "INFO"  # noqa: PLR2004
        logger.log(level, "request", **fields)
    response.headers["X-Request-ID"] = request_id
    return response


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
