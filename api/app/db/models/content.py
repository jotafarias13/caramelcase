"""Content: subjects, topics, questions and the reports about them.

The files in content/ are the source of truth for question text. These
tables hold the imported text and everything live: status, rating,
statistics, reports. Nothing here is ever deleted.
"""

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums import (
    Locale,
    QuestionStatus,
    QuestionType,
    ReportReason,
    ReportStatus,
    SubjectStatus,
    TopicEdgeKind,
)


class Subject(Base):
    __tablename__ = "subjects"

    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name_pt: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str] = mapped_column(String(120))
    # The label on the subject's badge: "ed" is shown as "ed/".
    short_pt: Mapped[str] = mapped_column(String(12))
    short_en: Mapped[str] = mapped_column(String(12))
    status: Mapped[SubjectStatus] = mapped_column(default=SubjectStatus.DRAFT)
    sort_order: Mapped[int]


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("subject_id", "slug"),)

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))
    slug: Mapped[str] = mapped_column(String(80))
    name_pt: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str] = mapped_column(String(120))
    sort_order: Mapped[int]


class TopicEdge(Base):
    """A link from one topic to another: a prerequisite or a related topic.

    Seeded later. Question selection does not use it in V1.
    """

    __tablename__ = "topic_edges"
    __table_args__ = (
        UniqueConstraint("from_topic_id", "to_topic_id", "kind"),
    )

    from_topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"))
    to_topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id"), index=True
    )
    kind: Mapped[TopicEdgeKind]
    weight: Mapped[float] = mapped_column(default=1.0)


class Question(Base):
    """A question's identity and live numbers. Its text is one row per
    language in question_translations.
    """

    __tablename__ = "questions"
    __table_args__ = (Index(None, "subject_id", "status"),)

    # The stable id in the content files: "estruturas-de-dados.pilhas.0001".
    external_id: Mapped[str] = mapped_column(String(160), unique=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"))
    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id"), index=True
    )
    type: Mapped[QuestionType] = mapped_column(default=QuestionType.MCQ)
    status: Mapped[QuestionStatus] = mapped_column(
        default=QuestionStatus.DRAFT
    )
    # 1 to 5. It only sets the rating the question starts with.
    difficulty_prior: Mapped[int]
    rating: Mapped[float]
    answers_count: Mapped[int] = mapped_column(default=0)
    correct_count: Mapped[int] = mapped_column(default=0)
    # Hash of the question's content in its file (see content_hash in
    # app/domain/question_doc.py); a change bumps version.
    content_hash: Mapped[str] = mapped_column(String(64))
    version: Mapped[int] = mapped_column(default=1)
    # Where the question came from, for example "generated".
    source: Mapped[str] = mapped_column(String(32))


class QuestionTranslation(Base):
    """A question's text in one language."""

    __tablename__ = "question_translations"
    __table_args__ = (UniqueConstraint("question_id", "locale"),)

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    locale: Mapped[Locale]
    stem: Mapped[str] = mapped_column(Text)
    code: Mapped[str | None] = mapped_column(Text)
    code_language: Mapped[str | None] = mapped_column(String(16))
    # What the student answers with. For a multiple-choice question:
    # {"options": [{"key", "text", "is_correct", "reason"}, ...]}.
    payload: Mapped[dict[str, Any]]
    explanation: Mapped[str] = mapped_column(Text)


class QuestionReport(Base):
    """A student saying that something is wrong with a question."""

    __tablename__ = "question_reports"

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # The language the student was reading the question in.
    locale: Mapped[Locale]
    reason: Mapped[ReportReason]
    comment: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ReportStatus] = mapped_column(default=ReportStatus.OPEN)
