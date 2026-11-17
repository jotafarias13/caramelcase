"""The fixed vocabularies of the product: statuses, modes, kinds, keys.

Each one is stored in Postgres as its text value in a VARCHAR(32) column.
The database does not restrict the values, so adding a member here needs
no migration. SQLAlchemy rejects a value that is not a member, on write
and on read.
"""

from enum import StrEnum


class Locale(StrEnum):
    PT_BR = "pt-BR"
    EN = "en"


# ---- identity ----


class UserRole(StrEnum):
    USER = "user"
    STAFF = "staff"


class AuthProvider(StrEnum):
    GOOGLE = "google"
    EMAIL = "email"


class Theme(StrEnum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class PushPlatform(StrEnum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"


# ---- content ----


class SubjectStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class TopicEdgeKind(StrEnum):
    PREREQUISITE = "prerequisite"
    RELATED = "related"


class QuestionType(StrEnum):
    MCQ = "mcq"
    # V2, behind question_types_v2
    TRUE_FALSE = "true_false"
    PREDICT_OUTPUT = "predict_output"
    FIND_BUG = "find_bug"
    FILL_BLANK = "fill_blank"
    ORDER_STEPS = "order_steps"
    # V3, behind write_code
    WRITE_CODE = "write_code"


class QuestionStatus(StrEnum):
    DRAFT = "draft"
    VERIFIED = "verified"
    PUBLISHED = "published"
    RETIRED = "retired"


class ReportReason(StrEnum):
    WRONG_ANSWER = "wrong_answer"
    AMBIGUOUS_WORDING = "ambiguous_wording"
    TYPO = "typo"
    OTHER = "other"


class ReportStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# ---- practice ----


class SessionMode(StrEnum):
    PRACTICE = "practice"
    REVIEW = "review"
    EXAM = "exam"
    CHALLENGE = "challenge"


# ---- feature flags ----


class FlagState(StrEnum):
    OFF = "off"
    STAFF = "staff"
    ON = "on"


class FlagKey(StrEnum):
    """Every feature flag. Seeding creates each one switched off."""

    # V2
    REVIEW_QUEUE = "review_queue"
    QUESTION_TYPES_V2 = "question_types_v2"
    EXAM_MODE = "exam_mode"
    LEAGUES = "leagues"
    ACHIEVEMENTS = "achievements"
    LIVES = "lives"
    STREAK_FREEZE = "streak_freeze"
    REMINDERS = "reminders"
    ADMIN_CONSOLE = "admin_console"
    # V3
    BILLING = "billing"
    ADS = "ads"
    BEAT_THE_AD = "beat_the_ad"
    STREAK_REPAIR = "streak_repair"
    AI_TUTOR = "ai_tutor"
    EXAM_TRACKS = "exam_tracks"
    WRITE_CODE = "write_code"
    REFERRAL = "referral"


# ---- leagues ----


class LeagueOutcome(StrEnum):
    PROMOTED = "promoted"
    STAYED = "stayed"
    RELEGATED = "relegated"


# ---- plans, billing, ads, tutor ----


class PlanKey(StrEnum):
    FREE = "free"
    PLUS = "plus"
    PRO = "pro"
    MAX = "max"


class SubscriptionStatus(StrEnum):
    PENDING = "pending"  # checkout started, not paid yet
    ACTIVE = "active"
    PAST_DUE = "past_due"  # a renewal charge failed
    CANCELED = "canceled"  # keeps access until current_period_end
    EXPIRED = "expired"


class AdEventKind(StrEnum):
    BREAK_DUE = "break_due"
    CHALLENGE_OFFERED = "challenge_offered"
    CHALLENGE_WON = "challenge_won"
    CHALLENGE_LOST = "challenge_lost"
    DOUBLE_ACCEPTED = "double_accepted"
    AD_SHOWN = "ad_shown"
    REWARDED_COMPLETED = "rewarded_completed"


class TutorRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
