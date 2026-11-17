"""promote: the last gate before the question bank."""

from pathlib import Path

import pytest

from app.services.question_files import load_bank
from app.settings import Settings
from content.tools import run_log
from content.tools.common import ToolError
from content.tools.promote import Dropped, PromoteResult, promote
from tests.support.questions import (
    PYTHON_PRINTS_2,
    STEMS,
    output_question,
    question,
    read_lines,
    the_catalog,
    write_lines,
)

SETTINGS = Settings()
SUBJECT = "estruturas-de-dados"


def _id(number: int, topic: str = "pilhas") -> str:
    return f"{SUBJECT}.{topic}.{number:04d}"


def _promote(
    work_file: Path, bank: Path, log: Path | None = None
) -> PromoteResult:
    return promote(work_file, bank, the_catalog(), SETTINGS, log=log)


def test_passing_questions_move_to_the_bank_and_the_work_file_goes(
    tmp_path: Path,
) -> None:
    bank = tmp_path / "bank"
    work = write_lines(
        tmp_path / "work" / SUBJECT / "pilhas.jsonl",
        [
            question(2, verified=True),
            question(1, verified=True),
            output_question(3, PYTHON_PRINTS_2, "python", verified=True),
        ],
    )

    result = _promote(work, bank)

    assert result == PromoteResult(
        promoted=[_id(2), _id(1), _id(3)], dropped=[]
    )
    assert not work.exists()
    # The bank file is sorted by id, and the bank is whole.
    in_bank = read_lines(bank / SUBJECT / "pilhas.jsonl")
    assert [line["id"] for line in in_bank] == [_id(1), _id(2), _id(3)]
    lines, problems = load_bank(bank, the_catalog())
    assert problems == []
    assert len(lines) == 3


def test_questions_join_the_ones_already_in_the_bank(tmp_path: Path) -> None:
    bank = tmp_path / "bank"
    write_lines(
        bank / SUBJECT / "pilhas.jsonl",
        [question(1, verified=True), question(4, verified=True)],
    )
    write_lines(
        bank / SUBJECT / "filas-e-deques.jsonl",
        [question(5, topic="filas-e-deques", verified=True)],
    )
    work = write_lines(
        tmp_path / "work" / SUBJECT / "pilhas.jsonl",
        [question(3, verified=True), question(2, verified=True)],
    )
    other_before = (bank / SUBJECT / "filas-e-deques.jsonl").read_text("utf-8")

    result = _promote(work, bank)

    assert result.dropped == []
    in_bank = read_lines(bank / SUBJECT / "pilhas.jsonl")
    assert [line["id"] for line in in_bank] == [_id(1), _id(2), _id(3), _id(4)]
    other_after = (bank / SUBJECT / "filas-e-deques.jsonl").read_text("utf-8")
    assert other_after == other_before


def test_a_question_that_did_not_pass_stays_behind_with_its_reasons(
    tmp_path: Path,
) -> None:
    bank = tmp_path / "bank"
    write_lines(bank / SUBJECT / "pilhas.jsonl", [question(1, verified=True)])
    disagreed = question(3)
    disagreed["verification"] = {"blind_key": "a", "blind_agrees": False}
    failed_run = output_question(4, PYTHON_PRINTS_2, "python", verified=True)
    failed_run["verification"]["code_ran"] = False
    broken = question(5, verified=True)
    broken["locales"]["en"]["explanation"] = ""
    work = write_lines(
        tmp_path / "work" / SUBJECT / "pilhas.jsonl",
        [
            question(2, verified=True),  # passes
            disagreed,
            failed_run,
            broken,
            question(
                1, stem="Outra pergunta, com um id já usado?", verified=True
            ),
            question(6, stem=STEMS[0], verified=True),  # repeats the bank's 1
            question(7, stem=STEMS[1], verified=True),  # repeats this file's 2
            question(6, topic="panquecas", verified=True),
        ],
    )
    raw_lines = work.read_text(encoding="utf-8").splitlines()
    log = tmp_path / "log.jsonl"

    result = _promote(work, bank, log)

    assert result.promoted == [_id(2)]
    assert [str(drop) for drop in result.dropped] == [
        f"{_id(3)}: the blind solver answered a, the key is b",
        f"{_id(4)}: its code failed the run",
        f"{_id(5)}: en explanation is empty",
        f"{_id(1)}: the id is already used at "
        f"{bank / SUBJECT / 'pilhas.jsonl'}:1",
        f"{_id(6)}: near-duplicate of {_id(1)} (similarity 1.00)",
        f"{_id(7)}: near-duplicate of {_id(2)} (similarity 1.00)",
        f"{_id(6, 'panquecas')}: belongs in {SUBJECT}/panquecas.jsonl; "
        f"no topic panquecas in {SUBJECT} in the catalog",
    ]
    # The dropped lines stay in the work file exactly as they were.
    assert work.read_text(encoding="utf-8").splitlines() == raw_lines[1:]
    in_bank = read_lines(bank / SUBJECT / "pilhas.jsonl")
    assert [line["id"] for line in in_bank] == [_id(1), _id(2)]
    [entry] = run_log.read_entries(log)
    assert (entry.step, entry.checked) == (run_log.Step.PROMOTE, 8)
    assert entry.failed == sorted(drop.label for drop in result.dropped)


def test_a_line_without_an_id_is_dropped_by_its_line_number(
    tmp_path: Path,
) -> None:
    work = write_lines(
        tmp_path / "work" / SUBJECT / "pilhas.jsonl",
        [question(1, verified=True)],
    )
    work.write_text(
        work.read_text(encoding="utf-8") + "not json\n", encoding="utf-8"
    )

    result = _promote(work, tmp_path / "bank")

    assert result.promoted == [_id(1)]
    [drop] = result.dropped
    assert drop.label == "line 2"
    assert work.read_text(encoding="utf-8") == "not json\n"


def test_a_duplicate_of_a_dropped_question_is_not_a_duplicate(
    tmp_path: Path,
) -> None:
    work = write_lines(
        tmp_path / "work" / SUBJECT / "pilhas.jsonl",
        [question(1), question(2, stem=STEMS[0], verified=True)],
    )

    result = _promote(work, tmp_path / "bank")

    assert result == PromoteResult(
        promoted=[_id(2)],
        dropped=[Dropped(_id(1), ["it was not blind-solved"])],
    )


def test_a_bank_with_problems_is_not_added_to(tmp_path: Path) -> None:
    bank = tmp_path / "bank"
    bank_file = write_lines(bank / SUBJECT / "pilhas.jsonl", [question(1)])
    work = write_lines(
        tmp_path / "work" / SUBJECT / "pilhas.jsonl",
        [question(2, verified=True)],
    )
    before = (bank_file.read_text("utf-8"), work.read_text("utf-8"))

    with pytest.raises(ToolError, match="has problems"):
        _promote(work, bank)

    assert (bank_file.read_text("utf-8"), work.read_text("utf-8")) == before


def test_a_file_of_the_bank_or_a_missing_file_cannot_be_promoted(
    tmp_path: Path,
) -> None:
    bank = tmp_path / "bank"
    in_bank = write_lines(
        bank / SUBJECT / "pilhas.jsonl", [question(1, verified=True)]
    )

    with pytest.raises(ToolError, match="already in the bank"):
        _promote(in_bank, bank)
    with pytest.raises(ToolError, match="does not exist"):
        _promote(tmp_path / "work" / SUBJECT / "pilhas.jsonl", bank)
    assert in_bank.exists()
