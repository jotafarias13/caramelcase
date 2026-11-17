"""QuestionDoc: the format of a line of the question bank."""

import json
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from pydantic import ValidationError

from app.domain.question_doc import (
    CodeCheck,
    QuestionDoc,
    content_hash,
    unverified_reasons,
    validation_problems,
)
from app.enums import CodeLanguage, Locale, QuestionType
from app.settings import get_settings
from tests.support.questions import (
    PYTHON_PRINTS_2,
    SPEC_SAMPLE_LINE,
    doc,
    output_question,
    question,
)

Change = Callable[[dict[str, Any]], None]


def problems_of(data: dict[str, Any]) -> list[str]:
    """What QuestionDoc says is wrong with the data. Empty when valid."""
    try:
        QuestionDoc.model_validate(data)
    except ValidationError as error:
        return validation_problems(error)
    return []


def pt(data: dict[str, Any]) -> dict[str, Any]:
    text: dict[str, Any] = data["locales"]["pt-BR"]
    return text


def en(data: dict[str, Any]) -> dict[str, Any]:
    text: dict[str, Any] = data["locales"]["en"]
    return text


# ---- the spec's sample line ----


def test_the_sample_line_of_the_spec_is_valid() -> None:
    sample = QuestionDoc.model_validate_json(SPEC_SAMPLE_LINE)

    assert sample.id == "estruturas-de-dados.pilhas.0001"
    assert sample.type is QuestionType.MCQ
    assert sample.correct_key == "b"
    assert sample.code_language is None
    assert sample.code_check is None
    assert set(sample.locales) == {Locale.PT_BR, Locale.EN}
    portuguese = sample.locales[Locale.PT_BR]
    assert [option.key for option in portuguese.options] == [
        "a",
        "b",
        "c",
        "d",
    ]
    assert portuguese.options[1].text == "Pilha"
    assert sample.verification.blind_agrees is True
    assert sample.verification.code_ran is None
    assert unverified_reasons(sample) == []


def test_a_question_is_written_as_one_line_that_reads_back_the_same() -> None:
    sample = QuestionDoc.model_validate_json(SPEC_SAMPLE_LINE)

    line = sample.to_line()

    assert "\n" not in line
    assert "política" in line  # written as UTF-8, not as \u escapes
    assert QuestionDoc.model_validate_json(line) == sample
    # The fields keep the order of the spec's sample.
    assert list(json.loads(line))[:4] == ["id", "subject", "topic", "type"]


def test_a_question_needs_no_verification_block() -> None:
    data = question()
    del data["verification"]

    new = QuestionDoc.model_validate(data)

    assert new.verification.blind_agrees is None
    assert new.verification.human_checked is False
    assert unverified_reasons(new) == ["it was not blind-solved"]


# ---- the rules ----


def _set(path: str, value: Any) -> Change:
    """A change that sets data[a][b]... = value, for a path "a.b"."""

    def change(data: dict[str, Any]) -> None:
        *parents, last = path.split(".")
        target: Any = data
        for key in parents:
            target = target[int(key)] if key.isdigit() else target[key]
        target[last] = value

    return change


def _in_both(field: str, value: Any) -> Change:
    def change(data: dict[str, Any]) -> None:
        pt(data)[field] = value
        en(data)[field] = value

    return change


def _drop_an_option(data: dict[str, Any]) -> None:
    del pt(data)["options"][3]


def _swap_two_options(data: dict[str, Any]) -> None:
    options = pt(data)["options"]
    options[0], options[1] = options[1], options[0]


def _drop_english(data: dict[str, Any]) -> None:
    del data["locales"]["en"]


INVALID: list[tuple[str, Change, str]] = [
    (
        "an id of another subject",
        _set("id", "banco-de-dados.pilhas.0001"),
        "id must be estruturas-de-dados.pilhas. followed by four digits",
    ),
    (
        "an id without four digits",
        _set("id", "estruturas-de-dados.pilhas.1"),
        "followed by four digits",
    ),
    ("a subject that is not a slug", _set("subject", "Estruturas"), "subject"),
    ("another question type", _set("type", "true_false"), "type"),
    ("a difficulty of 0", _set("difficulty_prior", 0), "difficulty_prior"),
    ("a difficulty of 6", _set("difficulty_prior", 6), "difficulty_prior"),
    (
        "a correct key that is no option",
        _set("correct_key", "e"),
        "correct_key",
    ),
    ("an unknown field", _set("hint", "LIFO"), "hint"),
    ("no English", _drop_english, "locales is missing en"),
    (
        "three options",
        _drop_an_option,
        "pt-BR options must have the keys a, b, c, d in that order, "
        "got a, b, c",
    ),
    (
        "options out of order",
        _swap_two_options,
        "pt-BR options must have the keys a, b, c, d in that order, "
        "got b, a, c, d",
    ),
    (
        "two options with the same text",
        _set("locales.en.options.2.text", "stack"),
        "en has two options with one text",
    ),
    (
        "all of the above",
        _set("locales.pt-BR.options.3.text", "Todas as anteriores"),
        "pt-BR option d says 'todas as anteriores'",
    ),
    (
        "none of the above",
        _set("locales.en.options.3.text", "None of the above"),
        "en option d says 'none of the above'",
    ),
    (
        "a reason of 161 characters",
        _set("locales.pt-BR.options.0.reason", "x" * 161),
        "pt-BR option a reason has 161 characters, the limit is 160",
    ),
    (
        "an empty reason",
        _set("locales.en.options.1.reason", " "),
        "en option b reason is empty",
    ),
    (
        "a stem that ends with a space",
        _set("locales.pt-BR.stem", "Qual estrutura segue a política LIFO? "),
        "pt-BR stem starts or ends with a space",
    ),
    (
        "an empty explanation",
        _set("locales.en.explanation", ""),
        "en explanation is empty",
    ),
    (
        "an option text over the limit",
        _set("locales.en.options.0.text", "x" * 141),
        "en option a text has 141 characters, the limit is 140",
    ),
    (
        "code without a language",
        _in_both("code", "print(1)"),
        "there is code but code_language is null",
    ),
    (
        "code without a code_check",
        _in_both("code", "print(1)"),
        "there is code but code_check is null",
    ),
    (
        "a language without code",
        _set("code_language", "python"),
        "code_language is set but there is no code",
    ),
    (
        "a code_check without code",
        _set("code_check", "runs"),
        "code_check is set but there is no code",
    ),
    (
        "code in one language only",
        _set("locales.pt-BR.code", "print(1)"),
        "code must be the same in every language",
    ),
    (
        "blind_agrees true with another key",
        _set("verification", {"blind_key": "a", "blind_agrees": True}),
        "blind_agrees is true but blind_key is a and correct_key is b",
    ),
    (
        "blind_agrees false with the correct key",
        _set("verification", {"blind_key": "b", "blind_agrees": False}),
        "blind_agrees is false but blind_key is b and correct_key is b",
    ),
    (
        "a blind key without blind_agrees",
        _set("verification", {"blind_key": "b"}),
        "blind_key is set but blind_agrees is null",
    ),
    (
        "code_ran without code",
        _set("verification", {"code_ran": True}),
        "code_ran is set but the question has no code to run",
    ),
]


@pytest.mark.parametrize(
    ("change", "message"),
    [(change, message) for _, change, message in INVALID],
    ids=[name for name, _, _ in INVALID],
)
def test_a_question_is_rejected_for(change: Change, message: str) -> None:
    data = question()
    assert problems_of(data) == []

    change(data)

    assert message in "\n".join(problems_of(data))


INVALID_CODE = [
    (
        "16 lines",
        "\n".join(["x = 1"] * 16),
        "code has 16 lines, the limit is 15",
    ),
    (
        "a line of 81 characters",
        "x = " + "1" * 77,
        "code has a line of 81 characters, the limit is 80",
    ),
    ("a tab", "if True:\n\tx = 1", "code has a tab: indent with spaces"),
    (
        "an empty last line",
        "x = 1\n",
        "code starts or ends with an empty line",
    ),
]


@pytest.mark.parametrize(
    ("code", "message"),
    [(code, message) for _, code, message in INVALID_CODE],
    ids=[name for name, _, _ in INVALID_CODE],
)
def test_code_is_rejected_for(code: str, message: str) -> None:
    data = question(code=code, code_language="python", code_check="runs")

    assert problems_of(data) == [message]


def test_every_problem_of_a_question_is_reported_at_once() -> None:
    data = question()
    data["id"] = "estruturas-de-dados.pilhas.1"
    pt(data)["options"][0]["reason"] = ""
    en(data)["options"][3]["text"] = "All of the above"

    assert len(problems_of(data)) == 3


def test_a_question_with_code_names_its_language_and_its_check() -> None:
    with_code = doc(output_question(1, PYTHON_PRINTS_2, "python"))

    assert with_code.code() == PYTHON_PRINTS_2
    assert with_code.code_language is CodeLanguage.PYTHON
    assert with_code.code_check is CodeCheck.OUTPUT


def test_code_of_15_lines_of_80_characters_is_accepted() -> None:
    code = "\n".join(["x = " + "1" * 76] * 15)

    assert (
        problems_of(question(code=code, code_language="c", code_check="skip"))
        == []
    )


def test_a_solver_that_found_no_answer_is_a_disagreement_without_a_key() -> (
    None
):
    data = question()
    data["verification"] = {"blind_key": None, "blind_agrees": False}

    unsolved = doc(data)

    assert unverified_reasons(unsolved) == [
        "the blind solver answered nothing, the key is b"
    ]


@pytest.fixture
def reasons_of_20_characters(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    monkeypatch.setenv("QUESTION_REASON_MAX_CHARS", "20")
    get_settings.cache_clear()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()


@pytest.mark.usefixtures("reasons_of_20_characters")
def test_the_limits_come_from_settings() -> None:
    problems = problems_of(question())

    assert (
        "pt-BR option a reason has 48 characters, the limit is 20" in problems
    )


# ---- what the pipeline still owes a question ----


def test_a_question_with_code_to_run_is_unverified_until_it_ran() -> None:
    data = output_question(1, PYTHON_PRINTS_2, "python", verified=True)
    assert unverified_reasons(doc(data)) == []

    data["verification"]["code_ran"] = None
    assert unverified_reasons(doc(data)) == ["its code was not run"]

    data["verification"]["code_ran"] = False
    assert unverified_reasons(doc(data)) == ["its code failed the run"]


def test_code_that_is_skipped_does_not_need_a_run() -> None:
    data = question(
        code="int *p = NULL;\n*p = 1;",
        code_language="c",
        code_check="skip",
        verified=True,
    )

    assert unverified_reasons(doc(data)) == []


# ---- content_hash ----


def test_the_content_hash_ignores_version_and_verification() -> None:
    data = question(verified=True)
    before = content_hash(doc(data))

    data["version"] = 7
    data["verification"]["human_checked"] = True
    data["verification"]["blind_key"] = None
    data["verification"]["blind_agrees"] = None

    assert content_hash(doc(data)) == before
    assert len(before) == 64


@pytest.mark.parametrize(
    "change",
    [
        _set("locales.pt-BR.stem", "Qual estrutura é LIFO?"),
        _set("locales.en.options.0.reason", "A queue is first in, first out."),
        _set("locales.en.explanation", "Last in, first out."),
        _set("difficulty_prior", 2),
        _set("source", "handwritten"),
    ],
    ids=["stem", "reason", "explanation", "difficulty", "source"],
)
def test_the_content_hash_changes_with_the_content(change: Change) -> None:
    data = question()
    before = content_hash(doc(data))

    change(data)

    assert content_hash(doc(data)) != before
