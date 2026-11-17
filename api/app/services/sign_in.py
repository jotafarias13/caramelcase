"""Signing in with Google or an email link, and what happens to the
guest who was playing in that browser.

- Nobody has this identity or email yet: the guest becomes the account
  and keeps everything. Without a guest, a new account is created.
- An account exists: the student is signed in to it, and a guest's
  history is merged into it. The guest is then deleted.

The caller starts the new session and commits.
"""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    AuthIdentity,
    DailyActivity,
    Event,
    PracticeSession,
    QuestionReport,
    ReviewItem,
    Streak,
    User,
    UserSettings,
    UserSubject,
    UserSubjectRating,
    UserTopicMastery,
)
from app.db.rows import ensure_row
from app.domain.streak import streak_from_days
from app.enums import AuthProvider
from app.services.users import create_user
from app.settings import Settings


async def sign_in(  # noqa: PLR0913  who is asking, and who they proved to be
    session: AsyncSession,
    settings: Settings,
    *,
    current_user: User | None,
    provider: AuthProvider,
    provider_subject: str,
    email: str,
    display_name: str | None = None,
) -> User:
    """Return the account for a proven identity, creating or upgrading
    as needed. email is lower case and belongs to whoever is asking:
    Google verified it, or they opened the link sent to it.
    """
    guest = current_user if current_user and current_user.is_guest else None
    account = await _account_of(session, provider, provider_subject, email)

    if account is None and guest is not None:
        account = guest
        account.email = email
        account.is_guest = False
    elif account is None:
        locale = current_user.locale if current_user else None
        timezone = current_user.timezone if current_user else None
        account = await create_user(
            session, settings, locale=locale, timezone=timezone, email=email
        )
    elif guest is not None:
        await merge_guest(session, guest=guest, account=account)

    if account.display_name is None and display_name:
        account.display_name = display_name[:80]
    await _remember_identity(session, account.id, provider, provider_subject)
    await session.flush()
    return account


async def _account_of(
    session: AsyncSession,
    provider: AuthProvider,
    provider_subject: str,
    email: str,
) -> User | None:
    """The account that signed in this way before, or that has this email."""
    by_identity = await session.scalar(
        select(User)
        .join(AuthIdentity, AuthIdentity.user_id == User.id)
        .where(
            AuthIdentity.provider == provider,
            AuthIdentity.provider_subject == provider_subject,
        )
    )
    if by_identity is not None:
        return by_identity
    return await session.scalar(select(User).where(User.email == email))


async def _remember_identity(
    session: AsyncSession,
    user_id: uuid.UUID,
    provider: AuthProvider,
    provider_subject: str,
) -> None:
    known = await session.scalar(
        select(AuthIdentity.id).where(
            AuthIdentity.provider == provider,
            AuthIdentity.provider_subject == provider_subject,
        )
    )
    if known is None:
        session.add(
            AuthIdentity(
                user_id=user_id,
                provider=provider,
                provider_subject=provider_subject,
            )
        )


async def merge_guest(
    session: AsyncSession, *, guest: User, account: User
) -> None:
    """Move everything a guest did into an account, then delete the guest.

    Sessions, answers, reports and events change owner. Where both have
    a row for the same thing (a subject's rating, a topic, a day, a
    question to review), the two rows become one. The account keeps its
    own settings and profile; the guest's fill only what is empty.
    """
    for model in (PracticeSession, Attempt, QuestionReport, Event):
        await session.execute(
            update(model)
            .where(model.user_id == guest.id)
            .values(user_id=account.id)
        )
    await _merge_ratings(session, guest.id, account.id)
    await _merge_mastery(session, guest.id, account.id)
    await _merge_days(session, guest.id, account.id)
    await _merge_streaks(session, guest.id, account.id)
    await _merge_review_items(session, guest.id, account.id)
    await _merge_subjects(session, guest.id, account.id)

    account.current_subject_id = (
        account.current_subject_id or guest.current_subject_id
    )
    account.university = account.university or guest.university
    account.course = account.course or guest.course
    # Whatever is left of the guest goes with it (ON DELETE CASCADE).
    await session.delete(guest)
    await session.flush()


async def _merge_ratings(
    session: AsyncSession, guest_id: uuid.UUID, account_id: uuid.UUID
) -> None:
    """Per subject: the rating built on more answers stays, and the
    answers add up.
    """
    rows = await session.scalars(
        select(UserSubjectRating).where(UserSubjectRating.user_id == guest_id)
    )
    for theirs in rows:
        ours = await ensure_row(
            session,
            UserSubjectRating,
            {"user_id": account_id, "subject_id": theirs.subject_id},
            {"rating": theirs.rating, "answers_count": 0},
        )
        if theirs.answers_count > ours.answers_count:
            ours.rating = theirs.rating
        ours.answers_count += theirs.answers_count


async def _merge_mastery(
    session: AsyncSession, guest_id: uuid.UUID, account_id: uuid.UUID
) -> None:
    rows = await session.scalars(
        select(UserTopicMastery).where(UserTopicMastery.user_id == guest_id)
    )
    for theirs in rows:
        ours = await ensure_row(
            session,
            UserTopicMastery,
            {"user_id": account_id, "topic_id": theirs.topic_id},
            {"last_seen_at": theirs.last_seen_at},
        )
        ours.correct += theirs.correct
        ours.total += theirs.total
        ours.last_seen_at = max(ours.last_seen_at, theirs.last_seen_at)


async def _merge_days(
    session: AsyncSession, guest_id: uuid.UUID, account_id: uuid.UUID
) -> None:
    daily_goal = await session.scalar(
        select(UserSettings.daily_goal).where(
            UserSettings.user_id == account_id
        )
    )
    rows = await session.scalars(
        select(DailyActivity).where(DailyActivity.user_id == guest_id)
    )
    for theirs in rows:
        ours = await ensure_row(
            session,
            DailyActivity,
            {"user_id": account_id, "local_date": theirs.local_date},
        )
        ours.xp += theirs.xp
        ours.questions += theirs.questions
        ours.sessions_finished += theirs.sessions_finished
        met_together = daily_goal is not None and ours.questions >= daily_goal
        ours.goal_met = ours.goal_met or theirs.goal_met or met_together


async def _merge_streaks(
    session: AsyncSession, guest_id: uuid.UUID, account_id: uuid.UUID
) -> None:
    """Rebuild the account's streak from the merged days."""
    await session.flush()
    theirs = await session.scalar(
        select(Streak).where(Streak.user_id == guest_id)
    )
    if theirs is None:
        return
    active_days = await session.scalars(
        select(DailyActivity.local_date).where(
            DailyActivity.user_id == account_id,
            DailyActivity.sessions_finished > 0,
        )
    )
    rebuilt = streak_from_days(active_days)
    ours = await ensure_row(session, Streak, {"user_id": account_id})
    ours.current = rebuilt.current
    ours.last_active_date = rebuilt.last_active_date
    ours.longest = max(ours.longest, theirs.longest, rebuilt.longest)


async def _merge_review_items(
    session: AsyncSession, guest_id: uuid.UUID, account_id: uuid.UUID
) -> None:
    """A question both have to review keeps the earlier date."""
    rows = await session.scalars(
        select(ReviewItem).where(ReviewItem.user_id == guest_id)
    )
    for theirs in rows:
        ours = await ensure_row(
            session,
            ReviewItem,
            {"user_id": account_id, "question_id": theirs.question_id},
            {
                "due_at": theirs.due_at,
                "interval_days": theirs.interval_days,
                "lapses": 0,
            },
        )
        if theirs.due_at < ours.due_at:
            ours.due_at = theirs.due_at
            ours.interval_days = theirs.interval_days
        ours.lapses += theirs.lapses


async def _merge_subjects(
    session: AsyncSession, guest_id: uuid.UUID, account_id: uuid.UUID
) -> None:
    subject_ids = await session.scalars(
        select(UserSubject.subject_id).where(UserSubject.user_id == guest_id)
    )
    for subject_id in subject_ids:
        await ensure_row(
            session,
            UserSubject,
            {"user_id": account_id, "subject_id": subject_id},
        )
