"""Every environment value and every tunable number of the API.

Nothing else in the code reads the environment or hardcodes a business
number. Each field can be overridden by an environment variable with the
same name in upper case, for example SESSION_LENGTH=5.

The defaults of the tunables come from docs/initial-spec.md ("Core logic"
and "Monetization structure") and, for lives and leagues, from
design/README.md ("Decisions made by the designer").
"""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # ---- environment ----
    environment: Literal["local", "test", "production"] = "local"
    database_url: str = (
        "postgresql+asyncpg://caramel:caramel@localhost:5432/caramelcase"
    )
    # Comma-separated in the environment: "https://a.com,https://b.com".
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    log_level: str = "INFO"
    # JSON lines for production; false gives readable lines for development.
    log_json: bool = True

    # ---- auth ----
    session_token_bytes: int = 32  # 256-bit opaque session tokens
    magic_link_expire_minutes: int = 15

    # ---- practice sessions and question selection ----
    session_length: int = 10
    selection_target_success: float = 0.80
    selection_pool_size: int = 30  # closest candidates kept before sampling
    selection_max_per_topic: int = 3
    selection_recent_days: int = 14  # skip questions answered this recently
    selection_review_slots: int = 3  # due review items per practice session
    first_session_prior_levels: tuple[int, ...] = (2, 3)

    # ---- rating ----
    rating_guess_chance: float = 0.25  # one in four options
    rating_scale: float = 400.0
    user_rating_start: float = 1000.0
    # Starting rating of a question, by difficulty_prior 1 to 5.
    question_rating_by_prior: tuple[float, float, float, float, float] = (
        700.0,
        850.0,
        1000.0,
        1150.0,
        1300.0,
    )
    user_k_early: float = 32.0
    user_k_early_answers: int = 30  # answers in a subject that use the early K
    user_k: float = 16.0
    question_k_early: float = 16.0
    question_k_early_answers: int = 50
    question_k: float = 4.0

    # ---- XP, levels, daily goal ----
    xp_correct: int = 10
    xp_harder_question_bonus: int = 5  # question rated above the student
    xp_session_finished: int = 10
    xp_per_level: int = 500
    daily_goal_options: tuple[int, ...] = (10, 20, 30)  # questions a day

    # ---- topic mastery ----
    mastery_new_below_answers: int = 5
    mastery_learning_below: float = 0.60
    mastery_mastered_from: float = 0.85
    mastery_mastered_min_answers: int = 10

    # ---- review schedule ----
    # Days until the next review after each correct review in a row. A wrong
    # review goes back to the first step; a correct one at the last step
    # takes the item out of the queue.
    review_intervals_days: tuple[int, ...] = (1, 3, 7, 18, 45)

    # ---- streak freeze and repair (V2, V3) ----
    streak_freeze_goal_days: int = 7  # days in a row meeting the goal
    streak_freeze_max_held: int = 2
    streak_repair_hours: int = 48

    # ---- lives (V2) ----
    lives_max: int = 3
    lives_refill_minutes: int = 30

    # ---- leagues (V2) ----
    league_size: int = 10
    league_promoted: int = 3
    league_relegated: int = 3
    league_tiers: tuple[str, ...] = ("bit", "byte", "kilobyte")

    # ---- reminders (V2) ----
    push_max_per_day: int = 1

    # ---- ads (V3) ----
    ad_break_every_sessions: int = 2
    ad_double_win_extra_sessions: int = 2
    ad_double_loss_sessions_sooner: int = 1

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_comma_separated(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
