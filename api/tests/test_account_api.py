"""The account over HTTP: preferences, export and deletion."""

import uuid
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import Column, Table, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.models import (
    Attempt,
    AuthSession,
    MagicLink,
    Question,
    User,
    UserSubject,
)
from app.services.account import EXPORTED_BY_USER_ID, NOT_EXPORTED
from tests.support.api import (
    API,
    OTHER_SUBJECT,
    SUBJECT,
    guest,
    play,
    publish_bank,
)
from tests.support.outbox import Outbox

pytestmark = pytest.mark.usefixtures("clock", "session")


async def _patch(client: AsyncClient, **fields: Any) -> dict[str, Any]:
    response = await client.patch(f"{API}/me/settings", json=fields)
    assert response.status_code == 200, response.text
    me: dict[str, Any] = response.json()
    return me


# ---- preferences ----


async def test_onboarding_saves_language_study_subject_and_goal(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    me = await guest(client)

    await _patch(client, locale="en")
    await _patch(client, university="UFRN", course="Ciência da Computação")
    await _patch(client, current_subject=SUBJECT)
    after = await _patch(client, daily_goal=30)

    assert after["locale"] == "en"
    assert after["university"] == "UFRN"
    assert after["course"] == "Ciência da Computação"
    assert after["current_subject"] == SUBJECT
    assert after["settings"]["daily_goal"] == 30
    assert (await client.get(f"{API}/me")).json() == after
    chosen = await session.scalar(select(UserSubject))
    assert chosen is not None
    assert chosen.user_id == uuid.UUID(me["id"])


async def test_the_settings_screen_saves_theme_reasons_and_reminder(
    client: AsyncClient,
) -> None:
    await guest(client)

    after = await _patch(
        client,
        theme="dark",
        show_option_reasons=False,
        daily_reminder=True,
        weekly_email=True,
        timezone="Europe/Lisbon",
        display_name="  Carol Nunes ",
    )

    assert after["settings"] == {
        "daily_goal": 20,
        "theme": "dark",
        "show_option_reasons": False,
        "daily_reminder": True,
        "weekly_email": True,
    }
    assert after["timezone"] == "Europe/Lisbon"
    assert after["display_name"] == "Carol Nunes"


async def test_only_the_fields_sent_are_changed(client: AsyncClient) -> None:
    await guest(client)
    await _patch(client, theme="dark", university="UFRN", course="CC")

    after = await _patch(client, show_option_reasons=False)

    assert after["settings"]["theme"] == "dark"
    assert after["settings"]["show_option_reasons"] is False
    assert after["university"] == "UFRN"
    assert after["course"] == "CC"


async def test_null_or_an_empty_text_clears_a_profile_field(
    client: AsyncClient,
) -> None:
    await guest(client)
    await _patch(client, university="UFRN", course="CC", locale="en")

    after = await _patch(client, university=None, course="  ", locale=None)

    assert after["university"] is None
    assert after["course"] is None
    assert after["locale"] == "en"


@pytest.mark.parametrize(
    "fields",
    [
        {"daily_goal": 15},
        {"daily_goal": 0},
        {"theme": "sepia"},
        {"locale": "fr"},
        {"timezone": "Nowhere/City"},
        {"university": "x" * 121},
        {"display_name": "x" * 81},
    ],
)
async def test_a_value_out_of_range_is_a_422_and_changes_nothing(
    client: AsyncClient, fields: dict[str, Any]
) -> None:
    before = await guest(client)

    response = await client.patch(f"{API}/me/settings", json=fields)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert (await client.get(f"{API}/me")).json() == before


async def test_the_current_subject_must_be_published(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    for slug in (OTHER_SUBJECT, "nope"):
        response = await client.patch(
            f"{API}/me/settings", json={"current_subject": slug}
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "subject_not_found"


async def test_a_lower_goal_can_be_met_by_what_was_already_answered(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    await play(client, session)
    before = (await client.get(f"{API}/me/stats")).json()["goal"]

    await _patch(client, daily_goal=10)

    after = (await client.get(f"{API}/me/stats")).json()["goal"]
    assert before == {
        "goal": 20,
        "questions": 10,
        "remaining": 10,
        "met": False,
    }
    assert after == {"goal": 10, "questions": 10, "remaining": 0, "met": True}
    day = (await client.get(f"{API}/me/activity")).json()["days"][0]
    assert day["goal_met"] is True


# ---- export ----

# The tables a V1 user has rows in once they have played, missed, reported,
# sent an event and signed in.
V1_TABLES = {
    "user_settings",
    "auth_identities",
    "user_subjects",
    "practice_sessions",
    "attempts",
    "user_subject_ratings",
    "user_topic_mastery",
    "daily_activity",
    "streaks",
    "review_items",
    "question_reports",
    "events",
}


async def _a_user_with_rows_everywhere(
    client: AsyncClient, session: AsyncSession, outbox: Outbox
) -> dict[str, Any]:
    """A student who set a profile, played a session with two misses,
    reported a question, sent an event and then signed in by email.
    """
    await publish_bank(session)
    await guest(client)
    await _patch(client, university="UFRN", current_subject=SUBJECT)
    started, _ = await play(client, session, wrong=2)
    question_id = started["questions"][0]["id"]
    reported = await client.post(
        f"{API}/questions/{question_id}/report",
        json={"reason": "typo", "comment": "Falta um acento."},
    )
    assert reported.status_code == 201, reported.text
    sent = await client.post(
        f"{API}/events",
        json={
            "events": [
                {
                    "name": "landing.viewed",
                    "occurred_at": "2026-11-16T14:59:00Z",
                }
            ]
        },
    )
    assert sent.status_code == 202, sent.text
    asked = await client.post(
        f"{API}/auth/magic-link", json={"email": "carol@example.com"}
    )
    assert asked.status_code == 202, asked.text
    verified = await client.post(
        f"{API}/auth/magic-link/verify", json={"token": outbox.token()}
    )
    assert verified.status_code == 200, verified.text
    me: dict[str, Any] = verified.json()
    return me


def _user_columns() -> list[tuple[Table, Column[Any]]]:
    """Every column that points at users.id, with its table."""
    return [
        (table, column)
        for table in Base.metadata.sorted_tables
        for column in table.columns
        if any(fk.column.table.name == "users" for fk in column.foreign_keys)
    ]


def test_every_table_that_points_at_users_is_exported_or_a_credential() -> (
    None
):
    exported = {model.__tablename__ for model in EXPORTED_BY_USER_ID}
    exported |= {"referrals"}  # by either of its two user columns
    credentials = {model.__tablename__ for model in NOT_EXPORTED}

    pointing = {table.name for table, _ in _user_columns()}

    assert {"attempts", "referrals", "sessions_auth"} <= pointing
    assert pointing <= exported | credentials
    assert not exported & credentials


async def test_the_export_has_every_row_of_the_user_and_no_credentials(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    outbox: Outbox,
) -> None:
    me = await _a_user_with_rows_everywhere(client, session, outbox)
    await guest(other_client)
    await play(other_client, session)

    response = await client.get(f"{API}/me/export")

    assert response.status_code == 200
    export = response.json()
    assert export["user"]["id"] == me["id"]
    assert export["user"]["email"] == "carol@example.com"
    assert export["user"]["university"] == "UFRN"
    assert export["user"]["timezone"] == "America/Sao_Paulo"
    tables = export["tables"]
    filled = {name for name, rows in tables.items() if rows}
    assert filled == V1_TABLES
    assert len(tables["attempts"]) == 10
    assert len(tables["practice_sessions"]) == 1
    assert len(tables["practice_sessions"][0]["question_ids"]) == 10
    assert len(tables["review_items"]) == 2
    assert tables["question_reports"][0]["comment"] == "Falta um acento."
    assert tables["events"][0]["name"] == "landing.viewed"
    assert tables["auth_identities"][0]["provider"] == "email"
    assert tables["user_settings"][0]["daily_goal"] == 20
    assert tables["streaks"][0]["current"] == 1
    # The tables of V2 and V3 are there, empty.
    assert tables["tutor_messages"] == []
    assert tables["referrals"] == []
    # Only this user's rows, in every table.
    for rows in tables.values():
        assert {row.get("user_id", me["id"]) for row in rows} <= {me["id"]}
    assert "sessions_auth" not in tables
    assert "magic_links" not in tables
    assert client.cookies["cc_session"] not in response.text
    for stored in await session.scalars(select(AuthSession.token_hash)):
        assert stored not in response.text


# ---- deletion ----


def test_every_foreign_key_to_users_deletes_with_the_user() -> None:
    """DELETE /me relies on it: deleting the users row takes the rest."""
    not_cascading = [
        f"{table.name}.{column.name}"
        for table, column in _user_columns()
        for fk in column.foreign_keys
        if fk.ondelete != "CASCADE"
    ]

    assert len(_user_columns()) > 20
    assert not_cascading == []


async def test_deleting_the_account_erases_every_row_of_the_user(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    outbox: Outbox,
) -> None:
    me = await _a_user_with_rows_everywhere(client, session, outbox)
    user_id = uuid.UUID(me["id"])
    other = await guest(other_client)
    await play(other_client, session)
    answered = await session.scalar(select(func.sum(Question.answers_count)))

    response = await client.delete(f"{API}/me")

    assert response.status_code == 204
    assert (await client.get(f"{API}/me")).status_code == 401
    assert await session.get(User, user_id) is None
    for table, column in _user_columns():
        left = await session.scalar(
            select(func.count()).select_from(table).where(column == user_id)
        )
        assert left == 0, f"{table.name}.{column.name}"
    links = await session.scalar(
        select(func.count())
        .select_from(MagicLink)
        .where(MagicLink.email == "carol@example.com")
    )
    assert links == 0
    # The other student keeps everything.
    others = set(await session.scalars(select(Attempt.user_id)))
    assert others == {uuid.UUID(other["id"])}
    assert (await other_client.get(f"{API}/me")).status_code == 200
    # The questions keep what they learned from the answers.
    after = await session.scalar(select(func.sum(Question.answers_count)))
    assert after == answered == 20


async def test_a_second_subject_does_not_get_in_the_way(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Two published subjects: each has its own rating and sessions."""
    await publish_bank(session, both_subjects=True)
    await guest(client)

    await play(client, session, subject=SUBJECT)
    _, summary = await play(client, session, subject=OTHER_SUBJECT, wrong=10)

    assert summary["rating"]["subject"]["slug"] == OTHER_SUBJECT
    assert summary["rating"]["before"] == 1000
    stats = (await client.get(f"{API}/me/stats")).json()
    ratings = {s["slug"]: s["rating"] for s in stats["subjects"]}
    assert ratings[SUBJECT] > 1000 > ratings[OTHER_SUBJECT]
    assert stats["last_rating_change"]["subject"]["slug"] == OTHER_SUBJECT
    assert stats["last_rating_change"]["delta"] < 0
