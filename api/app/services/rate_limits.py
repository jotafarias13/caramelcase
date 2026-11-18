"""Counting requests for the rate limits, in this process's memory.

Each API process counts on its own. Under gunicorn with several workers a
caller can therefore make up to the number of workers times a limit, and
a restart starts every count again. That is enough to stop a script that
hammers a route; nginx's limit on every request per address is the outer
layer (milestone 8). If that ever proves too loose, the counts can move
to a Postgres table without changing the routes.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.rate_limit import window_start
from app.settings import RateLimit


@dataclass
class _Window:
    start: datetime
    counts: defaultdict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )


class RateLimiter:
    """Counts each caller's requests under each rule, in the current
    window only.

    Every caller of a rule shares the rule's windows, so when a new window
    starts the counts of the last one are all dropped at once: the memory
    held is the callers of the current window, never more.
    """

    def __init__(self) -> None:
        self._windows: dict[str, _Window] = {}

    def count(
        self, rule: str, caller: str, limit: RateLimit, now: datetime
    ) -> int:
        """Count one request of `caller` under `rule`. Returns how many
        requests the caller has made in the current window, this one
        included.
        """
        start = window_start(now, limit.seconds)
        window = self._windows.get(rule)
        if window is None or window.start != start:
            window = _Window(start)
            self._windows[rule] = window
        window.counts[caller] += 1
        return window.counts[caller]


_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """The process's limiter. A dependency, so a test can use its own."""
    return _limiter
