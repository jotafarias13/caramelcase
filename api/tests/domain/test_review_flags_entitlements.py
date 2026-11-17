"""The review schedule, feature flags and entitlements."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.entitlements import (
    NO_LIMITS,
    SubscriptionState,
    entitlements_for,
)
from app.domain.flags import flag_is_on
from app.domain.review import after_correct_review, first_review
from app.enums import FlagState, PlanKey, SubscriptionStatus, UserRole
from app.settings import Settings

SETTINGS = Settings()
NOW = datetime(2026, 11, 16, 15, 0, tzinfo=UTC)
PLANS = {plan.key: plan.limits for plan in SETTINGS.plans}

# ---- review schedule ----


def test_a_wrong_answer_is_due_the_next_day() -> None:
    schedule = first_review(NOW, SETTINGS)

    assert schedule.interval_days == 1
    assert schedule.due_at == NOW + timedelta(days=1)


def test_correct_reviews_walk_1_3_7_18_45_days() -> None:
    intervals = []
    interval = 1
    while (
        schedule := after_correct_review(interval, NOW, SETTINGS)
    ) is not None:
        assert schedule.due_at == NOW + timedelta(days=schedule.interval_days)
        interval = schedule.interval_days
        intervals.append(interval)

    assert intervals == [3, 7, 18, 45]


def test_a_correct_review_at_45_days_leaves_the_queue() -> None:
    assert after_correct_review(45, NOW, SETTINGS) is None


def test_the_intervals_come_from_settings() -> None:
    settings = Settings(review_intervals_days=(2, 10))

    assert first_review(NOW, settings).interval_days == 2
    second = after_correct_review(2, NOW, settings)
    assert second is not None
    assert second.interval_days == 10
    assert after_correct_review(10, NOW, settings) is None


# ---- feature flags ----


@pytest.mark.parametrize(
    ("state", "role", "expected"),
    [
        (FlagState.OFF, None, False),
        (FlagState.OFF, UserRole.USER, False),
        (FlagState.OFF, UserRole.STAFF, False),
        (FlagState.STAFF, None, False),
        (FlagState.STAFF, UserRole.USER, False),
        (FlagState.STAFF, UserRole.STAFF, True),
        (FlagState.ON, None, True),
        (FlagState.ON, UserRole.USER, True),
        (FlagState.ON, UserRole.STAFF, True),
    ],
)
def test_a_flag_is_off_staff_only_or_on(
    state: FlagState, role: UserRole | None, expected: bool
) -> None:
    assert flag_is_on(state, role) is expected


# ---- entitlements ----


def _subscription(
    plan: PlanKey,
    status: SubscriptionStatus,
    ends_in_days: int | None = 10,
) -> SubscriptionState:
    end = None if ends_in_days is None else NOW + timedelta(days=ends_in_days)
    return SubscriptionState(plan, status, end)


def test_no_limits_and_no_ads_while_billing_is_off() -> None:
    free = entitlements_for(
        billing_on=False, subscription=None, plans=PLANS, now=NOW
    )

    assert free == NO_LIMITS
    assert free.sessions_per_day is None
    assert free.tutor_messages_per_day is None
    assert not free.ads
    assert free.exam_mode
    assert free.exam_tracks


def test_without_a_subscription_the_plan_is_free() -> None:
    free = entitlements_for(
        billing_on=True, subscription=None, plans=PLANS, now=NOW
    )

    assert free.plan_key is PlanKey.FREE
    assert free.sessions_per_day == 3
    assert free.ads
    assert free.tutor_messages_per_day == 0
    assert not free.exam_mode


def test_an_active_subscription_gives_its_plan() -> None:
    pro = entitlements_for(
        billing_on=True,
        subscription=_subscription(PlanKey.PRO, SubscriptionStatus.ACTIVE),
        plans=PLANS,
        now=NOW,
    )

    assert pro.plan_key is PlanKey.PRO
    assert pro.sessions_per_day is None
    assert not pro.ads
    assert pro.tutor_messages_per_day == 30
    assert pro.exam_mode
    assert not pro.exam_tracks


def test_a_canceled_subscription_keeps_its_plan_until_the_period_ends() -> (
    None
):
    running = _subscription(PlanKey.MAX, SubscriptionStatus.CANCELED, 3)
    over = _subscription(PlanKey.MAX, SubscriptionStatus.CANCELED, -1)

    def plan(subscription: SubscriptionState) -> PlanKey | None:
        return entitlements_for(
            billing_on=True, subscription=subscription, plans=PLANS, now=NOW
        ).plan_key

    assert plan(running) is PlanKey.MAX
    assert plan(over) is PlanKey.FREE


@pytest.mark.parametrize(
    "status",
    [
        SubscriptionStatus.PENDING,
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.EXPIRED,
    ],
)
def test_a_subscription_that_is_not_running_gives_the_free_plan(
    status: SubscriptionStatus,
) -> None:
    free = entitlements_for(
        billing_on=True,
        subscription=_subscription(PlanKey.PLUS, status),
        plans=PLANS,
        now=NOW,
    )

    assert free.plan_key is PlanKey.FREE


def test_an_active_subscription_past_its_period_gives_the_free_plan() -> None:
    late = _subscription(PlanKey.PLUS, SubscriptionStatus.ACTIVE, -1)

    free = entitlements_for(
        billing_on=True, subscription=late, plans=PLANS, now=NOW
    )

    assert free.plan_key is PlanKey.FREE
