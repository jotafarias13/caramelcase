"""Importing the question bank: python -m app.cli import-content."""

import shutil
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Question, QuestionTranslation, Subject, Topic
from app.domain.question_doc import QuestionDoc, content_hash
from app.enums import (
    CodeLanguage,
    Locale,
    QuestionStatus,
    QuestionType,
    SubjectStatus,
)
from app.services.catalog_file import Catalog, CatalogSubject, CatalogTopic
from app.services.content_import import (
    ImportCounts,
    InvalidBankError,
    import_content,
    import_questions,
)
from app.services.seed import seed_catalog
from app.settings import Settings
from tests.support.commands import alembic, cli, output_of
from tests.support.database import run_sql
from tests.support.questions import (
    PYTHON_PRINTS_2,
    doc,
    output_question,
    question,
    the_catalog,
    write_lines,
)

SUBJECT = "estruturas-de-dados"


def _docs(*questions: dict[str, Any]) -> list[QuestionDoc]:
    return [doc(data) for data in questions]


async def _import(
    session: AsyncSession, *questions: dict[str, Any]
) -> ImportCounts:
    """Import the questions as the whole bank, with the real catalog."""
    catalog = the_catalog()
    await seed_catalog(session, catalog)
    return await import_questions(
        session, _docs(*questions), catalog, Settings()
    )


async def _question(session: AsyncSession, number: int = 1) -> Question:
    row = await session.scalar(
        select(Question).where(
            Question.external_id == f"{SUBJECT}.pilhas.{number:04d}"
        )
    )
    assert row is not None
    await session.refresh(row)
    return row


async def _translations(
    session: AsyncSession, row: Question
) -> dict[Locale, QuestionTranslation]:
    translations = await session.scalars(
        select(QuestionTranslation).where(
            QuestionTranslation.question_id == row.id
        )
    )
    return {translation.locale: translation for translation in translations}


def _content_dir(tmp_path: Path, *questions: dict[str, Any]) -> Path:
    """A content directory with the real catalog and these questions."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    shutil.copy(Settings().content_dir / "catalog.yaml", content_dir)
    if questions:
        write_lines(content_dir / "bank" / SUBJECT / "pilhas.jsonl", questions)
    return content_dir


# ---- a new question ----


async def test_a_new_question_is_created_with_its_text_in_both_languages(
    session: AsyncSession,
) -> None:
    counts = await _import(session, question(1, difficulty=4, verified=True))

    assert counts == ImportCounts(
        created=1, updated=0, unchanged=0, retired=0, left_retired=()
    )
    row = await _question(session)
    subject = await session.get(Subject, row.subject_id)
    topic = await session.get(Topic, row.topic_id)
    assert subject is not None
    assert topic is not None
    assert (subject.slug, topic.slug) == (SUBJECT, "pilhas")
    assert topic.subject_id == subject.id
    assert row.type is QuestionType.MCQ
    assert row.difficulty_prior == 4
    assert row.rating == Settings().question_rating_by_prior[3] == 1150.0
    assert (row.answers_count, row.correct_count, row.version) == (0, 0, 1)
    assert row.source == "generated"
    assert row.content_hash == content_hash(doc(question(1, difficulty=4)))

    translations = await _translations(session, row)
    assert set(translations) == {Locale.PT_BR, Locale.EN}
    portuguese = translations[Locale.PT_BR]
    assert portuguese.stem == "Qual estrutura de dados segue a política LIFO?"
    assert portuguese.code is None
    assert portuguese.code_language is None
    assert portuguese.explanation.startswith("LIFO significa")
    assert portuguese.payload["options"][1] == {
        "key": "b",
        "text": "Pilha",
        "is_correct": True,
        "reason": "Na pilha, o último elemento inserido é o primeiro a sair.",
    }
    assert [o["is_correct"] for o in portuguese.payload["options"]] == [
        False,
        True,
        False,
        False,
    ]
    assert translations[Locale.EN].payload["options"][1]["text"] == "Stack"


async def test_a_question_with_code_stores_the_code_and_its_language(
    session: AsyncSession,
) -> None:
    await _import(
        session, output_question(1, PYTHON_PRINTS_2, "python", verified=True)
    )

    translations = await _translations(session, await _question(session))
    for translation in translations.values():
        assert translation.code == PYTHON_PRINTS_2
        assert translation.code_language == "python"


async def test_a_question_is_verified_in_a_launch_subject_and_a_draft_if_not(
    session: AsyncSession,
) -> None:
    def subject(slug: str, short: str, launch: bool) -> CatalogSubject:
        return CatalogSubject(
            slug=slug,
            name_pt=slug,
            name_en=slug,
            short_pt=short,
            short_en=short,
            typical_year="1",
            launch=launch,
            topics=[
                CatalogTopic(
                    slug="pilhas",
                    name_pt="Pilhas",
                    name_en="Stacks",
                    code_language=CodeLanguage.PYTHON,
                    covers="Pilhas.",
                )
            ],
        )

    catalog = Catalog(
        subjects=[
            subject("no-lancamento", "a", True),
            subject("depois", "b", False),
        ]
    )
    await seed_catalog(session, catalog)

    await import_questions(
        session,
        _docs(
            question(1, subject="no-lancamento", verified=True),
            question(1, subject="depois", verified=True),
        ),
        catalog,
        Settings(),
    )

    statuses = dict(
        (
            await session.execute(
                select(Question.external_id, Question.status)
            )
        ).all()
    )
    assert statuses == {
        "no-lancamento.pilhas.0001": QuestionStatus.VERIFIED,
        "depois.pilhas.0001": QuestionStatus.DRAFT,
    }


# ---- importing again ----


async def test_importing_again_touches_no_row(session: AsyncSession) -> None:
    bank = [question(1, verified=True), question(2, verified=True)]
    await _import(session, *bank)
    models = (Question, QuestionTranslation)
    before = [
        (row.id, row.updated_at)
        for model in models
        for row in await session.scalars(select(model).order_by(model.id))
    ]

    counts = await _import(session, *bank)

    after = [
        (row.id, row.updated_at)
        for model in models
        for row in await session.scalars(select(model).order_by(model.id))
    ]
    assert counts == ImportCounts(
        created=0, updated=0, unchanged=2, retired=0, left_retired=()
    )
    assert after == before
    assert len(before) == 2 + 4


async def test_a_change_of_verification_alone_is_not_a_change(
    session: AsyncSession,
) -> None:
    await _import(session, question(1, verified=True))
    checked = question(1, verified=True)
    checked["verification"]["human_checked"] = True

    counts = await _import(session, checked)

    assert (counts.updated, counts.unchanged) == (0, 1)
    assert (await _question(session)).version == 1


async def test_changed_content_rewrites_the_text_and_bumps_the_version(
    session: AsyncSession,
) -> None:
    await _import(
        session, question(1, verified=True), question(2, verified=True)
    )
    first = await _question(session)
    first.status = QuestionStatus.PUBLISHED
    first.rating = 1234.5
    first.answers_count = 9
    first.correct_count = 6
    await session.flush()
    old_hash = first.content_hash

    changed = question(1, difficulty=5, verified=True)
    changed["locales"]["pt-BR"]["stem"] = "Qual estrutura é LIFO?"
    changed["locales"]["en"]["options"][0]["text"] = "FIFO queue"
    counts = await _import(session, changed, question(2, verified=True))

    assert (counts.created, counts.updated, counts.unchanged) == (0, 1, 1)
    first = await _question(session)
    assert first.version == 2
    assert first.content_hash != old_hash
    assert first.difficulty_prior == 5
    # Everything live is the database's: the importer leaves it alone.
    assert first.status is QuestionStatus.PUBLISHED
    assert (first.rating, first.answers_count, first.correct_count) == (
        1234.5,
        9,
        6,
    )
    translations = await _translations(session, first)
    assert len(translations) == 2
    assert translations[Locale.PT_BR].stem == "Qual estrutura é LIFO?"
    assert (
        translations[Locale.EN].payload["options"][0]["text"] == "FIFO queue"
    )
    assert (await _question(session, 2)).version == 1


async def test_a_new_difficulty_resets_the_rating_only_while_unanswered(
    session: AsyncSession,
) -> None:
    await _import(
        session,
        question(1, difficulty=1, verified=True),
        question(2, difficulty=1, verified=True),
    )
    answered = await _question(session, 2)
    answered.answers_count = 1
    answered.rating = 712.0
    await session.flush()

    await _import(
        session,
        question(1, difficulty=3, verified=True),
        question(2, difficulty=3, verified=True),
    )

    assert (await _question(session, 1)).rating == 1000.0
    assert (await _question(session, 2)).rating == 712.0


# ---- retiring ----


async def test_a_question_that_left_the_files_is_retired_not_deleted(
    session: AsyncSession,
) -> None:
    await _import(
        session, question(1, verified=True), question(2, verified=True)
    )

    counts = await _import(session, question(1, verified=True))

    assert (counts.unchanged, counts.retired) == (1, 1)
    assert (await _question(session, 1)).status is QuestionStatus.VERIFIED
    gone = await _question(session, 2)
    assert gone.status is QuestionStatus.RETIRED
    assert len(await _translations(session, gone)) == 2

    again = await _import(session, question(1, verified=True))
    assert again.retired == 0


async def test_a_retired_question_stays_retired_unless_its_content_changed(
    session: AsyncSession,
) -> None:
    await _import(
        session, question(1, verified=True), question(2, verified=True)
    )
    for number in (1, 2):
        (await _question(session, number)).status = QuestionStatus.RETIRED
    await session.flush()

    rewritten = question(
        2, stem="O que significa a sigla LIFO?", verified=True
    )
    counts = await _import(session, question(1, verified=True), rewritten)

    assert counts == ImportCounts(
        created=0,
        updated=1,
        unchanged=1,
        retired=0,
        left_retired=(f"{SUBJECT}.pilhas.0001",),
    )
    assert (await _question(session, 1)).status is QuestionStatus.RETIRED
    back = await _question(session, 2)
    assert back.status is QuestionStatus.VERIFIED
    assert back.version == 2


# ---- the bank as a whole ----


async def test_importing_the_content_directory_also_writes_subjects_and_topics(
    session: AsyncSession, tmp_path: Path
) -> None:
    content_dir = _content_dir(
        tmp_path, question(1, verified=True), question(2, verified=True)
    )

    counts = await import_content(session, Settings(content_dir=content_dir))

    assert (counts.created, counts.retired) == (2, 0)
    subjects = list(await session.scalars(select(Subject)))
    assert len(subjects) == 20
    assert {subject.status for subject in subjects} == {SubjectStatus.DRAFT}


async def test_a_bank_with_a_problem_imports_nothing(
    session: AsyncSession, tmp_path: Path
) -> None:
    content_dir = _content_dir(
        tmp_path, question(1, verified=True), question(2)
    )

    with pytest.raises(InvalidBankError) as raised:
        await import_content(session, Settings(content_dir=content_dir))

    assert len(raised.value.problems) == 1
    assert raised.value.problems[0].endswith(
        f"{SUBJECT}.pilhas.0002: it was not blind-solved"
    )
    assert list(await session.scalars(select(Question))) == []


async def test_an_empty_bank_is_refused_so_that_nothing_is_retired(
    session: AsyncSession, tmp_path: Path
) -> None:
    await _import(session, question(1, verified=True))
    content_dir = _content_dir(tmp_path)

    with pytest.raises(InvalidBankError, match="1 problem in"):
        await import_content(session, Settings(content_dir=content_dir))

    assert (await _question(session)).status is QuestionStatus.VERIFIED


# ---- python -m app.cli import-content ----


async def test_the_import_command_commits_and_can_run_twice(
    scratch_database: str, tmp_path: Path
) -> None:
    content_dir = _content_dir(
        tmp_path, question(1, verified=True), question(2, verified=True)
    )
    upgrade = alembic("upgrade", "head", database_url=scratch_database)
    assert upgrade.returncode == 0, output_of(upgrade)

    def run(*args: str) -> str:
        result = cli(
            "import-content",
            *args,
            database_url=scratch_database,
            content_dir=content_dir,
        )
        assert result.returncode == 0, output_of(result)
        return result.stdout

    async def stored() -> list[tuple[object, ...]]:
        return await run_sql(
            scratch_database,
            "SELECT"
            " (SELECT count(*) FROM questions WHERE status = 'verified'),"
            " (SELECT count(*) FROM questions WHERE status = 'retired'),"
            " (SELECT count(*) FROM question_translations)",
        )

    dry = run("--dry-run")
    assert "Dry run, nothing saved" in dry
    assert "2 created, 0 updated, 0 unchanged, 0 retired" in dry
    assert await stored() == [(0, 0, 0)]

    assert "Imported: 2 created, 0 updated, 0 unchanged, 0 retired" in run()
    assert "Imported: 0 created, 0 updated, 2 unchanged, 0 retired" in run()
    assert await stored() == [(2, 0, 4)]

    write_lines(
        content_dir / "bank" / SUBJECT / "pilhas.jsonl",
        [question(1, verified=True)],
    )
    assert "Imported: 0 created, 0 updated, 1 unchanged, 1 retired" in run()
    assert await stored() == [(1, 1, 4)]


async def test_the_import_command_fails_and_lists_the_problems_of_the_bank(
    scratch_database: str, tmp_path: Path
) -> None:
    broken = question(2, verified=True)
    broken["locales"]["en"]["options"][0]["reason"] = ""
    content_dir = _content_dir(tmp_path, question(1, verified=True), broken)
    upgrade = alembic("upgrade", "head", database_url=scratch_database)
    assert upgrade.returncode == 0, output_of(upgrade)

    result = cli(
        "import-content",
        database_url=scratch_database,
        content_dir=content_dir,
    )

    assert result.returncode == 1
    assert "pilhas.jsonl:2" in result.stderr
    assert "en option a reason is empty" in result.stderr
    assert "Nothing imported: 1 problem in the question bank." in result.stderr
    count = await run_sql(scratch_database, "SELECT count(*) FROM questions")
    assert count == [(0,)]
