"""promote: move the questions that passed the pipeline into the bank.

The last step for a question file in content/work. A question is promoted
when its line is valid, it fits the catalog, its id is not in the bank,
it passed the blind solve and the code run, and it is not a near-duplicate
of a question in the bank or of one promoted before it. It is added to
content/bank/<subject>/<topic>.jsonl, which is kept sorted by id.

Every other line is dropped: it stays behind in the work file, with the
reasons printed. A work file with nothing left is deleted.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

from app.services.catalog_file import Catalog
from app.services.question_files import (
    QUESTION_FILE_SUFFIX,
    QuestionLine,
    catalog_problems,
    load_bank,
    read_question_file,
    unverified_problems,
    write_question_file,
)
from app.settings import get_settings
from content.tools import common, run_log
from content.tools.dedupe import find_duplicates


@dataclass(frozen=True)
class Dropped:
    # The question's id, or "line 7" for a line without one.
    label: str
    reasons: list[str]

    def __str__(self) -> str:
        return f"{self.label}: " + "; ".join(self.reasons)


@dataclass(frozen=True)
class PromoteResult:
    promoted: list[str]
    dropped: list[Dropped]


def promote(
    question_file: Path,
    bank: Path,
    catalog: Catalog,
    dedupe_threshold: float,
    *,
    log: Path | None = None,
) -> PromoteResult:
    """Add the file's passing questions to the bank and leave the others
    in the file.
    """
    if not question_file.exists():
        raise common.ToolError(f"{question_file} does not exist")
    if bank.resolve() in question_file.resolve().parents:
        raise common.ToolError(f"{question_file} is already in the bank")
    bank_lines, bank_problems = load_bank(bank, catalog)
    if bank_problems:
        raise common.ToolError(
            common.problem_list(bank_problems)
            + f"\nThe bank at {bank} has problems: fix them before adding "
            "to it."
        )

    lines, problems = read_question_file(question_file)
    # Why each line is dropped, by line number.
    reasons: dict[int, list[str]] = {}
    labels = {line.line_number: line.doc.id for line in lines}
    in_this_file = [
        *problems,
        *(
            problem
            for problem in catalog_problems([*bank_lines, *lines], catalog)
            if problem.path == question_file
        ),
        *unverified_problems(lines),
    ]
    for problem in in_this_file:
        reasons.setdefault(problem.line_number, []).append(problem.message)
        labels.setdefault(
            problem.line_number,
            problem.question_id or f"line {problem.line_number}",
        )

    # Only a question that passed everything else can make a later one a
    # duplicate.
    candidates = [line for line in lines if line.line_number not in reasons]
    line_number_of = {line.doc.id: line.line_number for line in candidates}
    for duplicate in find_duplicates(
        [line.doc for line in candidates],
        [line.doc for line in bank_lines],
        dedupe_threshold,
    ):
        reasons[line_number_of[duplicate.question_id]] = [
            f"near-duplicate of {duplicate.of_id} "
            f"(similarity {duplicate.similarity:.2f})"
        ]

    promoted = [line for line in candidates if line.line_number not in reasons]
    _add_to_bank(bank, bank_lines, promoted)
    _keep_only(question_file, sorted(reasons))

    dropped = [
        Dropped(labels[number], reasons[number]) for number in sorted(reasons)
    ]
    if log is not None:
        run_log.append_entry(
            log,
            run_log.Step.PROMOTE,
            question_file,
            checked=len(promoted) + len(dropped),
            failed=[drop.label for drop in dropped],
        )
    return PromoteResult([line.doc.id for line in promoted], dropped)


def _add_to_bank(
    bank: Path,
    bank_lines: Sequence[QuestionLine],
    promoted: Sequence[QuestionLine],
) -> None:
    """Write each promoted question into its topic's file in the bank."""
    targets = {
        bank / line.doc.subject / f"{line.doc.topic}{QUESTION_FILE_SUFFIX}"
        for line in promoted
    }
    for target in targets:
        docs = [line.doc for line in bank_lines if line.path == target]
        docs += [
            line.doc
            for line in promoted
            if (line.doc.subject, line.doc.topic)
            == (
                target.parent.name,
                target.name.removesuffix(QUESTION_FILE_SUFFIX),
            )
        ]
        write_question_file(target, sorted(docs, key=lambda doc: doc.id))


def _keep_only(question_file: Path, line_numbers: Sequence[int]) -> None:
    """Leave only these lines in the file, as they were written. Delete
    the file when none is left.
    """
    raw_lines = question_file.read_text(encoding="utf-8").splitlines()
    kept = [raw_lines[number - 1] for number in line_numbers]
    if kept:
        question_file.write_text("\n".join(kept) + "\n", encoding="utf-8")
    else:
        question_file.unlink()


def command(
    question_files: Annotated[
        list[Path], typer.Argument(help="Question files from content/work.")
    ],
    log: Annotated[
        bool,
        typer.Option("--log", help="Record the result in the pipeline log."),
    ] = False,
) -> None:
    """Move the questions that passed the pipeline into the bank."""
    promoted = 0
    dropped = 0
    for question_file in question_files:
        result = promote(
            question_file,
            common.bank_dir(),
            common.catalog(),
            get_settings().dedupe_similarity,
            log=run_log.pipeline_log_path() if log else None,
        )
        for drop in result.dropped:
            typer.echo(f"dropped {drop}")
        promoted += len(result.promoted)
        dropped += len(result.dropped)
    typer.echo(
        f"promote: {common.count(promoted, 'question')} added to the bank, "
        f"{dropped} dropped."
    )
    if dropped:
        raise typer.Exit(code=1)
