"""What the tools share: the catalog, reading files, the error they raise."""

from collections.abc import Iterable
from pathlib import Path

from app.services.catalog_file import CATALOG_FILE_NAME, Catalog, load_catalog
from app.services.question_files import (
    BANK_DIR_NAME,
    Problem,
    QuestionLine,
    read_question_files,
)
from app.settings import get_settings


class ToolError(Exception):
    """A tool cannot do its work: a missing file, lines that do not load."""


def catalog() -> Catalog:
    return load_catalog(get_settings().content_dir / CATALOG_FILE_NAME)


def bank_dir() -> Path:
    return get_settings().content_dir / BANK_DIR_NAME


def read_valid_questions(paths: Iterable[Path]) -> list[QuestionLine]:
    """Read the question files among the paths. Every line must load: the
    tools after validate work on questions, not on broken lines.
    """
    paths = list(paths)
    for path in paths:
        if not path.exists():
            raise ToolError(f"{path} does not exist")
    lines, problems = read_question_files(paths)
    if problems:
        raise ToolError(
            problem_list(problems)
            + "\nThese lines are not valid questions: run validate and fix "
            "them first."
        )
    return lines


def count(number: int, noun: str) -> str:
    """ "1 question", "2 questions": the number with its noun."""
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def problem_list(problems: Iterable[Problem]) -> str:
    return "\n".join(str(problem) for problem in problems)


def lines_by_file(
    lines: Iterable[QuestionLine],
) -> dict[Path, list[QuestionLine]]:
    """The questions of each file, files in the order first seen."""
    by_file: dict[Path, list[QuestionLine]] = {}
    for line in lines:
        by_file.setdefault(line.path, []).append(line)
    return by_file
