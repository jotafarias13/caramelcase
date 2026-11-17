"""validate: check question files against the format and the catalog.

A file passes when every line loads as a QuestionDoc, the file is named
after the subject and topic of its questions, both are in the catalog,
code is in the topic's language and no id is used twice. With --verified,
every question must also have passed the blind solve and the code run:
that is what the question bank promises.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import typer

from app.services.catalog_file import Catalog
from app.services.question_files import (
    Problem,
    QuestionLine,
    catalog_problems,
    find_question_files,
    read_question_file,
    unverified_problems,
)
from content.tools import common, run_log


def validate(
    paths: Sequence[Path],
    catalog: Catalog,
    *,
    require_verified: bool = False,
    log: Path | None = None,
) -> tuple[list[QuestionLine], list[Problem]]:
    """Check the question files among the paths. Returns the questions
    that loaded and every problem found.
    """
    lines: list[QuestionLine] = []
    problems: list[Problem] = []
    checked_in: dict[Path, int] = {}
    for file in find_question_files(paths):
        file_lines, file_problems = read_question_file(file)
        broken_lines = {problem.line_number for problem in file_problems}
        checked_in[file] = len(file_lines) + len(broken_lines)
        lines += file_lines
        problems += file_problems
    problems += catalog_problems(lines, catalog)
    if require_verified:
        problems += unverified_problems(lines)

    if log is not None:
        for file, checked in checked_in.items():
            failed = {
                problem.question_id or f"line {problem.line_number}"
                for problem in problems
                if problem.path == file
            }
            run_log.append_entry(
                log, run_log.Step.VALIDATE, file, checked, sorted(failed)
            )
    return lines, problems


def command(
    paths: Annotated[
        list[Path],
        typer.Argument(help="Question files, or directories of them."),
    ],
    verified: Annotated[
        bool,
        typer.Option(
            "--verified",
            help="Also require every question to have passed the pipeline.",
        ),
    ] = False,
    log: Annotated[
        bool,
        typer.Option("--log", help="Record the result in the pipeline log."),
    ] = False,
) -> None:
    """Check question files against the format and the catalog."""
    for path in paths:
        if not path.exists():
            raise common.ToolError(f"{path} does not exist")
    lines, problems = validate(
        paths,
        common.catalog(),
        require_verified=verified,
        log=run_log.pipeline_log_path() if log else None,
    )
    if problems:
        typer.echo(common.problem_list(problems))
    files = len(find_question_files(paths))
    typer.echo(
        f"validate: {common.count(len(lines), 'valid question')} in "
        f"{common.count(files, 'file')}, "
        f"{common.count(len(problems), 'problem')}."
    )
    if problems:
        raise typer.Exit(code=1)
