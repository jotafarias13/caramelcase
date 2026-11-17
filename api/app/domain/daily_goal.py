"""The daily goal: questions answered in one day of the student's own
calendar, against 10, 20 or 30.
"""

from dataclasses import dataclass

from app.settings import Settings


@dataclass(frozen=True)
class GoalProgress:
    goal: int
    questions: int
    remaining: int
    met: bool


def is_goal_option(goal: int, settings: Settings) -> bool:
    return goal in settings.daily_goal_options


def goal_progress(questions_today: int, goal: int) -> GoalProgress:
    return GoalProgress(
        goal=goal,
        questions=questions_today,
        remaining=max(goal - questions_today, 0),
        met=questions_today >= goal,
    )
