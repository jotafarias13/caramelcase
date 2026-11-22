"""GET /config: flags, plans, entitlements and the numbers the web app
needs to draw itself.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Plan, Subscription, User
from app.domain.entitlements import (
    Entitlements,
    SubscriptionState,
    entitlements_for,
)
from app.enums import FlagKey, PlanKey
from app.providers.google import google_provider_for
from app.schemas.config import (
    ConfigResponse,
    EntitlementsModel,
    PlanModel,
    RulesModel,
)
from app.services.flags import flags_for
from app.settings import PlanLimits, Settings


async def user_entitlements(
    session: AsyncSession,
    user: User | None,
    *,
    billing_on: bool,
    settings: Settings,
    now: datetime,
) -> Entitlements:
    subscription = None
    if user is not None and billing_on:
        row = await session.scalar(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        if row is not None:
            subscription = SubscriptionState(
                plan_key=PlanKey(row.plan_key),
                status=row.status,
                current_period_end=row.current_period_end,
            )
    return entitlements_for(
        billing_on=billing_on,
        subscription=subscription,
        plans={plan.key: plan.limits for plan in settings.plans},
        now=now,
    )


async def config_response(
    session: AsyncSession,
    user: User | None,
    *,
    settings: Settings,
    now: datetime,
) -> ConfigResponse:
    flags = await flags_for(session, user)
    entitlements = await user_entitlements(
        session,
        user,
        billing_on=flags[FlagKey.BILLING.value],
        settings=settings,
        now=now,
    )
    plans = await session.scalars(select(Plan).order_by(Plan.price_month_brl))
    return ConfigResponse(
        flags=flags,
        plans=[
            PlanModel(
                key=plan.key,
                price_month_brl=plan.price_month_brl,
                price_year_brl=plan.price_year_brl,
                price_semester_brl=plan.price_semester_brl,
                limits=PlanLimits.model_validate(plan.limits),
            )
            for plan in plans
        ],
        entitlements=EntitlementsModel.of(entitlements),
        google_sign_in=google_provider_for(settings) is not None,
        session_length=settings.session_length,
        daily_goal_options=list(settings.daily_goal_options),
        xp_per_level=settings.xp_per_level,
        rules=RulesModel(
            xp_correct=settings.xp_correct,
            xp_session_finished=settings.xp_session_finished,
            user_rating_start=settings.user_rating_start,
            mastery_mastered_from=settings.mastery_mastered_from,
            mastery_mastered_min_answers=(
                settings.mastery_mastered_min_answers
            ),
        ),
    )
