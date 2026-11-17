"""Rating: how a student's and a question's rating move after an answer.

    E = 1 / (1 + 10 ** ((Rq - Ru) / 400))      P = 0.25 + 0.75 * E
    Ru' = Ru + Ku * (S - P)                    Rq' = Rq - Kq * (S - P)

S is 1 for a correct answer and 0 otherwise. P is the chance of a correct
answer, counting the one-in-four chance of guessing it.
"""

from dataclasses import dataclass

from app.settings import Settings


@dataclass(frozen=True)
class RatingChange:
    user_before: float
    user_after: float
    question_before: float
    question_after: float

    @property
    def user_delta(self) -> float:
        return self.user_after - self.user_before


def predicted_success(
    user_rating: float, question_rating: float, settings: Settings
) -> float:
    """P: the chance that this student answers this question correctly."""
    exponent = (question_rating - user_rating) / settings.rating_scale
    expected = 1 / (1 + 10**exponent)
    guess = settings.rating_guess_chance
    return guess + (1 - guess) * expected


def user_k(answers_count: int, settings: Settings) -> float:
    """K for a student who has answers_count rated answers in the subject."""
    if answers_count < settings.user_k_early_answers:
        return settings.user_k_early
    return settings.user_k


def question_k(answers_count: int, settings: Settings) -> float:
    """K for a question that has answers_count rated answers."""
    if answers_count < settings.question_k_early_answers:
        return settings.question_k_early
    return settings.question_k


def question_starting_rating(
    difficulty_prior: int, settings: Settings
) -> float:
    """The rating of a question nobody has answered, by its level 1 to 5."""
    return settings.question_rating_by_prior[difficulty_prior - 1]


def rate_answer(  # noqa: PLR0913  the two ratings, their counts, the answer
    *,
    user_rating: float,
    user_answers: int,
    question_rating: float,
    question_answers: int,
    is_correct: bool,
    settings: Settings,
) -> RatingChange:
    """Both ratings after a student's first attempt at a question."""
    predicted = predicted_success(user_rating, question_rating, settings)
    surprise = (1.0 if is_correct else 0.0) - predicted
    return RatingChange(
        user_before=user_rating,
        user_after=user_rating + user_k(user_answers, settings) * surprise,
        question_before=question_rating,
        question_after=question_rating
        - question_k(question_answers, settings) * surprise,
    )


def unrated_answer(user_rating: float, question_rating: float) -> RatingChange:
    """An answer that moves no rating: not the student's first attempt."""
    return RatingChange(
        user_before=user_rating,
        user_after=user_rating,
        question_before=question_rating,
        question_after=question_rating,
    )
