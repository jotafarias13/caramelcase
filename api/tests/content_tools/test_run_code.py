"""run-code: executing a question's Python, C or SQL.

These tests start real processes: the Python interpreter, the C compiler
(`cc`, with the sanitizers) and SQLite.
"""

import json
from pathlib import Path

import pytest

from app.enums import CodeLanguage
from app.services.question_files import read_question_file
from app.settings import Settings
from content.tools import run_log
from content.tools.common import ToolError
from content.tools.run_code import (
    check_code,
    comparable,
    run_code,
    run_code_in_file,
)
from content.tools.sql_runner import statements_of
from tests.support.questions import (
    C_PRINTS_2,
    PYTHON_PRINTS_2,
    SQL_PRINTS_2,
    doc,
    output_question,
    question,
    write_lines,
)

SETTINGS = Settings()
SUBJECT = "estruturas-de-dados"

C_PROGRAM = (
    "#include <stdio.h>\n\nint main(void) {{\n{body}\n    return 0;\n}}"
)


def c_program(body: str) -> str:
    return C_PROGRAM.format(body=body)


# ---- running code ----


@pytest.mark.parametrize(
    ("code", "language"),
    [
        (PYTHON_PRINTS_2, CodeLanguage.PYTHON),
        (C_PRINTS_2, CodeLanguage.C),
        (SQL_PRINTS_2, CodeLanguage.SQL),
    ],
    ids=["python", "c", "sql"],
)
def test_code_runs_and_its_output_is_collected(
    code: str, language: CodeLanguage
) -> None:
    outcome = run_code(code, language, SETTINGS)

    assert outcome.ok, outcome.detail
    assert outcome.output == "2\n"
    assert outcome.detail == ""


FAILURES = [
    (
        "a Python exception",
        "pilha = []\npilha.pop()",
        CodeLanguage.PYTHON,
        "exit code 1: ",
        "IndexError: pop from empty list",
    ),
    (
        "a Python syntax error",
        "print('a'",
        CodeLanguage.PYTHON,
        "exit code 1: ",
        "SyntaxError",
    ),
    (
        "C that does not compile",
        c_program('    printf("%d\\n", x);'),
        CodeLanguage.C,
        "it does not compile: ",
        "undeclared",
    ),
    (
        "C with a compiler warning",
        c_program("    int unused = 1;"),
        CodeLanguage.C,
        "it does not compile: ",
        "unused",
    ),
    (
        "C that reads past the end of an array",
        c_program(
            "    int v[3] = {1, 2, 3};\n"
            "    int i = 3;\n"
            '    printf("%d\\n", v[i]);'
        ),
        CodeLanguage.C,
        "exit code ",
        "out of bounds",
    ),
    (
        "C that uses freed memory",
        "#include <stdio.h>\n#include <stdlib.h>\n\n"
        "int main(void) {\n"
        "    int *p = malloc(sizeof(int));\n"
        "    *p = 7;\n"
        "    free(p);\n"
        '    printf("%d\\n", *p);\n'
        "    return 0;\n"
        "}",
        CodeLanguage.C,
        # At run time for clang's sanitizer; gcc already sees it compiling.
        "",
        "use-after-free",
    ),
    (
        "C that exits with an error code",
        "int main(void) {\n    return 3;\n}",
        CodeLanguage.C,
        "exit code 3",
        "",
    ),
    (
        "SQL on a table that does not exist",
        "SELECT nome FROM aluno;",
        CodeLanguage.SQL,
        "exit code 1: ",
        "no such table: aluno",
    ),
    (
        "SQL that breaks a foreign key",
        "CREATE TABLE curso (id INTEGER PRIMARY KEY);\n"
        "CREATE TABLE aluno (curso_id INTEGER REFERENCES curso(id));\n"
        "INSERT INTO aluno VALUES (99);",
        CodeLanguage.SQL,
        "exit code 1: ",
        "FOREIGN KEY constraint failed",
    ),
]


@pytest.mark.parametrize(
    ("code", "language", "start", "detail"),
    [case[1:] for case in FAILURES],
    ids=[case[0] for case in FAILURES],
)
def test_code_fails_for(
    code: str, language: CodeLanguage, start: str, detail: str
) -> None:
    outcome = run_code(code, language, SETTINGS)

    assert not outcome.ok
    assert outcome.detail.startswith(start)
    assert detail in outcome.detail


def test_code_that_does_not_stop_fails_at_the_timeout() -> None:
    settings = Settings(code_run_timeout_seconds=0.5)

    outcome = run_code("while True:\n    pass", CodeLanguage.PYTHON, settings)

    assert not outcome.ok
    assert outcome.detail == "it ran for more than 0.5 s"


def test_code_that_prints_without_end_is_stopped_at_the_output_limit() -> None:
    settings = Settings(code_run_max_output_bytes=2000)

    outcome = run_code(
        "while True:\n    print('x' * 100)", CodeLanguage.PYTHON, settings
    )

    assert not outcome.ok
    assert outcome.detail == "it printed more than 2000 bytes"


@pytest.mark.parametrize(
    ("code", "language"),
    [
        ("import random\nprint(random.random())", CodeLanguage.PYTHON),
        ("import time\nprint(time.time_ns())", CodeLanguage.PYTHON),
        # The order of a set of strings changes from run to run.
        (
            "print(list({'pilha', 'fila', 'deque', 'lista'}))",
            CodeLanguage.PYTHON,
        ),
        ("SELECT random();", CodeLanguage.SQL),
    ],
    ids=["random", "time", "set order", "sql random"],
)
def test_code_that_prints_something_else_on_a_second_run_fails(
    code: str, language: CodeLanguage
) -> None:
    outcome = run_code(code, language, SETTINGS)

    assert not outcome.ok
    assert outcome.detail.startswith("it is not deterministic: a second run")


def test_code_runs_in_an_empty_directory_without_the_users_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://secret")
    code = (
        "import json, os\n"
        "print(json.dumps(os.listdir('.')))\n"
        "kept = {'PATH', 'TMPDIR', 'ASAN_OPTIONS'}\n"
        "print(json.dumps(sorted(set(os.environ) - kept)))\n"
        "print(input())"
    )

    outcome = run_code(code, CodeLanguage.PYTHON, SETTINGS)

    # It sees only its own files and has no input to read.
    assert not outcome.ok
    lines = outcome.output.splitlines()
    assert sorted(json.loads(lines[0])) == [
        "errors.txt",
        "output.txt",
        "question.py",
    ]
    # macOS adds one variable of its own to every process.
    assert set(json.loads(lines[1])) <= {"__CF_USER_TEXT_ENCODING", "LC_CTYPE"}
    assert "EOFError" in outcome.detail


def test_a_missing_compiler_stops_the_tool() -> None:
    settings = Settings(code_run_c_compiler="no-such-compiler")

    with pytest.raises(ToolError, match="no-such-compiler is not installed"):
        run_code(C_PRINTS_2, CodeLanguage.C, settings)


# ---- SQL ----


def test_sql_prints_rows_like_the_sqlite_shell() -> None:
    code = (
        "CREATE TABLE aluno (id INTEGER PRIMARY KEY, nome TEXT, nota REAL);\n"
        "INSERT INTO aluno VALUES (1, 'Ana', 8.5), (2, 'Bruno', NULL);\n"
        "UPDATE aluno SET nota = 7 WHERE id = 2;\n"
        "SELECT nome, nota FROM aluno ORDER BY id;\n"
        "SELECT COUNT(*), NULL FROM aluno"
    )

    outcome = run_code(code, CodeLanguage.SQL, SETTINGS)

    assert outcome.ok, outcome.detail
    assert outcome.output == "Ana|8.5\nBruno|7.0\n2|NULL\n"


def test_sql_is_split_at_the_end_of_each_statement_not_at_each_semicolon() -> (
    None
):
    trigger = (
        "CREATE TRIGGER conta AFTER INSERT ON aluno\n"
        "BEGIN\n"
        "    UPDATE total SET n = n + 1;\n"
        "    UPDATE total SET n = n + 1;\n"
        "END;"
    )
    sql = (
        "CREATE TABLE aluno (nome TEXT); CREATE TABLE total (n INTEGER);\n"
        f"{trigger}\n"
        "INSERT INTO total VALUES (0);\n"
        "INSERT INTO aluno VALUES ('a;b');\n"
        "SELECT n FROM total"
    )

    statements = statements_of(sql)

    assert statements[:2] == [
        "CREATE TABLE aluno (nome TEXT);",
        "CREATE TABLE total (n INTEGER);",
    ]
    assert statements[2] == trigger
    assert statements[-1] == "SELECT n FROM total"
    assert len(statements) == 6
    outcome = run_code(sql, CodeLanguage.SQL, SETTINGS)
    assert outcome.output == "2\n"


# ---- checking a question ----


@pytest.mark.parametrize(
    ("code", "language", "topic"),
    [
        (PYTHON_PRINTS_2, "python", "pilhas"),
        (C_PRINTS_2, "c", "listas-encadeadas"),
    ],
    ids=["python", "c"],
)
def test_an_output_question_passes_when_it_prints_the_correct_option(
    code: str, language: str, topic: str
) -> None:
    passing = doc(output_question(1, code, language, topic=topic))

    assert check_code(passing, SETTINGS) is None


def test_an_output_question_fails_when_it_prints_another_option() -> None:
    wrong_key = doc(
        output_question(1, PYTHON_PRINTS_2, "python", correct_key="c")
    )

    assert check_code(wrong_key, SETTINGS) == (
        "it printed '2', which is option b, but the key is c (pt-BR)"
    )


def test_an_output_question_fails_when_no_option_shows_the_output() -> None:
    data = output_question(1, "print(5)", "python")

    assert check_code(doc(data), SETTINGS) == (
        "it printed '5', which is no option, but the key is b (pt-BR)"
    )


def test_an_output_question_is_checked_in_every_language() -> None:
    data = output_question(1, PYTHON_PRINTS_2, "python")
    data["locales"]["en"]["options"][1]["text"] = "two"

    assert check_code(doc(data), SETTINGS) == (
        "it printed '2', which is no option, but the key is b (en)"
    )


def test_output_of_several_lines_is_compared_without_trailing_spaces() -> None:
    data = output_question(1, "print('a ')\nprint('b')\nprint()", "python")
    for text in data["locales"].values():
        text["options"][1]["text"] = "a\nb"

    assert check_code(doc(data), SETTINGS) is None
    assert comparable("\n a \nb  \n\n") == "a\nb"


def test_a_question_that_only_has_to_run_ignores_what_it_prints() -> None:
    runs = doc(
        question(code="print(5)", code_language="python", code_check="runs")
    )
    fails = doc(
        question(code="1 / 0", code_language="python", code_check="runs")
    )

    assert check_code(runs, SETTINGS) is None
    failure = check_code(fails, SETTINGS)
    assert failure is not None
    assert "ZeroDivisionError" in failure


# ---- a question file ----


def test_the_result_of_each_run_is_recorded_in_the_file(
    tmp_path: Path,
) -> None:
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [
            output_question(1, PYTHON_PRINTS_2, "python"),
            output_question(2, PYTHON_PRINTS_2, "python", correct_key="a"),
            question(3),
            question(
                4, code="pilha.pop(", code_language="python", code_check="skip"
            ),
        ],
    )
    log = tmp_path / "log.jsonl"

    ran, failures = run_code_in_file(path, SETTINGS, log=log)

    assert ran == 2
    assert [str(failure) for failure in failures] == [
        f"{SUBJECT}.pilhas.0002: it printed '2', which is option b, but "
        "the key is a (pt-BR)"
    ]
    lines, problems = read_question_file(path)
    assert problems == []
    assert [line.doc.verification.code_ran for line in lines] == [
        True,
        False,
        None,
        None,
    ]
    [entry] = run_log.read_entries(log)
    assert (entry.step, entry.checked, entry.failed) == (
        run_log.Step.RUN_CODE,
        2,
        [f"{SUBJECT}.pilhas.0002"],
    )


def test_a_dry_run_records_nothing(tmp_path: Path) -> None:
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [output_question(1, PYTHON_PRINTS_2, "python")],
    )
    before = path.read_text(encoding="utf-8")

    ran, failures = run_code_in_file(path, SETTINGS, write=False)

    assert (ran, failures) == (1, [])
    assert path.read_text(encoding="utf-8") == before
