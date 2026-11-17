"""The account over HTTP: preferences, export and deletion."""

import uuid
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    AuthSession,
    DailyActivity,
    PracticeSession,
    Question,
    Streak,
    User,
    UserSettings,
    UserSubject,
)
from tests.support.api import (
    API,
    OTHER_SUBJECT,
    SUBJECT,
    guest,
    play,
    publish_bank,
)

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


async def test_the_export_has_the_users_rows_and_no_credentials(
    client: AsyncClient, other_client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    me = await guest(client)
    await _patch(client, university="UFRN", current_subject=SUBJECT)
    await play(client, session, wrong=2)
    await guest(other_client)
    await play(other_client, session)

    response = await client.get(f"{API}/me/export")

    assert response.status_code == 200
    export = response.json()
    assert export["user"]["id"] == me["id"]
    assert export["user"]["university"] == "UFRN"
    assert export["user"]["timezone"] == "America/Sao_Paulo"
    tables = export["tables"]
    assert len(tables["attempts"]) == 10
    assert len(tables["practice_sessions"]) == 1
    assert len(tables["practice_sessions"][0]["question_ids"]) == 10
    assert len(tables["daily_activity"]) == 1
    assert len(tables["review_items"]) == 2
    assert tables["user_settings"][0]["daily_goal"] == 20
    assert tables["streaks"][0]["current"] == 1
    assert len(tables["user_subjects"]) == 1
    assert len(tables["user_subject_ratings"]) == 1
    # Only this user's rows, in every table.
    for rows in tables.values():
        assert {row["user_id"] for row in rows} <= {me["id"]}
    assert "sessions_auth" not in tables
    assert "magic_links" not in tables
    assert client.cookies["cc_session"] not in response.text
    stored = await session.scalar(select(AuthSession.token_hash))
    assert stored is not None
    assert stored not in response.text


# ---- deletion ----


async def test_deleting_the_account_erases_everything_of_the_user(
    client: AsyncClient, other_client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    me = await guest(client)
    await play(client, session, wrong=3)
    other = await guest(other_client)
    await play(other_client, session)
    answered = await session.scalar(select(func.sum(Question.answers_count)))

    response = await client.delete(f"{API}/me")

    assert response.status_code == 204
    assert (await client.get(f"{API}/me")).status_code == 401
    assert await session.get(User, uuid.UUID(me["id"])) is None
    for model in (
        Attempt,
        PracticeSession,
        DailyActivity,
        Streak,
        UserSettings,
        AuthSession,
    ):
        owners = set(await session.scalars(select(model.user_id)))
        assert owners == {uuid.UUID(other["id"])}, model.__tablename__
    # The questions keep what they learned from the answers.
    after = await session.scalar(select(func.sum(Question.answers_count)))
    assert after == answered == 20
    assert (await other_client.get(f"{API}/me")).status_code == 200


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
