"""Importing the question bank (content/bank) into the database.

The files are the source of truth for a question's text; the database is
the source of truth for everything live. So the importer:

- creates a question it has not seen, by its id (questions.external_id):
  as verified in a launch subject, as a draft in any other;
- rewrites the text of a question whose content changed, and adds 1 to
  its version;
- leaves an unchanged question alone;
- retires a question that is no longer in the files. Nothing is deleted.

It never touches a question's counts, and its rating only while nobody
has answered it. It sets a status in two cases only: on creating a
question, and when a retired question comes back with new content, which
starts over as if created.

The whole bank is checked first: one bad line and nothing is imported.
The caller commits.
"""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Question, QuestionTranslation, Subject, Topic
from app.domain.question_doc import QuestionDoc, content_hash
from app.enums import QuestionStatus
from app.services.catalog_file import CATALOG_FILE_NAME, Catalog, load_catalog
from app.services.question_files import BANK_DIR_NAME, Problem, load_bank
from app.services.seed import seed_catalog
from app.settings import Settings


@dataclass(frozen=True)
class ImportCounts:
    created: int
    updated: int
    unchanged: int
    retired: int
    # Ids that are in the files, unchanged, and retired in the database.
    # They stay retired: someone retired them on purpose, or a file went
    # missing for one import and came back.
    left_retired: tuple[str, ...]


class InvalidBankError(Exception):
    """The question bank cannot be imported as it is."""

    def __init__(self, problems: Sequence[Problem | str]) -> None:
        noun = "problem" if len(problems) == 1 else "problems"
        super().__init__(f"{len(problems)} {noun} in the question bank")
        self.problems = [str(problem) for problem in problems]


async def import_content(
    session: AsyncSession, settings: Settings
) -> ImportCounts:
    """Check the bank under settings.content_dir and import it."""
    catalog = load_catalog(settings.content_dir / CATALOG_FILE_NAME)
    bank_dir = settings.content_dir / BANK_DIR_NAME
    lines, problems = load_bank(bank_dir, catalog)
    if problems:
        raise InvalidBankError(problems)
    if not lines:
        # An empty bank would retire every question in the database.
        raise InvalidBankError([f"no questions under {bank_dir}"])

    # Questions point at subjects and topics, so those come first.
    await seed_catalog(session, catalog)
    return await import_questions(
        session, [line.doc for line in lines], catalog, settings
    )


async def import_questions(
    session: AsyncSession,
    docs: Sequence[QuestionDoc],
    catalog: Catalog,
    settings: Settings,
) -> ImportCounts:
    """Make the questions table match the docs. The docs are valid and
    their subjects and topics exist in the database.
    """
    topic_ids = await _topic_ids(session)
    existing = {
        question.external_id: question
        for question in await session.scalars(select(Question))
    }

    created: list[tuple[Question, QuestionDoc]] = []
    updated: list[tuple[Question, QuestionDoc]] = []
    unchanged = 0
    left_retired: list[str] = []
    for doc in docs:
        new_hash = content_hash(doc)
        question = existing.get(doc.id)
        if question is None:
            subject_id, topic_id = topic_ids[doc.subject, doc.topic]
            question = Question(
                external_id=doc.id,
                subject_id=subject_id,
                topic_id=topic_id,
                status=_first_status(doc, catalog),
                rating=_starting_rating(doc, settings),
                version=doc.version,
            )
            _write_content(question, doc, new_hash)
            session.add(question)
            created.append((question, doc))
        elif question.content_hash != new_hash:
            _write_content(question, doc, new_hash)
            question.version += 1
            if question.answers_count == 0:
                question.rating = _starting_rating(doc, settings)
            if question.status is QuestionStatus.RETIRED:
                question.status = _first_status(doc, catalog)
            updated.append((question, doc))
        else:
            unchanged += 1
            if question.status is QuestionStatus.RETIRED:
                left_retired.append(doc.id)

    # The new questions get their ids, which their translations point at.
    await session.flush()
    await _write_translations(session, created + updated)

    ids_in_files = {doc.id for doc in docs}
    retired = 0
    for external_id, question in existing.items():
        gone = external_id not in ids_in_files
        if gone and question.status is not QuestionStatus.RETIRED:
            question.status = QuestionStatus.RETIRED
            retired += 1
    await session.flush()

    return ImportCounts(
        created=len(created),
        updated=len(updated),
        unchanged=unchanged,
        retired=retired,
        left_retired=tuple(left_retired),
    )


def _first_status(doc: QuestionDoc, catalog: Catalog) -> QuestionStatus:
    """The status of a question entering the database. Every question in
    the bank passed the pipeline; outside the launch subjects it still
    waits, as a draft, for a subject that is not ready.
    """
    subject = catalog.subject(doc.subject)
    if subject is not None and subject.launch:
        return QuestionStatus.VERIFIED
    return QuestionStatus.DRAFT


def _starting_rating(doc: QuestionDoc, settings: Settings) -> float:
    return settings.question_rating_by_prior[doc.difficulty_prior - 1]


def _write_content(
    question: Question, doc: QuestionDoc, new_hash: str
) -> None:
    question.type = doc.type
    question.difficulty_prior = doc.difficulty_prior
    question.source = doc.source
    question.content_hash = new_hash


async def _write_translations(
    session: AsyncSession, changed: Sequence[tuple[Question, QuestionDoc]]
) -> None:
    """Write the text of each question, one row per language."""
    question_ids = [question.id for question, _ in changed]
    existing = {
        (translation.question_id, translation.locale): translation
        for translation in await session.scalars(
            select(QuestionTranslation).where(
                QuestionTranslation.question_id.in_(question_ids)
            )
        )
    }
    for question, doc in changed:
        for locale, text in doc.locales.items():
            translation = existing.get((question.id, locale))
            if translation is None:
                translation = QuestionTranslation(
                    question_id=question.id, locale=locale
                )
                session.add(translation)
            translation.stem = text.stem
            translation.code = text.code
            translation.code_language = (
                doc.code_language.value if doc.code_language else None
            )
            translation.payload = {
                "options": [
                    {
                        "key": option.key,
                        "text": option.text,
                        "is_correct": option.key == doc.correct_key,
                        "reason": option.reason,
                    }
                    for option in text.options
                ]
            }
            translation.explanation = text.explanation
    await session.flush()


async def _topic_ids(
    session: AsyncSession,
) -> dict[tuple[str, str], tuple[uuid.UUID, uuid.UUID]]:
    """(subject slug, topic slug) -> (subject id, topic id)."""
    rows = await session.execute(
        select(Subject.slug, Topic.slug, Subject.id, Topic.id).join(
            Topic, Topic.subject_id == Subject.id
        )
    )
    return {
        (subject_slug, topic_slug): (subject_id, topic_id)
        for subject_slug, topic_slug, subject_id, topic_id in rows
    }
