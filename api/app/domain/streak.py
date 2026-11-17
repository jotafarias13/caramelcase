"""The streak: days in a row with at least one finished session.

Days are the student's own (see local_time.local_date). The stored streak
is only rewritten when a session is finished, so a streak that ran out
keeps its old length in the database until then; what the student sees
comes from streak_today.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum


class StreakStatus(StrEnum):
    NONE = "none"  # never finished a session
    ACTIVE = "active"  # finished a session today
    AT_RISK = "at_risk"  # yesterday yes, today not yet
    LOST = "lost"  # missed a whole day


@dataclass(frozen=True)
class StreakState:
    """The streaks row: the numbers as of last_active_date."""

    current: int = 0
    longest: int = 0
    last_active_date: date | None = None


@dataclass(frozen=True)
class StreakToday:
    """The streak as the student sees it today."""

    status: StreakStatus
    current: int  # 0 when lost or never started
    longest: int
    # The length of the streak that ended, when status is lost.
    lost_length: int | None


def streak_after_session(state: StreakState, today: date) -> StreakState:
    """The streak after a session is finished today."""
    last = state.last_active_date
    if last is not None and last >= today:
        # A second session today, or a day the student already has from
        # a timezone further east: nothing changes.
        return state
    yesterday = today - timedelta(days=1)
    current = state.current + 1 if last == yesterday else 1
    return StreakState(
        current=current,
        longest=max(state.longest, current),
        last_active_date=today,
    )


def streak_today(state: StreakState, today: date) -> StreakToday:
    """What the stored streak means today."""
    last = state.last_active_date
    if last is None or state.current == 0:
        status, current, lost = StreakStatus.NONE, 0, None
    elif last >= today:
        status, current, lost = StreakStatus.ACTIVE, state.current, None
    elif last == today - timedelta(days=1):
        status, current, lost = StreakStatus.AT_RISK, state.current, None
    else:
        status, current, lost = StreakStatus.LOST, 0, state.current
    return StreakToday(
        status=status,
        current=current,
        longest=state.longest,
        lost_length=lost,
    )


def streak_from_days(active_days: Iterable[date]) -> StreakState:
    """Rebuild the streak from every day with a finished session.

    Used when two histories are merged into one account.
    """
    state = StreakState()
    for day in sorted(set(active_days)):
        state = streak_after_session(state, day)
    return state
