"""An email sender for the tests: it keeps what was sent."""

import re

from app.providers.email import Email


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
