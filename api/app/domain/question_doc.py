"""The format of a question in the content files: QuestionDoc.

A question is one JSON object on one line of
content/bank/<subject>/<topic>.jsonl. This model is the only definition
of that format: the tools in content/tools/ and the importer both read a
line through it, so a line that loads is a line that follows every rule
below.

Three fields go beyond the spec's sample line:

- code_check says what the run-code tool does with the question's code;
- verification.blind_agrees is false, with no blind_key, when the blind
  solver found no single defensible option;
- version is where questions.version starts; the importer raises the
  database's number on its own when the content changes.

The limits (characters, lines) are in app/settings.py.
"""

import hashlib
import json
import re
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)

from app.enums import CodeLanguage, Locale, QuestionType
from app.settings import Settings, get_settings

Slug = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", max_length=80)
]

OptionKey = Literal["a", "b", "c", "d"]
OPTION_KEYS: tuple[OptionKey, ...] = ("a", "b", "c", "d")

DIFFICULTY_MIN = 1
DIFFICULTY_MAX = 5

# The length of questions.external_id, which stores the id.
ID_MAX_CHARS = 160
_ID_NUMBER = re.compile(r"^\d{4}$")

# Options the writing rules forbid, in lower case.
_FORBIDDEN_OPTION_PHRASES = (
    "todas as anteriores",
    "todas as alternativas",
    "todas as opções",
    "nenhuma das anteriores",
    "nenhuma das alternativas",
    "nenhuma das opções",
    "all of the above",
    "none of the above",
    "all of these",
    "none of these",
)


class CodeCheck(StrEnum):
    """What the run-code tool does with a question's code."""

    # Run it: what it prints must be the text of the correct option.
    OUTPUT = "output"
    # Run it: it must finish without an error. What it prints is not
    # compared.
    RUNS = "runs"
    # Do not run it: a fragment, or code that is meant to fail.
    SKIP = "skip"


class QuestionOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: OptionKey
    text: str
    # One sentence saying why this option is right or wrong.
    reason: str


class QuestionText(BaseModel):
    """A question's text in one language."""

    model_config = ConfigDict(extra="forbid")

    stem: str
    code: str | None
    options: list[QuestionOption]
    explanation: str


class Verification(BaseModel):
    """What the pipeline found out about a question. All empty at first."""

    model_config = ConfigDict(extra="forbid")

    # The key the blind solver chose. None before the blind solve, and
    # when the solver found no single defensible option.
    blind_key: OptionKey | None = None
    # None before the blind solve.
    blind_agrees: bool | None = None
    # None when the code is not run: there is none, or code_check is skip.
    code_ran: bool | None = None
    human_checked: bool = False


class QuestionDoc(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # "<subject>.<topic>.<four digits>". Never reused for another question.
    id: str
    subject: Slug
    topic: Slug
    type: Literal[QuestionType.MCQ]
    # It only sets the rating the question starts with.
    difficulty_prior: int = Field(ge=DIFFICULTY_MIN, le=DIFFICULTY_MAX)
    correct_key: OptionKey
    code_language: CodeLanguage | None
    code_check: CodeCheck | None = None
    # Where the question came from, for example "generated".
    source: str = Field(min_length=1, max_length=32)
    version: int = Field(default=1, ge=1)
    locales: dict[Locale, QuestionText]
    verification: Verification = Field(default_factory=Verification)

    @model_validator(mode="after")
    def follows_the_format_rules(self) -> Self:
        settings = get_settings()
        problems = [
            *_id_problems(self),
            *_locale_problems(self),
            *_text_problems(self, settings),
            *_option_problems(self),
            *_code_problems(self, settings),
            *_verification_problems(self),
        ]
        if problems:
            raise ValueError("\n".join(problems))
        return self

    def code(self) -> str | None:
        """The question's code, which is the same in every language."""
        return self.locales[Locale.PT_BR].code

    def to_line(self) -> str:
        """The question as its line in a content file."""
        return self.model_dump_json()


# ---- the rules, each returning the problems it finds ----


def _id_problems(doc: QuestionDoc) -> list[str]:
    prefix = f"{doc.subject}.{doc.topic}."
    number = doc.id.removeprefix(prefix)
    problems = []
    if not doc.id.startswith(prefix) or not _ID_NUMBER.match(number):
        problems.append(
            f"id must be {prefix} followed by four digits, got {doc.id!r}"
        )
    if len(doc.id) > ID_MAX_CHARS:
        problems.append(f"id is longer than {ID_MAX_CHARS} characters")
    return problems


def _locale_problems(doc: QuestionDoc) -> list[str]:
    missing = [locale.value for locale in Locale if locale not in doc.locales]
    if missing:
        return ["locales is missing " + ", ".join(missing)]
    return []


def _text_problems(doc: QuestionDoc, settings: Settings) -> list[str]:
    problems = []
    for locale, text in doc.locales.items():
        fields = [
            ("stem", text.stem, settings.question_stem_max_chars),
            (
                "explanation",
                text.explanation,
                settings.question_explanation_max_chars,
            ),
        ]
        for option in text.options:
            name = f"option {option.key}"
            fields.append(
                (
                    f"{name} text",
                    option.text,
                    settings.question_option_max_chars,
                )
            )
            fields.append(
                (
                    f"{name} reason",
                    option.reason,
                    settings.question_reason_max_chars,
                )
            )
        for name, value, max_chars in fields:
            problems += [
                f"{locale.value} {name} {problem}"
                for problem in _string_problems(value, max_chars)
            ]
    return problems


def _string_problems(value: str, max_chars: int) -> list[str]:
    if not value.strip():
        return ["is empty"]
    problems = []
    if value != value.strip():
        problems.append("starts or ends with a space")
    if len(value) > max_chars:
        problems.append(
            f"has {len(value)} characters, the limit is {max_chars}"
        )
    return problems


def _option_problems(doc: QuestionDoc) -> list[str]:
    problems = []
    for locale, text in doc.locales.items():
        keys = tuple(option.key for option in text.options)
        if keys != OPTION_KEYS:
            problems.append(
                f"{locale.value} options must have the keys a, b, c, d in "
                f"that order, got {', '.join(keys) or 'none'}"
            )
        texts = [_folded(option.text) for option in text.options]
        if len(set(texts)) != len(texts):
            problems.append(f"{locale.value} has two options with one text")
        for option in text.options:
            for phrase in _FORBIDDEN_OPTION_PHRASES:
                if phrase in _folded(option.text):
                    problems.append(
                        f"{locale.value} option {option.key} says "
                        f"{phrase!r}, which the writing rules forbid"
                    )
    return problems


def _folded(text: str) -> str:
    """The text in lower case with single spaces, for comparing."""
    return " ".join(text.casefold().split())


def _code_problems(doc: QuestionDoc, settings: Settings) -> list[str]:
    codes = {text.code for text in doc.locales.values()}
    if len(codes) > 1:
        return ["code must be the same in every language"]
    code = codes.pop() if codes else None

    if code is None:
        problems = []
        if doc.code_language is not None:
            problems.append("code_language is set but there is no code")
        if doc.code_check is not None:
            problems.append("code_check is set but there is no code")
        return problems

    problems = []
    if doc.code_language is None:
        problems.append("there is code but code_language is null")
    if doc.code_check is None:
        problems.append(
            "there is code but code_check is null: say output, runs or skip"
        )
    lines = code.split("\n")
    if not lines[0].strip() or not lines[-1].strip():
        problems.append("code starts or ends with an empty line")
    if len(lines) > settings.question_code_max_lines:
        problems.append(
            f"code has {len(lines)} lines, the limit is "
            f"{settings.question_code_max_lines}"
        )
    longest = max(len(line) for line in lines)
    if longest > settings.question_code_max_line_chars:
        problems.append(
            f"code has a line of {longest} characters, the limit is "
            f"{settings.question_code_max_line_chars}"
        )
    if "\t" in code:
        problems.append("code has a tab: indent with spaces")
    return problems


def _verification_problems(doc: QuestionDoc) -> list[str]:
    verification = doc.verification
    problems = []
    if verification.blind_agrees is None:
        if verification.blind_key is not None:
            problems.append("blind_key is set but blind_agrees is null")
    else:
        agrees = verification.blind_key == doc.correct_key
        if verification.blind_agrees != agrees:
            problems.append(
                f"blind_agrees is {str(verification.blind_agrees).lower()} "
                f"but blind_key is {verification.blind_key or 'null'} and "
                f"correct_key is {doc.correct_key}"
            )
    code_is_run = doc.code_check in (CodeCheck.OUTPUT, CodeCheck.RUNS)
    if verification.code_ran is not None and not code_is_run:
        problems.append("code_ran is set but the question has no code to run")
    return problems


# ---- what the tools and the importer ask about a question ----


def validation_problems(error: ValidationError) -> list[str]:
    """One readable line per problem pydantic found in a question."""
    problems = []
    for detail in error.errors():
        where = ".".join(str(part) for part in detail["loc"])
        message = detail["msg"].removeprefix("Value error, ")
        for line in message.split("\n"):
            problems.append(f"{where}: {line}" if where else line)
    return problems


def unverified_reasons(doc: QuestionDoc) -> list[str]:
    """Why the question has not passed the pipeline. Empty when it has."""
    verification = doc.verification
    reasons = []
    if verification.blind_agrees is None:
        reasons.append("it was not blind-solved")
    elif not verification.blind_agrees:
        reasons.append(
            f"the blind solver answered {verification.blind_key or 'nothing'}"
            f", the key is {doc.correct_key}"
        )
    if doc.code_check in (CodeCheck.OUTPUT, CodeCheck.RUNS):
        if verification.code_ran is None:
            reasons.append("its code was not run")
        elif not verification.code_ran:
            reasons.append("its code failed the run")
    return reasons


def content_hash(doc: QuestionDoc) -> str:
    """A hash of what the question says and how it is graded.

    It leaves out version and verification, so recording a check does not
    look like a change of content.
    """
    content = doc.model_dump(mode="json", exclude={"version", "verification"})
    canonical = json.dumps(
        content, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
