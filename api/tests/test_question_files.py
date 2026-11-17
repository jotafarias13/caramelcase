"""Reading question files and checking them against the catalog."""

from pathlib import Path

from app.services.question_files import (
    catalog_problems,
    find_question_files,
    load_bank,
    read_question_file,
    read_question_files,
    unverified_problems,
    write_question_file,
)
from tests.support.questions import (
    PYTHON_PRINTS_2,
    doc,
    output_question,
    question,
    the_catalog,
    write_lines,
)

SUBJECT = "estruturas-de-dados"


def test_a_file_is_read_line_by_line_and_empty_lines_are_skipped(
    tmp_path: Path,
) -> None:
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl", [question(1), question(2)]
    )
    path.write_text(
        path.read_text(encoding="utf-8") + "\n\n", encoding="utf-8"
    )

    lines, problems = read_question_file(path)

    assert problems == []
    assert [(line.line_number, line.doc.id) for line in lines] == [
        (1, f"{SUBJECT}.pilhas.0001"),
        (2, f"{SUBJECT}.pilhas.0002"),
    ]
    assert lines[0].path == path


def test_a_bad_line_becomes_problems_and_the_other_lines_still_load(
    tmp_path: Path,
) -> None:
    bad = question(2)
    bad["correct_key"] = "e"
    bad["locales"]["en"]["options"][0]["reason"] = ""
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl", [question(1), bad, question(3)]
    )
    path.write_text(
        path.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8"
    )

    lines, problems = read_question_file(path)

    assert [line.line_number for line in lines] == [1, 3]
    assert [(p.line_number, p.question_id) for p in problems] == [
        (2, f"{SUBJECT}.pilhas.0002"),
        (4, None),
    ]
    # pydantic stops at the first kind of error: the bad key hides the
    # empty reason until the key is fixed.
    assert "correct_key" in problems[0].message
    assert str(problems[0]).startswith(
        f"{path}:2 {SUBJECT}.pilhas.0002: correct_key"
    )
    assert str(problems[1]).startswith(f"{path}:4: ")


def test_a_directory_gives_its_question_files_without_the_blind_solve_files(
    tmp_path: Path,
) -> None:
    for name in (
        f"{SUBJECT}/pilhas.jsonl",
        f"{SUBJECT}/pilhas.stripped.jsonl",
        f"{SUBJECT}/pilhas.answers.jsonl",
        f"{SUBJECT}/filas-e-deques.jsonl",
        "banco-de-dados/visoes.jsonl",
        "README.md",
    ):
        path = tmp_path / name
        path.parent.mkdir(exist_ok=True)
        path.touch()
    alone = tmp_path / SUBJECT / "pilhas.stripped.jsonl"

    assert find_question_files([tmp_path, alone]) == [
        tmp_path / "banco-de-dados" / "visoes.jsonl",
        tmp_path / SUBJECT / "filas-e-deques.jsonl",
        tmp_path / SUBJECT / "pilhas.jsonl",
        # A file given by name is taken as it is.
        alone,
    ]


def test_writing_a_file_and_reading_it_gives_the_same_questions(
    tmp_path: Path,
) -> None:
    docs = [
        doc(question(1)),
        doc(output_question(2, PYTHON_PRINTS_2, "python")),
    ]
    path = tmp_path / "new" / SUBJECT / "pilhas.jsonl"

    write_question_file(path, docs)

    lines, problems = read_question_file(path)
    assert problems == []
    assert [line.doc for line in lines] == docs
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


# ---- against the catalog ----


def test_questions_that_fit_the_catalog_have_no_problem(
    tmp_path: Path,
) -> None:
    write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl", [question(1), question(2)]
    )
    write_lines(
        tmp_path / SUBJECT / "listas-encadeadas.jsonl",
        [
            question(
                1,
                topic="listas-encadeadas",
                code="no->prox = NULL;",
                code_language="c",
                code_check="skip",
            )
        ],
    )

    lines, problems = read_question_files([tmp_path])

    assert problems == []
    assert len(lines) == 3
    assert catalog_problems(lines, the_catalog()) == []


def test_the_catalog_rejects_unknown_subjects_topics_and_wrong_languages(
    tmp_path: Path,
) -> None:
    write_lines(
        tmp_path / "culinaria" / "pilhas.jsonl",
        [question(1, subject="culinaria")],
    )
    write_lines(
        tmp_path / SUBJECT / "panquecas.jsonl",
        [question(1, topic="panquecas")],
    )
    write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [
            question(
                1, code="SELECT 1;", code_language="sql", code_check="runs"
            )
        ],
    )

    lines, _ = read_question_files([tmp_path])
    problems = catalog_problems(lines, the_catalog())

    assert sorted(problem.message for problem in problems) == [
        "code_language is sql, the topic's is python",
        "no subject culinaria in the catalog",
        "no topic panquecas in estruturas-de-dados in the catalog",
    ]


def test_a_question_must_be_in_the_file_of_its_subject_and_topic(
    tmp_path: Path,
) -> None:
    write_lines(tmp_path / SUBJECT / "filas-e-deques.jsonl", [question(1)])
    write_lines(tmp_path / "pilhas.jsonl", [question(2)])

    lines, _ = read_question_files([tmp_path])
    problems = catalog_problems(lines, the_catalog())

    assert [problem.message for problem in problems] == [
        "belongs in estruturas-de-dados/pilhas.jsonl",
        "belongs in estruturas-de-dados/pilhas.jsonl",
    ]


def test_an_id_used_twice_is_a_problem_of_the_second_question(
    tmp_path: Path,
) -> None:
    path = write_lines(
        tmp_path / SUBJECT / "pilhas.jsonl",
        [question(1), question(2), question(1, stem="Outra pergunta?")],
    )

    lines, _ = read_question_files([tmp_path])
    problems = catalog_problems(lines, the_catalog())

    assert [(p.line_number, p.message) for p in problems] == [
        (3, f"the id is already used at {path}:1")
    ]


# ---- the bank ----


def test_the_bank_accepts_only_questions_that_passed_the_pipeline(
    tmp_path: Path,
) -> None:
    bank = tmp_path / "bank"
    write_lines(
        bank / SUBJECT / "pilhas.jsonl",
        [
            question(1, verified=True),
            question(2),
            output_question(3, PYTHON_PRINTS_2, "python"),
        ],
    )

    lines, problems = load_bank(bank, the_catalog())

    assert len(lines) == 3
    assert problems == unverified_problems(lines)
    assert [(p.question_id, p.message) for p in problems] == [
        (f"{SUBJECT}.pilhas.0002", "it was not blind-solved"),
        (f"{SUBJECT}.pilhas.0003", "it was not blind-solved"),
        (f"{SUBJECT}.pilhas.0003", "its code was not run"),
    ]


def test_a_bank_that_does_not_exist_is_empty(tmp_path: Path) -> None:
    assert load_bank(tmp_path / "bank", the_catalog()) == ([], [])
