"""Question selection, on the spec's numbers: target 80%, the 30 closest,
10 drawn, at most 3 per topic, 14 days, levels 2 and 3 in a first session.
"""

import random
import uuid
from collections import Counter

from app.domain.selection import (
    Candidate,
    select_questions,
    shuffled_option_keys,
)
from app.settings import Settings

SETTINGS = Settings()
TOPICS = [uuid.uuid4() for _ in range(8)]


def _candidate(
    number: int,
    *,
    rating: float = 850,
    prior: int = 2,
    recent: bool = False,
    topic: uuid.UUID | None = None,
) -> Candidate:
    return Candidate(
        question_id=uuid.uuid4(),
        topic_id=topic or TOPICS[number % len(TOPICS)],
        rating=rating,
        difficulty_prior=prior,
        answered_recently=recent,
    )


def _select(
    candidates: list[Candidate],
    *,
    user_rating: float = 1000,
    first_session: bool = False,
    seed: int = 1,
    settings: Settings = SETTINGS,
) -> list[uuid.UUID]:
    return select_questions(
        candidates,
        user_rating=user_rating,
        first_session=first_session,
        settings=settings,
        rng=random.Random(seed),
    )


def test_a_session_has_10_different_questions() -> None:
    candidates = [_candidate(n) for n in range(100)]

    chosen = _select(candidates)

    assert len(chosen) == 10
    assert len(set(chosen)) == 10
    assert set(chosen) <= {c.question_id for c in candidates}


def test_the_questions_come_from_the_30_closest_to_80_percent() -> None:
    # For a student at 1000, a question at 830 is predicted at about 80%.
    close = [_candidate(n, rating=830) for n in range(30)]
    far = [_candidate(n, rating=1300) for n in range(100)]

    chosen = _select(far + close)

    assert set(chosen) <= {c.question_id for c in close}


def test_the_draw_among_the_closest_is_random() -> None:
    candidates = [_candidate(n) for n in range(30)]

    sessions = {tuple(_select(candidates, seed=seed)) for seed in range(20)}

    assert len(sessions) > 1


def test_at_most_3_questions_come_from_one_topic() -> None:
    crowded = TOPICS[0]
    candidates = [_candidate(n, topic=crowded) for n in range(25)]
    candidates += [_candidate(n) for n in range(40)]

    for seed in range(20):
        chosen = set(_select(candidates, seed=seed))
        topics = Counter(
            c.topic_id for c in candidates if c.question_id in chosen
        )
        assert max(topics.values()) <= 3


def test_the_topic_limit_reaches_past_the_30_closest_before_it_bends() -> None:
    crowded = TOPICS[0]
    close = [_candidate(n, rating=830, topic=crowded) for n in range(30)]
    far = [_candidate(n, rating=1300) for n in range(1, 8)]

    chosen = set(_select(close + far))

    assert len(chosen) == 10
    from_crowded = [c for c in close if c.question_id in chosen]
    assert len(from_crowded) == 3
    assert {c.question_id for c in far} <= chosen


def test_one_topic_alone_still_fills_the_session() -> None:
    only = TOPICS[0]
    candidates = [_candidate(n, topic=only) for n in range(12)]

    assert len(_select(candidates)) == 10


def test_questions_answered_in_the_last_14_days_are_left_out() -> None:
    fresh = [_candidate(n) for n in range(10)]
    recent = [_candidate(n, rating=830, recent=True) for n in range(50)]

    chosen = _select(fresh + recent)

    assert set(chosen) == {c.question_id for c in fresh}


def test_recent_questions_come_back_when_too_few_remain() -> None:
    fresh = [_candidate(n) for n in range(4)]
    recent = [_candidate(n, recent=True) for n in range(20)]

    chosen = _select(fresh + recent)

    assert len(chosen) == 10


def test_a_first_session_uses_levels_2_and_3_only() -> None:
    easy = [_candidate(n, rating=700, prior=1) for n in range(40)]
    calibrating = [_candidate(n, rating=850, prior=2) for n in range(10)]
    calibrating += [_candidate(n, rating=1000, prior=3) for n in range(10)]
    hard = [_candidate(n, rating=1150, prior=4) for n in range(40)]
    candidates = easy + calibrating + hard

    chosen = _select(candidates, first_session=True)

    assert set(chosen) <= {c.question_id for c in calibrating}


def test_a_first_session_takes_other_levels_when_2_and_3_are_too_few() -> None:
    calibrating = [_candidate(n, prior=3) for n in range(4)]
    others = [_candidate(n, prior=5) for n in range(20)]

    chosen = _select(calibrating + others, first_session=True)

    assert len(chosen) == 10


def test_a_small_bank_gives_a_short_session() -> None:
    candidates = [_candidate(n) for n in range(6)]

    assert len(_select(candidates)) == 6
    assert _select([]) == []


def test_the_numbers_come_from_settings() -> None:
    settings = Settings(session_length=4, selection_max_per_topic=1)
    candidates = [_candidate(n) for n in range(40)]

    chosen = set(_select(candidates, settings=settings))

    topics = [c.topic_id for c in candidates if c.question_id in chosen]
    assert len(chosen) == 4
    assert len(set(topics)) == 4


def test_option_order_is_shuffled_but_stable_within_a_session() -> None:
    keys = ["a", "b", "c", "d"]
    session_id, question_id = uuid.uuid4(), uuid.uuid4()

    first = shuffled_option_keys(keys, session_id, question_id)
    again = shuffled_option_keys(keys, session_id, question_id)
    orders = {
        tuple(shuffled_option_keys(keys, uuid.uuid4(), question_id))
        for _ in range(30)
    }

    assert first == again
    assert sorted(first) == keys
    assert keys == ["a", "b", "c", "d"]  # the input is left alone
    assert len(orders) > 1
