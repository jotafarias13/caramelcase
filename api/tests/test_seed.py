"""Seeding plans, feature flags, subjects and topics, and the catalog file."""

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FeatureFlag, Plan, Subject, Topic
from app.enums import (
    CodeLanguage,
    FlagKey,
    FlagState,
    PlanKey,
    SubjectStatus,
)
from app.services.catalog_file import (
    Catalog,
    CatalogSubject,
    CatalogTopic,
    load_catalog,
)
from app.services.seed import (
    SeedCounts,
    seed_all,
    seed_catalog,
    seed_flags,
    seed_plans,
    seed_subjects,
)
from app.settings import Settings
from tests.support.commands import alembic, cli, output_of
from tests.support.database import run_sql

LAUNCH_SUBJECTS = [
    "introducao-a-programacao",
    "estruturas-de-dados",
    "banco-de-dados",
]


def _catalog() -> Catalog:
    return load_catalog(Settings().content_dir / "catalog.yaml")


def _entry(
    slug: str, name: str, short: str, topics: list[CatalogTopic] | None = None
) -> CatalogSubject:
    return CatalogSubject(
        slug=slug,
        name_pt=name,
        name_en=name,
        short_pt=short,
        short_en=short,
        typical_year="1",
        topics=topics or [],
    )


def _topic(slug: str, name: str) -> CatalogTopic:
    return CatalogTopic(
        slug=slug,
        name_pt=name,
        name_en=name,
        code_language=CodeLanguage.PYTHON,
        covers="Tudo sobre o tópico.",
    )


# ---- content/catalog.yaml ----


def test_the_catalog_lists_the_20_subjects_launch_subjects_first() -> None:
    subjects = _catalog().subjects

    assert len(subjects) == 20
    assert [s.slug for s in subjects if s.launch] == LAUNCH_SUBJECTS
    assert [s.slug for s in subjects[:3]] == LAUNCH_SUBJECTS
    assert subjects[1].name_pt == "Estruturas de Dados"
    assert subjects[1].name_en == "Data Structures"


def test_a_catalog_with_a_repeated_slug_or_badge_is_rejected() -> None:
    first = _entry("pilhas", "Pilhas", "p")

    with pytest.raises(ValidationError, match="slug is used by more than one"):
        Catalog(subjects=[first, _entry("pilhas", "Outra", "o")])
    with pytest.raises(ValidationError, match="short_pt is used by more"):
        Catalog(subjects=[first, _entry("filas", "Filas", "p")])


def test_a_catalog_file_with_an_unknown_field_is_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        "subjects:\n"
        "  - slug: pilhas\n"
        "    name_pt: Pilhas\n"
        "    name_en: Stacks\n"
        "    short_pt: p\n"
        "    short_en: s\n"
        "    typical_year: '1'\n"
        "    colour: caramel\n",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="colour"):
        load_catalog(path)


def test_the_launch_subjects_have_their_topics_and_the_others_none() -> None:
    topics = {s.slug: s.topics for s in _catalog().subjects}

    assert {slug: len(topics[slug]) for slug in LAUNCH_SUBJECTS} == {
        "introducao-a-programacao": 13,
        "estruturas-de-dados": 19,
        "banco-de-dados": 18,
    }
    assert all(
        topics[slug] == [] for slug in topics if slug not in LAUNCH_SUBJECTS
    )


def test_each_topic_has_the_code_language_agreed_for_its_subject() -> None:
    catalog = _catalog()

    def languages(slug: str) -> dict[str, CodeLanguage]:
        subject = catalog.subject(slug)
        assert subject is not None
        return {topic.slug: topic.code_language for topic in subject.topics}

    assert set(languages("introducao-a-programacao").values()) == {
        CodeLanguage.C
    }
    assert set(languages("banco-de-dados").values()) == {CodeLanguage.SQL}
    # C for the pointer and dynamic-allocation topics, Python elsewhere.
    data_structures = languages("estruturas-de-dados")
    in_c = {slug for slug, lang in data_structures.items() if lang == "c"}
    assert in_c == {"ponteiros-e-alocacao-dinamica", "listas-encadeadas"}
    assert set(data_structures.values()) == {
        CodeLanguage.C,
        CodeLanguage.PYTHON,
    }
    # The topic of the spec's sample question.
    assert "pilhas" in data_structures


def test_a_subject_with_a_repeated_topic_slug_is_rejected() -> None:
    with pytest.raises(ValidationError, match="more than one topic"):
        _entry(
            "estruturas",
            "Estruturas",
            "e",
            [_topic("pilhas", "Pilhas"), _topic("pilhas", "Pilhas de novo")],
        )


# ---- seeding ----


async def test_seeding_writes_the_plans_every_flag_off_and_draft_subjects(
    session: AsyncSession,
) -> None:
    counts = await seed_all(session, Settings())

    assert counts == SeedCounts(plans=4, flags=17, subjects=20, topics=50)

    plans = {plan.key: plan for plan in await session.scalars(select(Plan))}
    assert {key: plan.price_month_brl for key, plan in plans.items()} == {
        "free": Decimal(0),
        "plus": Decimal(15),
        "pro": Decimal(40),
        "max": Decimal(100),
    }
    assert plans["free"].limits == {
        "sessions_per_day": 3,
        "ads": True,
        "tutor_messages_per_day": 0,
        "exam_mode": False,
        "exam_tracks": False,
    }
    assert plans["max"].limits["sessions_per_day"] is None
    assert plans["max"].limits["tutor_messages_per_day"] == 200

    flags = list(await session.scalars(select(FeatureFlag)))
    assert {flag.key for flag in flags} == {key.value for key in FlagKey}
    assert {flag.state for flag in flags} == {FlagState.OFF}

    subjects = list(
        await session.scalars(select(Subject).order_by(Subject.sort_order))
    )
    assert [s.slug for s in subjects] == [s.slug for s in _catalog().subjects]
    assert [s.sort_order for s in subjects] == list(range(1, 21))
    assert {s.status for s in subjects} == {SubjectStatus.DRAFT}
    assert (subjects[1].short_pt, subjects[1].short_en) == ("ed", "ds")

    topics = list(
        await session.scalars(
            select(Topic)
            .where(Topic.subject_id == subjects[1].id)
            .order_by(Topic.sort_order)
        )
    )
    in_catalog = _catalog().subjects[1].topics
    assert [t.slug for t in topics] == [t.slug for t in in_catalog]
    assert [t.sort_order for t in topics] == list(range(1, 20))
    assert (topics[6].slug, topics[6].name_pt, topics[6].name_en) == (
        "pilhas",
        "Pilhas",
        "Stacks",
    )


async def test_seeding_again_changes_no_row(session: AsyncSession) -> None:
    settings = Settings()
    first = await seed_all(session, settings)
    models = (Plan, FeatureFlag, Subject, Topic)
    before = [
        (row.id, row.updated_at)
        for model in models
        for row in await session.scalars(select(model).order_by(model.id))
    ]

    second = await seed_all(session, settings)

    after = [
        (row.id, row.updated_at)
        for model in models
        for row in await session.scalars(select(model).order_by(model.id))
    ]
    assert second == first
    assert after == before


async def test_seeding_keeps_a_switched_flag_and_a_published_subject(
    session: AsyncSession,
) -> None:
    await seed_all(session, Settings())
    flag = await session.scalar(
        select(FeatureFlag).where(FeatureFlag.key == FlagKey.LEAGUES)
    )
    subject = await session.scalar(
        select(Subject).where(Subject.slug == "banco-de-dados")
    )
    assert flag is not None
    assert subject is not None
    flag.state = FlagState.STAFF
    subject.status = SubjectStatus.PUBLISHED
    await session.flush()

    await seed_flags(session)
    await seed_subjects(session, _catalog())

    await session.refresh(flag)
    await session.refresh(subject)
    assert flag.state is FlagState.STAFF
    assert subject.status is SubjectStatus.PUBLISHED


async def test_seeding_brings_a_plan_in_line_with_settings(
    session: AsyncSession,
) -> None:
    settings = Settings()
    await seed_plans(session, settings.plans)
    free = settings.plans[0]
    assert free.key is PlanKey.FREE
    cheaper = free.model_copy(
        update={
            "price_year_brl": Decimal("99.90"),
            "limits": free.limits.model_copy(update={"sessions_per_day": 5}),
        }
    )

    await seed_plans(session, [cheaper, *settings.plans[1:]])

    plan = await session.scalar(select(Plan).where(Plan.key == "free"))
    assert plan is not None
    assert plan.price_year_brl == Decimal("99.90")
    assert plan.limits["sessions_per_day"] == 5


async def test_seeding_renames_and_reorders_subjects_and_adds_new_ones(
    session: AsyncSession,
) -> None:
    await seed_subjects(
        session,
        Catalog(
            subjects=[
                _entry("pilhas", "Pilhas", "p"),
                _entry("filas", "Filas", "f"),
            ]
        ),
    )

    await seed_subjects(
        session,
        Catalog(
            subjects=[
                _entry("grafos", "Grafos", "g"),
                _entry("pilhas", "Pilhas e deques", "pd"),
            ]
        ),
    )

    subjects = {
        s.slug: (s.name_pt, s.short_pt, s.sort_order, s.status)
        for s in await session.scalars(select(Subject))
    }
    assert subjects == {
        "grafos": ("Grafos", "g", 1, SubjectStatus.DRAFT),
        "pilhas": ("Pilhas e deques", "pd", 2, SubjectStatus.DRAFT),
        # No longer in the catalog: left as it was, never deleted.
        "filas": ("Filas", "f", 2, SubjectStatus.DRAFT),
    }


async def test_seeding_renames_and_reorders_topics_and_keeps_removed_ones(
    session: AsyncSession,
) -> None:
    def catalog_with(topics: list[CatalogTopic]) -> Catalog:
        return Catalog(
            subjects=[
                _entry("estruturas", "Estruturas", "e", topics),
                # The same topic slug in another subject is another topic.
                _entry("algoritmos", "Algoritmos", "a", [topics[0]]),
            ]
        )

    await seed_catalog(
        session,
        catalog_with([_topic("pilhas", "Pilhas"), _topic("filas", "Filas")]),
    )
    await seed_catalog(
        session,
        catalog_with(
            [_topic("deques", "Deques"), _topic("pilhas", "Pilhas e pilhas")]
        ),
    )

    rows = await session.execute(
        select(Subject.slug, Topic.slug, Topic.name_pt, Topic.sort_order).join(
            Subject, Subject.id == Topic.subject_id
        )
    )
    assert {(row[0], row[1]): (row[2], row[3]) for row in rows} == {
        ("estruturas", "deques"): ("Deques", 1),
        ("estruturas", "pilhas"): ("Pilhas e pilhas", 2),
        # No longer in the catalog: left as it was, never deleted.
        ("estruturas", "filas"): ("Filas", 2),
        ("algoritmos", "pilhas"): ("Pilhas", 1),
        ("algoritmos", "deques"): ("Deques", 1),
    }


# ---- python -m app.cli seed ----


async def test_the_seed_command_commits_and_can_run_twice(
    scratch_database: str,
) -> None:
    upgrade = alembic("upgrade", "head", database_url=scratch_database)
    assert upgrade.returncode == 0, output_of(upgrade)

    first = cli("seed", database_url=scratch_database)
    second = cli("seed", database_url=scratch_database)

    for run in (first, second):
        assert run.returncode == 0, output_of(run)
        assert (
            "4 plans, 17 feature flags, 20 subjects, 50 topics" in run.stdout
        )
    counts = await run_sql(
        scratch_database,
        "SELECT (SELECT count(*) FROM plans),"
        " (SELECT count(*) FROM feature_flags),"
        " (SELECT count(*) FROM subjects WHERE status = 'draft'),"
        " (SELECT count(*) FROM topics)",
    )
    assert counts == [(4, 17, 20, 50)]
