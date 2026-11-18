"""Rate limits: how many requests one caller may make in a span of time.

Time is cut into fixed windows of `limit.seconds`, counted from the Unix
epoch, so the windows of every caller start at the same instants. A
caller may make `limit.requests` requests in a window; the ones after
that are refused until the window ends, and the next window starts from
zero.
"""

import math
from datetime import UTC, datetime, timedelta

from app.settings import RateLimit

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def window_start(now: datetime, seconds: int) -> datetime:
    """The start of the window of `seconds` that `now` falls in."""
    length = timedelta(seconds=seconds)
    return _EPOCH + ((now - _EPOCH) // length) * length


def is_over_limit(count: int, limit: RateLimit) -> bool:
    """Whether the request numbered `count` in its window is refused."""
    return count > limit.requests


def retry_after_seconds(now: datetime, limit: RateLimit) -> int:
    """Whole seconds until the window of `now` ends, at least one: the
    Retry-After of a refused request.
    """
    end = window_start(now, limit.seconds) + timedelta(seconds=limit.seconds)
    return max(1, math.ceil((end - now).total_seconds()))
