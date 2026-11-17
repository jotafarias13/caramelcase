"""XP, levels, the daily goal and topic mastery, on the spec's numbers."""

import pytest

from app.domain.daily_goal import goal_progress, is_goal_option
from app.domain.mastery import MasteryLevel, accuracy, mastery_level
from app.domain.xp import level_progress, xp_for_answer, xp_for_finishing
from app.settings import Settings

SETTINGS = Settings()

# ---- XP ----


def test_a_correct_answer_earns_10_xp() -> None:
    xp = xp_for_answer(
        is_correct=True,
        question_rating=900,
        user_rating=1000,
        settings=SETTINGS,
    )

    assert xp == 10


def test_a_question_rated_above_the_student_earns_5_more() -> None:
    xp = xp_for_answer(
        is_correct=True,
        question_rating=1001,
        user_rating=1000,
        settings=SETTINGS,
    )

    assert xp == 15


def test_equal_ratings_earn_no_bonus() -> None:
    xp = xp_for_answer(
        is_correct=True,
        question_rating=1000,
        user_rating=1000,
        settings=SETTINGS,
    )

    assert xp == 10


def test_a_wrong_answer_earns_nothing_even_on_a_hard_question() -> None:
    xp = xp_for_answer(
        is_correct=False,
        question_rating=1300,
        user_rating=1000,
        settings=SETTINGS,
    )

    assert xp == 0


def test_finishing_a_session_earns_10_xp() -> None:
    assert xp_for_finishing(SETTINGS) == 10


def test_xp_numbers_come_from_settings() -> None:
    settings = Settings(
        xp_correct=3, xp_harder_question_bonus=2, xp_session_finished=7
    )

    xp = xp_for_answer(
        is_correct=True,
        question_rating=1100,
        user_rating=1000,
        settings=settings,
    )

    assert xp == 5
    assert xp_for_finishing(settings) == 7


# ---- levels ----


@pytest.mark.parametrize(
    ("total_xp", "level", "xp_in_level"),
    [(0, 1, 0), (499, 1, 499), (500, 2, 0), (1820, 4, 320)],
)
def test_a_level_is_500_xp(
    total_xp: int, level: int, xp_in_level: int
) -> None:
    progress = level_progress(total_xp, SETTINGS)

    assert progress.level == level
    assert progress.xp_in_level == xp_in_level
    assert progress.xp_per_level == 500


# ---- daily goal ----


def test_the_goal_is_10_20_or_30_questions() -> None:
    assert [is_goal_option(n, SETTINGS) for n in (10, 20, 30)] == [True] * 3
    assert not is_goal_option(15, SETTINGS)
    assert not is_goal_option(0, SETTINGS)


def test_goal_progress_counts_questions_left() -> None:
    progress = goal_progress(12, 20)

    assert progress.questions == 12
    assert progress.goal == 20
    assert progress.remaining == 8
    assert not progress.met


def test_the_goal_is_met_at_the_goal_and_beyond() -> None:
    assert goal_progress(20, 20).met
    assert goal_progress(20, 20).remaining == 0
    assert goal_progress(34, 20).met
    assert goal_progress(34, 20).remaining == 0


# ---- topic mastery ----


@pytest.mark.parametrize(
    ("correct", "total", "level"),
    [
        (0, 0, MasteryLevel.NEW),
        (4, 4, MasteryLevel.NEW),  # under 5 answers, whatever the share
        (2, 5, MasteryLevel.LEARNING),  # 40%
        (59, 100, MasteryLevel.LEARNING),
        (3, 5, MasteryLevel.PRACTICED),  # 60%
        (84, 100, MasteryLevel.PRACTICED),
        (9, 9, MasteryLevel.PRACTICED),  # 100%, but under 10 answers
        (17, 20, MasteryLevel.MASTERED),  # 85%
        (10, 10, MasteryLevel.MASTERED),
    ],
)
def test_mastery_levels(correct: int, total: int, level: MasteryLevel) -> None:
    assert mastery_level(correct, total, SETTINGS) is level


def test_accuracy_is_zero_without_answers() -> None:
    assert accuracy(0, 0) == 0
    assert accuracy(3, 4) == 0.75
