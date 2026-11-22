"""Catalog, stats, activity, config, feature flags, reports and events
over HTTP.
"""

import uuid
from datetime import timedelta
from typing import Any

import pytest
from fastapi import Depends, FastAPI
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Event,
    FeatureFlag,
    Question,
    QuestionReport,
    Subscription,
    User,
)
from app.enums import (
    FlagKey,
    FlagState,
    SubscriptionStatus,
    UserRole,
)
from app.routes.dependencies import require_csrf_header, require_flag
from tests.conftest import Clock
from tests.support.api import (
    API,
    OTHER_SUBJECT,
    SUBJECT,
    TOPICS,
    answer,
    correct_keys,
    guest,
    play,
    publish_bank,
    start,
    wrong_key,
)

pytestmark = pytest.mark.usefixtures("clock", "session")


async def _set_flag(
    session: AsyncSession, key: FlagKey, state: FlagState
) -> None:
    flag = await session.scalar(
        select(FeatureFlag).where(FeatureFlag.key == key.value)
    )
    assert flag is not None
    flag.state = state
    await session.flush()


async def _make_staff(session: AsyncSession, user_id: str) -> None:
    user = await session.get(User, uuid.UUID(user_id))
    assert user is not None
    user.role = UserRole.STAFF
    await session.flush()


# ---- catalog ----


async def test_the_catalog_lists_the_published_subjects_only(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    response = await client.get(f"{API}/subjects")

    assert response.status_code == 200
    (subject,) = response.json()["subjects"]
    assert subject == {
        "slug": SUBJECT,
        "name_pt": "Estruturas de Dados",
        "name_en": "Data Structures",
        "short_pt": "ed",
        "short_en": "ds",
        "topics_count": 5,
        "questions_count": 40,
        "rating": None,
        "answers_count": 0,
        "is_current": False,
    }


async def test_subjects_come_in_catalog_order_with_the_users_rating(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session, both_subjects=True)
    await guest(client)
    await client.patch(
        f"{API}/me/settings", json={"current_subject": OTHER_SUBJECT}
    )
    await play(client, session, subject=OTHER_SUBJECT)

    subjects = (await client.get(f"{API}/subjects")).json()["subjects"]

    assert [s["slug"] for s in subjects] == [SUBJECT, OTHER_SUBJECT]
    assert [s["is_current"] for s in subjects] == [False, True]
    assert subjects[0]["rating"] is None
    assert subjects[1]["rating"] > 1000
    assert subjects[1]["answers_count"] == 10


async def test_a_subject_has_its_topics_in_order_with_the_users_mastery(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    keys = await correct_keys(session)
    started = await start(client)
    answered: dict[str, list[bool]] = {}
    for position, shown in enumerate(started["questions"]):
        right = position % 2 == 0
        key = keys[shown["id"]]
        await answer(
            client,
            started["id"],
            shown["id"],
            key if right else wrong_key(key),
        )
        answered.setdefault(shown["topic"]["slug"], []).append(right)

    response = await client.get(f"{API}/subjects/{SUBJECT}")

    assert response.status_code == 200
    subject = response.json()
    assert subject["slug"] == SUBJECT
    assert subject["questions_count"] == 40
    # Catalog order, which is not the order of TOPICS, and only the
    # topics that have questions: 5 of the subject's 19.
    assert [t["slug"] for t in subject["topics"]] == [
        "listas-encadeadas",
        "pilhas",
        "filas-e-deques",
        "busca-linear-e-binaria",
        "tabelas-de-dispersao",
    ]
    assert subject["topics_count"] == 5
    for topic in subject["topics"]:
        results = answered.get(topic["slug"], [])
        assert topic["total"] == len(results)
        assert topic["correct"] == sum(results)
        expected = sum(results) / len(results) if results else 0
        assert topic["accuracy"] == pytest.approx(expected)
        assert topic["mastery"] == "new"  # under 5 answers each
        assert topic["name_pt"]
        assert topic["name_en"]
    assert subject["next_topic"] == "listas-encadeadas"


async def test_mastery_grows_with_the_answers(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    # One topic of 12 questions: every session is about it.
    await publish_bank(session, topics=("pilhas",), per_topic=12)
    await guest(client)

    await play(client, session, wrong=5)
    learning = (await client.get(f"{API}/subjects/{SUBJECT}")).json()
    clock.advance(minutes=5)
    await play(client, session)
    practiced = (await client.get(f"{API}/subjects/{SUBJECT}")).json()
    for _ in range(5):
        clock.advance(minutes=5)
        await play(client, session)
    mastered = (await client.get(f"{API}/subjects/{SUBJECT}")).json()

    assert learning["topics"][0]["mastery"] == "learning"  # 5 of 10
    assert practiced["topics"][0]["mastery"] == "practiced"  # 15 of 20
    assert practiced["next_topic"] == "pilhas"
    assert mastered["topics"][0]["mastery"] == "mastered"  # 65 of 70
    assert mastered["topics"][0]["accuracy"] == pytest.approx(65 / 70)
    assert mastered["next_topic"] is None


async def test_a_draft_subject_is_a_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    for slug in (OTHER_SUBJECT, "nope"):
        response = await client.get(f"{API}/subjects/{slug}")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "subject_not_found"


# ---- stats ----


async def test_stats_of_a_user_who_has_not_played(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    stats = (await client.get(f"{API}/me/stats")).json()

    assert stats == {
        "today": "2026-11-16",
        "level": {
            "total_xp": 0,
            "level": 1,
            "xp_in_level": 0,
            "xp_per_level": 500,
        },
        "streak": {
            "status": "none",
            "current": 0,
            "longest": 0,
            "lost_length": None,
        },
        "goal": {"goal": 20, "questions": 0, "remaining": 20, "met": False},
        "questions_answered": 0,
        "correct_answers": 0,
        "accuracy": 0,
        "sessions_finished": 0,
        "subjects": [
            {
                "slug": SUBJECT,
                "name_pt": "Estruturas de Dados",
                "name_en": "Data Structures",
                "short_pt": "ed",
                "short_en": "ds",
                "rating": None,
                "answers_count": 0,
            }
        ],
        "last_rating_change": None,
    }


async def test_stats_after_two_sessions(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    _, first = await play(client, session, wrong=2)
    _, second = await play(client, session, wrong=4)

    stats = (await client.get(f"{API}/me/stats")).json()

    xp = first["xp_earned"] + second["xp_earned"]
    assert stats["level"]["total_xp"] == xp
    assert stats["level"] == second["level_after"]
    assert stats["questions_answered"] == 20
    assert stats["correct_answers"] == 14
    assert stats["accuracy"] == pytest.approx(0.7)
    assert stats["sessions_finished"] == 2
    assert stats["goal"] == {
        "goal": 20,
        "questions": 20,
        "remaining": 0,
        "met": True,
    }
    assert stats["streak"] == second["streak"]
    assert stats["subjects"][0]["rating"] == pytest.approx(
        second["rating"]["after"]
    )
    assert stats["subjects"][0]["answers_count"] == 20
    assert stats["last_rating_change"] == second["rating"]


async def test_the_streak_grows_is_at_risk_and_is_lost_by_the_calendar(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    await publish_bank(session, per_topic=12)
    await guest(client)

    async def streak() -> dict[str, Any]:
        stats = (await client.get(f"{API}/me/stats")).json()
        streak: dict[str, Any] = stats["streak"]
        return streak

    await play(client, session)  # Monday
    monday = await streak()
    clock.advance(days=1)
    tuesday_morning = await streak()
    await play(client, session)
    tuesday = await streak()
    clock.advance(days=2)  # Wednesday passes without a session
    thursday = await streak()
    _, summary = await play(client, session)

    assert monday["status"] == "active"
    assert monday["current"] == 1
    assert tuesday_morning["status"] == "at_risk"
    assert tuesday_morning["current"] == 1
    assert tuesday["status"] == "active"
    assert tuesday["current"] == 2
    assert thursday == {
        "status": "lost",
        "current": 0,
        "longest": 2,
        "lost_length": 2,
    }
    assert summary["streak"] == {
        "status": "active",
        "current": 1,
        "longest": 2,
        "lost_length": None,
    }


async def test_the_day_is_the_users_own(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    clock: Clock,
) -> None:
    await publish_bank(session)
    # 23:30 on Monday in São Paulo is 11:30 on Tuesday in Tokyo.
    clock.advance(hours=11, minutes=30)
    await guest(client, timezone="America/Sao_Paulo")
    await guest(other_client, timezone="Asia/Tokyo")

    await play(client, session)
    await play(other_client, session)
    clock.advance(hours=1)  # past midnight in São Paulo

    here = (await client.get(f"{API}/me/stats")).json()
    there = (await other_client.get(f"{API}/me/stats")).json()
    assert here["today"] == "2026-11-17"
    assert there["today"] == "2026-11-17"
    assert here["streak"]["status"] == "at_risk"  # played on the 16th
    assert here["goal"]["questions"] == 0
    assert there["streak"]["status"] == "active"  # played on the 17th
    assert there["goal"]["questions"] == 10
    days_here = (await client.get(f"{API}/me/activity")).json()["days"]
    days_there = (await other_client.get(f"{API}/me/activity")).json()["days"]
    assert [day["date"] for day in days_here] == ["2026-11-16"]
    assert [day["date"] for day in days_there] == ["2026-11-17"]


# ---- activity ----


async def test_activity_is_the_current_month_by_default(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    await publish_bank(session, per_topic=12)
    await guest(client)
    clock.advance(days=-20)  # October 27
    await play(client, session)
    clock.advance(days=20)
    _, summary = await play(client, session, wrong=1)

    activity = (await client.get(f"{API}/me/activity")).json()

    assert activity["today"] == "2026-11-16"
    assert activity["start"] == "2026-11-01"
    assert activity["end"] == "2026-11-30"
    assert activity["days"] == [
        {
            "date": "2026-11-16",
            "xp": summary["xp_earned"],
            "questions": 10,
            "sessions_finished": 1,
            "goal_met": False,
        }
    ]


async def test_activity_between_two_dates(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    await publish_bank(session, per_topic=12)
    await guest(client)
    clock.advance(days=-20)
    await play(client, session)
    clock.advance(days=20)
    await play(client, session)

    october = await client.get(f"{API}/me/activity?start=2026-10-01")
    both = await client.get(
        f"{API}/me/activity?start=2026-10-27&end=2026-11-16"
    )

    assert october.json()["end"] == "2026-10-31"
    assert [d["date"] for d in october.json()["days"]] == ["2026-10-27"]
    assert [d["date"] for d in both.json()["days"]] == [
        "2026-10-27",
        "2026-11-16",
    ]


@pytest.mark.parametrize(
    "query",
    [
        "start=2026-11-10&end=2026-11-09",
        "start=2025-01-01&end=2026-11-16",
        "start=yesterday",
    ],
)
async def test_a_bad_range_of_dates_is_a_422(
    client: AsyncClient, query: str
) -> None:
    await guest(client)

    response = await client.get(f"{API}/me/activity?{query}")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


# ---- config ----


async def test_config_for_a_visitor_has_every_flag_off_and_no_limits(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)

    response = await client.get(f"{API}/config")

    assert response.status_code == 200
    config = response.json()
    assert set(config["flags"]) == {key.value for key in FlagKey}
    assert not any(config["flags"].values())
    assert config["entitlements"] == {
        "plan_key": None,
        "sessions_per_day": None,
        "ads": False,
        "tutor_messages_per_day": None,
        "exam_mode": True,
        "exam_tracks": True,
    }
    assert [plan["key"] for plan in config["plans"]] == [
        "free",
        "plus",
        "pro",
        "max",
    ]
    assert config["plans"][0]["limits"]["sessions_per_day"] == 3
    assert float(config["plans"][3]["price_month_brl"]) == 100
    assert config["google_sign_in"] is True
    assert config["session_length"] == 10
    assert config["daily_goal_options"] == [10, 20, 30]
    assert config["xp_per_level"] == 500
    # The numbers the app quotes when it explains XP, rating and mastery.
    assert config["rules"] == {
        "xp_correct": 10,
        "xp_session_finished": 10,
        "user_rating_start": 1000,
        "mastery_mastered_from": 0.85,
        "mastery_mastered_min_answers": 10,
    }


async def test_config_shows_a_flag_as_it_is_for_whoever_asks(
    client: AsyncClient, other_client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    staff = await guest(other_client)
    await _make_staff(session, staff["id"])
    await _set_flag(session, FlagKey.REVIEW_QUEUE, FlagState.STAFF)
    await _set_flag(session, FlagKey.LEAGUES, FlagState.ON)

    for_user = (await client.get(f"{API}/config")).json()["flags"]
    for_staff = (await other_client.get(f"{API}/config")).json()["flags"]

    assert for_user["review_queue"] is False
    assert for_staff["review_queue"] is True
    assert for_user["leagues"] is True
    assert for_staff["leagues"] is True
    assert for_user["exam_mode"] is False
    assert for_staff["exam_mode"] is False


async def test_with_billing_on_the_entitlements_follow_the_plan(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    clock: Clock,
) -> None:
    await publish_bank(session)
    await guest(client)
    subscriber = await guest(other_client)
    await _set_flag(session, FlagKey.BILLING, FlagState.ON)
    session.add(
        Subscription(
            user_id=uuid.UUID(subscriber["id"]),
            plan_key="pro",
            status=SubscriptionStatus.ACTIVE,
            provider="mock",
            provider_ref="sub-1",
            current_period_end=clock.now + timedelta(days=20),
        )
    )
    await session.flush()

    free = (await client.get(f"{API}/config")).json()["entitlements"]
    pro = (await other_client.get(f"{API}/config")).json()["entitlements"]

    assert free["plan_key"] == "free"
    assert free["sessions_per_day"] == 3
    assert free["ads"] is True
    assert pro["plan_key"] == "pro"
    assert pro["sessions_per_day"] is None
    assert pro["tutor_messages_per_day"] == 30


# ---- flagged routes ----


@pytest.fixture
def flagged_route(app: FastAPI) -> str:
    """A route behind the leagues flag, as milestone 9 will have."""
    path = "/api/v1/test-only/flagged"
    if not any(getattr(r, "path", "") == path for r in app.routes):

        @app.get(
            path,
            dependencies=[
                Depends(require_csrf_header),
                Depends(require_flag(FlagKey.LEAGUES)),
            ],
        )
        async def flagged() -> dict[str, bool]:
            return {"on": True}

    return path


async def test_a_flagged_route_is_a_404_while_its_flag_is_off(
    client: AsyncClient, session: AsyncSession, flagged_route: str
) -> None:
    await publish_bank(session)
    await guest(client)

    flagged = await client.get(flagged_route)
    unknown = await client.get(f"{API}/does-not-exist")

    assert flagged.status_code == 404
    # Nothing tells it apart from a route that does not exist.
    assert flagged.json() == unknown.json()


async def test_a_flag_for_staff_opens_the_route_to_staff_only(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    flagged_route: str,
) -> None:
    await publish_bank(session)
    await guest(client)
    staff = await guest(other_client)
    await _make_staff(session, staff["id"])
    await _set_flag(session, FlagKey.LEAGUES, FlagState.STAFF)

    as_user = await client.get(flagged_route)
    as_staff = await other_client.get(flagged_route)
    client.cookies.clear()
    as_visitor = await client.get(flagged_route)

    assert as_user.status_code == 404
    assert as_visitor.status_code == 404
    assert as_staff.status_code == 200
    assert as_staff.json() == {"on": True}


async def test_a_flag_that_is_on_opens_the_route_to_everyone(
    client: AsyncClient, session: AsyncSession, flagged_route: str
) -> None:
    await publish_bank(session)
    await _set_flag(session, FlagKey.LEAGUES, FlagState.ON)

    as_visitor = await client.get(flagged_route)
    await guest(client)
    as_user = await client.get(flagged_route)

    assert as_visitor.status_code == 200
    assert as_user.status_code == 200


async def test_a_flag_without_a_row_is_off(
    client: AsyncClient,
    session: AsyncSession,  # noqa: ARG001  an empty database: nothing seeded
    flagged_route: str,
) -> None:
    flagged = await client.get(flagged_route)
    config = await client.get(f"{API}/config")

    assert flagged.status_code == 404
    assert config.json()["flags"]["leagues"] is False


# ---- reports ----


async def test_a_report_is_stored_with_the_language_it_was_read_in(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    me = await guest(client, locale="en")
    started = await start(client)
    question_id = started["questions"][3]["id"]

    response = await client.post(
        f"{API}/questions/{question_id}/report",
        json={"reason": "ambiguous_wording", "comment": "  Two fit.  "},
    )

    assert response.status_code == 201
    report = await session.scalar(select(QuestionReport))
    assert report is not None
    assert response.json()["id"] == str(report.id)
    assert report.question_id == uuid.UUID(question_id)
    assert report.user_id == uuid.UUID(me["id"])
    assert report.reason == "ambiguous_wording"
    assert report.comment == "Two fit."
    assert report.locale == "en"
    assert report.status == "open"


@pytest.mark.parametrize(
    "reason", ["wrong_answer", "ambiguous_wording", "typo", "other"]
)
async def test_the_four_reasons_of_the_design_are_accepted(
    client: AsyncClient, session: AsyncSession, reason: str
) -> None:
    await publish_bank(session)
    await guest(client)
    started = await start(client)
    question_id = started["questions"][0]["id"]

    response = await client.post(
        f"{API}/questions/{question_id}/report", json={"reason": reason}
    )

    assert response.status_code == 201
    report = await session.scalar(select(QuestionReport))
    assert report is not None
    assert report.comment is None


async def test_only_a_question_the_user_was_served_can_be_reported(
    client: AsyncClient, other_client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    await guest(other_client)
    started = await start(client)
    served = {q["id"] for q in started["questions"]}
    never_served = next(
        str(q.id)
        for q in await session.scalars(select(Question))
        if str(q.id) not in served
    )
    body = {"reason": "typo"}

    responses = [
        await client.post(f"{API}/questions/{never_served}/report", json=body),
        await client.post(f"{API}/questions/{uuid.uuid4()}/report", json=body),
        # Served to someone else.
        await other_client.post(
            f"{API}/questions/{started['questions'][0]['id']}/report",
            json=body,
        ),
    ]

    for response in responses:
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "question_not_found"
    assert await session.scalar(select(QuestionReport)) is None


@pytest.mark.parametrize(
    "body",
    [
        {"reason": "boring"},
        {"comment": "no reason"},
        {"reason": "other", "comment": "x" * 1001},
    ],
)
async def test_a_bad_report_is_a_422(
    client: AsyncClient, session: AsyncSession, body: dict[str, str]
) -> None:
    await publish_bank(session)
    await guest(client)
    started = await start(client)
    question_id = started["questions"][0]["id"]

    response = await client.post(
        f"{API}/questions/{question_id}/report", json=body
    )

    assert response.status_code == 422
    assert await session.scalar(select(QuestionReport)) is None


# ---- events ----


async def test_a_batch_of_events_is_stored_for_the_user(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    me = await guest(client)
    earlier = (clock.now - timedelta(minutes=3)).isoformat()
    ahead = (clock.now + timedelta(hours=2)).isoformat()

    response = await client.post(
        f"{API}/events",
        json={
            "events": [
                {
                    "name": "session.started",
                    "props": {"subject": SUBJECT, "n": 1},
                    "occurred_at": earlier,
                },
                {"name": "summary_viewed", "occurred_at": ahead},
            ]
        },
    )

    assert response.status_code == 202
    assert response.json() == {"accepted": 2}
    events = list(await session.scalars(select(Event).order_by(Event.name)))
    assert [e.name for e in events] == ["session.started", "summary_viewed"]
    assert {e.user_id for e in events} == {uuid.UUID(me["id"])}
    assert events[0].props == {"subject": SUBJECT, "n": 1}
    assert events[0].occurred_at.isoformat() == earlier
    assert events[1].props == {}
    # A clock that runs ahead cannot put an event in the future.
    assert events[1].occurred_at == clock.now


async def test_a_visitors_events_are_stored_without_a_user(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    response = await client.post(
        f"{API}/events",
        json={
            "events": [
                {
                    "name": "landing.viewed",
                    "occurred_at": clock.now.isoformat(),
                }
            ]
        },
    )

    assert response.status_code == 202
    event = await session.scalar(select(Event))
    assert event is not None
    assert event.user_id is None


def _event(**changes: Any) -> dict[str, Any]:
    return {
        "name": "session.started",
        "occurred_at": "2026-11-16T15:00:00Z",
        **changes,
    }


@pytest.mark.parametrize(
    "events",
    [
        [_event()] * 51,
        [_event(name="Not A Name")],
        [_event(name="x" * 65)],
        [_event(occurred_at="2026-11-16T15:00:00")],  # no timezone
        [_event(props={"blob": "x" * 2001})],
        [_event(), _event(props="text")],
    ],
)
async def test_a_bad_batch_stores_nothing(
    client: AsyncClient, session: AsyncSession, events: list[dict[str, Any]]
) -> None:
    response = await client.post(f"{API}/events", json={"events": events})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert await session.scalar(select(Event)) is None


def test_the_topics_of_the_test_bank_are_not_in_catalog_order() -> None:
    # The catalog-order test above relies on it.
    assert TOPICS[0] == "pilhas"
