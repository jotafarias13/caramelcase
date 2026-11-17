"""Sending email: an interface, a console sender for development and an
SMTP sender for production.
"""

import asyncio
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

from loguru import logger

from app.settings import Settings, get_settings


@dataclass(frozen=True)
class Email:
    to: str
    subject: str
    text: str


class EmailSender(Protocol):
    async def send(self, email: Email) -> None: ...


class ConsoleEmailSender:
    """Writes the email to the log instead of sending it."""

    async def send(self, email: Email) -> None:
        logger.info(
            "email not sent, no SMTP server is set:\n"
            f"To: {email.to}\nSubject: {email.subject}\n\n{email.text}"
        )


class SmtpEmailSender:
    """Sends through an SMTP server with STARTTLS."""

    def __init__(self, settings: Settings) -> None:
        assert settings.smtp_host is not None
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_username
        self._password = settings.smtp_password
        self._sender = settings.email_from

    async def send(self, email: Email) -> None:
        message = EmailMessage()
        message["From"] = self._sender
        message["To"] = email.to
        message["Subject"] = email.subject
        message.set_content(email.text)
        # smtplib blocks, so it runs in a thread.
        await asyncio.to_thread(self._send_blocking, message)

    def _send_blocking(self, message: EmailMessage) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=10) as server:
            server.starttls()
            if self._username and self._password:
                server.login(self._username, self._password)
            server.send_message(message)


def get_email_sender() -> EmailSender:
    """The sender the settings ask for. A FastAPI dependency."""
    settings = get_settings()
    if settings.smtp_host:
        return SmtpEmailSender(settings)
    return ConsoleEmailSender()
