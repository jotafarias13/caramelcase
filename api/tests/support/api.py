"""Helpers for the API tests: a published bank, and playing a session
over HTTP.
"""

import random
from typing import Any

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import QuestionTranslation
from app.domain.question_doc import QuestionDoc
from app.services.content_import import import_questions
from app.services.publishing import publish_subject
from app.services.seed import seed_all
from app.settings import Settings
from tests.support.questions import question, the_catalog

API = "/api/v1"
SUBJECT = "estruturas-de-dados"
TOPICS = (
    "pilhas",
    "filas-e-deques",
    "listas-encadeadas",
    "tabelas-de-dispersao",
    "busca-linear-e-binaria",
)
OTHER_SUBJECT = "banco-de-dados"
OTHER_TOPICS = ("sql-consultas", "sql-juncoes", "normalizacao", "sql-ddl")


async def publish_bank(
    session: AsyncSession,
    *,
    topics: tuple[str, ...] = TOPICS,
    per_topic: int = 8,
    both_subjects: bool = False,
) -> None:
    """Seed the plans, flags and catalog, then import and publish a small
    bank in SUBJECT: per_topic questions in each topic, levels 1 to 4,
    each with a different correct key.

    both_subjects adds the same in OTHER_SUBJECT and publishes it too.
    """
    settings = Settings()
    await seed_all(session, settings)
    bank = {SUBJECT: topics}
    if both_subjects:
        bank[OTHER_SUBJECT] = OTHER_TOPICS
    docs = []
    for subject, subject_topics in bank.items():
        for topic in subject_topics:
            for number in range(1, per_topic + 1):
                data = question(
                    number,
                    subject=subject,
                    topic=topic,
                    stem=f"Pergunta {number} sobre {topic}?",
                    difficulty=number % 4 + 1,
                    correct_key="abcd"[number % 4],
                    verified=True,
                )
                docs.append(QuestionDoc.model_validate(data))
    # One import for everything: the importer retires what it is not
    # given.
    await import_questions(session, docs, the_catalog(), settings)
    for subject in bank:
        await publish_subject(session, subject)


async def correct_keys(session: AsyncSession) -> dict[str, str]:
    """Question id -> the key of its correct option."""
    rows = await session.scalars(select(QuestionTranslation))
    keys = {}
    for row in rows:
        correct = [o["key"] for o in row.payload["options"] if o["is_correct"]]
        keys[str(row.question_id)] = correct[0]
    return keys


def wrong_key(correct: str) -> str:
    return "a" if correct != "a" else "b"


async def guest(client: AsyncClient, **body: Any) -> dict[str, Any]:
    """Become a guest in this client. Returns the user."""
    response = await client.post(f"{API}/auth/guest", json=body)
    assert response.status_code == 200, response.text
    user: dict[str, Any] = response.json()
    return user


async def start(client: AsyncClient, subject: str = SUBJECT) -> dict[str, Any]:
    response = await client.post(f"{API}/sessions", json={"subject": subject})
    assert response.status_code == 200, response.text
    payload: dict[str, Any] = response.json()
    return payload


async def answer(
    client: AsyncClient,
    session_id: str,
    question_id: str,
    key: str,
    time_ms: int = 5000,
) -> dict[str, Any]:
    response = await client.post(
        f"{API}/sessions/{session_id}/answers",
        json={"question_id": question_id, "key": key, "time_ms": time_ms},
    )
    assert response.status_code == 200, response.text
    feedback: dict[str, Any] = response.json()
    return feedback


async def finish(client: AsyncClient, session_id: str) -> dict[str, Any]:
    response = await client.post(f"{API}/sessions/{session_id}/finish")
    assert response.status_code == 200, response.text
    summary: dict[str, Any] = response.json()
    return summary


async def play(
    client: AsyncClient,
    session: AsyncSession,
    *,
    subject: str = SUBJECT,
    wrong: int = 0,
    seed: int = 0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Play a whole session, with `wrong` wrong answers, and finish it.

    Returns the session as it was started and its summary.
    """
    keys = await correct_keys(session)
    started = await start(client, subject)
    questions = started["questions"]
    missed = set(random.Random(seed).sample(range(len(questions)), wrong))
    for position, shown in enumerate(questions):
        key = keys[shown["id"]]
        if position in missed:
            key = wrong_key(key)
        await answer(client, started["id"], shown["id"], key)
    return started, await finish(client, started["id"])
