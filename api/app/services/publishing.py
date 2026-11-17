"""Publishing a subject: the step that puts it in front of students.

A subject is published after the owner has checked a sample of its
questions by hand. Publishing makes the subject visible and its verified
questions playable. Drafts and retired questions stay as they are.
"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Question, Subject
from app.enums import QuestionStatus, SubjectStatus


class UnknownSubjectError(Exception):
    def __init__(self, slug: str) -> None:
        super().__init__(f"no subject with the slug {slug}")
        self.slug = slug


async def publish_subject(session: AsyncSession, slug: str) -> int:
    """Publish a subject and its verified questions. Safe to run again,
    which is how questions imported later are published.

    Returns how many questions this run published.
    """
    subject = await session.scalar(select(Subject).where(Subject.slug == slug))
    if subject is None:
        raise UnknownSubjectError(slug)
    subject.status = SubjectStatus.PUBLISHED
    result = await session.execute(
        update(Question)
        .where(
            Question.subject_id == subject.id,
            Question.status == QuestionStatus.VERIFIED,
        )
        .values(status=QuestionStatus.PUBLISHED)
        .returning(Question.id)
    )
    await session.flush()
    return len(result.all())
