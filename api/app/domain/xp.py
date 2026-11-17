"""XP and levels.

XP is a score of its own: the daily goal counts questions, not XP.
"""

from dataclasses import dataclass

from app.settings import Settings


@dataclass(frozen=True)
class LevelProgress:
    level: int  # starts at 1
    xp_in_level: int
    xp_per_level: int


def xp_for_answer(
    *,
    is_correct: bool,
    question_rating: float,
    user_rating: float,
    settings: Settings,
) -> int:
    """XP for one answer: a wrong one earns nothing, and a correct one
    earns more when the question was rated above the student. Both
    ratings are the ones from before the answer.
    """
    if not is_correct:
        return 0
    if question_rating > user_rating:
        return settings.xp_correct + settings.xp_harder_question_bonus
    return settings.xp_correct


def xp_for_finishing(settings: Settings) -> int:
    """XP for finishing a session."""
    return settings.xp_session_finished


def level_progress(total_xp: int, settings: Settings) -> LevelProgress:
    """The level a student with total_xp is on, and how far into it."""
    return LevelProgress(
        level=total_xp // settings.xp_per_level + 1,
        xp_in_level=total_xp % settings.xp_per_level,
        xp_per_level=settings.xp_per_level,
    )
