"""dedupe: flag near-duplicate questions within a subject.

Two questions are near-duplicates when their Portuguese stems are at
least as similar as settings.dedupe_similarity, and so is their code.
Many questions share a stem such as "O que este programa imprime?", so
the stem alone does not decide: two questions with code are duplicates
only if the code is nearly the same too. A question with code and one
without are never duplicates.

Similarity is difflib's ratio, from 0 to 1: twice the number of matching
characters over the total. Stems are compared without case, accents or
punctuation; code is compared as written, with its spacing collapsed.

Of two near-duplicates the later one is flagged: the one checked against
questions already in the bank, or the one further down the file.
"""

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Annotated

import typer

from app.domain.question_doc import QuestionDoc
from app.enums import Locale
from app.settings import get_settings
from content.tools import common, run_log

_NOT_A_LETTER_OR_DIGIT = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class Duplicate:
    # The later of the two questions: the one to rewrite or drop.
    question_id: str
    of_id: str
    similarity: float

    def __str__(self) -> str:
        return (
            f"{self.question_id}: near-duplicate of {self.of_id} "
            f"(similarity {self.similarity:.2f})"
        )


@dataclass(frozen=True)
class _Comparable:
    """A question reduced to what dedupe compares."""

    question_id: str
    subject: str
    stem: str
    code: str | None


def find_duplicates(
    new: Sequence[QuestionDoc],
    existing: Sequence[QuestionDoc],
    threshold: float,
) -> list[Duplicate]:
    """Compare each new question with the existing ones of its subject and
    with the new ones before it. Returns each flagged question once, with
    the question it is most similar to.
    """
    seen = [_comparable(doc) for doc in existing]
    duplicates = []
    for doc in new:
        question = _comparable(doc)
        closest: Duplicate | None = None
        for other in seen:
            if other.subject != question.subject:
                continue
            similarity = _similarity(question, other, threshold)
            if similarity >= threshold and (
                closest is None or similarity > closest.similarity
            ):
                closest = Duplicate(
                    question.question_id, other.question_id, similarity
                )
        if closest is not None:
            duplicates.append(closest)
        seen.append(question)
    return duplicates


def _comparable(doc: QuestionDoc) -> _Comparable:
    code = doc.code()
    return _Comparable(
        question_id=doc.id,
        subject=doc.subject,
        stem=_plain(doc.locales[Locale.PT_BR].stem),
        code=None if code is None else " ".join(code.split()),
    )


def _plain(text: str) -> str:
    """Lower case, no accents, and one space for every run of anything
    that is not a letter or a digit.
    """
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return _NOT_A_LETTER_OR_DIGIT.sub(" ", without_accents).strip()


def _similarity(a: _Comparable, b: _Comparable, threshold: float) -> float:
    """The similarity of two questions: the lower of stem and code. 0 as
    soon as one of them is known to be under the threshold.
    """
    if (a.code is None) != (b.code is None):
        return 0.0
    stems = _ratio(a.stem, b.stem, threshold)
    if stems < threshold or a.code is None or b.code is None:
        return stems
    return min(stems, _ratio(a.code, b.code, threshold))


def _ratio(a: str, b: str, threshold: float) -> float:
    matcher = SequenceMatcher(None, a, b, autojunk=False)
    # Two cheap upper bounds of the ratio spare most of the full
    # comparisons.
    if matcher.real_quick_ratio() < threshold:
        return 0.0
    if matcher.quick_ratio() < threshold:
        return 0.0
    return matcher.ratio()


def dedupe(
    paths: Sequence[Path],
    against: Sequence[Path],
    threshold: float,
    *,
    log: Path | None = None,
) -> tuple[int, list[Duplicate]]:
    """Look for near-duplicates among the questions of the paths, and
    between them and the questions of `against`. Returns how many
    questions were checked, and the flagged ones.
    """
    new_lines = common.read_valid_questions(paths)
    new_ids = {line.doc.id for line in new_lines}
    existing = [
        line.doc
        for line in common.read_valid_questions(against)
        if line.doc.id not in new_ids
    ]
    duplicates = find_duplicates(
        [line.doc for line in new_lines], existing, threshold
    )
    if log is not None:
        flagged = {duplicate.question_id for duplicate in duplicates}
        for file, lines in common.lines_by_file(new_lines).items():
            run_log.append_entry(
                log,
                run_log.Step.DEDUPE,
                file,
                checked=len(lines),
                failed=[
                    line.doc.id for line in lines if line.doc.id in flagged
                ],
            )
    return len(new_lines), duplicates


def command(
    paths: Annotated[
        list[Path],
        typer.Argument(help="Question files, or directories of them."),
    ],
    against: Annotated[
        list[Path] | None,
        typer.Option(
            "--against",
            help="Also compare with these files or directories, for example "
            "content/bank. Their questions are not flagged themselves.",
        ),
    ] = None,
    log: Annotated[
        bool,
        typer.Option("--log", help="Record the result in the pipeline log."),
    ] = False,
) -> None:
    """Flag near-duplicate questions within a subject."""
    checked, duplicates = dedupe(
        paths,
        # A bank that does not exist yet is an empty bank.
        [path for path in against or [] if path.exists()],
        get_settings().dedupe_similarity,
        log=run_log.pipeline_log_path() if log else None,
    )
    for duplicate in duplicates:
        typer.echo(str(duplicate))
    typer.echo(
        f"dedupe: {common.count(checked, 'question')} checked, "
        f"{common.count(len(duplicates), 'near-duplicate')}."
    )
    if duplicates:
        raise typer.Exit(code=1)
