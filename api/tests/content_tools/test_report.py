"""report: content/REPORT.md, and the pipeline log it reads."""

from datetime import UTC, date, datetime
from pathlib import Path

from content.tools import run_log
from content.tools.report import build_report
from content.tools.run_log import LogEntry, Step
from tests.support.questions import (
    PYTHON_PRINTS_2,
    doc,
    output_question,
    question,
    the_catalog,
)

SUBJECT = "estruturas-de-dados"
TODAY = date(2026, 11, 16)


def _entry(
    step: Step, checked: int, failed: int, subject: str = SUBJECT
) -> LogEntry:
    return LogEntry(
        at=datetime(2026, 11, 16, 12, 0, tzinfo=UTC),
        step=step,
        subject=subject,
        topic="pilhas",
        checked=checked,
        failed=[f"q{number}" for number in range(failed)],
    )


def _row(report: str, first_cell: str) -> list[str]:
    """The cells of the first table row that starts with the cell."""
    for line in report.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells[0] == first_cell:
            return cells
    raise AssertionError(f"no row {first_cell!r} in the report")


def _section(report: str, title: str) -> str:
    """The text of the section with this "## " title."""
    after = report.split(f"## {title}\n", 1)[1]
    return after.split("\n## ", 1)[0]


def test_an_empty_bank_gives_a_report_with_every_topic_at_zero() -> None:
    report = build_report([], [], the_catalog(), TODAY)

    assert report.startswith("# Question bank report\n")
    assert "on 2026-11-16" in report
    assert _row(report, "Estruturas de Dados") == [
        "Estruturas de Dados",
        "0",
        "-",
        "-",
        "-",
        "0",
        "0",
        "-",
        "0",
    ]
    assert _row(report, "Pilhas") == [
        "Pilhas",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "-",
        "-",
        "-",
    ]
    # The three launch subjects have a section each, the others none.
    assert report.count("\n## ") == 5
    assert "## Programação Orientada a Objetos" not in report
    assert "No pipeline run is logged yet." in report


def test_questions_are_counted_by_subject_topic_and_difficulty() -> None:
    longest = question(6, topic="filas-e-deques", difficulty=5, verified=True)
    longest["locales"]["pt-BR"]["options"][1]["text"] = "Uma pilha, e só ela"
    longest["verification"]["human_checked"] = True
    docs = [
        doc(question(1, difficulty=1, verified=True)),
        doc(question(2, difficulty=2, verified=True)),
        doc(question(3, difficulty=3, verified=True)),
        doc(question(4, difficulty=3, verified=True)),
        doc(
            output_question(
                5, PYTHON_PRINTS_2, "python", difficulty=3, verified=True
            )
        ),
        doc(longest),
        doc(
            question(
                1,
                subject="banco-de-dados",
                topic="visoes",
                difficulty=4,
                code="CREATE VIEW v AS SELECT 1",
                code_language="sql",
                code_check="skip",
                verified=True,
            )
        ),
    ]

    report = build_report(docs, [], the_catalog(), TODAY)

    # Subject, questions, level 1 to 2, level 3, level 4 to 5, with code,
    # code run, key is longest, human-checked. Five of the six questions
    # have a longest option (the options 1, 2, 3 and 4 have none), and it
    # is the correct one in one of the five.
    assert _row(report, "Estruturas de Dados")[1:] == [
        "6",
        "33%",
        "50%",
        "17%",
        "1",
        "1",
        "20%",
        "1",
    ]
    assert _row(report, "Banco de Dados")[1:] == [
        "1",
        "0%",
        "0%",
        "100%",
        "1",
        "0",
        "0%",
        "0",
    ]
    assert _row(report, "Introdução à Programação")[1] == "0"
    assert _row(_section(report, "Totals"), "**Total**")[1:6] == [
        "7",
        "29%",
        "43%",
        "29%",
        "2",
    ]

    data_structures = _section(report, "Estruturas de Dados")
    # Topic, questions, L1 to L5, then the three bands.
    assert _row(data_structures, "Pilhas")[1:] == [
        "5",
        "1",
        "1",
        "3",
        "0",
        "0",
        "40%",
        "60%",
        "0%",
    ]
    assert _row(data_structures, "Filas e deques")[1:] == [
        "1",
        "0",
        "0",
        "0",
        "0",
        "1",
        "0%",
        "0%",
        "100%",
    ]
    assert _row(data_structures, "Heaps e listas de prioridade")[1] == "0"
    assert _row(data_structures, "**Total**")[1] == "6"
    assert _row(_section(report, "Banco de Dados"), "Visões")[1] == "1"


def test_the_failure_rate_of_each_step_comes_from_the_log() -> None:
    entries = [
        _entry(Step.VALIDATE, checked=30, failed=3),
        _entry(Step.VALIDATE, checked=3, failed=0),
        _entry(Step.RUN_CODE, checked=12, failed=1),
        _entry(Step.BLIND_SOLVE, checked=30, failed=6),
        _entry(Step.PROMOTE, checked=30, failed=2),
        _entry(Step.VALIDATE, checked=10, failed=0, subject="banco-de-dados"),
    ]

    pipeline = _section(
        build_report([], entries, the_catalog(), TODAY), "Pipeline"
    )

    rows = [
        line.strip("| ").split(" | ")
        for line in pipeline.splitlines()
        if line.startswith("| ") and "---" not in line
    ]
    assert rows == [
        ["Subject", "Step", "Checked", "Failed", "Failure rate"],
        ["Estruturas de Dados", "Validate", "33", "3", "9%"],
        ["Estruturas de Dados", "Run code", "12", "1", "8%"],
        ["Estruturas de Dados", "Blind solve", "30", "6", "20%"],
        [
            "Estruturas de Dados",
            "Promote (failed means dropped)",
            "30",
            "2",
            "7%",
        ],
        ["Banco de Dados", "Validate", "10", "0", "0%"],
    ]


# ---- the pipeline log ----


def test_the_log_is_appended_to_and_read_back(tmp_path: Path) -> None:
    log = tmp_path / "content" / "pipeline-log.jsonl"
    file = tmp_path / "work" / SUBJECT / "pilhas.jsonl"
    assert run_log.read_entries(log) == []

    run_log.append_entry(
        log, Step.VALIDATE, file, checked=30, failed=["b", "a"]
    )
    run_log.append_entry(log, Step.BLIND_SOLVE, file, checked=28, failed=[])

    entries = run_log.read_entries(log)
    assert [
        (e.step, e.subject, e.topic, e.checked, e.failed) for e in entries
    ] == [
        (Step.VALIDATE, SUBJECT, "pilhas", 30, ["a", "b"]),
        (Step.BLIND_SOLVE, SUBJECT, "pilhas", 28, []),
    ]
    assert entries[0].at.tzinfo is not None
    assert len(log.read_text(encoding="utf-8").splitlines()) == 2
