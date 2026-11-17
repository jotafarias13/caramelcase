"""Entitlements: what a user may do. Nothing else decides access.

While billing is off for the user, there are no limits and no ads. With
billing on, the user has what their plan allows, and the plan is the free
one unless a subscription is still running.

Milestone 10 builds the rest on this: usage counters that enforce the
daily numbers, and what a failed renewal does to a subscription.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from app.enums import PlanKey, SubscriptionStatus
from app.settings import PlanLimits

# A canceled subscription keeps its plan until the period it paid for ends.
_RUNNING = (SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELED)


@dataclass(frozen=True)
class SubscriptionState:
    """The part of a subscriptions row that decides access."""

    plan_key: PlanKey
    status: SubscriptionStatus
    current_period_end: datetime | None


@dataclass(frozen=True)
class Entitlements:
    plan_key: PlanKey | None  # None while billing is off
    sessions_per_day: int | None  # None means no limit
    ads: bool
    tutor_messages_per_day: int | None  # None means no limit
    exam_mode: bool
    exam_tracks: bool


NO_LIMITS = Entitlements(
    plan_key=None,
    sessions_per_day=None,
    ads=False,
    tutor_messages_per_day=None,
    exam_mode=True,
    exam_tracks=True,
)


def entitlements_for(
    *,
    billing_on: bool,
    subscription: SubscriptionState | None,
    plans: Mapping[PlanKey, PlanLimits],
    now: datetime,
) -> Entitlements:
    """What the user may do now.

    billing_on is the billing flag as it applies to this user; plans maps
    each plan to its limits.
    """
    if not billing_on:
        return NO_LIMITS
    plan_key = PlanKey.FREE
    if subscription is not None and _is_running(subscription, now):
        plan_key = subscription.plan_key
    limits = plans[plan_key]
    return Entitlements(
        plan_key=plan_key,
        sessions_per_day=limits.sessions_per_day,
        ads=limits.ads,
        tutor_messages_per_day=limits.tutor_messages_per_day,
        exam_mode=limits.exam_mode,
        exam_tracks=limits.exam_tracks,
    )


def _is_running(subscription: SubscriptionState, now: datetime) -> bool:
    if subscription.status not in _RUNNING:
        return False
    end = subscription.current_period_end
    return end is None or end > now
