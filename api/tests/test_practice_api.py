"""Practice over HTTP, against Postgres: starting a session, answering,
finishing, and everything an answer writes.
"""

import uuid
from collections import Counter
from datetime import timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    DailyActivity,
    Question,
    ReviewItem,
    UserSubjectRating,
    UserTopicMastery,
)
from tests.conftest import Clock
from tests.support.api import (
    API,
    OTHER_SUBJECT,
    SUBJECT,
    TOPICS,
    answer,
    correct_keys,
    finish,
    guest,
    play,
    publish_bank,
    start,
    wrong_key,
)

pytestmark = pytest.mark.usefixtures("clock")

# Text that only the answer route may send: the reasons and the
# explanation of the spec's sample question, in both languages.
SECRET_TEXT = (
    "A fila é FIFO",
    "o último elemento inserido",
    "pilha de pratos",
    "A queue is FIFO",
    "like a stack of plates",
)
SECRET_FIELDS = {"correct_key", "reason", "reasons", "explanation"}


def _fields(value: Any) -> set[str]:
    """Every field name anywhere inside a JSON value."""
    if isinstance(value, dict):
        names = set(value)
        for inner in value.values():
            names |= _fields(inner)
        return names
    if isinstance(value, list):
        return set().union(*(_fields(item) for item in value))
    return set()


async def _count(session: AsyncSession, model: Any) -> int:
    count = await session.scalar(select(func.count()).select_from(model))
    return count or 0


# ---- a whole session ----


async def test_a_guest_plays_a_session_of_10_through_to_the_summary(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    await guest(client)

    started = await start(client)
    questions = started["questions"]
    assert len(questions) == 10
    assert started["finished_at"] is None
    assert started["summary"] is None

    for position, shown in enumerate(questions):
        # Seven right, three wrong.
        key = keys[shown["id"]]
        if position >= 7:
            key = wrong_key(key)
        feedback = await answer(client, started["id"], shown["id"], key)
        assert feedback["is_correct"] is (position < 7)
        assert feedback["session_complete"] is (position == 9)

    summary = await finish(client, started["id"])
    assert summary["correct_count"] == 7
    assert summary["total"] == 10
    assert summary["sessions_finished"] == 1
    assert summary["streak"]["current"] == 1
    assert summary["streak"]["status"] == "active"
    assert summary["goal"] == {
        "goal": 20,
        "questions": 10,
        "remaining": 10,
        "met": False,
    }

    again = (await client.get(f"{API}/sessions/{started['id']}")).json()
    assert again["finished_at"] is not None
    assert again["answered_count"] == 10
    assert again["correct_count"] == 7
    assert again["summary"] == summary


async def test_the_session_names_its_subject_and_each_questions_topic(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    started = await start(client)

    assert started["mode"] == "practice"
    assert started["subject"]["slug"] == SUBJECT
    assert started["subject"]["name_pt"] == "Estruturas de Dados"
    assert started["subject"]["name_en"] == "Data Structures"
    for shown in started["questions"]:
        assert shown["topic"]["slug"] in TOPICS
        assert shown["type"] == "mcq"
        assert 1 <= shown["difficulty"] <= 5
        assert shown["locale"] == "pt-BR"
        assert shown["answer"] is None
        assert sorted(o["key"] for o in shown["options"]) == list("abcd")


# ---- what the session payload hides ----


async def test_a_session_payload_never_has_the_key_the_reasons_or_the_explanation(  # noqa: E501
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    await guest(client)

    created = await client.post(f"{API}/sessions", json={"subject": SUBJECT})
    started = created.json()
    first, second = started["questions"][0], started["questions"][1]
    await answer(client, started["id"], first["id"], keys[first["id"]])
    await answer(
        client, started["id"], second["id"], wrong_key(keys[second["id"]])
    )
    resumed = await client.get(f"{API}/sessions/{started['id']}")

    for response in (created, resumed):
        assert not _fields(response.json()) & SECRET_FIELDS
        for text in SECRET_TEXT:
            assert text not in response.text
        for shown in response.json()["questions"]:
            assert set(shown["options"][0]) == {"key", "text"}
    # An answered question shows what was answered, and nothing else.
    by_id = {q["id"]: q for q in resumed.json()["questions"]}
    assert by_id[first["id"]]["answer"] == {
        "selected_key": keys[first["id"]],
        "is_correct": True,
        "xp_earned": by_id[first["id"]]["answer"]["xp_earned"],
    }
    assert by_id[second["id"]]["answer"]["is_correct"] is False
    assert by_id[started["questions"][2]["id"]]["answer"] is None


async def test_the_summary_of_a_finished_session_still_hides_the_answers(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    started, _ = await play(client, session, wrong=3)

    response = await client.get(f"{API}/sessions/{started['id']}")

    assert not _fields(response.json()) & SECRET_FIELDS
    for text in SECRET_TEXT:
        assert text not in response.text


async def test_option_order_is_shuffled_and_stays_put_within_a_session(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    started = await start(client)
    resumed = (await client.get(f"{API}/sessions/{started['id']}")).json()

    def orders(payload: dict[str, Any]) -> list[str]:
        return [
            "".join(o["key"] for o in q["options"])
            for q in payload["questions"]
        ]

    assert orders(started) == orders(resumed)
    assert set(orders(started)) != {"abcd"}


# ---- the answer response ----


async def test_the_answer_response_has_every_field_of_the_spec(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    await guest(client)
    started = await start(client)
    shown = started["questions"][0]

    feedback = await answer(client, started["id"], shown["id"], "a")

    assert set(feedback) == {
        "is_correct",
        "correct_key",
        "reasons",
        "explanation",
        "rating",
        "xp_earned",
        "session_complete",
    }
    assert feedback["correct_key"] == keys[shown["id"]]
    assert feedback["is_correct"] is (keys[shown["id"]] == "a")
    assert [r["key"] for r in feedback["reasons"]] == list("abcd")
    assert feedback["reasons"][0]["reason"].startswith("A fila é FIFO")
    assert "pilha de pratos" in feedback["explanation"]
    assert set(feedback["rating"]) == {"before", "after", "delta"}
    assert feedback["session_complete"] is False


async def test_the_reasons_are_sent_even_when_the_user_turned_them_off(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    await client.patch(
        f"{API}/me/settings", json={"show_option_reasons": False}
    )
    started = await start(client)

    feedback = await answer(
        client, started["id"], started["questions"][0]["id"], "a"
    )

    assert len(feedback["reasons"]) == 4


async def test_a_student_reading_in_english_gets_english_text(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client, locale="en")
    started = await start(client)
    shown = started["questions"][0]

    feedback = await answer(client, started["id"], shown["id"], "a")

    assert shown["locale"] == "en"
    assert [o["text"] for o in sorted(shown["options"], key=str)] == [
        "Queue",
        "Stack",
        "Linked list",
        "Binary tree",
    ]
    assert feedback["reasons"][0]["reason"].startswith("A queue is FIFO")
    assert "stack of plates" in feedback["explanation"]
    attempt = await session.scalar(select(Attempt))
    assert attempt is not None
    assert attempt.locale == "en"


# ---- ratings ----


async def test_a_first_attempt_moves_both_ratings(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    me = await guest(client)
    started = await start(client)
    shown = started["questions"][0]
    question_id = uuid.UUID(shown["id"])
    before = await session.get(Question, question_id)
    assert before is not None
    question_rating = before.rating

    feedback = await answer(
        client, started["id"], shown["id"], keys[shown["id"]]
    )

    # P for a student at 1000, then K 32 for them and 16 for the question.
    predicted = 0.25 + 0.75 / (1 + 10 ** ((question_rating - 1000) / 400))
    assert feedback["rating"]["before"] == 1000
    assert feedback["rating"]["after"] == pytest.approx(
        1000 + 32 * (1 - predicted)
    )
    assert feedback["rating"]["delta"] == pytest.approx(32 * (1 - predicted))

    question = await session.get(Question, question_id)
    assert question is not None
    await session.refresh(question)
    assert question.rating == pytest.approx(
        question_rating - 16 * (1 - predicted)
    )
    assert question.answers_count == 1
    assert question.correct_count == 1
    rating = await session.scalar(
        select(UserSubjectRating).where(
            UserSubjectRating.user_id == uuid.UUID(me["id"])
        )
    )
    assert rating is not None
    assert rating.rating == pytest.approx(feedback["rating"]["after"])
    assert rating.answers_count == 1
    attempt = await session.scalar(select(Attempt))
    assert attempt is not None
    assert attempt.answer == {"key": keys[shown["id"]]}
    assert attempt.time_ms == 5000
    assert attempt.user_rating_before == 1000
    assert attempt.user_rating_after == pytest.approx(rating.rating)
    assert attempt.question_rating_before == question_rating
    assert attempt.question_rating_after == pytest.approx(question.rating)


async def test_answering_the_same_question_again_changes_nothing(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    await guest(client)
    started = await start(client)
    shown = started["questions"][0]
    right = keys[shown["id"]]

    first = await answer(client, started["id"], shown["id"], right)
    # The client lost the response and sends it again, with another key.
    second = await answer(client, started["id"], shown["id"], wrong_key(right))

    assert second == first
    assert await _count(session, Attempt) == 1
    day = await session.scalar(select(DailyActivity))
    assert day is not None
    assert day.questions == 1
    assert day.xp == first["xp_earned"]
    question = await session.get(Question, uuid.UUID(shown["id"]))
    assert question is not None
    assert question.answers_count == 1


async def test_a_question_seen_before_moves_no_rating(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    # Ten questions in all: the second session repeats the first.
    await publish_bank(session, topics=TOPICS[:5], per_topic=2)
    keys = await correct_keys(session)
    me = await guest(client)
    await play(client, session)
    clock.advance(hours=1)

    again = await start(client)
    shown = again["questions"][0]
    feedback = await answer(
        client, again["id"], shown["id"], keys[shown["id"]]
    )

    assert feedback["rating"]["delta"] == 0
    assert feedback["rating"]["after"] == feedback["rating"]["before"]
    # It still earns XP and counts for the day and the topic.
    assert feedback["xp_earned"] >= 10
    rating = await session.scalar(
        select(UserSubjectRating).where(
            UserSubjectRating.user_id == uuid.UUID(me["id"])
        )
    )
    assert rating is not None
    assert rating.answers_count == 10
    question = await session.get(Question, uuid.UUID(shown["id"]))
    assert question is not None
    assert question.answers_count == 1
    total = await session.scalar(select(func.sum(UserTopicMastery.total)))
    assert total == 11


# ---- XP ----


async def test_xp_is_10_or_15_per_correct_answer_and_10_for_finishing(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    await guest(client)
    started = await start(client)
    earned = []
    for position, shown in enumerate(started["questions"]):
        key = keys[shown["id"]]
        if position < 2:
            key = wrong_key(key)
        feedback = await answer(client, started["id"], shown["id"], key)
        harder = feedback["rating"]["before"] < await _rating_before(
            session, shown["id"]
        )
        expected = 0 if position < 2 else (15 if harder else 10)
        assert feedback["xp_earned"] == expected
        earned.append(feedback["xp_earned"])

    summary = await finish(client, started["id"])

    assert summary["xp_earned"] == sum(earned) + 10
    assert summary["level_before"]["total_xp"] == 0
    assert summary["level_after"]["total_xp"] == sum(earned) + 10
    assert summary["level_after"]["level"] == 1
    assert summary["level_after"]["xp_per_level"] == 500
    day = await session.scalar(select(DailyActivity))
    assert day is not None
    assert day.xp == sum(earned) + 10
    assert day.questions == 10
    assert day.sessions_finished == 1


async def _rating_before(session: AsyncSession, question_id: str) -> float:
    rating = await session.scalar(
        select(Attempt.question_rating_before).where(
            Attempt.question_id == uuid.UUID(question_id)
        )
    )
    assert rating is not None
    return rating


# ---- review items ----


async def test_a_wrong_answer_writes_a_review_item_due_the_next_day(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    me = await guest(client)
    started = await start(client)
    right, wrong = started["questions"][0], started["questions"][1]

    await answer(client, started["id"], right["id"], keys[right["id"]])
    assert await _count(session, ReviewItem) == 0
    await answer(
        client, started["id"], wrong["id"], wrong_key(keys[wrong["id"]])
    )

    item = await session.scalar(select(ReviewItem))
    assert item is not None
    assert item.user_id == uuid.UUID(me["id"])
    assert item.question_id == uuid.UUID(wrong["id"])
    assert item.interval_days == 1
    assert item.due_at == clock.now + timedelta(days=1)
    assert item.lapses == 0
    assert await _count(session, ReviewItem) == 1


# ---- finishing ----


async def test_a_session_cannot_be_finished_before_every_answer(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    started = await start(client)
    for shown in started["questions"][:9]:
        await answer(client, started["id"], shown["id"], "a")

    response = await client.post(f"{API}/sessions/{started['id']}/finish")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "session_incomplete"
    day = await session.scalar(select(DailyActivity))
    assert day is not None
    assert day.sessions_finished == 0


async def test_finishing_twice_counts_once(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    started, summary = await play(client, session)

    again = await finish(client, started["id"])

    assert again == summary
    day = await session.scalar(select(DailyActivity))
    assert day is not None
    assert day.sessions_finished == 1
    assert day.xp == summary["xp_earned"]


async def test_the_summary_lists_the_topics_of_the_wrong_answers(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    await guest(client)
    started = await start(client)
    wrong_topics: Counter[str] = Counter()
    for position, shown in enumerate(started["questions"]):
        key = keys[shown["id"]]
        if position < 4:
            key = wrong_key(key)
            wrong_topics[shown["topic"]["slug"]] += 1
        await answer(client, started["id"], shown["id"], key)

    summary = await finish(client, started["id"])

    listed = summary["topics_to_review"]
    assert {t["slug"]: t["wrong_count"] for t in listed} == wrong_topics
    counts = [t["wrong_count"] for t in listed]
    assert counts == sorted(counts, reverse=True)
    assert listed[0]["name_pt"]
    assert listed[0]["name_en"]


async def test_the_summary_has_the_rating_before_and_after_the_session(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    _, gain = await play(client, session)
    _, loss = await play(client, session, wrong=10)

    assert gain["rating"]["subject"]["slug"] == SUBJECT
    assert gain["rating"]["before"] == 1000
    assert gain["rating"]["after"] > 1000
    assert gain["rating"]["delta"] == pytest.approx(
        gain["rating"]["after"] - 1000
    )
    assert loss["rating"]["before"] == pytest.approx(gain["rating"]["after"])
    assert loss["rating"]["delta"] < 0
    assert loss["sessions_finished"] == 2
    assert loss["goal"]["met"] is True


# ---- starting ----


async def test_an_unfinished_session_comes_back_instead_of_a_new_one(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    keys = await correct_keys(session)
    await guest(client)
    started = await start(client)
    first = started["questions"][0]
    await answer(client, started["id"], first["id"], keys[first["id"]])

    resumed = await start(client)

    assert resumed["id"] == started["id"]
    assert resumed["answered_count"] == 1
    assert resumed["questions"][0]["answer"]["is_correct"] is True
    assert [q["id"] for q in resumed["questions"]] == [
        q["id"] for q in started["questions"]
    ]


async def test_a_new_session_starts_once_the_last_one_is_finished(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    first, _ = await play(client, session)

    second = await start(client)

    assert second["id"] != first["id"]
    # Nothing answered in the last 14 days comes back while there is more.
    assert not {q["id"] for q in second["questions"]} & {
        q["id"] for q in first["questions"]
    }


async def test_a_first_session_has_levels_2_and_3_and_3_questions_a_topic(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    started = await start(client)

    assert {q["difficulty"] for q in started["questions"]} <= {2, 3}
    per_topic = Counter(q["topic"]["slug"] for q in started["questions"])
    assert max(per_topic.values()) <= 3


async def test_only_published_questions_are_served(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session, per_topic=3)
    retired = list(
        await session.scalars(select(Question).order_by(Question.external_id))
    )[:6]
    for question in retired:
        question.status = "retired"  # type: ignore[assignment]
    await session.flush()
    await guest(client)

    started = await start(client)

    served = {q["id"] for q in started["questions"]}
    assert len(served) == 9
    assert not served & {str(q.id) for q in retired}


async def test_a_subject_that_is_not_published_cannot_be_practiced(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    draft = await client.post(
        f"{API}/sessions", json={"subject": OTHER_SUBJECT}
    )
    unknown = await client.post(f"{API}/sessions", json={"subject": "nope"})

    for response in (draft, unknown):
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "subject_not_found"


async def test_a_published_subject_without_questions_is_a_409(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session, topics=())
    await guest(client)

    response = await client.post(f"{API}/sessions", json={"subject": SUBJECT})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "no_questions"


async def test_only_practice_sessions_can_be_started_in_v1(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)

    response = await client.post(
        f"{API}/sessions", json={"subject": SUBJECT, "mode": "review"}
    )

    assert response.status_code == 422


# ---- whose session it is ----


async def test_another_users_session_does_not_exist(
    client: AsyncClient, other_client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    await guest(other_client)
    started = await start(client)
    path = f"{API}/sessions/{started['id']}"
    body = {
        "question_id": started["questions"][0]["id"],
        "key": "a",
        "time_ms": 1,
    }

    responses = [
        await other_client.get(path),
        await other_client.post(f"{path}/answers", json=body),
        await other_client.post(f"{path}/finish"),
    ]

    for response in responses:
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "session_not_found"
    assert await _count(session, Attempt) == 0


async def test_a_question_from_outside_the_session_is_refused(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    started = await start(client)
    served = {q["id"] for q in started["questions"]}
    outside = next(
        str(q.id)
        for q in await session.scalars(select(Question))
        if str(q.id) not in served
    )

    response = await client.post(
        f"{API}/sessions/{started['id']}/answers",
        json={"question_id": outside, "key": "a", "time_ms": 1},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "question_not_in_session"


async def test_practice_needs_a_user(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)

    response = await client.post(f"{API}/sessions", json={"subject": SUBJECT})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


async def test_an_answer_must_be_one_of_the_four_keys(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    await guest(client)
    started = await start(client)

    response = await client.post(
        f"{API}/sessions/{started['id']}/answers",
        json={
            "question_id": started["questions"][0]["id"],
            "key": "e",
            "time_ms": 1,
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
