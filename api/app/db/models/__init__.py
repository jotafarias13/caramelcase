"""Every table of the database, one module per area of the data model.

Importing this package registers all of them on Base.metadata, which is
what Alembic compares the database against.
"""

from app.db.models.content import (
    Question,
    QuestionReport,
    QuestionTranslation,
    Subject,
    Topic,
    TopicEdge,
)
from app.db.models.identity import (
    AuthIdentity,
    AuthSession,
    MagicLink,
    PushSubscription,
    User,
    UserSettings,
    UserSubject,
)
from app.db.models.monetization import (
    AdEvent,
    Plan,
    Referral,
    Subscription,
    TutorMessage,
    TutorThread,
    UsageCounter,
)
from app.db.models.practice import (
    Attempt,
    DailyActivity,
    Lives,
    PracticeSession,
    ReviewItem,
    Streak,
    UserSubjectRating,
    UserTopicMastery,
)
from app.db.models.product import Event, FeatureFlag
from app.db.models.retention import (
    Achievement,
    ExamAttempt,
    ExamTemplate,
    LeagueMembership,
    LeagueWeek,
    UserAchievement,
)

__all__ = [
    "Achievement",
    "AdEvent",
    "Attempt",
    "AuthIdentity",
    "AuthSession",
    "DailyActivity",
    "Event",
    "ExamAttempt",
    "ExamTemplate",
    "FeatureFlag",
    "LeagueMembership",
    "LeagueWeek",
    "Lives",
    "MagicLink",
    "Plan",
    "PracticeSession",
    "PushSubscription",
    "Question",
    "QuestionReport",
    "QuestionTranslation",
    "Referral",
    "ReviewItem",
    "Streak",
    "Subject",
    "Subscription",
    "Topic",
    "TopicEdge",
    "TutorMessage",
    "TutorThread",
    "UsageCounter",
    "User",
    "UserAchievement",
    "UserSettings",
    "UserSubject",
    "UserSubjectRating",
    "UserTopicMastery",
]
