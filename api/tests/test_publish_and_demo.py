"""Publishing subjects, the demo user, and the commands make seed runs."""

import random
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AuthIdentity,
    DailyActivity,
    PracticeSession,
    Question,
    Subject,
    User,
)
from app.enums import QuestionStatus
from app.services.content_import import import_questions
from app.services.demo import NoPublishedSubjectError, create_demo_user
from app.services.publishing import UnknownSubjectError, publish_subject
from app.services.seed import seed_all
from app.settings import Settings
from tests.conftest import Clock
from tests.support.api import API, OTHER_SUBJECT, SUBJECT, publish_bank
from tests.support.commands import alembic, cli, output_of
from tests.support.database import run_sql
from tests.support.questions import doc, question, the_catalog, write_lines

SETTINGS = Settings()
NOW = datetime(2026, 11, 16, 15, 0, tzinfo=UTC)

# ---- publishing ----


async def _statuses(session: AsyncSession) -> dict[str, int]:
    rows = await session.execute(
        select(Question.status, func.count()).group_by(Question.status)
    )
    return {status.value: count for status, count in rows}


async def test_publishing_shows_the_subject_and_its_verified_questions(
    session: AsyncSession,
) -> None:
    await seed_all(session, SETTINGS)
    docs = [doc(question(n, stem=f"Pergunta {n}?")) for n in range(1, 5)]
    await import_questions(session, docs, the_catalog(), SETTINGS)
    rows = list(
        await session.scalars(select(Question).order_by(Question.external_id))
    )
    rows[0].status = QuestionStatus.DRAFT
    rows[1].status = QuestionStatus.RETIRED
    await session.flush()

    published = await publish_subject(session, SUBJECT)

    assert published == 2
    assert await _statuses(session) == {
        "draft": 1,
        "retired": 1,
        "published": 2,
    }
    subjects = await session.execute(select(Subject.slug, Subject.status))
    public = [slug for slug, status in subjects if status == "published"]
    assert public == [SUBJECT]


async def test_publishing_again_publishes_only_what_was_imported_since(
    session: AsyncSession,
) -> None:
    await seed_all(session, SETTINGS)
    docs = [doc(question(n, stem=f"Pergunta {n}?")) for n in range(1, 5)]
    await import_questions(session, docs[:2], the_catalog(), SETTINGS)
    first = await publish_subject(session, SUBJECT)
    await import_questions(session, docs, the_catalog(), SETTINGS)

    second = await publish_subject(session, SUBJECT)
    third = await publish_subject(session, SUBJECT)

    assert (first, second, third) == (2, 2, 0)
    assert await _statuses(session) == {"published": 4}


async def test_a_subject_that_does_not_exist_cannot_be_published(
    session: AsyncSession,
) -> None:
    await seed_all(session, SETTINGS)

    with pytest.raises(UnknownSubjectError, match="nope"):
        await publish_subject(session, "nope")


# ---- the demo user ----


async def test_the_demo_user_has_three_weeks_of_history_and_a_streak_of_7(
    session: AsyncSession, client: AsyncClient, clock: Clock
) -> None:
    await publish_bank(session, per_topic=12, both_subjects=True)

    demo = await create_demo_user(
        session, SETTINGS, clock.now, random.Random(1)
    )
    again = await create_demo_user(
        session, SETTINGS, clock.now, random.Random(2)
    )

    assert demo.created
    assert demo.user.email == "demo@example.com"
    assert demo.user.display_name == "Carol Demo"
    assert not demo.user.is_guest
    assert demo.sessions >= 7
    # A second run finds it and adds nothing.
    assert not again.created
    assert again.user.id == demo.user.id
    assert await session.scalar(select(func.count()).select_from(User)) == 1
    finished = await session.scalar(
        select(func.count())
        .select_from(PracticeSession)
        .where(PracticeSession.finished_at.is_not(None))
    )
    assert finished == demo.sessions
    days = list(
        await session.scalars(
            select(DailyActivity.local_date).order_by(DailyActivity.local_date)
        )
    )
    assert 7 <= len(days) <= 21
    assert (days[-1] - days[0]).days <= 20
    identity = await session.scalar(select(AuthIdentity))
    assert identity is not None
    assert identity.provider_subject == "demo@example.com"

    # Signing in with the mock Google account lands on the demo user.
    started = await client.get(f"{API}/auth/google/start")
    await client.get(
        started.headers["location"].removeprefix("http://localhost:5173")
    )
    me = (await client.get(f"{API}/me")).json()
    stats = (await client.get(f"{API}/me/stats")).json()
    assert me["id"] == str(demo.user.id)
    assert me["current_subject"] == OTHER_SUBJECT
    assert me["course"] == "Ciência da Computação"
    assert stats["streak"]["status"] == "active"
    assert stats["streak"]["current"] == 7
    assert stats["sessions_finished"] == demo.sessions
    assert stats["questions_answered"] == demo.sessions * 10
    assert 0.6 < stats["accuracy"] < 0.95
    assert stats["level"]["total_xp"] > 0
    assert {s["slug"] for s in stats["subjects"] if s["rating"]} == {
        SUBJECT,
        OTHER_SUBJECT,
    }


async def test_the_demo_user_plays_only_subjects_that_have_questions(
    session: AsyncSession,
) -> None:
    await publish_bank(session, per_topic=12)
    # Published, but empty.
    await publish_subject(session, OTHER_SUBJECT)

    demo = await create_demo_user(session, SETTINGS, NOW, random.Random(1))

    subject_ids = set(
        await session.scalars(select(PracticeSession.subject_id))
    )
    assert demo.created
    assert len(subject_ids) == 1
    assert demo.user.current_subject_id in subject_ids


async def test_no_demo_user_without_something_to_practice(
    session: AsyncSession,
) -> None:
    await seed_all(session, SETTINGS)

    with pytest.raises(NoPublishedSubjectError):
        await create_demo_user(session, SETTINGS, NOW, random.Random(1))

    assert await session.scalar(select(User)) is None


# ---- the commands of make seed ----


def _content_dir(tmp_path: Path) -> Path:
    """A content directory with the real catalog and a bank of 12."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    shutil.copy(SETTINGS.content_dir / "catalog.yaml", content_dir)
    write_lines(
        content_dir / "bank" / SUBJECT / "pilhas.jsonl",
        [
            question(
                n,
                stem=f"Pergunta {n}?",
                difficulty=n % 3 + 1,
                verified=True,
            )
            for n in range(1, 13)
        ],
    )
    return content_dir


async def test_the_commands_of_make_seed_lead_to_a_playable_database(
    scratch_database: str, tmp_path: Path
) -> None:
    content_dir = _content_dir(tmp_path)

    def run(*args: str, **env: str) -> str:
        result = cli(
            *args,
            database_url=scratch_database,
            content_dir=content_dir,
            env=env,
        )
        assert result.returncode == 0, output_of(result)
        return result.stdout

    upgrade = alembic("upgrade", "head", database_url=scratch_database)
    assert upgrade.returncode == 0, output_of(upgrade)
    run("seed")
    run("import-content")
    published = run("publish-subjects", "--launch")
    demo = run("demo-user")
    demo_again = run("demo-user")
    published_again = run("publish-subjects", SUBJECT)

    assert f"Published {SUBJECT}: 12 more questions." in published
    assert "Published banco-de-dados: 0 more questions." in published
    assert "Published introducao-a-programacao: 0 more" in published
    assert f"Published {SUBJECT}: 0 more questions." in published_again
    created = re.search(r"Created demo@example.com with (\d+) sessions", demo)
    assert created is not None
    assert "demo@example.com was already there." in demo_again
    link = re.compile(
        r"^http://localhost:5173/auth/callback\?token=\S+$", re.MULTILINE
    )
    links = link.findall(demo) + link.findall(demo_again)
    assert len(set(links)) == 2

    counts = await run_sql(
        scratch_database,
        "SELECT"
        " (SELECT count(*) FROM subjects WHERE status = 'published'),"
        " (SELECT count(*) FROM questions WHERE status = 'published'),"
        " (SELECT count(*) FROM users),"
        " (SELECT count(*) FROM practice_sessions"
        "   WHERE finished_at IS NOT NULL),"
        " (SELECT current FROM streaks),"
        " (SELECT count(*) FROM magic_links)",
    )
    assert counts == [(3, 12, 1, int(created.group(1)), 7, 2)]


async def test_the_demo_user_command_refuses_to_run_in_production(
    scratch_database: str, tmp_path: Path
) -> None:
    upgrade = alembic("upgrade", "head", database_url=scratch_database)
    assert upgrade.returncode == 0, output_of(upgrade)

    result = cli(
        "demo-user",
        database_url=scratch_database,
        content_dir=_content_dir(tmp_path),
        env={"ENVIRONMENT": "production"},
    )

    assert result.returncode == 1
    assert "not for production" in result.stderr
    users = await run_sql(scratch_database, "SELECT count(*) FROM users")
    assert users == [(0,)]


async def test_publish_subjects_needs_a_subject_that_exists(
    scratch_database: str, tmp_path: Path
) -> None:
    content_dir = _content_dir(tmp_path)
    upgrade = alembic("upgrade", "head", database_url=scratch_database)
    assert upgrade.returncode == 0, output_of(upgrade)
    seeded = cli(
        "seed", database_url=scratch_database, content_dir=content_dir
    )
    assert seeded.returncode == 0, output_of(seeded)

    def run(*args: str) -> tuple[int, str]:
        result = cli(
            "publish-subjects",
            *args,
            database_url=scratch_database,
            content_dir=content_dir,
        )
        return result.returncode, result.stderr

    unknown = run(SUBJECT, "nope")
    nothing = run()

    assert unknown[0] == 1
    assert "no subject with the slug nope" in unknown[1]
    assert nothing[0] == 2
    # One unknown subject and none is published.
    public = await run_sql(
        scratch_database,
        "SELECT count(*) FROM subjects WHERE status = 'published'",
    )
    assert public == [(0,)]
