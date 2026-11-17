"""strip-keys and check-blind: the two ends of the blind solve."""

import json
from pathlib import Path

import pytest

from app.services.question_files import read_question_file
from content.tools import run_log
from content.tools.check_blind import (
    BlindAnswer,
    Disagreement,
    answers_path_of,
    check_blind,
    record_answer,
)
from content.tools.common import ToolError
from content.tools.strip_keys import strip, strip_file, stripped_path_of
from tests.support.questions import (
    PYTHON_PRINTS_2,
    doc,
    output_question,
    question,
    read_lines,
    write_lines,
)

SUBJECT = "estruturas-de-dados"
ID_1 = f"{SUBJECT}.pilhas.0001"
ID_2 = f"{SUBJECT}.pilhas.0002"
ID_3 = f"{SUBJECT}.pilhas.0003"


def _questions(tmp_path: Path) -> Path:
    return write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [question(1), question(2), question(3)],
    )


def _answers(path: Path, *answers: dict[str, object]) -> Path:
    path.write_text(
        "".join(json.dumps(answer) + "\n" for answer in answers),
        encoding="utf-8",
    )
    return path


# ---- strip-keys ----


def test_a_stripped_question_keeps_only_what_the_solver_may_see() -> None:
    stripped = strip(doc(output_question(1, PYTHON_PRINTS_2, "python")))

    data = json.loads(stripped.model_dump_json())
    assert data == {
        "id": ID_1,
        "code_language": "python",
        "locales": {
            "pt-BR": {
                "stem": "Qual estrutura de dados segue a política LIFO?",
                "code": PYTHON_PRINTS_2,
                "options": [
                    {"key": "a", "text": "1"},
                    {"key": "b", "text": "2"},
                    {"key": "c", "text": "3"},
                    {"key": "d", "text": "4"},
                ],
            },
            "en": {
                "stem": "Qual estrutura de dados segue a política LIFO?",
                "code": PYTHON_PRINTS_2,
                "options": [
                    {"key": "a", "text": "1"},
                    {"key": "b", "text": "2"},
                    {"key": "c", "text": "3"},
                    {"key": "d", "text": "4"},
                ],
            },
        },
    }


def test_the_stripped_file_has_no_key_reason_or_explanation(
    tmp_path: Path,
) -> None:
    source = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [question(1, verified=True), question(2, correct_key="d")],
    )
    target = stripped_path_of(source)

    count = strip_file(source, target)

    assert count == 2
    assert target == tmp_path / SUBJECT / "pilhas.stripped.jsonl"
    text = target.read_text(encoding="utf-8")
    assert [line["id"] for line in read_lines(target)] == [ID_1, ID_2]
    for leaked in (
        "correct_key",
        "reason",
        "explanation",
        "verification",
        "blind_key",
        "difficulty",
        "é o primeiro a sair",  # a reason's text
        "pilha de pratos",  # the explanation's text
    ):
        assert leaked not in text


def test_a_file_with_a_broken_line_is_not_stripped(tmp_path: Path) -> None:
    source = _questions(tmp_path)
    source.write_text(
        source.read_text(encoding="utf-8") + "{}\n", encoding="utf-8"
    )

    with pytest.raises(ToolError, match="run validate"):
        strip_file(source, stripped_path_of(source))


# ---- check-blind ----


def test_an_answer_is_recorded_in_the_verification() -> None:
    agreed = record_answer(doc(), BlindAnswer(id=ID_1, key="b"))
    disagreed = record_answer(doc(), BlindAnswer(id=ID_1, key="c"))
    no_answer = record_answer(doc(), BlindAnswer(id=ID_1, key=None))

    assert (
        agreed.verification.blind_key,
        agreed.verification.blind_agrees,
    ) == (
        "b",
        True,
    )
    assert (
        disagreed.verification.blind_key,
        disagreed.verification.blind_agrees,
    ) == ("c", False)
    assert (
        no_answer.verification.blind_key,
        no_answer.verification.blind_agrees,
    ) == (None, False)


def test_the_answers_are_written_to_the_file_and_disagreements_returned(
    tmp_path: Path,
) -> None:
    source = _questions(tmp_path)
    answers = _answers(
        answers_path_of(source),
        {"id": ID_1, "key": "b"},
        {"id": ID_2, "key": "a", "note": "b is a queue, not a stack"},
        {"id": ID_3, "key": None, "note": "a and b are both right"},
    )
    assert answers == tmp_path / SUBJECT / "pilhas.answers.jsonl"
    log = tmp_path / "log.jsonl"

    disagreements = check_blind(source, answers, log=log)

    assert disagreements == [
        Disagreement(ID_2, "b", "a", "b is a queue, not a stack"),
        Disagreement(ID_3, "b", None, "a and b are both right"),
    ]
    assert str(disagreements[1]) == (
        f"{ID_3}: the blind solver answered nothing, the key is b. "
        "Solver's note: a and b are both right"
    )
    lines, problems = read_question_file(source)
    assert problems == []
    assert [
        (line.doc.verification.blind_key, line.doc.verification.blind_agrees)
        for line in lines
    ] == [("b", True), ("a", False), (None, False)]
    [entry] = run_log.read_entries(log)
    assert (entry.step, entry.checked, entry.failed) == (
        run_log.Step.BLIND_SOLVE,
        3,
        [ID_2, ID_3],
    )


def test_a_dry_run_leaves_the_question_file_alone(tmp_path: Path) -> None:
    source = _questions(tmp_path)
    before = source.read_text(encoding="utf-8")
    answers = _answers(
        tmp_path / "answers.jsonl",
        {"id": ID_1, "key": "b"},
        {"id": ID_2, "key": "b"},
        {"id": ID_3, "key": "c"},
    )

    disagreements = check_blind(source, answers, write=False)

    assert [d.question_id for d in disagreements] == [ID_3]
    assert source.read_text(encoding="utf-8") == before


@pytest.mark.parametrize(
    ("answers", "message"),
    [
        (
            [{"id": ID_1, "key": "b"}, {"id": ID_2, "key": "b"}],
            f"no answer for {ID_3}",
        ),
        (
            [
                {"id": ID_1, "key": "b"},
                {"id": ID_2, "key": "b"},
                {"id": ID_3, "key": "b"},
                {"id": "estruturas-de-dados.pilhas.0009", "key": "b"},
            ],
            "an answer for estruturas-de-dados.pilhas.0009, which is not in",
        ),
        (
            [{"id": ID_1, "key": "b"}, {"id": ID_1, "key": "c"}],
            f"a second answer for {ID_1}",
        ),
        ([{"id": ID_1, "key": "e"}], "not an answer line: key"),
        ([{"id": ID_1}], "not an answer line: key"),
    ],
    ids=["missing", "unknown id", "twice", "bad key", "no key"],
)
def test_answers_that_do_not_match_the_questions_stop_the_tool(
    tmp_path: Path, answers: list[dict[str, object]], message: str
) -> None:
    source = _questions(tmp_path)
    before = source.read_text(encoding="utf-8")
    answers_file = _answers(tmp_path / "answers.jsonl", *answers)

    with pytest.raises(ToolError, match=message):
        check_blind(source, answers_file)

    assert source.read_text(encoding="utf-8") == before


def test_a_missing_answers_file_stops_the_tool(tmp_path: Path) -> None:
    source = _questions(tmp_path)

    with pytest.raises(ToolError, match="does not exist"):
        check_blind(source, answers_path_of(source))
