"""Question selection: which questions a practice session gets, and the
order a question's options are shown in.

The session aims at a predicted success of about 80%:

1. Leave out the questions the student answered in the last days, unless
   too few remain.
2. In the student's first session in a subject, keep levels 2 and 3 only,
   unless too few remain.
3. Keep the 30 questions whose predicted success is closest to the target.
4. Draw 10 of them at random, at most 3 from any one topic.

When the 30 cannot fill the session under the topic limit, the next
closest questions are used, and after them the limit is dropped: a short
bank gives a full session before it gives a balanced one.
"""

import random
import uuid
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from app.domain.rating import predicted_success
from app.settings import Settings


@dataclass(frozen=True)
class Candidate:
    """A question the student could get: published, in the session's
    subject, with text in the student's language.
    """

    question_id: uuid.UUID
    topic_id: uuid.UUID
    rating: float
    difficulty_prior: int
    answered_recently: bool


def select_questions(
    candidates: Sequence[Candidate],
    *,
    user_rating: float,
    first_session: bool,
    settings: Settings,
    rng: random.Random,
) -> list[uuid.UUID]:
    """The ids of a session's questions, in the order they are served.

    Fewer than settings.session_length only when there are fewer
    candidates.
    """
    length = settings.session_length
    pool = _enough_of(
        [c for c in candidates if not c.answered_recently], candidates, length
    )
    if first_session:
        levels = settings.first_session_prior_levels
        calibrating = [c for c in pool if c.difficulty_prior in levels]
        pool = _enough_of(calibrating, pool, length)

    # Shuffled first, and the sort keeps that order among equals: fresh
    # questions share five ratings, so most of a bank is tied.
    shuffled = list(pool)
    rng.shuffle(shuffled)
    by_closeness = sorted(
        shuffled,
        key=lambda c: abs(
            predicted_success(user_rating, c.rating, settings)
            - settings.selection_target_success
        ),
    )
    closest = by_closeness[: settings.selection_pool_size]
    rest = by_closeness[settings.selection_pool_size :]
    rng.shuffle(closest)

    chosen: list[Candidate] = []
    per_topic: Counter[uuid.UUID] = Counter()
    for candidate in closest + rest:
        if len(chosen) == length:
            break
        if per_topic[candidate.topic_id] < settings.selection_max_per_topic:
            chosen.append(candidate)
            per_topic[candidate.topic_id] += 1

    if len(chosen) < length:
        taken = {c.question_id for c in chosen}
        spare = [c for c in closest + rest if c.question_id not in taken]
        chosen += spare[: length - len(chosen)]
    return [c.question_id for c in chosen]


def _enough_of(
    preferred: Sequence[Candidate], everything: Sequence[Candidate], need: int
) -> Sequence[Candidate]:
    """The preferred candidates when they fill a session, else all."""
    return preferred if len(preferred) >= need else everything


def shuffled_option_keys(
    keys: Sequence[str], session_id: uuid.UUID, question_id: uuid.UUID
) -> list[str]:
    """The order a question's options are shown in, in one session.

    Shuffled, but the same every time the session is loaded, so that a
    resumed session looks as it did. The keys themselves never change.
    """
    order = list(keys)
    random.Random(f"{session_id}:{question_id}").shuffle(order)
    return order
