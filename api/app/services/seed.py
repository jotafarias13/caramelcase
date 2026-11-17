"""Seeding: the rows every environment needs before the app can run.

Plans, feature flags and subjects. Seeding again changes only what differs
from its sources, so it is safe to run at every deploy:

- plans follow settings.plans: prices and limits are overwritten;
- feature flags are created switched off and never switched again;
- subjects follow content/catalog.yaml, except for their status.

Nothing is ever deleted. The caller commits.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.models import FeatureFlag, Plan, Subject
from app.enums import FlagKey, FlagState, SubjectStatus
from app.services.catalog_file import Catalog, load_catalog
from app.settings import PlanDefinition, Settings

CATALOG_FILE_NAME = "catalog.yaml"


@dataclass(frozen=True)
class SeedCounts:
    """How many rows each seeded table holds after seeding."""

    plans: int
    flags: int
    subjects: int


async def seed_all(session: AsyncSession, settings: Settings) -> SeedCounts:
    catalog = load_catalog(settings.content_dir / CATALOG_FILE_NAME)
    await seed_plans(session, settings.plans)
    await seed_flags(session)
    await seed_subjects(session, catalog)
    return SeedCounts(
        plans=await _count(session, Plan),
        flags=await _count(session, FeatureFlag),
        subjects=await _count(session, Subject),
    )


async def seed_plans(
    session: AsyncSession, definitions: Sequence[PlanDefinition]
) -> None:
    """Make each plan's row match its definition in settings."""
    existing = {plan.key: plan for plan in await session.scalars(select(Plan))}
    for definition in definitions:
        plan = existing.get(definition.key)
        if plan is None:
            plan = Plan(key=definition.key.value)
            session.add(plan)
        plan.price_month_brl = definition.price_month_brl
        plan.price_year_brl = definition.price_year_brl
        plan.price_semester_brl = definition.price_semester_brl
        plan.limits = definition.limits.model_dump()
    await session.flush()


async def seed_flags(session: AsyncSession) -> None:
    """Create each missing feature flag, switched off.

    A flag that exists keeps its state: seeding never switches a feature.
    """
    existing = set(await session.scalars(select(FeatureFlag.key)))
    for key in FlagKey:
        if key.value not in existing:
            session.add(FeatureFlag(key=key.value, state=FlagState.OFF))
    await session.flush()


async def seed_subjects(session: AsyncSession, catalog: Catalog) -> None:
    """Create each new catalog subject as a draft, and bring the names,
    badge and order of the others up to date.

    A subject's status is never changed: publishing is a separate step.
    """
    existing = {
        subject.slug: subject
        for subject in await session.scalars(select(Subject))
    }
    for position, entry in enumerate(catalog.subjects, start=1):
        subject = existing.get(entry.slug)
        if subject is None:
            subject = Subject(slug=entry.slug, status=SubjectStatus.DRAFT)
            session.add(subject)
        subject.name_pt = entry.name_pt
        subject.name_en = entry.name_en
        subject.short_pt = entry.short_pt
        subject.short_en = entry.short_en
        subject.sort_order = position
    await session.flush()


async def _count(session: AsyncSession, model: type[Base]) -> int:
    count = await session.scalar(select(func.count()).select_from(model))
    return count or 0
