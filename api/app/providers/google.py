"""Google sign-in: an interface, the real provider (authorization-code
flow, through Authlib) and a mock for development.

The mock skips Google: its "consent screen" is our own callback, and the
profile it returns is the demo user's. It exists only outside production.
"""

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlencode

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.settings import Settings, get_settings

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
SCOPE = "openid email profile"


@dataclass(frozen=True)
class GoogleProfile:
    subject: str  # Google's stable id of the account
    email: str
    email_verified: bool
    name: str | None


class GoogleError(Exception):
    """Google refused the code or did not answer as expected."""


class GoogleProvider(Protocol):
    def authorization_url(self, state: str, redirect_uri: str) -> str:
        """Where to send the student to sign in."""
        ...

    async def fetch_profile(
        self, code: str, redirect_uri: str
    ) -> GoogleProfile:
        """Exchange the code Google sent back for the student's profile."""
        ...


class GoogleOAuthProvider:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        # Tests pass a transport that answers in Google's place.
        self._transport = transport

    def _client(self, redirect_uri: str) -> AsyncOAuth2Client:
        return AsyncOAuth2Client(
            client_id=self._client_id,
            client_secret=self._client_secret,
            scope=SCOPE,
            redirect_uri=redirect_uri,
            transport=self._transport,
        )

    def authorization_url(self, state: str, redirect_uri: str) -> str:
        url, _ = self._client(redirect_uri).create_authorization_url(
            AUTHORIZE_URL, state=state
        )
        return str(url)

    async def fetch_profile(
        self, code: str, redirect_uri: str
    ) -> GoogleProfile:
        try:
            async with self._client(redirect_uri) as client:
                await client.fetch_token(
                    TOKEN_URL, code=code, grant_type="authorization_code"
                )
                response = await client.get(USERINFO_URL)
                response.raise_for_status()
                data = response.json()
            return GoogleProfile(
                subject=str(data["sub"]),
                email=str(data["email"]),
                email_verified=bool(data.get("email_verified", False)),
                name=data.get("name"),
            )
        except Exception as error:
            raise GoogleError(str(error)) from error


class MockGoogleProvider:
    """Signs in as one fixed account, without leaving the app."""

    CODE = "mock-code"

    def __init__(self, email: str, name: str) -> None:
        self._email = email
        self._name = name

    def authorization_url(self, state: str, redirect_uri: str) -> str:
        query = urlencode({"code": self.CODE, "state": state})
        return f"{redirect_uri}?{query}"

    async def fetch_profile(
        self,
        code: str,
        redirect_uri: str,  # noqa: ARG002
    ) -> GoogleProfile:
        if code != self.CODE:
            raise GoogleError("not the mock provider's code")
        return GoogleProfile(
            subject=f"mock:{self._email}",
            email=self._email,
            email_verified=True,
            name=self._name,
        )


def google_provider_for(settings: Settings) -> GoogleProvider | None:
    """The provider the settings ask for; None when there is none."""
    if settings.google_client_id and settings.google_client_secret:
        return GoogleOAuthProvider(
            settings.google_client_id, settings.google_client_secret
        )
    if settings.environment == "production":
        return None
    return MockGoogleProvider(
        settings.mock_google_email, settings.mock_google_name
    )


def get_google_provider() -> GoogleProvider | None:
    """A FastAPI dependency."""
    return google_provider_for(get_settings())
