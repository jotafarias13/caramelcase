"""strip-keys: write a question file without its answers, for the blind
solver.

A stripped question keeps its id, its code language and, in each
language, the stem, the code and the options' keys and texts. The correct
key, the reasons, the explanation, the difficulty and the verification
are left out: the solver must reach the answer alone.
"""

from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel

from app.domain.question_doc import OptionKey, QuestionDoc
from app.enums import CodeLanguage, Locale
from app.services.question_files import (
    QUESTION_FILE_SUFFIX,
    STRIPPED_FILE_SUFFIX,
)
from content.tools import common


class StrippedOption(BaseModel):
    key: OptionKey
    text: str


class StrippedText(BaseModel):
    stem: str
    code: str | None
    options: list[StrippedOption]


class StrippedQuestion(BaseModel):
    id: str
    code_language: CodeLanguage | None
    locales: dict[Locale, StrippedText]


def strip(doc: QuestionDoc) -> StrippedQuestion:
    """The question as the blind solver may see it."""
    return StrippedQuestion(
        id=doc.id,
        code_language=doc.code_language,
        locales={
            locale: StrippedText(
                stem=text.stem,
                code=text.code,
                options=[
                    StrippedOption(key=option.key, text=option.text)
                    for option in text.options
                ],
            )
            for locale, text in doc.locales.items()
        },
    )


def strip_file(question_file: Path, stripped_file: Path) -> int:
    """Write the stripped copy of a question file. Returns how many
    questions it holds.
    """
    lines = common.read_valid_questions([question_file])
    text = "".join(strip(line.doc).model_dump_json() + "\n" for line in lines)
    stripped_file.parent.mkdir(parents=True, exist_ok=True)
    stripped_file.write_text(text, encoding="utf-8")
    return len(lines)


def stripped_path_of(question_file: Path) -> Path:
    """pilhas.jsonl -> pilhas.stripped.jsonl, in the same directory."""
    name = question_file.name.removesuffix(QUESTION_FILE_SUFFIX)
    return question_file.with_name(name + STRIPPED_FILE_SUFFIX)


def command(
    question_file: Annotated[Path, typer.Argument(help="The question file.")],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Where to write. Default: <topic>.stripped.jsonl beside it.",
        ),
    ] = None,
) -> None:
    """Write a question file without its answers, for the blind solver."""
    target = output or stripped_path_of(question_file)
    count = strip_file(question_file, target)
    typer.echo(
        f"strip-keys: {common.count(count, 'question')} written to {target}."
    )
