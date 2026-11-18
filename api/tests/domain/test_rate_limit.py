"""Rate limits: fixed windows, the limit, Retry-After, and the counter."""

from datetime import UTC, datetime, timedelta

from app.domain.rate_limit import (
    is_over_limit,
    retry_after_seconds,
    window_start,
)
from app.services.rate_limits import RateLimiter
from app.settings import RateLimit

NOW = datetime(2026, 11, 16, 15, 0, 25, tzinfo=UTC)
PER_MINUTE = RateLimit(requests=3, seconds=60)


def test_windows_start_on_whole_multiples_of_their_length() -> None:
    assert window_start(NOW, 60) == datetime(2026, 11, 16, 15, 0, tzinfo=UTC)
    assert window_start(NOW, 600) == datetime(2026, 11, 16, 15, 0, tzinfo=UTC)
    assert window_start(NOW, 3600) == datetime(2026, 11, 16, 15, 0, tzinfo=UTC)
    later = NOW + timedelta(minutes=17)
    assert window_start(later, 600) == datetime(
        2026, 11, 16, 15, 10, tzinfo=UTC
    )


def test_a_window_holds_its_start_and_not_its_end() -> None:
    start = datetime(2026, 11, 16, 15, 1, tzinfo=UTC)

    assert window_start(start, 60) == start
    assert window_start(start - timedelta(microseconds=1), 60) == (
        start - timedelta(minutes=1)
    )


def test_the_requests_up_to_the_limit_pass_and_the_next_is_refused() -> None:
    assert [is_over_limit(n, PER_MINUTE) for n in (1, 2, 3, 4, 5)] == [
        False,
        False,
        False,
        True,
        True,
    ]


def test_retry_after_is_the_rest_of_the_window_rounded_up() -> None:
    assert retry_after_seconds(NOW, PER_MINUTE) == 35
    almost_over = NOW + timedelta(seconds=34, milliseconds=500)
    assert retry_after_seconds(almost_over, PER_MINUTE) == 1


def test_retry_after_is_never_zero() -> None:
    start = datetime(2026, 11, 16, 15, 1, tzinfo=UTC)

    assert retry_after_seconds(start, PER_MINUTE) == 60
    last_instant = start - timedelta(microseconds=1)
    assert retry_after_seconds(last_instant, PER_MINUTE) == 1


# ---- the counter ----


def test_the_counter_counts_each_caller_apart() -> None:
    limiter = RateLimiter()

    counts = [limiter.count("answers", "ana", PER_MINUTE, NOW) for _ in "abc"]
    other = limiter.count("answers", "bia", PER_MINUTE, NOW)

    assert counts == [1, 2, 3]
    assert other == 1


def test_the_counter_counts_each_rule_apart() -> None:
    limiter = RateLimiter()
    limiter.count("answers", "ana", PER_MINUTE, NOW)

    assert limiter.count("reports", "ana", PER_MINUTE, NOW) == 1
    assert limiter.count("answers", "ana", PER_MINUTE, NOW) == 2


def test_a_new_window_starts_every_count_from_zero() -> None:
    limiter = RateLimiter()
    for _ in range(5):
        limiter.count("answers", "ana", PER_MINUTE, NOW)
    limiter.count("answers", "bia", PER_MINUTE, NOW)
    next_window = NOW + timedelta(seconds=35)

    assert limiter.count("answers", "ana", PER_MINUTE, next_window) == 1
    assert limiter.count("answers", "bia", PER_MINUTE, next_window) == 1


def test_the_end_of_a_window_is_still_that_window() -> None:
    limiter = RateLimiter()
    limiter.count("answers", "ana", PER_MINUTE, NOW)
    last_instant = NOW + timedelta(seconds=34, microseconds=999_999)

    assert limiter.count("answers", "ana", PER_MINUTE, last_instant) == 2
