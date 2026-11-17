"""Topic mastery, from a student's correct and total answers in a topic.

- new: fewer than 5 answers
- learning: under 60% correct
- practiced: 60% or more
- mastered: 85% or more, with at least 10 answers
"""

from enum import StrEnum

from app.settings import Settings


class MasteryLevel(StrEnum):
    NEW = "new"
    LEARNING = "learning"
    PRACTICED = "practiced"
    MASTERED = "mastered"


def accuracy(correct: int, total: int) -> float:
    """The share of correct answers, 0 to 1; 0 with no answers."""
    return correct / total if total else 0.0


def mastery_level(
    correct: int, total: int, settings: Settings
) -> MasteryLevel:
    if total < settings.mastery_new_below_answers:
        return MasteryLevel.NEW
    share = accuracy(correct, total)
    if share < settings.mastery_learning_below:
        return MasteryLevel.LEARNING
    enough = total >= settings.mastery_mastered_min_answers
    if share >= settings.mastery_mastered_from and enough:
        return MasteryLevel.MASTERED
    return MasteryLevel.PRACTICED
