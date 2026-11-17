"""The review schedule of a question the student got wrong.

A wrong answer makes the question due the next day. Each correct review
moves it one step along settings.review_intervals_days (1, 3, 7, 18, 45
days); a wrong review sends it back to the first step. A correct review
at the last step takes it out of the queue.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.settings import Settings


@dataclass(frozen=True)
class ReviewSchedule:
    interval_days: int
    due_at: datetime


def first_review(now: datetime, settings: Settings) -> ReviewSchedule:
    """The schedule after a wrong answer, in practice or in a review."""
    interval = settings.review_intervals_days[0]
    return ReviewSchedule(interval, now + timedelta(days=interval))


def after_correct_review(
    interval_days: int, now: datetime, settings: Settings
) -> ReviewSchedule | None:
    """The schedule after a correct review of an item that waited
    interval_days. None means the item leaves the queue.
    """
    longer = [d for d in settings.review_intervals_days if d > interval_days]
    if not longer:
        return None
    return ReviewSchedule(longer[0], now + timedelta(days=longer[0]))
