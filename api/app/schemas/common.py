"""Shapes that more than one area of the API returns."""

from pydantic import BaseModel

from app.domain.daily_goal import GoalProgress
from app.domain.streak import StreakStatus, StreakToday
from app.domain.xp import LevelProgress


class SubjectRef(BaseModel):
    """Enough of a subject to name it and link to it."""

    slug: str
    name_pt: str
    name_en: str
    # The label on the subject's badge: "ed" is shown as "ed/".
    short_pt: str
    short_en: str


class TopicRef(BaseModel):
    slug: str
    name_pt: str
    name_en: str


class StreakModel(BaseModel):
    status: StreakStatus
    current: int
    longest: int
    # The length of the streak that ended, when status is "lost".
    lost_length: int | None

    @classmethod
    def of(cls, streak: StreakToday) -> "StreakModel":
        return cls(
            status=streak.status,
            current=streak.current,
            longest=streak.longest,
            lost_length=streak.lost_length,
        )


class GoalModel(BaseModel):
    """Questions answered today against the daily goal."""

    goal: int
    questions: int
    remaining: int
    met: bool

    @classmethod
    def of(cls, progress: GoalProgress) -> "GoalModel":
        return cls(
            goal=progress.goal,
            questions=progress.questions,
            remaining=progress.remaining,
            met=progress.met,
        )


class LevelModel(BaseModel):
    total_xp: int
    level: int
    xp_in_level: int
    xp_per_level: int

    @classmethod
    def of(cls, total_xp: int, progress: LevelProgress) -> "LevelModel":
        return cls(
            total_xp=total_xp,
            level=progress.level,
            xp_in_level=progress.xp_in_level,
            xp_per_level=progress.xp_per_level,
        )


class RatingChangeModel(BaseModel):
    """A student's rating in a subject before and after something."""

    subject: SubjectRef
    before: float
    after: float
    delta: float
