"""The streak, and the student's own calendar across timezones."""

from datetime import UTC, date, datetime, timedelta

import pytest

from app.domain.local_time import is_timezone, local_date
from app.domain.streak import (
    StreakState,
    StreakStatus,
    streak_after_session,
    streak_from_days,
    streak_today,
)

SAO_PAULO = "America/Sao_Paulo"  # UTC-3
TOKYO = "Asia/Tokyo"  # UTC+9
MONDAY = date(2026, 11, 16)


def _days(start: date, count: int) -> list[date]:
    return [start + timedelta(days=n) for n in range(count)]


# ---- the student's own calendar ----


def test_late_evening_in_sao_paulo_is_still_the_same_day() -> None:
    # 23:30 on Monday in São Paulo is 02:30 on Tuesday in UTC.
    instant = datetime(2026, 11, 17, 2, 30, tzinfo=UTC)

    assert local_date(instant, SAO_PAULO) == MONDAY
    assert local_date(instant, "UTC") == date(2026, 11, 17)
    assert local_date(instant, TOKYO) == date(2026, 11, 17)


def test_one_instant_is_two_days_apart_across_the_date_line() -> None:
    instant = datetime(2026, 11, 16, 11, 0, tzinfo=UTC)

    assert local_date(instant, "Pacific/Kiritimati") == date(2026, 11, 17)
    assert local_date(instant, "Pacific/Pago_Pago") == date(2026, 11, 16)
    assert local_date(instant, "Etc/GMT+12") == date(2026, 11, 15)


def test_an_instant_without_a_timezone_is_refused() -> None:
    with pytest.raises(ValueError, match="no timezone"):
        local_date(datetime(2026, 11, 16, 12, 0), SAO_PAULO)


def test_timezone_names() -> None:
    assert is_timezone(SAO_PAULO)
    assert is_timezone("UTC")
    assert not is_timezone("Mars/Olympus_Mons")
    assert not is_timezone("")
    assert not is_timezone("../etc/passwd")


# ---- finishing a session ----


def test_the_first_session_starts_a_streak_of_1() -> None:
    state = streak_after_session(StreakState(), MONDAY)

    assert state == StreakState(1, 1, MONDAY)


def test_a_session_on_the_next_day_extends_the_streak() -> None:
    state = StreakState(6, 9, MONDAY)

    after = streak_after_session(state, MONDAY + timedelta(days=1))

    assert after.current == 7
    assert after.longest == 9
    assert after.last_active_date == MONDAY + timedelta(days=1)


def test_a_second_session_on_the_same_day_changes_nothing() -> None:
    state = StreakState(6, 9, MONDAY)

    assert streak_after_session(state, MONDAY) == state


def test_a_missed_day_starts_over_and_keeps_the_longest() -> None:
    state = StreakState(6, 9, MONDAY)

    after = streak_after_session(state, MONDAY + timedelta(days=2))

    assert after == StreakState(1, 9, MONDAY + timedelta(days=2))


def test_the_longest_streak_grows_with_the_current_one() -> None:
    state = StreakState(9, 9, MONDAY)

    after = streak_after_session(state, MONDAY + timedelta(days=1))

    assert after.longest == 10


def test_a_day_before_the_last_active_day_changes_nothing() -> None:
    # The student flew west: their calendar went back a day.
    state = StreakState(3, 3, MONDAY)

    assert streak_after_session(state, MONDAY - timedelta(days=1)) == state


# ---- streaks across timezones ----


def _streak_of(instants: list[datetime], timezone: str) -> StreakState:
    state = StreakState()
    for instant in instants:
        state = streak_after_session(state, local_date(instant, timezone))
    return state


def test_two_sessions_20_hours_apart_can_be_one_day_or_two() -> None:
    sessions = [
        datetime(2026, 11, 16, 4, 0, tzinfo=UTC),
        datetime(2026, 11, 17, 0, 0, tzinfo=UTC),
    ]

    # São Paulo: 01:00 and 21:00 of the same Monday.
    assert _streak_of(sessions, SAO_PAULO).current == 1
    # Tokyo: 13:00 on Monday and 09:00 on Tuesday.
    assert _streak_of(sessions, TOKYO).current == 2


def test_two_sessions_28_hours_apart_can_skip_a_day() -> None:
    sessions = [
        datetime(2026, 11, 16, 2, 0, tzinfo=UTC),
        datetime(2026, 11, 17, 6, 0, tzinfo=UTC),
    ]

    # São Paulo: 23:00 on Sunday and 03:00 on Tuesday. Monday is missed.
    assert _streak_of(sessions, SAO_PAULO).current == 1
    # UTC: Monday and Tuesday.
    assert _streak_of(sessions, "UTC").current == 2


def test_a_week_of_late_evenings_in_sao_paulo_is_a_streak_of_7() -> None:
    # 23:30 local every evening: every one of them is the next day in UTC.
    first = datetime(2026, 11, 10, 2, 30, tzinfo=UTC)
    sessions = [first + timedelta(days=n) for n in range(7)]

    state = _streak_of(sessions, SAO_PAULO)

    assert state.current == 7
    assert state.last_active_date == date(2026, 11, 15)


def test_the_streak_survives_the_day_a_dst_change_makes_shorter() -> None:
    # New York leaves daylight saving time on 2026-11-01.
    sessions = [
        datetime(2026, 11, 1, 3, 30, tzinfo=UTC),  # 23:30 on Oct 31, EDT
        datetime(2026, 11, 2, 4, 30, tzinfo=UTC),  # 23:30 on Nov 1, EST
        datetime(2026, 11, 3, 4, 30, tzinfo=UTC),  # 23:30 on Nov 2, EST
    ]

    assert _streak_of(sessions, "America/New_York").current == 3


# ---- what the student sees today ----


def test_no_streak_before_the_first_session() -> None:
    today = streak_today(StreakState(), MONDAY)

    assert today.status is StreakStatus.NONE
    assert today.current == 0
    assert today.lost_length is None


def test_active_on_a_day_with_a_session() -> None:
    today = streak_today(StreakState(7, 12, MONDAY), MONDAY)

    assert today.status is StreakStatus.ACTIVE
    assert today.current == 7
    assert today.longest == 12


def test_at_risk_the_day_after_until_a_session_is_finished() -> None:
    today = streak_today(
        StreakState(7, 12, MONDAY), MONDAY + timedelta(days=1)
    )

    assert today.status is StreakStatus.AT_RISK
    assert today.current == 7


def test_lost_after_a_whole_day_without_a_session() -> None:
    today = streak_today(
        StreakState(7, 12, MONDAY), MONDAY + timedelta(days=2)
    )

    assert today.status is StreakStatus.LOST
    assert today.current == 0
    assert today.lost_length == 7
    assert today.longest == 12


def test_at_risk_or_lost_depends_on_the_students_timezone() -> None:
    state = StreakState(7, 7, MONDAY)
    # Wednesday 01:00 UTC is still Tuesday evening in São Paulo.
    instant = datetime(2026, 11, 18, 1, 0, tzinfo=UTC)

    in_sao_paulo = streak_today(state, local_date(instant, SAO_PAULO))
    in_tokyo = streak_today(state, local_date(instant, TOKYO))

    assert in_sao_paulo.status is StreakStatus.AT_RISK
    assert in_tokyo.status is StreakStatus.LOST


# ---- rebuilding from the days ----


def test_rebuilding_from_days_finds_the_current_and_longest_runs() -> None:
    days = _days(date(2026, 11, 1), 5) + _days(date(2026, 11, 10), 3)

    state = streak_from_days(days)

    assert state == StreakState(3, 5, date(2026, 11, 12))


def test_rebuilding_ignores_order_and_repeated_days() -> None:
    days = [MONDAY, MONDAY - timedelta(days=1), MONDAY]

    assert streak_from_days(days) == StreakState(2, 2, MONDAY)
    assert streak_from_days([]) == StreakState()
