"""Auth over HTTP: guests, session tokens, the CSRF header, CORS, email
links, Google sign-in, and what signing in does to a guest's history.
"""

import hashlib
import re
import uuid
from collections.abc import Iterator
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    AuthIdentity,
    AuthSession,
    MagicLink,
    User,
)
from app.providers.email import Email, get_email_sender
from app.providers.google import (
    AUTHORIZE_URL,
    TOKEN_URL,
    USERINFO_URL,
    GoogleError,
    GoogleOAuthProvider,
    GoogleProfile,
    get_google_provider,
    google_provider_for,
)
from app.settings import Settings
from tests.conftest import CSRF_HEADERS, Clock
from tests.support.api import API, guest, play, publish_bank

pytestmark = pytest.mark.usefixtures("clock", "session")

COOKIE = "cc_session"
CAROL = "carol@example.com"


class Outbox:
    """Stands in for the email sender and keeps what was sent."""

    def __init__(self) -> None:
        self.emails: list[Email] = []

    async def send(self, email: Email) -> None:
        self.emails.append(email)

    def token(self) -> str:
        """The token of the link in the last email."""
        match = re.search(r"/auth/callback\?token=(\S+)", self.emails[-1].text)
        assert match is not None
        return match.group(1)


@pytest.fixture
def outbox(app: FastAPI) -> Iterator[Outbox]:
    outbox = Outbox()
    app.dependency_overrides[get_email_sender] = lambda: outbox
    yield outbox
    app.dependency_overrides.pop(get_email_sender, None)


async def _sign_in_by_email(
    client: AsyncClient, outbox: Outbox, email: str = CAROL
) -> dict[str, Any]:
    """Ask for a link and open it in the same browser."""
    asked = await client.post(f"{API}/auth/magic-link", json={"email": email})
    assert asked.status_code == 202, asked.text
    verified = await client.post(
        f"{API}/auth/magic-link/verify", json={"token": outbox.token()}
    )
    assert verified.status_code == 200, verified.text
    user: dict[str, Any] = verified.json()
    return user


def _set_cookie(response: httpx.Response, name: str = COOKIE) -> Any:
    """The Set-Cookie of a response, parsed."""
    cookies: SimpleCookie = SimpleCookie()
    for header in response.headers.get_list("set-cookie"):
        cookies.load(header)
    return cookies[name]


# ---- guests and session tokens ----


async def test_a_guest_is_a_real_user_with_default_preferences(
    client: AsyncClient, session: AsyncSession
) -> None:
    me = await guest(client)

    assert me["is_guest"] is True
    assert me["email"] is None
    assert me["display_name"] is None
    assert me["role"] == "user"
    assert me["locale"] == "pt-BR"
    assert me["timezone"] == "America/Sao_Paulo"
    assert me["current_subject"] is None
    assert me["settings"] == {
        "daily_goal": 20,
        "theme": "system",
        "show_option_reasons": True,
        "daily_reminder": False,
        "weekly_email": False,
    }
    user = await session.get(User, uuid.UUID(me["id"]))
    assert user is not None
    assert user.is_guest


async def test_a_guest_takes_the_browsers_language_and_timezone(
    client: AsyncClient,
) -> None:
    me = await guest(client, locale="en", timezone="Asia/Tokyo")

    assert me["locale"] == "en"
    assert me["timezone"] == "Asia/Tokyo"


async def test_a_timezone_must_be_an_iana_name(client: AsyncClient) -> None:
    response = await client.post(
        f"{API}/auth/guest", json={"timezone": "Mars/Olympus_Mons"}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


async def test_the_token_is_an_httponly_secure_lax_cookie(
    client: AsyncClient,
) -> None:
    response = await client.post(f"{API}/auth/guest", json={})

    cookie = _set_cookie(response)
    assert cookie["httponly"] is True
    assert cookie["secure"] is True
    assert cookie["samesite"] == "lax"
    assert cookie["path"] == "/"
    assert int(cookie["max-age"]) == 90 * 24 * 3600
    # 256 random bits, and the body does not repeat them.
    assert len(cookie.value) >= 43
    assert cookie.value not in response.text


async def test_only_the_hash_of_the_token_is_stored(
    client: AsyncClient, session: AsyncSession
) -> None:
    await guest(client)
    token = client.cookies[COOKIE]

    stored = await session.scalar(select(AuthSession))

    assert stored is not None
    assert stored.token_hash == hashlib.sha256(token.encode()).hexdigest()
    assert stored.token_hash != token


async def test_asking_for_a_guest_twice_makes_one_guest(
    client: AsyncClient, session: AsyncSession
) -> None:
    first = await guest(client)
    second = await guest(client)

    assert second["id"] == first["id"]
    assert await session.scalar(select(func.count()).select_from(User)) == 1


async def test_without_a_token_the_user_routes_answer_401(
    client: AsyncClient,
) -> None:
    for path in ("/me", "/me/stats", "/me/activity", "/subjects"):
        response = await client.get(f"{API}{path}")
        assert response.status_code == 401, path
        assert response.json() == {
            "error": {"code": "unauthenticated", "message": "Sign in first."}
        }


async def test_a_token_that_is_not_a_session_is_a_401(
    client: AsyncClient,
) -> None:
    client.cookies.set(COOKIE, "not-a-token")

    response = await client.get(f"{API}/me")

    assert response.status_code == 401


async def test_the_token_also_works_as_a_bearer_header(
    client: AsyncClient, other_client: AsyncClient
) -> None:
    me = await guest(client)
    token = client.cookies[COOKIE]

    response = await other_client.get(
        f"{API}/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == me["id"]


async def test_a_session_expires_after_its_lifetime(
    client: AsyncClient, clock: Clock
) -> None:
    await guest(client)
    clock.advance(days=91)

    response = await client.get(f"{API}/me")

    assert response.status_code == 401


async def test_a_session_in_use_is_renewed_past_half_of_its_lifetime(
    client: AsyncClient, session: AsyncSession, clock: Clock
) -> None:
    await guest(client)
    clock.advance(days=30)
    early = await client.get(f"{API}/me")
    clock.advance(days=30)  # day 60: less than half of 90 is left
    renewed = await client.get(f"{API}/me")
    clock.advance(days=80)  # day 140: past the first expiry
    later = await client.get(f"{API}/me")

    assert "set-cookie" not in early.headers
    assert _set_cookie(renewed).value == client.cookies[COOKIE]
    assert later.status_code == 200
    stored = await session.scalar(select(AuthSession))
    assert stored is not None
    await session.refresh(stored)
    assert stored.expires_at > clock.now


async def test_logout_ends_the_session(
    client: AsyncClient, session: AsyncSession
) -> None:
    await guest(client)
    token = client.cookies[COOKIE]

    response = await client.post(f"{API}/auth/logout")
    client.cookies.set(COOKIE, token)  # the browser kept it anyway
    after = await client.get(f"{API}/me")

    assert response.status_code == 204
    assert _set_cookie(response).value == ""
    assert after.status_code == 401
    assert await session.scalar(select(AuthSession)) is None


# ---- CSRF and CORS ----


async def test_state_changing_routes_require_the_csrf_header(
    app: FastAPI, session: AsyncSession
) -> None:
    await publish_bank(session)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="https://test"
    ) as browser:
        # Become a guest properly, then drop the header, as a form on
        # another site would.
        await browser.post(f"{API}/auth/guest", json={}, headers=CSRF_HEADERS)
        refused = [
            await browser.post(f"{API}/auth/guest", json={}),
            await browser.post(f"{API}/auth/logout"),
            await browser.post(
                f"{API}/auth/magic-link", json={"email": CAROL}
            ),
            await browser.post(
                f"{API}/auth/magic-link/verify", json={"token": "x"}
            ),
            await browser.patch(f"{API}/me/settings", json={"theme": "dark"}),
            await browser.delete(f"{API}/me"),
            await browser.post(
                f"{API}/sessions", json={"subject": "estruturas-de-dados"}
            ),
            await browser.post(f"{API}/sessions/{uuid.uuid4()}/answers"),
            await browser.post(f"{API}/sessions/{uuid.uuid4()}/finish"),
            await browser.post(f"{API}/questions/{uuid.uuid4()}/report"),
            await browser.post(f"{API}/events", json={"events": []}),
        ]
        read = await browser.get(f"{API}/me")

    for response in refused:
        assert response.status_code == 403, response.request.url
        assert response.json()["error"]["code"] == "csrf_header_missing"
    assert read.status_code == 200
    # Nothing happened: the guest is still there and signed in.
    assert await session.scalar(select(func.count()).select_from(User)) == 1


async def test_cors_allows_the_origins_in_settings_and_no_other(
    client: AsyncClient,
) -> None:
    ours = await client.get(
        f"{API}/config", headers={"Origin": "http://localhost:5173"}
    )
    theirs = await client.get(
        f"{API}/config", headers={"Origin": "https://evil.example"}
    )
    preflight = await client.options(
        f"{API}/sessions",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    allowed = ours.headers["access-control-allow-origin"]
    assert allowed == "http://localhost:5173"
    assert allowed in Settings().cors_origins
    assert ours.headers["access-control-allow-credentials"] == "true"
    assert "access-control-allow-origin" not in theirs.headers
    assert preflight.status_code == 400
    assert "access-control-allow-origin" not in preflight.headers


# ---- email links ----


async def test_a_magic_link_is_emailed_and_only_its_hash_is_stored(
    client: AsyncClient, session: AsyncSession, outbox: Outbox, clock: Clock
) -> None:
    response = await client.post(
        f"{API}/auth/magic-link", json={"email": " Carol@Example.com "}
    )

    assert response.status_code == 202
    (email,) = outbox.emails
    assert email.to == CAROL
    assert email.subject == "Seu link pra entrar no CaramelCase"
    assert "http://localhost:5173/auth/callback?token=" in email.text
    assert "15 minutos" in email.text
    link = await session.scalar(select(MagicLink))
    assert link is not None
    assert link.email == CAROL
    token = outbox.token()
    assert link.token_hash == hashlib.sha256(token.encode()).hexdigest()
    assert link.used_at is None
    assert (link.expires_at - clock.now).total_seconds() == 15 * 60


async def test_the_email_is_in_the_language_of_whoever_asks(
    client: AsyncClient, outbox: Outbox
) -> None:
    await guest(client, locale="en")

    await client.post(f"{API}/auth/magic-link", json={"email": CAROL})

    assert outbox.emails[0].subject == "Your CaramelCase sign-in link"
    assert "15 minutes" in outbox.emails[0].text


async def test_something_that_is_not_an_address_is_refused(
    client: AsyncClient, outbox: Outbox
) -> None:
    response = await client.post(
        f"{API}/auth/magic-link", json={"email": "carol"}
    )

    assert response.status_code == 422
    assert outbox.emails == []


async def test_a_magic_link_signs_in_and_upgrades_the_guest(
    client: AsyncClient, session: AsyncSession, outbox: Outbox
) -> None:
    await publish_bank(session)
    me = await guest(client)
    guest_token = client.cookies[COOKIE]
    await play(client, session, wrong=2)

    account = await _sign_in_by_email(client, outbox)

    # The same user, now with an address, and with everything it did.
    assert account["id"] == me["id"]
    assert account["is_guest"] is False
    assert account["email"] == CAROL
    stats = (await client.get(f"{API}/me/stats")).json()
    assert stats["sessions_finished"] == 1
    assert stats["questions_answered"] == 10
    assert stats["correct_answers"] == 8
    assert stats["streak"]["current"] == 1
    identity = await session.scalar(select(AuthIdentity))
    assert identity is not None
    assert identity.provider == "email"
    assert identity.provider_subject == CAROL
    assert identity.user_id == uuid.UUID(me["id"])
    # Signing in changed the token: the guest's no longer works.
    assert client.cookies[COOKIE] != guest_token
    client.cookies.set(COOKIE, guest_token)
    assert (await client.get(f"{API}/me")).status_code == 401


async def test_a_magic_link_works_once(
    client: AsyncClient, other_client: AsyncClient, outbox: Outbox
) -> None:
    await _sign_in_by_email(client, outbox)

    again = await other_client.post(
        f"{API}/auth/magic-link/verify", json={"token": outbox.token()}
    )

    assert again.status_code == 400
    assert again.json()["error"]["code"] == "invalid_magic_link"
    assert COOKIE not in other_client.cookies


async def test_a_magic_link_expires_after_15_minutes(
    client: AsyncClient, outbox: Outbox, clock: Clock
) -> None:
    await client.post(f"{API}/auth/magic-link", json={"email": CAROL})
    late = outbox.token()
    clock.advance(minutes=15)
    expired = await client.post(
        f"{API}/auth/magic-link/verify", json={"token": late}
    )

    await client.post(f"{API}/auth/magic-link", json={"email": CAROL})
    in_time = outbox.token()
    clock.advance(minutes=14, seconds=59)
    accepted = await client.post(
        f"{API}/auth/magic-link/verify", json={"token": in_time}
    )

    assert expired.status_code == 400
    assert expired.json()["error"]["code"] == "invalid_magic_link"
    assert accepted.status_code == 200
    assert accepted.json()["email"] == CAROL


async def test_a_token_nobody_was_sent_is_refused(client: AsyncClient) -> None:
    response = await client.post(
        f"{API}/auth/magic-link/verify", json={"token": "made-up"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_magic_link"


async def test_a_link_opened_without_a_guest_creates_the_account(
    client: AsyncClient, outbox: Outbox
) -> None:
    account = await _sign_in_by_email(client, outbox)

    assert account["is_guest"] is False
    assert account["email"] == CAROL
    assert account["settings"]["daily_goal"] == 20


async def test_signing_in_again_returns_the_same_account(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    outbox: Outbox,
) -> None:
    first = await _sign_in_by_email(client, outbox)
    second = await _sign_in_by_email(other_client, outbox)

    assert second["id"] == first["id"]
    assert await session.scalar(select(func.count()).select_from(User)) == 1
    identities = await session.scalar(
        select(func.count()).select_from(AuthIdentity)
    )
    assert identities == 1
    # Both browsers stay signed in.
    assert (await client.get(f"{API}/me")).status_code == 200


# ---- merging a guest into an existing account ----


async def test_a_guest_is_merged_into_the_account_that_has_the_email(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    outbox: Outbox,
    clock: Clock,
) -> None:
    await publish_bank(session, per_topic=10)
    # Carol has an account with one session, played yesterday at home.
    await guest(client)
    await play(client, session, wrong=1)
    account = await _sign_in_by_email(client, outbox)
    home = (await client.get(f"{API}/me/stats")).json()
    clock.advance(days=1)

    # Today, on another computer, she plays as a guest and signs in.
    visitor = await guest(other_client, locale="en")
    await other_client.patch(
        f"{API}/me/settings", json={"university": "UFRN", "daily_goal": 10}
    )
    await play(other_client, session, wrong=4)
    lab = (await other_client.get(f"{API}/me/stats")).json()
    merged = await _sign_in_by_email(other_client, outbox)

    assert merged["id"] == account["id"] != visitor["id"]
    assert merged["is_guest"] is False
    # The account keeps its own preferences; the guest fills what is empty.
    assert merged["locale"] == "pt-BR"
    assert merged["settings"]["daily_goal"] == 20
    assert merged["university"] == "UFRN"
    stats = (await other_client.get(f"{API}/me/stats")).json()
    assert stats["sessions_finished"] == 2
    assert stats["questions_answered"] == 20
    assert stats["correct_answers"] == 9 + 6
    assert stats["level"]["total_xp"] == (
        home["level"]["total_xp"] + lab["level"]["total_xp"]
    )
    # Yesterday at home, today at the lab: a streak of two days.
    assert stats["streak"]["current"] == 2
    assert stats["streak"]["longest"] == 2
    assert stats["subjects"][0]["answers_count"] == 20
    days = (await other_client.get(f"{API}/me/activity")).json()["days"]
    assert [day["questions"] for day in days] == [10, 10]
    # The guest is gone, and its answers belong to the account.
    assert await session.get(User, uuid.UUID(visitor["id"])) is None
    owners = set(await session.scalars(select(Attempt.user_id)))
    assert owners == {uuid.UUID(account["id"])}
    # The first computer is still signed in to the same account.
    assert (await client.get(f"{API}/me/stats")).json() == stats


async def test_merging_two_histories_of_one_day_adds_them_up(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    outbox: Outbox,
) -> None:
    await publish_bank(session, per_topic=10)
    await guest(client)
    await play(client, session)
    await _sign_in_by_email(client, outbox)
    await guest(other_client)
    await play(other_client, session)

    await _sign_in_by_email(other_client, outbox)

    stats = (await client.get(f"{API}/me/stats")).json()
    days = (await client.get(f"{API}/me/activity")).json()["days"]
    assert len(days) == 1
    assert days[0]["questions"] == 20
    assert days[0]["sessions_finished"] == 2
    assert days[0]["goal_met"] is True
    assert days[0]["xp"] == stats["level"]["total_xp"]
    assert stats["streak"]["current"] == 1
    assert stats["goal"]["met"] is True


# ---- Google ----


async def _google_round_trip(client: AsyncClient) -> httpx.Response:
    """Go to "Google" and come back. The mock provider's consent screen
    is our own callback.
    """
    started = await client.get(f"{API}/auth/google/start")
    assert started.status_code == 307
    callback = urlsplit(started.headers["location"])
    assert callback.path == f"{API}/auth/google/callback"
    return await client.get(f"{callback.path}?{callback.query}")


async def test_google_sign_in_upgrades_the_guest_and_takes_the_name(
    client: AsyncClient, session: AsyncSession
) -> None:
    await publish_bank(session)
    me = await guest(client)
    await play(client, session)

    returned = await _google_round_trip(client)

    assert returned.status_code == 307
    assert returned.headers["location"] == (
        "http://localhost:5173/auth/callback"
    )
    account = (await client.get(f"{API}/me")).json()
    assert account["id"] == me["id"]
    assert account["is_guest"] is False
    assert account["email"] == "demo@example.com"
    assert account["display_name"] == "Carol Demo"
    stats = (await client.get(f"{API}/me/stats")).json()
    assert stats["sessions_finished"] == 1
    identity = await session.scalar(select(AuthIdentity))
    assert identity is not None
    assert identity.provider == "google"
    assert identity.provider_subject == "mock:demo@example.com"


async def test_google_and_an_email_link_reach_the_same_account(
    client: AsyncClient,
    other_client: AsyncClient,
    session: AsyncSession,
    outbox: Outbox,
) -> None:
    by_email = await _sign_in_by_email(client, outbox, "demo@example.com")

    await _google_round_trip(other_client)

    by_google = (await other_client.get(f"{API}/me")).json()
    assert by_google["id"] == by_email["id"]
    providers = set(await session.scalars(select(AuthIdentity.provider)))
    assert providers == {"email", "google"}


async def test_a_callback_with_a_state_this_browser_did_not_start_is_refused(
    client: AsyncClient, other_client: AsyncClient
) -> None:
    started = await client.get(f"{API}/auth/google/start")
    callback = urlsplit(started.headers["location"])
    state = parse_qs(callback.query)["state"][0]

    # Another browser is sent to the callback with the first one's state.
    forged = await other_client.get(
        f"{callback.path}?code=mock-code&state={state}"
    )
    no_state = await client.get(f"{callback.path}?code=mock-code")
    odd_state = await client.get(f"{callback.path}?code=mock-code&state=ação")

    for response in (forged, no_state, odd_state):
        assert response.status_code == 307
        assert response.headers["location"].endswith(
            "/auth/callback?error=google_sign_in_failed"
        )
    assert COOKIE not in other_client.cookies
    assert COOKIE not in client.cookies


async def test_the_state_cookie_is_httponly_and_only_for_the_google_routes(
    client: AsyncClient,
) -> None:
    started = await client.get(f"{API}/auth/google/start")

    cookie = _set_cookie(started, "cc_oauth_state")
    assert cookie["httponly"] is True
    assert cookie["secure"] is True
    assert cookie["samesite"] == "lax"
    assert cookie["path"] == "/api/v1/auth/google"
    assert int(cookie["max-age"]) == 600


class _Google:
    """A provider that returns whatever profile the test gives it."""

    def __init__(self, profile: GoogleProfile | None) -> None:
        self.profile = profile

    def authorization_url(self, state: str, redirect_uri: str) -> str:
        return f"{redirect_uri}?code=any&state={state}"

    async def fetch_profile(
        self,
        code: str,  # noqa: ARG002
        redirect_uri: str,  # noqa: ARG002
    ) -> GoogleProfile:
        if self.profile is None:
            raise GoogleError("the code was refused")
        return self.profile


@pytest.mark.parametrize(
    ("profile", "error"),
    [
        (None, "google_sign_in_failed"),
        (
            GoogleProfile("1", "carol@example.com", False, "Carol"),
            "google_email_not_verified",
        ),
    ],
)
async def test_a_failed_google_sign_in_goes_back_to_the_app_with_an_error(
    client: AsyncClient,
    app: FastAPI,
    session: AsyncSession,
    profile: GoogleProfile | None,
    error: str,
) -> None:
    app.dependency_overrides[get_google_provider] = lambda: _Google(profile)

    returned = await _google_round_trip(client)

    assert returned.headers["location"] == (
        f"http://localhost:5173/auth/callback?error={error}"
    )
    assert COOKIE not in client.cookies
    assert await session.scalar(select(User)) is None


async def test_without_a_provider_the_google_routes_do_not_exist(
    client: AsyncClient, app: FastAPI
) -> None:
    app.dependency_overrides[get_google_provider] = lambda: None

    for path in ("/auth/google/start", "/auth/google/callback?code=x"):
        response = await client.get(f"{API}{path}")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"


def test_production_has_no_mock_provider() -> None:
    production = Settings(environment="production")
    with_keys = Settings(
        environment="production",
        google_client_id="id",
        google_client_secret="secret",
    )

    assert google_provider_for(production) is None
    assert isinstance(google_provider_for(with_keys), GoogleOAuthProvider)
    assert google_provider_for(Settings()) is not None


# ---- the real provider, with a transport that answers as Google ----


def _google_api(userinfo: dict[str, Any], token_status: int = 200) -> Any:
    seen: list[httpx.Request] = []

    def answer(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if str(request.url) == TOKEN_URL:
            return httpx.Response(
                token_status,
                json={"access_token": "at-1", "token_type": "Bearer"},
            )
        assert str(request.url) == USERINFO_URL
        assert request.headers["authorization"] == "Bearer at-1"
        return httpx.Response(200, json=userinfo)

    return httpx.MockTransport(answer), seen


def test_the_google_address_carries_the_client_the_state_and_the_scope() -> (
    None
):
    provider = GoogleOAuthProvider("client-1", "secret-1")

    url = urlsplit(provider.authorization_url("state-1", "https://cc/cb"))

    query = {key: value[0] for key, value in parse_qs(url.query).items()}
    assert f"{url.scheme}://{url.netloc}{url.path}" == AUTHORIZE_URL
    assert query == {
        "response_type": "code",
        "client_id": "client-1",
        "redirect_uri": "https://cc/cb",
        "scope": "openid email profile",
        "state": "state-1",
    }


async def test_the_code_is_exchanged_for_the_students_profile() -> None:
    transport, seen = _google_api(
        {
            "sub": "108",
            "email": "carol@example.com",
            "email_verified": True,
            "name": "Carol Nunes",
        }
    )
    provider = GoogleOAuthProvider("client-1", "secret-1", transport)

    profile = await provider.fetch_profile("code-1", "https://cc/cb")

    assert profile == GoogleProfile(
        "108", "carol@example.com", True, "Carol Nunes"
    )
    form = parse_qs(seen[0].content.decode())
    assert form["code"] == ["code-1"]
    assert form["grant_type"] == ["authorization_code"]
    assert form["redirect_uri"] == ["https://cc/cb"]


async def test_a_refused_code_is_a_google_error() -> None:
    transport, _ = _google_api({}, token_status=400)
    provider = GoogleOAuthProvider("client-1", "secret-1", transport)

    with pytest.raises(GoogleError):
        await provider.fetch_profile("bad-code", "https://cc/cb")
