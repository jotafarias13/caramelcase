"""Rating, on the spec's numbers: start at 1000, priors 700 to 1300,
K 32 then 16 for a student, 16 then 4 for a question.
"""

import pytest

from app.domain.rating import (
    predicted_success,
    question_k,
    question_starting_rating,
    rate_answer,
    unrated_answer,
    user_k,
)
from app.settings import Settings

SETTINGS = Settings()


def test_equal_ratings_predict_62_5_percent() -> None:
    # E is 0.5, and P = 0.25 + 0.75 * 0.5.
    assert predicted_success(1000, 1000, SETTINGS) == pytest.approx(0.625)


def test_400_points_apart_is_ten_to_one() -> None:
    # E = 1 / 11 against a harder question, 10 / 11 against an easier one.
    harder = predicted_success(1000, 1400, SETTINGS)
    easier = predicted_success(1400, 1000, SETTINGS)

    assert harder == pytest.approx(0.25 + 0.75 / 11)
    assert easier == pytest.approx(0.25 + 0.75 * 10 / 11)


def test_a_hopeless_question_is_still_a_one_in_four_guess() -> None:
    assert predicted_success(0, 4000, SETTINGS) == pytest.approx(0.25)


def test_a_student_has_k_32_for_the_first_30_answers_then_16() -> None:
    assert user_k(0, SETTINGS) == 32
    assert user_k(29, SETTINGS) == 32
    assert user_k(30, SETTINGS) == 16


def test_a_question_has_k_16_for_its_first_50_answers_then_4() -> None:
    assert question_k(0, SETTINGS) == 16
    assert question_k(49, SETTINGS) == 16
    assert question_k(50, SETTINGS) == 4


def test_levels_1_to_5_start_at_700_to_1300() -> None:
    ratings = [question_starting_rating(n, SETTINGS) for n in range(1, 6)]

    assert ratings == [700, 850, 1000, 1150, 1300]


def test_a_correct_answer_raises_the_student_and_lowers_the_question() -> None:
    change = rate_answer(
        user_rating=1000,
        user_answers=0,
        question_rating=1000,
        question_answers=0,
        is_correct=True,
        settings=SETTINGS,
    )

    # S - P = 1 - 0.625 = 0.375; times 32 and times 16.
    assert change.user_before == 1000
    assert change.user_after == pytest.approx(1012)
    assert change.user_delta == pytest.approx(12)
    assert change.question_before == 1000
    assert change.question_after == pytest.approx(994)


def test_a_wrong_answer_lowers_the_student_and_raises_the_question() -> None:
    change = rate_answer(
        user_rating=1000,
        user_answers=0,
        question_rating=1000,
        question_answers=0,
        is_correct=False,
        settings=SETTINGS,
    )

    # S - P = -0.625.
    assert change.user_after == pytest.approx(980)
    assert change.question_after == pytest.approx(1010)


def test_the_later_k_factors_move_the_ratings_less() -> None:
    change = rate_answer(
        user_rating=1000,
        user_answers=30,
        question_rating=1000,
        question_answers=50,
        is_correct=True,
        settings=SETTINGS,
    )

    assert change.user_after == pytest.approx(1006)
    assert change.question_after == pytest.approx(998.5)


def test_every_number_comes_from_settings() -> None:
    settings = Settings(
        rating_guess_chance=0.5,
        rating_scale=200,
        user_k_early=10,
        question_k_early=20,
    )

    change = rate_answer(
        user_rating=1000,
        user_answers=0,
        question_rating=1200,
        question_answers=0,
        is_correct=True,
        settings=settings,
    )

    # E = 1 / 11, P = 0.5 + 0.5 / 11, S - P = 5 / 11.
    assert change.user_after == pytest.approx(1000 + 10 * 5 / 11)
    assert change.question_after == pytest.approx(1200 - 20 * 5 / 11)


def test_an_unrated_answer_moves_nothing() -> None:
    change = unrated_answer(1040.5, 870.25)

    assert change.user_after == change.user_before == 1040.5
    assert change.question_after == change.question_before == 870.25
    assert change.user_delta == 0
