"""A student's own calendar: which day an instant falls on for them.

The daily goal, the streak and the profile calendar all count days in the
student's timezone, so 23:30 on Monday in São Paulo is Monday, although
it is already Tuesday in UTC.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def is_timezone(name: str) -> bool:
    """Is name an IANA timezone such as "America/Sao_Paulo"?"""
    try:
        ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        return False
    return True


def local_date(instant: datetime, timezone: str) -> date:
    """The calendar day of an instant in a timezone.

    The instant must carry its own offset, as every timestamp in the
    database does.
    """
    if instant.tzinfo is None:
        raise ValueError("the instant has no timezone")
    return instant.astimezone(ZoneInfo(timezone)).date()
