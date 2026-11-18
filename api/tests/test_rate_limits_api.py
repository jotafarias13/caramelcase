"""Rate limits over HTTP: the auth routes per network address, sign-in
links per email address, answers and reports per user.

Each test sets small limits of its own; the defaults are generous enough
for every other test to play whole sessions.
"""

from collections.abc import Callable, Iterator
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.settings import RateLimit, Settings, get_settings
from tests.conftest import Clock
from tests.support.api import API, guest, publish_bank, start
from tests.support.outbox import Outbox

pytestmark = pytest.mark.usefixtures("clock", "session")

SetLimits = Callable[..., None]


@pytest.fixture
def limits(app: FastAPI) -> Iterator[SetLimits]:
    """Call with the rate-limit settings a test wants, as keywords."""

    def set_limits(**limits: RateLimit) -> None:
        settings = Settings(**limits)  # type: ignore[arg-type]
        app.dependency_overrides[get_settings] = lambda: settings

    yield set_limits
    app.dependency_overrides.pop(get_settings, None)


def _from(address: str) -> dict[str, str]:
    """The header nginx sets to the caller's address."""
    return {"X-Real-IP": address}


def _assert_refused(response: httpx.Response) -> None:
    assert response.status_code == 429, response.text
    assert response.json()["error"]["code"] == "rate_limited"
    assert int(response.headers["Retry-After"]) >= 1


# ---- auth, per network address ----


async def test_the_auth_routes_share_one_limit_per_address(
    client: AsyncClient, limits: SetLimits, outbox: Outbox
) -> None:
    limits(rate_limit_auth=RateLimit(requests=4, seconds=600))
    here = _from("203.0.113.7")

    answers = [
        await client.post(f"{API}/auth/guest", json={}, headers=here),
        await client.post(
            f"{API}/auth/magic-link",
            json={"email": "ana@example.com"},
            headers=here,
        ),
        await client.post(
            f"{API}/auth/magic-link/verify",
            json={"token": "not-a-token"},
            headers=here,
        ),
        await client.get(f"{API}/auth/google/start", headers=here),
    ]
    refused = await client.post(f"{API}/auth/guest", json={}, headers=here)

    assert [r.status_code for r in answers] == [200, 202, 400, 307]
    _assert_refused(refused)
    assert len(outbox.emails) == 1


async def test_another_address_is_counted_apart(
    client: AsyncClient, other_client: AsyncClient, limits: SetLimits
) -> None:
    limits(rate_limit_auth=RateLimit(requests=1, seconds=600))
    await client.post(f"{API}/auth/guest", json={}, headers=_from("10.0.0.1"))

    again = await client.post(
        f"{API}/auth/guest", json={}, headers=_from("10.0.0.1")
    )
    elsewhere = await other_client.post(
        f"{API}/auth/guest", json={}, headers=_from("10.0.0.2")
    )

    _assert_refused(again)
    assert elsewhere.status_code == 200


async def test_the_limit_lifts_when_its_window_ends(
    client: AsyncClient, limits: SetLimits, clock: Clock
) -> None:
    limits(rate_limit_auth=RateLimit(requests=1, seconds=600))
    await client.post(f"{API}/auth/guest", json={})
    refused = await client.post(f"{API}/auth/guest", json={})
    wait = int(refused.headers["Retry-After"])

    clock.advance(seconds=wait)
    after = await client.post(f"{API}/auth/guest", json={})

    _assert_refused(refused)
    assert after.status_code == 200


async def test_signing_out_is_not_limited(
    client: AsyncClient, limits: SetLimits
) -> None:
    limits(rate_limit_auth=RateLimit(requests=1, seconds=600))
    await guest(client)
    _assert_refused(await client.post(f"{API}/auth/guest", json={}))

    response = await client.post(f"{API}/auth/logout")

    assert response.status_code == 204


# ---- sign-in links, per email address ----


async def test_an_address_gets_a_limited_number_of_links(
    client: AsyncClient, limits: SetLimits, outbox: Outbox, clock: Clock
) -> None:
    limits(rate_limit_sign_in_email=RateLimit(requests=2, seconds=3600))

    async def ask(email: str) -> httpx.Response:
        return await client.post(
            f"{API}/auth/magic-link", json={"email": email}
        )

    first = [await ask("carol@example.com") for _ in range(2)]
    third = await ask("Carol@Example.com")
    someone_else = await ask("bia@example.com")
    clock.advance(hours=1)
    next_hour = await ask("carol@example.com")

    assert [r.status_code for r in first] == [202, 202]
    _assert_refused(third)
    assert someone_else.status_code == 202
    assert next_hour.status_code == 202
    assert [e.to for e in outbox.emails] == [
        "carol@example.com",
        "carol@example.com",
        "bia@example.com",
        "carol@example.com",
    ]


# ---- answers and reports, per user ----


async def _answer(
    client: AsyncClient, started: dict[str, Any], position: int
) -> httpx.Response:
    question = started["questions"][position]
    return await client.post(
        f"{API}/sessions/{started['id']}/answers",
        json={"question_id": question["id"], "key": "a", "time_ms": 3000},
    )


async def test_answers_are_limited_per_user(
    client: AsyncClient,
    other_client: AsyncClient,
    limits: SetLimits,
    session: Any,
    clock: Clock,
) -> None:
    await publish_bank(session)
    limits(rate_limit_answers=RateLimit(requests=3, seconds=60))
    await guest(client)
    await guest(other_client)
    mine = await start(client)
    theirs = await start(other_client)

    allowed = [await _answer(client, mine, n) for n in range(3)]
    refused = await _answer(client, mine, 3)
    other_user = await _answer(other_client, theirs, 0)
    clock.advance(minutes=1)
    next_minute = await _answer(client, mine, 3)

    assert [r.status_code for r in allowed] == [200, 200, 200]
    _assert_refused(refused)
    assert other_user.status_code == 200
    assert next_minute.status_code == 200
    resumed = (await client.get(f"{API}/sessions/{mine['id']}")).json()
    answered = [q for q in resumed["questions"] if q["answer"] is not None]
    assert len(answered) == 4


async def test_reports_are_limited_per_user(
    client: AsyncClient, limits: SetLimits, session: Any
) -> None:
    await publish_bank(session)
    limits(rate_limit_reports=RateLimit(requests=2, seconds=3600))
    await guest(client)
    started = await start(client)

    async def report(position: int) -> httpx.Response:
        question_id = started["questions"][position]["id"]
        return await client.post(
            f"{API}/questions/{question_id}/report",
            json={"reason": "typo"},
        )

    allowed = [await report(n) for n in range(2)]
    refused = await report(2)

    assert [r.status_code for r in allowed] == [201, 201]
    _assert_refused(refused)


async def test_a_signed_out_answer_is_a_401_not_a_429(
    client: AsyncClient,
) -> None:
    response = await client.post(
        f"{API}/sessions/00000000-0000-0000-0000-000000000000/answers",
        json={"question_id": "00000000-0000-0000-0000-000000000000"},
    )

    assert response.status_code == 401
