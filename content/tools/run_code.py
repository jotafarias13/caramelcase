"""run-code: execute each question's code and check it against the key.

What happens to a question depends on its code_check:

- output: the code runs, and what it prints must be the text of the
  correct option, in every language;
- runs: the code runs and must finish without an error;
- skip, or no code: nothing runs.

"Runs" means: it compiles (C, with warnings as errors and the sanitizers
on), exits with code 0 inside the timeout, and prints the same thing on
every run, so the output cannot depend on chance, time or addresses. The
code runs settings.code_run_count times, and each Python run has another
hash seed: that is what changes the order of a set of strings.

Python runs in the interpreter the tools run in, C is compiled with the
compiler in settings, and SQL runs in an empty SQLite database
(sql_runner.py). Each run is its own process, in an empty temporary
directory, with no input and almost no environment. It is not a sandbox:
the code runs as you. Read a file from an unknown source before running
this tool on it.

The result is recorded in each question's verification.code_ran.
"""

import os
import resource
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

from app.domain.question_doc import CodeCheck, QuestionDoc
from app.enums import CodeLanguage
from app.services.question_files import write_question_file
from app.settings import Settings, get_settings
from content.tools import common, run_log

_SQL_RUNNER = Path(__file__).with_name("sql_runner.py")
# Lines of the error output shown when a run fails.
_ERROR_LINES_SHOWN = 6


@dataclass(frozen=True)
class RunOutcome:
    ok: bool
    # What the code printed.
    output: str
    # Why it failed. Empty when ok.
    detail: str = ""


@dataclass(frozen=True)
class CodeFailure:
    question_id: str
    reason: str

    def __str__(self) -> str:
        return f"{self.question_id}: {self.reason}"


def run_code(
    code: str, language: CodeLanguage, settings: Settings
) -> RunOutcome:
    """Run the code several times in an empty directory. It passes when
    every run exits with code 0 and prints the same thing.
    """
    with tempfile.TemporaryDirectory(prefix="run-code-") as directory:
        workdir = Path(directory)
        if language is CodeLanguage.PYTHON:
            (workdir / "question.py").write_text(code, encoding="utf-8")
            # -s and -P keep the user's site packages and the file's
            # directory out of the imports. -I would do the same, but it
            # also ignores PYTHONHASHSEED, which every run sets.
            command = [sys.executable, "-s", "-P", "-X", "utf8", "question.py"]
        elif language is CodeLanguage.SQL:
            (workdir / "question.sql").write_text(code, encoding="utf-8")
            command = [
                sys.executable,
                "-I",
                "-X",
                "utf8",
                str(_SQL_RUNNER),
                "question.sql",
            ]
        else:
            (workdir / "question.c").write_text(code, encoding="utf-8")
            compiled = _execute(
                [
                    settings.code_run_c_compiler,
                    *settings.code_run_c_flags,
                    "-o",
                    "question",
                    "question.c",
                    "-lm",
                ],
                workdir,
                settings,
                limit_output=False,
            )
            if not compiled.ok:
                return RunOutcome(
                    False, "", f"it does not compile: {compiled.detail}"
                )
            command = ["./question"]

        first = _execute(command, workdir, settings, hash_seed=1)
        if not first.ok:
            return first
        for hash_seed in range(2, settings.code_run_count + 1):
            again = _execute(command, workdir, settings, hash_seed=hash_seed)
            if not again.ok or again.output != first.output:
                return RunOutcome(
                    False,
                    first.output,
                    "it is not deterministic: another run "
                    + (
                        f"printed {again.output!r} after {first.output!r}"
                        if again.ok
                        else f"failed: {again.detail}"
                    ),
                )
        return first


def _execute(
    command: list[str],
    workdir: Path,
    settings: Settings,
    *,
    limit_output: bool = True,
    hash_seed: int = 1,
) -> RunOutcome:
    """Run one command in workdir and collect what it printed."""
    max_bytes = settings.code_run_max_output_bytes
    timeout = settings.code_run_timeout_seconds

    def stop_at_max_output() -> None:
        # Runs in the child before the command: a file it writes, its
        # output included, cannot grow past the limit.
        resource.setrlimit(resource.RLIMIT_FSIZE, (max_bytes, max_bytes))

    output_file = workdir / "output.txt"
    error_file = workdir / "errors.txt"
    try:
        with output_file.open("wb") as output, error_file.open("wb") as errors:
            completed = subprocess.run(
                command,
                cwd=workdir,
                env=_environment(hash_seed),
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=errors,
                timeout=timeout,
                preexec_fn=stop_at_max_output if limit_output else None,
                check=False,
            )
    except subprocess.TimeoutExpired:
        return RunOutcome(False, "", f"it ran for more than {timeout:g} s")
    except FileNotFoundError:
        raise common.ToolError(f"{command[0]} is not installed") from None

    printed = output_file.read_text(encoding="utf-8", errors="replace")
    if limit_output and output_file.stat().st_size >= max_bytes:
        return RunOutcome(False, "", f"it printed more than {max_bytes} bytes")
    if completed.returncode != 0:
        error_text = error_file.read_text(encoding="utf-8", errors="replace")
        return RunOutcome(
            False,
            printed,
            f"exit code {completed.returncode}: {_summary(error_text)}",
        )
    return RunOutcome(True, printed)


def _summary(error_text: str) -> str:
    """The lines of an error output that say what went wrong, on one
    line. A compiler and a sanitizer name the error in their "error:" and
    SUMMARY lines, among dozens of others; everything else says it last.
    """
    lines = error_text.strip().splitlines()
    naming_the_error = [
        line.strip()
        for line in lines
        if "error:" in line or line.startswith("SUMMARY: ")
    ]
    return " | ".join(naming_the_error or lines[-_ERROR_LINES_SHOWN:])


def _environment(hash_seed: int) -> dict[str, str]:
    """The environment of a run: where programs are, and nothing of the
    user's. Leak reports are off because they exist on Linux only, and a
    question must pass or fail the same way everywhere. The hash seed is
    read by Python only: with a seed of its own, each run of a question
    puts a set of strings in another order.
    """
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "ASAN_OPTIONS": "detect_leaks=0",
        "PYTHONHASHSEED": str(hash_seed),
    }
    if "TMPDIR" in os.environ:
        environment["TMPDIR"] = os.environ["TMPDIR"]
    return environment


def comparable(text: str) -> str:
    """Output or option text without the whitespace that cannot be seen:
    around the whole text and at the end of each line.
    """
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def check_code(doc: QuestionDoc, settings: Settings) -> str | None:
    """Run the question's code as its code_check asks. Returns why it
    failed, or None when it passed. The question has code to run.
    """
    code = doc.code()
    assert code is not None
    assert doc.code_language is not None
    outcome = run_code(code, doc.code_language, settings)
    if not outcome.ok:
        return outcome.detail
    if doc.code_check is not CodeCheck.OUTPUT:
        return None

    printed = comparable(outcome.output)
    for locale, text in doc.locales.items():
        shown_by = [
            option.key
            for option in text.options
            if comparable(option.text) == printed
        ]
        if shown_by != [doc.correct_key]:
            which = f"option {shown_by[0]}" if shown_by else "no option"
            return (
                f"it printed {printed!r}, which is {which}, but the key is "
                f"{doc.correct_key} ({locale.value})"
            )
    return None


def has_code_to_run(doc: QuestionDoc) -> bool:
    return doc.code_check in (CodeCheck.OUTPUT, CodeCheck.RUNS)


def record_run(doc: QuestionDoc, code_ran: bool | None) -> QuestionDoc:
    """The question with the result of the run in its verification."""
    verification = doc.verification.model_copy(update={"code_ran": code_ran})
    return doc.model_copy(update={"verification": verification})


def run_code_in_file(
    question_file: Path,
    settings: Settings,
    *,
    write: bool = True,
    log: Path | None = None,
) -> tuple[int, list[CodeFailure]]:
    """Run the code of every question of the file that has code to run,
    and record the result. Returns how many ran, and the failures.
    """
    lines = common.read_valid_questions([question_file])
    docs = []
    ran = 0
    failures = []
    for line in lines:
        doc = line.doc
        if not has_code_to_run(doc):
            docs.append(record_run(doc, None))
            continue
        ran += 1
        reason = check_code(doc, settings)
        if reason is not None:
            failures.append(CodeFailure(doc.id, reason))
        docs.append(record_run(doc, reason is None))

    if write:
        write_question_file(question_file, docs)
    if log is not None:
        run_log.append_entry(
            log,
            run_log.Step.RUN_CODE,
            question_file,
            checked=ran,
            failed=[failure.question_id for failure in failures],
        )
    return ran, failures


def command(
    paths: Annotated[
        list[Path],
        typer.Argument(help="Question files, or directories of them."),
    ],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Run, but leave the question files alone."
        ),
    ] = False,
    log: Annotated[
        bool,
        typer.Option("--log", help="Record the result in the pipeline log."),
    ] = False,
) -> None:
    """Execute each question's code and check it against the key."""
    # Read everything first: nothing runs if any line is broken.
    lines = common.read_valid_questions(paths)
    total_ran = 0
    total_failures = []
    for file in common.lines_by_file(lines):
        ran, failures = run_code_in_file(
            file,
            get_settings(),
            write=not dry_run,
            log=run_log.pipeline_log_path() if log else None,
        )
        total_ran += ran
        total_failures += failures
    for failure in total_failures:
        typer.echo(str(failure))
    typer.echo(
        f"run-code: {common.count(total_ran, 'question')} run, "
        f"{common.count(len(total_failures), 'failure')}."
    )
    if total_failures:
        raise typer.Exit(code=1)
