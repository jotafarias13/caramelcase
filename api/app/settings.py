"""Every environment value and every tunable number of the API.

Nothing else in the code reads the environment or hardcodes a business
number. Each field can be overridden by an environment variable with the
same name in upper case, for example SESSION_LENGTH=5.

The defaults of the tunables come from docs/initial-spec.md ("Core logic"
and "Monetization structure") and, for lives and leagues, from
design/README.md ("Decisions made by the designer").
"""

from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from app.enums import PlanKey

# The repository's content/ directory, when the API runs from a checkout.
_REPO_CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


class PlanLimits(BaseModel):
    """What a plan allows. Stored in plans.limits."""

    sessions_per_day: int | None  # None means no limit
    ads: bool
    tutor_messages_per_day: int
    exam_mode: bool
    exam_tracks: bool


class PlanDefinition(BaseModel):
    """A plan as seeding writes it to the plans table."""

    key: PlanKey
    price_month_brl: Decimal
    # None until the price of the yearly and of the semester pass is set.
    price_year_brl: Decimal | None = None
    price_semester_brl: Decimal | None = None
    limits: PlanLimits


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
    # Where catalog.yaml and the question bank are read from.
    content_dir: Path = _REPO_CONTENT_DIR

    # The web app's public address: the start of the links in emails and
    # of the address Google sends the student back to. The API is reached
    # under it, at /api.
    app_base_url: str = "http://localhost:5173"

    # ---- auth ----
    session_token_bytes: int = 32  # 256-bit opaque session tokens
    magic_link_expire_minutes: int = 15
    # A session ends this long after its last renewal. It is renewed, and
    # the cookie sent again, once less than half of the time is left, so
    # a student who keeps coming back is never signed out.
    session_lifetime_days: int = 90
    session_cookie_name: str = "cc_session"
    # False only for local development over plain http.
    session_cookie_secure: bool = True
    # State-changing requests must carry this header, with any value.
    # A browser does not send it across sites.
    csrf_header_name: str = "X-Requested-With"
    # Google sign-in. Without both values the mock provider is used, which
    # signs in as mock_google_email; in production there is no mock and
    # the Google routes answer 404.
    google_client_id: str | None = None
    google_client_secret: str | None = None
    mock_google_email: str = "demo@example.com"
    mock_google_name: str = "Carol Demo"
    # Minutes the student has to come back from Google's consent screen.
    oauth_state_expire_minutes: int = 10

    # ---- email ----
    # Without smtp_host, emails are written to the log instead of sent.
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    email_from: str = "CaramelCase <no-reply@localhost>"

    # ---- new users ----
    default_timezone: str = "America/Sao_Paulo"
    daily_goal_default: int = 20  # one of daily_goal_options

    # ---- demo user (make seed, local only) ----
    demo_user_email: str = "demo@example.com"
    demo_user_name: str = "Carol Demo"
    demo_history_days: int = 21

    # ---- limits on what a client may send ----
    report_comment_max_chars: int = 1000
    events_max_batch: int = 50
    event_props_max_bytes: int = 2000
    # Days of activity GET /me/activity returns at most.
    activity_max_days: int = 366

    # ---- question format (content/bank) ----
    # The limits a line of the question bank must respect. The reason and
    # code-line limits are the spec's; the others keep a question on one
    # phone screen.
    question_stem_max_chars: int = 400
    question_option_max_chars: int = 140
    question_reason_max_chars: int = 160
    question_explanation_max_chars: int = 500
    question_code_max_lines: int = 15
    question_code_max_line_chars: int = 80

    # ---- content pipeline (content/tools) ----
    # Seconds one compile or one run of a question's code may take.
    code_run_timeout_seconds: float = 10.0
    # Bytes of output a question's code may print before it is stopped.
    code_run_max_output_bytes: int = 100_000
    # How many times a question's code runs. Every run must print the same
    # thing. Run number n gives Python the hash seed n, so the order of a
    # set of strings changes between runs, the same way on every machine.
    code_run_count: int = 5
    code_run_c_compiler: str = "cc"
    # A warning fails the compile. The sanitizers stop a C snippet that
    # reads out of bounds, uses freed memory or overflows, instead of
    # letting it print an arbitrary value.
    code_run_c_flags: tuple[str, ...] = (
        "-std=c11",
        "-Wall",
        "-Werror",
        "-fsanitize=address,undefined",
        "-fno-sanitize-recover=all",
    )
    # Two questions of a subject are near-duplicates when their stems are
    # at least this similar (0 to 1) and, if they have code, so is the
    # code, against its own number. Code has the higher bar because short
    # programs share their frame (include and main, CREATE TABLE): in the
    # pilot, unrelated C programs were as similar as 0.88.
    dedupe_similarity: float = 0.85
    dedupe_code_similarity: float = 0.92

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

    # ---- plans (V3) ----
    # Seeding copies these to the plans table. The prices are set; the
    # limits are placeholders until the owner decides them.
    plans: tuple[PlanDefinition, ...] = (
        PlanDefinition(
            key=PlanKey.FREE,
            price_month_brl=Decimal(0),
            limits=PlanLimits(
                sessions_per_day=3,
                ads=True,
                tutor_messages_per_day=0,
                exam_mode=False,
                exam_tracks=False,
            ),
        ),
        PlanDefinition(
            key=PlanKey.PLUS,
            price_month_brl=Decimal(15),
            limits=PlanLimits(
                sessions_per_day=None,
                ads=False,
                tutor_messages_per_day=0,
                exam_mode=True,
                exam_tracks=False,
            ),
        ),
        PlanDefinition(
            key=PlanKey.PRO,
            price_month_brl=Decimal(40),
            limits=PlanLimits(
                sessions_per_day=None,
                ads=False,
                tutor_messages_per_day=30,
                exam_mode=True,
                exam_tracks=False,
            ),
        ),
        PlanDefinition(
            key=PlanKey.MAX,
            price_month_brl=Decimal(100),
            limits=PlanLimits(
                sessions_per_day=None,
                ads=False,
                tutor_messages_per_day=200,
                exam_mode=True,
                exam_tracks=True,
            ),
        ),
    )

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
