"""validate: question files against the format and the catalog."""

from pathlib import Path

from content.tools import run_log
from content.tools.validate import validate
from tests.support.questions import question, the_catalog, write_lines

SUBJECT = "estruturas-de-dados"


def test_valid_files_have_no_problems(tmp_path: Path) -> None:
    write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl", [question(1), question(2)]
    )
    write_lines(
        tmp_path / SUBJECT / "filas-e-deques.jsonl",
        [question(1, topic="filas-e-deques")],
    )

    lines, problems = validate([tmp_path], the_catalog())

    assert problems == []
    assert len(lines) == 3


def test_format_and_catalog_problems_are_reported_together(
    tmp_path: Path,
) -> None:
    long_reason = question(2)
    long_reason["locales"]["pt-BR"]["options"][2]["reason"] = "x" * 200
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [question(1), long_reason, question(3, topic="panquecas")],
    )

    lines, problems = validate([path], the_catalog())

    assert len(lines) == 2
    assert [str(problem) for problem in problems] == [
        f"{path}:2 {SUBJECT}.pilhas.0002: pt-BR option c reason has 200 "
        "characters, the limit is 160",
        f"{path}:3 {SUBJECT}.panquecas.0003: belongs in "
        f"{SUBJECT}/panquecas.jsonl",
        f"{path}:3 {SUBJECT}.panquecas.0003: no topic panquecas in "
        f"{SUBJECT} in the catalog",
    ]


def test_unverified_questions_are_problems_only_when_asked(
    tmp_path: Path,
) -> None:
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [question(1, verified=True), question(2)],
    )

    _, in_the_pipeline = validate([path], the_catalog())
    _, in_the_bank = validate([path], the_catalog(), require_verified=True)

    assert in_the_pipeline == []
    assert [problem.message for problem in in_the_bank] == [
        "it was not blind-solved"
    ]


def test_the_log_gets_one_entry_per_file_with_the_failed_lines(
    tmp_path: Path,
) -> None:
    bad = question(2)
    bad["correct_key"] = "z"
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl", [question(1), bad, question(3)]
    )
    path.write_text(
        path.read_text(encoding="utf-8") + "not json\n", encoding="utf-8"
    )
    other = write_lines(
        tmp_path / SUBJECT / "filas-e-deques.jsonl",
        [question(1, topic="filas-e-deques")],
    )
    log = tmp_path / "log.jsonl"

    validate([path, other], the_catalog(), log=log)

    entries = run_log.read_entries(log)
    assert [
        (e.step, e.subject, e.topic, e.checked, e.failed) for e in entries
    ] == [
        (
            run_log.Step.VALIDATE,
            SUBJECT,
            "pilhas",
            4,
            [f"{SUBJECT}.pilhas.0002", "line 4"],
        ),
        (run_log.Step.VALIDATE, SUBJECT, "filas-e-deques", 1, []),
    ]
