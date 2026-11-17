"""The pipeline log: what each step checked and what failed.

content/pipeline-log.jsonl gets one line each time a tool runs with --log
on a question file. The report tool turns the log into the failure rate
of each step. The log is committed: it is the only record of the
questions that failed and were repaired or dropped.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.services.question_files import QUESTION_FILE_SUFFIX
from app.settings import get_settings

PIPELINE_LOG_NAME = "pipeline-log.jsonl"


class Step(StrEnum):
    """The steps that can fail a question, in pipeline order."""

    VALIDATE = "validate"
    RUN_CODE = "run-code"
    DEDUPE = "dedupe"
    BLIND_SOLVE = "blind-solve"
    # A question that fails here is dropped: it did not reach the bank.
    PROMOTE = "promote"


class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    at: datetime
    step: Step
    subject: str
    topic: str
    # How many questions the step looked at.
    checked: int
    # The ids of those that failed; "line 7" for a line without an id.
    failed: list[str]


def pipeline_log_path() -> Path:
    return get_settings().content_dir / PIPELINE_LOG_NAME


def append_entry(
    log: Path,
    step: Step,
    question_file: Path,
    checked: int,
    failed: Sequence[str],
) -> None:
    """Add one line to the log, for one step on one question file."""
    entry = LogEntry(
        at=datetime.now(UTC).replace(microsecond=0),
        step=step,
        subject=question_file.parent.name,
        topic=question_file.name.removesuffix(QUESTION_FILE_SUFFIX),
        checked=checked,
        failed=sorted(failed),
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as file:
        file.write(entry.model_dump_json() + "\n")


def read_entries(log: Path) -> list[LogEntry]:
    """Every entry of the log. A missing log is an empty one."""
    if not log.exists():
        return []
    return [
        LogEntry.model_validate_json(line)
        for line in log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
