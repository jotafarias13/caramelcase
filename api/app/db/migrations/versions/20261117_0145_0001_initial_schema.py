"""Initial schema: every table of V1, V2 and V3.

The tables are the models in app/db/models/. Columns typed with an enum
from app/enums.py are VARCHAR(32); the database does not list their values.

Revision ID: 0001
Revises:
Create Date: 2026-11-17 01:45 UTC
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "achievements",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_achievements")),
        sa.UniqueConstraint("key", name=op.f("uq_achievements_key")),
    )
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feature_flags")),
        sa.UniqueConstraint("key", name=op.f("uq_feature_flags_key")),
    )
    op.create_table(
        "league_weeks",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_league_weeks")),
        sa.UniqueConstraint("week_start", name=op.f("uq_league_weeks_week_start")),
    )
    op.create_table(
        "magic_links",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_magic_links")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_magic_links_token_hash")),
    )
    op.create_index(op.f("ix_magic_links_email"), "magic_links", ["email"], unique=False)
    op.create_table(
        "plans",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("key", sa.String(length=32), nullable=False),
        sa.Column("price_month_brl", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("price_year_brl", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("price_semester_brl", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("limits", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_plans")),
        sa.UniqueConstraint("key", name=op.f("uq_plans_key")),
    )
    op.create_table(
        "subjects",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name_pt", sa.String(length=120), nullable=False),
        sa.Column("name_en", sa.String(length=120), nullable=False),
        sa.Column("short_pt", sa.String(length=12), nullable=False),
        sa.Column("short_en", sa.String(length=12), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subjects")),
        sa.UniqueConstraint("slug", name=op.f("uq_subjects_slug")),
    )
    op.create_table(
        "exam_templates",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name_pt", sa.String(length=120), nullable=False),
        sa.Column("name_en", sa.String(length=120), nullable=False),
        sa.Column("track", sa.String(length=64), nullable=True),
        sa.Column("subject_id", sa.Uuid(), nullable=True),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("composition", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_exam_templates_subject_id_subjects")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exam_templates")),
        sa.UniqueConstraint("slug", name=op.f("uq_exam_templates_slug")),
    )
    op.create_index(op.f("ix_exam_templates_track"), "exam_templates", ["track"], unique=False)
    op.create_table(
        "topics",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name_pt", sa.String(length=120), nullable=False),
        sa.Column("name_en", sa.String(length=120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_topics_subject_id_subjects")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_topics")),
        sa.UniqueConstraint("subject_id", "slug", name=op.f("uq_topics_subject_id_slug")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("display_name", sa.String(length=80), nullable=True),
        sa.Column("locale", sa.String(length=32), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("is_guest", sa.Boolean(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("university", sa.String(length=120), nullable=True),
        sa.Column("course", sa.String(length=120), nullable=True),
        sa.Column("current_subject_id", sa.Uuid(), nullable=True),
        sa.Column("referral_code", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["current_subject_id"], ["subjects.id"], name=op.f("fk_users_current_subject_id_subjects")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("referral_code", name=op.f("uq_users_referral_code")),
    )
    op.create_table(
        "ad_events",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("meta", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_ad_events_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ad_events")),
    )
    op.create_index(op.f("ix_ad_events_user_id_created_at"), "ad_events", ["user_id", "created_at"], unique=False)
    op.create_table(
        "auth_identities",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_subject", sa.String(length=320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_auth_identities_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_identities")),
        sa.UniqueConstraint("provider", "provider_subject", name=op.f("uq_auth_identities_provider_provider_subject")),
    )
    op.create_index(op.f("ix_auth_identities_user_id"), "auth_identities", ["user_id"], unique=False)
    op.create_table(
        "daily_activity",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("questions", sa.Integer(), nullable=False),
        sa.Column("sessions_finished", sa.Integer(), nullable=False),
        sa.Column("goal_met", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_daily_activity_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_activity")),
        sa.UniqueConstraint("user_id", "local_date", name=op.f("uq_daily_activity_user_id_local_date")),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("props", postgresql.JSONB(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_events_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )
    op.create_index(op.f("ix_events_name_occurred_at"), "events", ["name", "occurred_at"], unique=False)
    op.create_index(op.f("ix_events_user_id_occurred_at"), "events", ["user_id", "occurred_at"], unique=False)
    op.create_table(
        "league_memberships",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("league_week_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("tier", sa.String(length=32), nullable=False),
        sa.Column("cohort", sa.Integer(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("final_rank", sa.Integer(), nullable=True),
        sa.Column("outcome", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["league_week_id"], ["league_weeks.id"], name=op.f("fk_league_memberships_league_week_id_league_weeks")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_league_memberships_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_league_memberships")),
        sa.UniqueConstraint("league_week_id", "user_id", name=op.f("uq_league_memberships_league_week_id_user_id")),
    )
    op.create_index(
        op.f("ix_league_memberships_league_week_id_tier_cohort"),
        "league_memberships",
        ["league_week_id", "tier", "cohort"],
        unique=False,
    )
    op.create_index(op.f("ix_league_memberships_user_id"), "league_memberships", ["user_id"], unique=False)
    op.create_table(
        "lives",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("remaining", sa.Integer(), nullable=False),
        sa.Column("refill_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_lives_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lives")),
        sa.UniqueConstraint("user_id", name=op.f("uq_lives_user_id")),
    )
    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=True),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("question_ids", postgresql.ARRAY(sa.Uuid()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("xp_earned", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_practice_sessions_subject_id_subjects")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_practice_sessions_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_practice_sessions")),
    )
    op.create_index(
        op.f("ix_practice_sessions_user_id_started_at"), "practice_sessions", ["user_id", "started_at"], unique=False
    )
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh", sa.String(length=255), nullable=True),
        sa.Column("auth", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_push_subscriptions_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_push_subscriptions")),
        sa.UniqueConstraint("endpoint", name=op.f("uq_push_subscriptions_endpoint")),
    )
    op.create_index(op.f("ix_push_subscriptions_user_id"), "push_subscriptions", ["user_id"], unique=False)
    op.create_table(
        "questions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("external_id", sa.String(length=160), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("difficulty_prior", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Double(), nullable=False),
        sa.Column("answers_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_questions_subject_id_subjects")),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], name=op.f("fk_questions_topic_id_topics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_questions")),
        sa.UniqueConstraint("external_id", name=op.f("uq_questions_external_id")),
    )
    op.create_index(op.f("ix_questions_subject_id_status"), "questions", ["subject_id", "status"], unique=False)
    op.create_index(op.f("ix_questions_topic_id"), "questions", ["topic_id"], unique=False)
    op.create_table(
        "referrals",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("referrer_user_id", sa.Uuid(), nullable=False),
        sa.Column("referred_user_id", sa.Uuid(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rewarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["referred_user_id"], ["users.id"], name=op.f("fk_referrals_referred_user_id_users"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["referrer_user_id"], ["users.id"], name=op.f("fk_referrals_referrer_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_referrals")),
        sa.UniqueConstraint("referred_user_id", name=op.f("uq_referrals_referred_user_id")),
    )
    op.create_index(op.f("ix_referrals_referrer_user_id"), "referrals", ["referrer_user_id"], unique=False)
    op.create_table(
        "sessions_auth",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_sessions_auth_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions_auth")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_auth_token_hash")),
    )
    op.create_index(op.f("ix_sessions_auth_user_id"), "sessions_auth", ["user_id"], unique=False)
    op.create_table(
        "streaks",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("current", sa.Integer(), nullable=False),
        sa.Column("longest", sa.Integer(), nullable=False),
        sa.Column("last_active_date", sa.Date(), nullable=True),
        sa.Column("freezes", sa.Integer(), nullable=False),
        sa.Column("lost_length", sa.Integer(), nullable=True),
        sa.Column("lost_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_streaks_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_streaks")),
        sa.UniqueConstraint("user_id", name=op.f("uq_streaks_user_id")),
    )
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("plan_key", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_ref", sa.String(length=255), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["plan_key"], ["plans.key"], name=op.f("fk_subscriptions_plan_key_plans")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_subscriptions_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscriptions")),
        sa.UniqueConstraint("provider", "provider_ref", name=op.f("uq_subscriptions_provider_provider_ref")),
    )
    op.create_index(op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=False)
    op.create_table(
        "topic_edges",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("from_topic_id", sa.Uuid(), nullable=False),
        sa.Column("to_topic_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Double(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["from_topic_id"], ["topics.id"], name=op.f("fk_topic_edges_from_topic_id_topics")),
        sa.ForeignKeyConstraint(["to_topic_id"], ["topics.id"], name=op.f("fk_topic_edges_to_topic_id_topics")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_topic_edges")),
        sa.UniqueConstraint(
            "from_topic_id", "to_topic_id", "kind", name=op.f("uq_topic_edges_from_topic_id_to_topic_id_kind")
        ),
    )
    op.create_index(op.f("ix_topic_edges_to_topic_id"), "topic_edges", ["to_topic_id"], unique=False)
    op.create_table(
        "usage_counters",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("questions_answered", sa.Integer(), nullable=False),
        sa.Column("tutor_messages", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_usage_counters_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usage_counters")),
        sa.UniqueConstraint("user_id", "local_date", name=op.f("uq_usage_counters_user_id_local_date")),
    )
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("achievement_id", sa.Uuid(), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["achievement_id"], ["achievements.id"], name=op.f("fk_user_achievements_achievement_id_achievements")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_achievements_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_achievements")),
        sa.UniqueConstraint("user_id", "achievement_id", name=op.f("uq_user_achievements_user_id_achievement_id")),
    )
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("daily_goal", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=32), nullable=False),
        sa.Column("show_option_reasons", sa.Boolean(), nullable=False),
        sa.Column("daily_reminder", sa.Boolean(), nullable=False),
        sa.Column("weekly_email", sa.Boolean(), nullable=False),
        sa.Column("reminder_time", sa.Time(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_settings_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_settings")),
        sa.UniqueConstraint("user_id", name=op.f("uq_user_settings_user_id")),
    )
    op.create_table(
        "user_subject_ratings",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.Double(), nullable=False),
        sa.Column("answers_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id"], ["subjects.id"], name=op.f("fk_user_subject_ratings_subject_id_subjects")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_subject_ratings_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_subject_ratings")),
        sa.UniqueConstraint("user_id", "subject_id", name=op.f("uq_user_subject_ratings_user_id_subject_id")),
    )
    op.create_table(
        "user_subjects",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_user_subjects_subject_id_subjects")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_subjects_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_subjects")),
        sa.UniqueConstraint("user_id", "subject_id", name=op.f("uq_user_subjects_user_id_subject_id")),
    )
    op.create_table(
        "user_topic_mastery",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], name=op.f("fk_user_topic_mastery_topic_id_topics")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_topic_mastery_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_topic_mastery")),
        sa.UniqueConstraint("user_id", "topic_id", name=op.f("uq_user_topic_mastery_user_id_topic_id")),
    )
    op.create_table(
        "attempts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("answer", postgresql.JSONB(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("time_ms", sa.Integer(), nullable=False),
        sa.Column("user_rating_before", sa.Double(), nullable=False),
        sa.Column("user_rating_after", sa.Double(), nullable=False),
        sa.Column("question_rating_before", sa.Double(), nullable=False),
        sa.Column("question_rating_after", sa.Double(), nullable=False),
        sa.Column("locale", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_attempts_question_id_questions")),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["practice_sessions.id"],
            name=op.f("fk_attempts_session_id_practice_sessions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_attempts_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_attempts")),
        sa.UniqueConstraint("session_id", "question_id", name=op.f("uq_attempts_session_id_question_id")),
    )
    op.create_index(op.f("ix_attempts_user_id_created_at"), "attempts", ["user_id", "created_at"], unique=False)
    op.create_index(op.f("ix_attempts_user_id_question_id"), "attempts", ["user_id", "question_id"], unique=False)
    op.create_table(
        "exam_attempts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("exam_template_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("results", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["exam_template_id"], ["exam_templates.id"], name=op.f("fk_exam_attempts_exam_template_id_exam_templates")
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["practice_sessions.id"],
            name=op.f("fk_exam_attempts_session_id_practice_sessions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_exam_attempts_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exam_attempts")),
        sa.UniqueConstraint("session_id", name=op.f("uq_exam_attempts_session_id")),
    )
    op.create_index(op.f("ix_exam_attempts_exam_template_id"), "exam_attempts", ["exam_template_id"], unique=False)
    op.create_index(op.f("ix_exam_attempts_user_id"), "exam_attempts", ["user_id"], unique=False)
    op.create_table(
        "question_reports",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("locale", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=32), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"], ["questions.id"], name=op.f("fk_question_reports_question_id_questions")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_question_reports_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_reports")),
    )
    op.create_index(op.f("ix_question_reports_question_id"), "question_reports", ["question_id"], unique=False)
    op.create_index(op.f("ix_question_reports_user_id"), "question_reports", ["user_id"], unique=False)
    op.create_table(
        "question_translations",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("locale", sa.String(length=32), nullable=False),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("code", sa.Text(), nullable=True),
        sa.Column("code_language", sa.String(length=16), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name=op.f("fk_question_translations_question_id_questions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_translations")),
        sa.UniqueConstraint("question_id", "locale", name=op.f("uq_question_translations_question_id_locale")),
    )
    op.create_table(
        "review_items",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False),
        sa.Column("lapses", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_review_items_question_id_questions")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_review_items_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_review_items")),
        sa.UniqueConstraint("user_id", "question_id", name=op.f("uq_review_items_user_id_question_id")),
    )
    op.create_index(op.f("ix_review_items_user_id_due_at"), "review_items", ["user_id", "due_at"], unique=False)
    op.create_table(
        "tutor_threads",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=True),
        sa.Column("topic_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_tutor_threads_question_id_questions")),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], name=op.f("fk_tutor_threads_topic_id_topics")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_tutor_threads_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tutor_threads")),
    )
    op.create_index(op.f("ix_tutor_threads_user_id"), "tutor_threads", ["user_id"], unique=False)
    op.create_table(
        "tutor_messages",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["thread_id"],
            ["tutor_threads.id"],
            name=op.f("fk_tutor_messages_thread_id_tutor_threads"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tutor_messages")),
    )
    op.create_index(
        op.f("ix_tutor_messages_thread_id_created_at"), "tutor_messages", ["thread_id", "created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tutor_messages_thread_id_created_at"), table_name="tutor_messages")
    op.drop_table("tutor_messages")
    op.drop_index(op.f("ix_tutor_threads_user_id"), table_name="tutor_threads")
    op.drop_table("tutor_threads")
    op.drop_index(op.f("ix_review_items_user_id_due_at"), table_name="review_items")
    op.drop_table("review_items")
    op.drop_table("question_translations")
    op.drop_index(op.f("ix_question_reports_user_id"), table_name="question_reports")
    op.drop_index(op.f("ix_question_reports_question_id"), table_name="question_reports")
    op.drop_table("question_reports")
    op.drop_index(op.f("ix_exam_attempts_user_id"), table_name="exam_attempts")
    op.drop_index(op.f("ix_exam_attempts_exam_template_id"), table_name="exam_attempts")
    op.drop_table("exam_attempts")
    op.drop_index(op.f("ix_attempts_user_id_question_id"), table_name="attempts")
    op.drop_index(op.f("ix_attempts_user_id_created_at"), table_name="attempts")
    op.drop_table("attempts")
    op.drop_table("user_topic_mastery")
    op.drop_table("user_subjects")
    op.drop_table("user_subject_ratings")
    op.drop_table("user_settings")
    op.drop_table("user_achievements")
    op.drop_table("usage_counters")
    op.drop_index(op.f("ix_topic_edges_to_topic_id"), table_name="topic_edges")
    op.drop_table("topic_edges")
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_table("streaks")
    op.drop_index(op.f("ix_sessions_auth_user_id"), table_name="sessions_auth")
    op.drop_table("sessions_auth")
    op.drop_index(op.f("ix_referrals_referrer_user_id"), table_name="referrals")
    op.drop_table("referrals")
    op.drop_index(op.f("ix_questions_topic_id"), table_name="questions")
    op.drop_index(op.f("ix_questions_subject_id_status"), table_name="questions")
    op.drop_table("questions")
    op.drop_index(op.f("ix_push_subscriptions_user_id"), table_name="push_subscriptions")
    op.drop_table("push_subscriptions")
    op.drop_index(op.f("ix_practice_sessions_user_id_started_at"), table_name="practice_sessions")
    op.drop_table("practice_sessions")
    op.drop_table("lives")
    op.drop_index(op.f("ix_league_memberships_user_id"), table_name="league_memberships")
    op.drop_index(op.f("ix_league_memberships_league_week_id_tier_cohort"), table_name="league_memberships")
    op.drop_table("league_memberships")
    op.drop_index(op.f("ix_events_user_id_occurred_at"), table_name="events")
    op.drop_index(op.f("ix_events_name_occurred_at"), table_name="events")
    op.drop_table("events")
    op.drop_table("daily_activity")
    op.drop_index(op.f("ix_auth_identities_user_id"), table_name="auth_identities")
    op.drop_table("auth_identities")
    op.drop_index(op.f("ix_ad_events_user_id_created_at"), table_name="ad_events")
    op.drop_table("ad_events")
    op.drop_table("users")
    op.drop_table("topics")
    op.drop_index(op.f("ix_exam_templates_track"), table_name="exam_templates")
    op.drop_table("exam_templates")
    op.drop_table("subjects")
    op.drop_table("plans")
    op.drop_index(op.f("ix_magic_links_email"), table_name="magic_links")
    op.drop_table("magic_links")
    op.drop_table("league_weeks")
    op.drop_table("feature_flags")
    op.drop_table("achievements")
