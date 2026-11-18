"""Production logging: every line is one JSON object, gunicorn's included."""

import json
import logging
import logging.config
import runpy
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from gunicorn.util import import_app, load_class
from gunicorn.workers.base import Worker
from loguru import logger

from app.logger import InterceptHandler, setup_logging
from app.settings import get_settings

GUNICORN_CONF = Path(__file__).resolve().parents[1] / "gunicorn.conf.py"
# The standard loggers these tests change: the root and the servers'.
TOUCHED_LOGGERS = (
    "",
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "gunicorn.error",
    "gunicorn.access",
)


@pytest.fixture
def json_logs(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Logging as production sets it up; put back as it was afterwards."""
    touched = [logging.getLogger(name) for name in TOUCHED_LOGGERS]
    saved = [(lg, lg.handlers[:], lg.level, lg.propagate) for lg in touched]
    monkeypatch.setenv("LOG_JSON", "true")
    get_settings.cache_clear()
    setup_logging()
    yield
    get_settings.cache_clear()
    for touched_logger, handlers, level, propagate in saved:
        touched_logger.handlers = handlers
        touched_logger.setLevel(level)
        touched_logger.propagate = propagate
    logging.captureWarnings(False)
    logger.remove()
    logger.add(sys.stderr)


def last_line(capsys: pytest.CaptureFixture[str]) -> dict[str, object]:
    lines = capsys.readouterr().out.strip().splitlines()
    line: dict[str, object] = json.loads(lines[-1])
    return line


@pytest.mark.usefixtures("json_logs")
def test_a_line_is_one_json_object_with_its_fields(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger.info("question imported", external_id="pilhas.0001")

    line = last_line(capsys)
    assert line["level"] == "INFO"
    assert line["message"] == "question imported"
    assert line["external_id"] == "pilhas.0001"
    assert str(line["time"]).endswith("+00:00")


@pytest.mark.usefixtures("json_logs")
def test_standard_logging_lines_are_json_too(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logging.getLogger("uvicorn.error").info("Started server process [%d]", 7)

    line = last_line(capsys)
    assert line["message"] == "Started server process [7]"
    assert line["logger"] == "uvicorn.error"


@pytest.mark.usefixtures("json_logs")
def test_uvicorn_does_not_repeat_the_request_line(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # What a Uvicorn worker does before the app starts.
    logging.getLogger("uvicorn.access").addHandler(InterceptHandler())
    setup_logging()

    logging.getLogger("uvicorn.access").info('"GET /api/v1/health" 200')

    assert capsys.readouterr().out == ""


@pytest.mark.usefixtures("json_logs")
def test_a_standard_logging_exception_keeps_its_traceback(
    capsys: pytest.CaptureFixture[str],
) -> None:
    try:
        _ = 1 / 0
    except ZeroDivisionError:
        logging.getLogger("some.library").exception("it broke")

    line = last_line(capsys)
    assert line["level"] == "ERROR"
    assert "ZeroDivisionError" in str(line["exception"])


@pytest.mark.usefixtures("json_logs")
def test_gunicorn_runs_the_app_in_uvicorn_workers() -> None:
    conf = runpy.run_path(str(GUNICORN_CONF))

    assert issubclass(load_class(conf["worker_class"]), Worker)
    assert isinstance(import_app(conf["wsgi_app"]), FastAPI)
    assert conf["workers"] == get_settings().gunicorn_workers
    assert conf["accesslog"] is None


@pytest.mark.usefixtures("json_logs")
def test_gunicorn_lines_are_json(capsys: pytest.CaptureFixture[str]) -> None:
    conf = runpy.run_path(str(GUNICORN_CONF))
    logging.config.dictConfig(conf["logconfig_dict"])

    gunicorn_error = logging.getLogger("gunicorn.error")
    handlers = gunicorn_error.handlers
    assert any(isinstance(h, InterceptHandler) for h in handlers)
    gunicorn_error.info("Booting worker with pid: %s", 42)

    line = last_line(capsys)
    assert line["message"] == "Booting worker with pid: 42"
    assert line["logger"] == "gunicorn.error"
