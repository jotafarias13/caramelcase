"""Logging: one JSON object per line, or readable lines for development.

Call sites use loguru directly: `logger.info("message", key=value)`. The
keyword arguments become fields of the JSON line. Inside a request every
line also carries its request_id (see log_request).

Lines written with Python's standard logging module, by gunicorn, uvicorn
and other libraries, go through the same sink (InterceptHandler), with
the logger's name in a `logger` field.
"""

import json
import logging
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


class InterceptHandler(logging.Handler):
    """Hands a record of the standard logging module to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.bind(logger=record.name).opt(exception=record.exc_info).log(
            level, record.getMessage()
        )


# Loggers that come with handlers of their own, writing plain text.
_LIBRARY_LOGGERS = ("uvicorn", "uvicorn.error")
# uvicorn's line per request, which log_request already writes with more
# in it. A Uvicorn worker under gunicorn turns it on.
_SILENCED_LOGGERS = ("uvicorn.access",)


def setup_logging() -> None:
    settings = get_settings()
    logger.remove()
    if settings.log_json:
        logger.add(_write_json_line, level=settings.log_level)
    else:
        logger.add(
            sys.stdout, level=settings.log_level, format=_READABLE_FORMAT
        )
    _route_standard_logging(settings.log_level)


def _route_standard_logging(level: str) -> None:
    """Send the standard logging module's records to loguru."""
    root = logging.getLogger()
    if not any(isinstance(h, InterceptHandler) for h in root.handlers):
        root.addHandler(InterceptHandler())
    root.setLevel(level)
    for name in _LIBRARY_LOGGERS:
        library_logger = logging.getLogger(name)
        library_logger.handlers = []
        library_logger.propagate = True
    for name in _SILENCED_LOGGERS:
        silenced_logger = logging.getLogger(name)
        silenced_logger.handlers = []
        silenced_logger.propagate = False
    # Python's warnings (deprecations of libraries) become log lines too.
    logging.captureWarnings(True)


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
