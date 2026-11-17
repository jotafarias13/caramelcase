"""The tools' command line: python -m content.tools <command>.

One pipeline is run from end to end the way content/README.md describes
it, in a content directory of the test's own.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from app.settings import Settings
from tests.support.questions import (
    C_PRINTS_2,
    PYTHON_PRINTS_2,
    STEMS,
    output_question,
    question,
    read_lines,
    write_lines,
)

REPO_DIR = Path(__file__).resolve().parents[3]
SUBJECT = "estruturas-de-dados"


def _id(number: int) -> str:
    return f"{SUBJECT}.pilhas.{number:04d}"


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    """An empty content directory with the real catalog."""
    directory = tmp_path / "content"
    directory.mkdir()
    shutil.copy(Settings().content_dir / "catalog.yaml", directory)
    return directory


def tool(
    content_dir: Path, *args: str | Path
) -> subprocess.CompletedProcess[str]:
    """Run a tool from the repository root, as the README says."""
    return subprocess.run(
        [sys.executable, "-m", "content.tools", *map(str, args)],
        cwd=REPO_DIR,
        env={**os.environ, "CONTENT_DIR": str(content_dir)},
        capture_output=True,
        text=True,
        check=False,
    )


def test_a_topic_goes_through_the_whole_pipeline(content_dir: Path) -> None:
    work = write_lines(
        content_dir / "work" / SUBJECT / "pilhas.jsonl",
        [
            question(1),
            output_question(2, PYTHON_PRINTS_2, "python", stem=STEMS[1]),
            # The key is wrong: the code prints 3, which is option c.
            output_question(
                3,
                PYTHON_PRINTS_2.replace("3]", "3, 4]"),
                "python",
                stem=STEMS[2],
            ),
            question(4),  # the blind solver will disagree
            question(5, stem=STEMS[0]),  # repeats question 1
        ],
    )
    stripped = work.with_name("pilhas.stripped.jsonl")
    answers = work.with_name("pilhas.answers.jsonl")

    validated = tool(content_dir, "validate", work, "--log")
    assert validated.returncode == 0, validated.stderr
    assert (
        "validate: 5 valid questions in 1 file, 0 problems."
        in validated.stdout
    )

    ran = tool(content_dir, "run-code", work, "--log")
    assert ran.returncode == 1
    assert (
        f"{_id(3)}: it printed '3', which is option c, but the key is b"
        in ran.stdout
    )
    assert "run-code: 2 questions run, 1 failure." in ran.stdout

    deduped = tool(
        content_dir, "dedupe", work, "--against", content_dir / "bank", "--log"
    )
    assert deduped.returncode == 1
    assert f"{_id(5)}: near-duplicate of {_id(1)}" in deduped.stdout

    stripping = tool(content_dir, "strip-keys", work)
    assert stripping.returncode == 0, stripping.stderr
    assert f"5 questions written to {stripped}" in stripping.stdout
    assert "correct_key" not in stripped.read_text(encoding="utf-8")

    answers.write_text(
        "".join(
            json.dumps({"id": _id(number), "key": key}) + "\n"
            for number, key in (
                (1, "b"),
                (2, "b"),
                (3, "c"),
                (4, "d"),
                (5, "b"),
            )
        ),
        encoding="utf-8",
    )
    checked = tool(content_dir, "check-blind", work, "--log")
    assert checked.returncode == 1
    assert (
        f"{_id(4)}: the blind solver answered d, the key is b"
        in checked.stdout
    )
    assert "check-blind: 2 disagreements." in checked.stdout

    promoted = tool(content_dir, "promote", work, "--log")
    assert promoted.returncode == 1
    assert (
        "promote: 2 questions added to the bank, 3 dropped." in promoted.stdout
    )
    assert f"dropped {_id(5)}: near-duplicate of {_id(1)}" in promoted.stdout
    in_bank = read_lines(content_dir / "bank" / SUBJECT / "pilhas.jsonl")
    assert [line["id"] for line in in_bank] == [_id(1), _id(2)]
    assert [line["id"] for line in read_lines(work)] == [
        _id(3),
        _id(4),
        _id(5),
    ]

    bank_check = tool(
        content_dir, "validate", content_dir / "bank", "--verified"
    )
    assert bank_check.returncode == 0, bank_check.stdout

    reported = tool(content_dir, "report")
    assert reported.returncode == 0, reported.stderr
    report = (content_dir / "REPORT.md").read_text(encoding="utf-8")
    assert "| Pilhas | 2 | 2 | 0 | 0 | 0 | 0 | 100% | 0% | 0% |" in report
    assert "| Estruturas de Dados | Validate | 5 | 0 | 0% |" in report
    assert "| Estruturas de Dados | Run code | 2 | 1 | 50% |" in report
    assert "| Estruturas de Dados | Dedupe | 5 | 1 | 20% |" in report
    assert "| Estruturas de Dados | Blind solve | 5 | 2 | 40% |" in report
    assert "| Promote (failed means dropped) | 5 | 3 | 60% |" in report
    log = (content_dir / "pipeline-log.jsonl").read_text(encoding="utf-8")
    assert len(log.splitlines()) == 5


def test_a_c_question_runs_from_the_command_line(content_dir: Path) -> None:
    work = write_lines(
        content_dir / "work" / SUBJECT / "listas-encadeadas.jsonl",
        [output_question(1, C_PRINTS_2, "c", topic="listas-encadeadas")],
    )

    ran = tool(content_dir, "run-code", work)

    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert "run-code: 1 question run, 0 failures." in ran.stdout
    assert read_lines(work)[0]["verification"]["code_ran"] is True


def test_validate_fails_with_exit_code_1_and_lists_the_problems(
    content_dir: Path,
) -> None:
    bad = question(1)
    bad["locales"]["pt-BR"]["options"][3]["text"] = "Nenhuma das anteriores"
    work = write_lines(content_dir / "work" / SUBJECT / "pilhas.jsonl", [bad])

    result = tool(content_dir, "validate", work)

    assert result.returncode == 1
    assert (
        f"{work}:1 {_id(1)}: pt-BR option d says 'nenhuma das anteriores'"
        in (result.stdout)
    )
    assert "validate: 0 valid questions in 1 file, 1 problem." in result.stdout


@pytest.mark.parametrize(
    "command",
    ["validate", "run-code", "dedupe", "strip-keys", "check-blind", "promote"],
)
def test_a_tool_that_cannot_work_exits_with_code_2(
    content_dir: Path, command: str
) -> None:
    missing = content_dir / "work" / SUBJECT / "pilhas.jsonl"

    result = tool(content_dir, command, missing)

    assert result.returncode == 2
    assert result.stderr.strip() == f"{missing} does not exist"
    assert "Traceback" not in result.stderr


def test_a_tool_refuses_a_file_with_a_broken_line(content_dir: Path) -> None:
    work = write_lines(
        content_dir / "work" / SUBJECT / "pilhas.jsonl", [question(1)]
    )
    work.write_text(
        work.read_text(encoding="utf-8") + "{}\n", encoding="utf-8"
    )

    result = tool(content_dir, "run-code", work)

    assert result.returncode == 2
    assert f"{work}:2: id: Field required" in result.stderr
    assert "run validate and fix them first" in result.stderr
