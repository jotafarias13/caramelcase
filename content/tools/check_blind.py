"""check-blind: compare the blind solver's answers with the keys.

The solver writes one line per question to an answers file:

    {"id": "estruturas-de-dados.pilhas.0001", "key": "b"}
    {"id": "estruturas-de-dados.pilhas.0002", "key": null,
     "note": "a and c are both correct: a deque also allows this"}

key is null when the solver found no option, or more than one, that it
could defend. A different key, or none, is a disagreement: the question
failed. The result is recorded in each question's verification.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel, ConfigDict, ValidationError

from app.domain.question_doc import OptionKey, QuestionDoc
from app.services.question_files import (
    ANSWERS_FILE_SUFFIX,
    QUESTION_FILE_SUFFIX,
    write_question_file,
)
from content.tools import common, run_log


class BlindAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    key: OptionKey | None
    # Why the solver chose no key, or anything it found wrong.
    note: str | None = None


@dataclass(frozen=True)
class Disagreement:
    question_id: str
    correct_key: str
    blind_key: str | None
    note: str | None

    def __str__(self) -> str:
        text = (
            f"{self.question_id}: the blind solver answered "
            f"{self.blind_key or 'nothing'}, the key is {self.correct_key}"
        )
        return f"{text}. Solver's note: {self.note}" if self.note else text


def read_answers(answers_file: Path) -> dict[str, BlindAnswer]:
    """The solver's answers by question id."""
    if not answers_file.exists():
        raise common.ToolError(f"{answers_file} does not exist")
    answers: dict[str, BlindAnswer] = {}
    text = answers_file.read_text(encoding="utf-8")
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            answer = BlindAnswer.model_validate_json(raw)
        except ValidationError as error:
            first = error.errors()[0]
            where = ".".join(str(part) for part in first["loc"])
            raise common.ToolError(
                f"{answers_file}:{number}: not an answer line: "
                f"{where}: {first['msg']}"
            ) from error
        if answer.id in answers:
            raise common.ToolError(
                f"{answers_file}:{number}: a second answer for {answer.id}"
            )
        answers[answer.id] = answer
    return answers


def record_answer(doc: QuestionDoc, answer: BlindAnswer) -> QuestionDoc:
    """The question with the blind solver's answer in its verification."""
    verification = doc.verification.model_copy(
        update={
            "blind_key": answer.key,
            "blind_agrees": answer.key == doc.correct_key,
        }
    )
    return doc.model_copy(update={"verification": verification})


def check_blind(
    question_file: Path,
    answers_file: Path,
    *,
    write: bool = True,
    log: Path | None = None,
) -> list[Disagreement]:
    """Record the solver's answers in the question file and return the
    disagreements. Every question needs exactly one answer.
    """
    lines = common.read_valid_questions([question_file])
    answers = read_answers(answers_file)
    ids = {line.doc.id for line in lines}
    unanswered = sorted(ids - set(answers))
    unknown = sorted(set(answers) - ids)
    if unanswered or unknown:
        problems = [
            f"no answer for {question_id}" for question_id in unanswered
        ]
        problems += [
            f"an answer for {question_id}, which is not in {question_file}"
            for question_id in unknown
        ]
        raise common.ToolError(
            f"{answers_file} does not match {question_file}:\n"
            + "\n".join(problems)
        )

    docs = [record_answer(line.doc, answers[line.doc.id]) for line in lines]
    disagreements = [
        Disagreement(
            question_id=doc.id,
            correct_key=doc.correct_key,
            blind_key=doc.verification.blind_key,
            note=answers[doc.id].note,
        )
        for doc in docs
        if not doc.verification.blind_agrees
    ]
    if write:
        write_question_file(question_file, docs)
    if log is not None:
        run_log.append_entry(
            log,
            run_log.Step.BLIND_SOLVE,
            question_file,
            checked=len(docs),
            failed=[
                disagreement.question_id for disagreement in disagreements
            ],
        )
    return disagreements


def answers_path_of(question_file: Path) -> Path:
    """pilhas.jsonl -> pilhas.answers.jsonl, in the same directory."""
    name = question_file.name.removesuffix(QUESTION_FILE_SUFFIX)
    return question_file.with_name(name + ANSWERS_FILE_SUFFIX)


def command(
    question_file: Annotated[Path, typer.Argument(help="The question file.")],
    answers: Annotated[
        Path | None,
        typer.Option(
            "--answers",
            "-a",
            help="The solver's answers. Default: <topic>.answers.jsonl "
            "beside the question file.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Compare, but leave the question file alone."
        ),
    ] = False,
    log: Annotated[
        bool,
        typer.Option("--log", help="Record the result in the pipeline log."),
    ] = False,
) -> None:
    """Compare the blind solver's answers with the keys and record them."""
    disagreements = check_blind(
        question_file,
        answers or answers_path_of(question_file),
        write=not dry_run,
        log=run_log.pipeline_log_path() if log else None,
    )
    for disagreement in disagreements:
        typer.echo(str(disagreement))
    typer.echo(
        f"check-blind: {common.count(len(disagreements), 'disagreement')}."
    )
    if disagreements:
        raise typer.Exit(code=1)
