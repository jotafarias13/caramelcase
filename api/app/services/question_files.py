"""Reading and writing question files: <subject>/<topic>.jsonl, one
question per line.

The importer and the tools in content/tools/ share this module, so they
agree on what a valid file is:

- each line loads as a QuestionDoc (app/domain/question_doc.py);
- the file is named after the subject and topic of its questions, and
  both are in the catalog;
- a question's code is in its topic's language;
- no two questions share an id.

The question bank (content/bank) asks for one thing more: every question
has passed the pipeline. Files still in the pipeline do not.
"""

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from app.domain.question_doc import (
    QuestionDoc,
    unverified_reasons,
    validation_problems,
)
from app.services.catalog_file import Catalog

BANK_DIR_NAME = "bank"
QUESTION_FILE_SUFFIX = ".jsonl"
# Files the blind solve leaves next to a question file. They are not
# question files, and a directory is read without them.
STRIPPED_FILE_SUFFIX = ".stripped.jsonl"
ANSWERS_FILE_SUFFIX = ".answers.jsonl"


@dataclass(frozen=True)
class QuestionLine:
    """A question and where it was read from."""

    path: Path
    line_number: int
    doc: QuestionDoc


@dataclass(frozen=True)
class Problem:
    """Something wrong in a question file."""

    path: Path
    # 0 when the problem is about the file as a whole.
    line_number: int
    # None when the line could not be read as a question.
    question_id: str | None
    message: str

    def __str__(self) -> str:
        where = f"{self.path}:{self.line_number}"
        if self.question_id:
            where += f" {self.question_id}"
        return f"{where}: {self.message}"


def find_question_files(paths: Iterable[Path]) -> list[Path]:
    """The question files among the paths: each file given, and every
    .jsonl file under each directory given, in a stable order.
    """
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files += sorted(
                file
                for file in path.rglob(f"*{QUESTION_FILE_SUFFIX}")
                if not file.name.endswith(
                    (STRIPPED_FILE_SUFFIX, ANSWERS_FILE_SUFFIX)
                )
            )
        else:
            files.append(path)
    return files


def read_question_file(path: Path) -> tuple[list[QuestionLine], list[Problem]]:
    """Read one file. A line that is not a valid question becomes a
    problem; the other lines are still returned. Empty lines are skipped.
    """
    lines: list[QuestionLine] = []
    problems: list[Problem] = []
    text = path.read_text(encoding="utf-8")
    for line_number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            doc = QuestionDoc.model_validate_json(raw)
        except ValidationError as error:
            question_id = _id_of(raw)
            problems += [
                Problem(path, line_number, question_id, message)
                for message in validation_problems(error)
            ]
            continue
        lines.append(QuestionLine(path, line_number, doc))
    return lines, problems


def read_question_files(
    paths: Iterable[Path],
) -> tuple[list[QuestionLine], list[Problem]]:
    """Read every question file among the paths."""
    lines: list[QuestionLine] = []
    problems: list[Problem] = []
    for file in find_question_files(paths):
        file_lines, file_problems = read_question_file(file)
        lines += file_lines
        problems += file_problems
    return lines, problems


def write_question_file(path: Path, docs: Sequence[QuestionDoc]) -> None:
    """Write the questions to the file, one per line, replacing it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(doc.to_line() + "\n" for doc in docs)
    path.write_text(text, encoding="utf-8")


def catalog_problems(
    lines: Sequence[QuestionLine], catalog: Catalog
) -> list[Problem]:
    """What is wrong with the questions as a set, given the catalog."""
    problems = []
    first_line_of: dict[str, QuestionLine] = {}
    for line in lines:
        doc = line.doc
        expected_path = (
            Path(doc.subject) / f"{doc.topic}{QUESTION_FILE_SUFFIX}"
        )
        if Path(line.path.parent.name) / line.path.name != expected_path:
            problems.append(_problem(line, f"belongs in {expected_path}"))

        subject = catalog.subject(doc.subject)
        topic = subject.topic(doc.topic) if subject else None
        if subject is None:
            problems.append(
                _problem(line, f"no subject {doc.subject} in the catalog")
            )
        elif topic is None:
            problems.append(
                _problem(
                    line,
                    f"no topic {doc.topic} in {doc.subject} in the catalog",
                )
            )
        elif doc.code_language not in (None, topic.code_language):
            problems.append(
                _problem(
                    line,
                    f"code_language is {doc.code_language.value}, the "
                    f"topic's is {topic.code_language.value}",
                )
            )

        first = first_line_of.setdefault(doc.id, line)
        if first is not line:
            problems.append(
                _problem(
                    line,
                    f"the id is already used at {first.path}:"
                    f"{first.line_number}",
                )
            )
    return problems


def unverified_problems(lines: Sequence[QuestionLine]) -> list[Problem]:
    """The questions that have not passed the pipeline, and why."""
    return [
        _problem(line, reason)
        for line in lines
        for reason in unverified_reasons(line.doc)
    ]


def load_bank(
    bank_dir: Path, catalog: Catalog
) -> tuple[list[QuestionLine], list[Problem]]:
    """Read the question bank and check everything it promises: valid
    lines, the catalog's subjects and topics, unique ids, and every
    question through the pipeline. A missing directory is an empty bank.
    """
    if not bank_dir.is_dir():
        return [], []
    lines, problems = read_question_files([bank_dir])
    problems += catalog_problems(lines, catalog)
    problems += unverified_problems(lines)
    return lines, problems


def _problem(line: QuestionLine, message: str) -> Problem:
    return Problem(line.path, line.line_number, line.doc.id, message)


def _id_of(raw_line: str) -> str | None:
    """The id of a line that is not a valid question, if it has one."""
    try:
        data = json.loads(raw_line)
    except ValueError:
        return None
    if isinstance(data, dict) and isinstance(data.get("id"), str):
        return str(data["id"])
    return None
