"""The conventions every table follows, and how rows behave in Postgres."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
import sqlalchemy as sa
from sqlalchemy import select, text
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import ENUM_LENGTH, Base
from app.db.models import (
    Attempt,
    Event,
    FeatureFlag,
    PracticeSession,
    Question,
    Streak,
    Subject,
    Topic,
    User,
    UserSettings,
)
from app.enums import FlagState, Locale, QuestionStatus

# The tables of the spec's data model, section by section.
SPEC_TABLES = {
    # Identity
    "users",
    "auth_identities",
    "sessions_auth",
    "magic_links",
    "user_settings",
    # Content
    "subjects",
    "topics",
    "topic_edges",
    "questions",
    "question_translations",
    "question_reports",
    # Practice
    "practice_sessions",
    "attempts",
    "user_subject_ratings",
    "user_topic_mastery",
    "daily_activity",
    "streaks",
    "review_items",
    # V2 and V3
    "feature_flags",
    "league_weeks",
    "league_memberships",
    "achievements",
    "user_achievements",
    "exam_templates",
    "exam_attempts",
    "plans",
    "subscriptions",
    "usage_counters",
    "ad_events",
    "tutor_threads",
    "tutor_messages",
    "events",
}
# The tables docs/DECISIONS.md adds for features the spec describes.
EXTRA_TABLES = {"lives", "referrals", "push_subscriptions", "user_subjects"}

TABLES = Base.metadata.sorted_tables


def test_every_table_of_the_data_model_exists() -> None:
    assert set(Base.metadata.tables) == SPEC_TABLES | EXTRA_TABLES


def test_the_columns_the_plan_adds_to_the_spec_exist() -> None:
    assert "external_id" in Base.metadata.tables["questions"].c
    assert {"university", "course"} <= set(
        Base.metadata.tables["users"].c.keys()
    )
    # The streak-repair state: the lost streak's length and time.
    assert {"lost_length", "lost_at"} <= set(
        Base.metadata.tables["streaks"].c.keys()
    )


@pytest.mark.parametrize("table", TABLES, ids=lambda table: table.name)
def test_a_table_has_a_uuid_key_and_two_timestamps(table: sa.Table) -> None:
    assert [column.name for column in table.primary_key] == ["id"]
    assert isinstance(table.c.id.type, sa.Uuid)
    for name in ("created_at", "updated_at"):
        assert isinstance(table.c[name].type, sa.DateTime)
        assert not table.c[name].nullable


@pytest.mark.parametrize("table", TABLES, ids=lambda table: table.name)
def test_every_timestamp_of_a_table_has_a_timezone(table: sa.Table) -> None:
    naive = [
        column.name
        for column in table.columns
        if isinstance(column.type, sa.DateTime) and not column.type.timezone
    ]

    assert naive == []


@pytest.mark.parametrize("table", TABLES, ids=lambda table: table.name)
def test_an_enum_column_is_a_varchar_without_a_database_type(
    table: sa.Table,
) -> None:
    for column in table.columns:
        if isinstance(column.type, sa.Enum):
            assert not column.type.native_enum
            assert column.type.length == ENUM_LENGTH


def test_a_users_rows_are_deleted_with_the_user() -> None:
    not_cascading = [
        f"{table.name}.{key.parent.name}"
        for table in TABLES
        for key in table.foreign_keys
        if key.column.table.name == "users" and key.ondelete != "CASCADE"
    ]

    assert not_cascading == []


async def test_a_new_row_has_a_key_and_equal_utc_timestamps(
    session: AsyncSession,
) -> None:
    before = datetime.now(UTC)
    flag = FeatureFlag(key="probe")
    session.add(flag)
    await session.flush()

    assert isinstance(flag.id, uuid.UUID)
    assert flag.state is FlagState.OFF
    assert before <= flag.created_at <= datetime.now(UTC)
    assert flag.updated_at == flag.created_at


async def test_updated_at_moves_when_a_row_changes(
    session: AsyncSession,
) -> None:
    flag = FeatureFlag(key="probe")
    session.add(flag)
    await session.flush()
    created_at = flag.created_at

    flag.state = FlagState.ON
    await session.flush()

    assert flag.created_at == created_at
    assert flag.updated_at > created_at


async def test_a_timestamp_read_from_postgres_is_in_utc(
    session: AsyncSession,
) -> None:
    flag = FeatureFlag(key="probe")
    session.add(flag)
    await session.flush()
    written = flag.created_at

    await session.refresh(flag)

    assert flag.created_at == written
    assert flag.created_at.utcoffset() == timedelta(0)


async def test_a_row_inserted_with_plain_sql_gets_its_key_and_timestamps(
    session: AsyncSession,
) -> None:
    await session.execute(
        text("INSERT INTO feature_flags (key, state) VALUES ('probe', 'off')")
    )

    flag = await session.scalar(
        select(FeatureFlag).where(FeatureFlag.key == "probe")
    )

    assert flag is not None
    assert isinstance(flag.id, uuid.UUID)
    assert flag.updated_at == flag.created_at


async def test_an_enum_is_stored_as_its_value(session: AsyncSession) -> None:
    user = User(timezone="America/Sao_Paulo", locale=Locale.PT_BR)
    session.add(user)
    await session.flush()

    stored = await session.scalar(
        text("SELECT locale FROM users WHERE id = :id"), {"id": user.id}
    )

    assert stored == "pt-BR"


async def test_a_value_outside_the_enum_is_rejected(
    session: AsyncSession,
) -> None:
    session.add(FeatureFlag(key="probe", state="sometimes"))

    with pytest.raises(StatementError, match="sometimes"):
        await session.flush()


async def test_deleting_a_user_deletes_their_rows_and_keeps_the_content(
    session: AsyncSession,
) -> None:
    subject = Subject(
        slug="s",
        name_pt="S",
        name_en="S",
        short_pt="s",
        short_en="s",
        sort_order=1,
    )
    session.add(subject)
    await session.flush()
    topic = Topic(
        subject_id=subject.id, slug="t", name_pt="T", name_en="T", sort_order=1
    )
    session.add(topic)
    await session.flush()
    question = Question(
        external_id="s.t.0001",
        subject_id=subject.id,
        topic_id=topic.id,
        status=QuestionStatus.PUBLISHED,
        difficulty_prior=3,
        rating=1000.0,
        content_hash="0" * 64,
        source="generated",
    )
    user = User(timezone="America/Sao_Paulo", current_subject_id=subject.id)
    session.add_all([question, user])
    await session.flush()
    practice = PracticeSession(
        user_id=user.id,
        subject_id=subject.id,
        question_ids=[question.id],
        started_at=datetime.now(UTC),
    )
    session.add_all(
        [
            practice,
            UserSettings(user_id=user.id, daily_goal=10),
            Streak(user_id=user.id),
            Event(
                user_id=user.id, name="probe", occurred_at=datetime.now(UTC)
            ),
        ]
    )
    await session.flush()
    session.add(
        Attempt(
            user_id=user.id,
            question_id=question.id,
            session_id=practice.id,
            answer={"key": "b"},
            is_correct=True,
            time_ms=4200,
            user_rating_before=1000.0,
            user_rating_after=1012.0,
            question_rating_before=1000.0,
            question_rating_after=994.0,
            locale=Locale.PT_BR,
        )
    )
    await session.flush()

    await session.delete(user)
    await session.flush()

    for model in (PracticeSession, Attempt, UserSettings, Streak, Event):
        assert (
            await session.scalar(select(sa.func.count()).select_from(model))
            == 0
        )
    assert (
        await session.scalar(select(sa.func.count()).select_from(Question))
        == 1
    )
