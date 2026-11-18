"""Auth and account: who the user is, and their preferences."""

import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, Field, StringConstraints

from app.domain.local_time import is_timezone
from app.enums import Locale, Theme, UserRole


def _lower(value: str) -> str:
    return value.lower()


def _timezone(value: str) -> str:
    if not is_timezone(value):
        raise ValueError("not an IANA timezone name")
    return value


# An address is checked by sending a link to it, not by its form.
EmailAddress = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=320,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
    AfterValidator(_lower),
]
Timezone = Annotated[
    str, StringConstraints(max_length=64), AfterValidator(_timezone)
]
ShortText = Annotated[
    str, StringConstraints(strip_whitespace=True, max_length=120)
]
DisplayName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)
]


class GuestRequest(BaseModel):
    """What the browser knows about a first-time visitor."""

    locale: Locale | None = None
    timezone: Timezone | None = None


class MagicLinkRequest(BaseModel):
    email: EmailAddress
    # The language of the email. Defaults to the signed-in guest's.
    locale: Locale | None = None


class MagicLinkVerifyRequest(BaseModel):
    token: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    # The device's language and timezone, for an account this sign-in
    # creates. A guest who signs in keeps their own.
    locale: Locale | None = None
    timezone: Timezone | None = None


class SettingsModel(BaseModel):
    daily_goal: int
    theme: Theme
    show_option_reasons: bool
    daily_reminder: bool
    weekly_email: bool


class MeResponse(BaseModel):
    id: uuid.UUID
    email: str | None
    display_name: str | None
    locale: Locale
    timezone: str
    is_guest: bool
    role: UserRole
    university: str | None
    course: str | None
    # The slug of the subject Home shows.
    current_subject: str | None
    settings: SettingsModel


class SettingsPatch(BaseModel):
    """Every field is optional: only the ones sent are changed.

    Sending null clears display_name, university or course. For the
    other fields null is the same as not sending them.
    """

    # On the user.
    locale: Locale | None = None
    timezone: Timezone | None = None
    display_name: DisplayName | None = None
    university: ShortText | None = None
    course: ShortText | None = None
    current_subject: str | None = Field(
        default=None, description="A published subject's slug."
    )
    # On the user's settings.
    daily_goal: int | None = Field(default=None, description="10, 20 or 30.")
    theme: Theme | None = None
    show_option_reasons: bool | None = None
    daily_reminder: bool | None = None
    weekly_email: bool | None = None


class ExportResponse(BaseModel):
    """Everything stored about the user, table by table."""

    exported_at: datetime
    user: dict[str, Any]
    # Table name -> the user's rows in it.
    tables: dict[str, list[dict[str, Any]]]
