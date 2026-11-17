"""dedupe: near-duplicate questions within a subject."""

from difflib import SequenceMatcher
from pathlib import Path

from app.settings import Settings
from content.tools import run_log
from content.tools.dedupe import Duplicate, dedupe, find_duplicates
from tests.support.questions import (
    PYTHON_PRINTS_2,
    STEMS,
    doc,
    output_question,
    question,
    write_lines,
)

SETTINGS = Settings()
THRESHOLD = SETTINGS.dedupe_similarity
CODE_THRESHOLD = SETTINGS.dedupe_code_similarity
SUBJECT = "estruturas-de-dados"
PRINTS = "O que este programa imprime?"


def _ids(duplicates: list[Duplicate]) -> list[tuple[str, str]]:
    """(flagged question, the question it repeats), without the subject."""
    return [
        (
            d.question_id.removeprefix(SUBJECT + "."),
            d.of_id.removeprefix(SUBJECT + "."),
        )
        for d in duplicates
    ]


def test_different_questions_are_not_duplicates() -> None:
    docs = [doc(question(number)) for number in range(1, len(STEMS) + 1)]

    assert find_duplicates(docs, [], SETTINGS) == []


def test_a_reworded_stem_is_a_duplicate_of_the_question_before_it() -> None:
    docs = [
        doc(
            question(1, stem="Qual estrutura de dados segue a política LIFO?")
        ),
        doc(question(2)),
        doc(
            question(3, stem="Qual estrutura de dados segue a politica LIFO ?")
        ),
        doc(
            question(
                4, stem="Qual a estrutura de dados que segue a política LIFO?"
            )
        ),
    ]

    duplicates = find_duplicates(docs, [], SETTINGS)

    assert _ids(duplicates) == [
        ("pilhas.0003", "pilhas.0001"),
        ("pilhas.0004", "pilhas.0001"),
    ]
    # Case, accents and punctuation do not count.
    assert duplicates[0].similarity == 1.0
    assert THRESHOLD <= duplicates[1].similarity < 1.0
    assert str(duplicates[0]) == (
        f"{SUBJECT}.pilhas.0003: near-duplicate of {SUBJECT}.pilhas.0001 "
        "(similarity 1.00)"
    )


def test_a_question_is_flagged_once_with_its_closest_match() -> None:
    docs = [
        doc(
            question(
                1, stem="Qual a estrutura de dados que segue a política LIFO?"
            )
        ),
        doc(
            question(2, stem="Qual estrutura de dados segue a política LIFO?")
        ),
        doc(
            question(3, stem="Qual estrutura de dados segue a política LIFO?")
        ),
    ]

    duplicates = find_duplicates(docs[2:], docs[:2], SETTINGS)

    assert _ids(duplicates) == [("pilhas.0003", "pilhas.0002")]


def test_the_same_stem_in_another_subject_is_not_a_duplicate() -> None:
    here = doc(question(1))
    there = doc(question(1, subject="banco-de-dados", topic="visoes"))
    other_topic = doc(question(1, topic="filas-e-deques"))

    assert find_duplicates([here], [there], SETTINGS) == []
    assert _ids(find_duplicates([here], [other_topic], SETTINGS)) == [
        ("pilhas.0001", "filas-e-deques.0001")
    ]


def test_questions_with_one_stem_and_different_code_are_not_duplicates() -> (
    None
):
    other_code = (
        "fila = [4, 5, 6]\n"
        "fila.append(7)\n"
        "primeiro = fila.pop(0)\n"
        "print(primeiro + len(fila))"
    )
    docs = [
        doc(output_question(1, PYTHON_PRINTS_2, "python", stem=PRINTS)),
        doc(output_question(2, other_code, "python", stem=PRINTS)),
        # No code at all: never a duplicate of a question with code.
        doc(question(3, stem=PRINTS)),
    ]

    assert find_duplicates(docs, [], SETTINGS) == []


def test_one_stem_and_nearly_the_same_code_is_a_duplicate() -> None:
    one_number_changed = PYTHON_PRINTS_2.replace("[1, 2, 3]", "[1, 2, 5]")
    respaced = PYTHON_PRINTS_2.replace("\n", "\n\n").replace(", ", ",  ")
    docs = [
        doc(output_question(1, PYTHON_PRINTS_2, "python", stem=PRINTS)),
        doc(output_question(2, one_number_changed, "python", stem=PRINTS)),
        doc(output_question(3, respaced, "python", stem=PRINTS)),
    ]

    duplicates = find_duplicates(docs, [], SETTINGS)

    assert _ids(duplicates) == [
        ("pilhas.0002", "pilhas.0001"),
        ("pilhas.0003", "pilhas.0001"),
    ]
    assert duplicates[1].similarity == 1.0


def test_programs_that_share_only_their_frame_are_not_duplicates() -> None:
    frame = (
        "#include <stdio.h>\n\nint main(void) {{\n{body}\n    return 0;\n}}"
    )
    through_a_pointer = frame.format(
        body="    int a = 2, b = 5;\n"
        "    int *p = &a;\n"
        "    *p = b + 1;\n"
        '    printf("%d %d\\n", a, b);'
    )
    in_an_array = frame.format(
        body="    int v[3] = {2, 5, 8};\n"
        "    int *p = v + 1;\n"
        "    *p = v[0] + 1;\n"
        '    printf("%d %d\\n", v[1], v[2]);'
    )
    docs = [
        doc(output_question(1, through_a_pointer, "c", stem=PRINTS)),
        doc(output_question(2, in_an_array, "c", stem=PRINTS)),
    ]
    similarity = SequenceMatcher(
        None,
        " ".join(through_a_pointer.split()),
        " ".join(in_an_array.split()),
        autojunk=False,
    ).ratio()

    # Similar enough for two stems, but not for two programs.
    assert THRESHOLD <= similarity < CODE_THRESHOLD
    assert find_duplicates(docs, [], SETTINGS) == []


def test_files_are_compared_with_each_other_and_with_the_bank(
    tmp_path: Path,
) -> None:
    bank = tmp_path / "bank"
    write_lines(bank / SUBJECT / "pilhas.jsonl", [question(1), question(2)])
    work = write_lines(
        tmp_path / "work" / SUBJECT / "pilhas.jsonl",
        [
            question(3),
            question(4, stem=STEMS[0]),  # repeats question 1 of the bank
            question(5, stem=STEMS[2]),  # repeats question 3 of this file
        ],
    )
    other = write_lines(
        tmp_path / "work" / SUBJECT / "filas-e-deques.jsonl",
        [question(1, topic="filas-e-deques", stem=STEMS[5])],
    )
    log = tmp_path / "log.jsonl"

    checked, duplicates = dedupe([work, other], [bank], SETTINGS, log=log)

    assert checked == 4
    assert _ids(duplicates) == [
        ("pilhas.0004", "pilhas.0001"),
        ("pilhas.0005", "pilhas.0003"),
    ]
    entries = run_log.read_entries(log)
    assert [(e.step, e.topic, e.checked, e.failed) for e in entries] == [
        (
            run_log.Step.DEDUPE,
            "pilhas",
            3,
            [f"{SUBJECT}.pilhas.0004", f"{SUBJECT}.pilhas.0005"],
        ),
        (run_log.Step.DEDUPE, "filas-e-deques", 1, []),
    ]


def test_the_bank_can_be_checked_against_itself(tmp_path: Path) -> None:
    bank = tmp_path / "bank"
    write_lines(
        bank / SUBJECT / "pilhas.jsonl",
        [question(1), question(2), question(3, stem=STEMS[0])],
    )

    checked, duplicates = dedupe([bank], [bank], SETTINGS)

    assert checked == 3
    assert _ids(duplicates) == [("pilhas.0003", "pilhas.0001")]
