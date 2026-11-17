"""Reading content/catalog.yaml: the subjects and their topics, in the
order they are shown.
"""

from collections import Counter
from pathlib import Path
from typing import Annotated, Self

import yaml
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from app.domain.question_doc import Slug
from app.enums import CodeLanguage

Name = Annotated[str, StringConstraints(min_length=1, max_length=120)]
# The label on a subject's badge: "ed" is shown as "ed/".
Short = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9]+$", max_length=12)
]


class CatalogTopic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    name_pt: Name
    name_en: Name
    # The language of the code in the topic's questions. Kept in the file
    # only: each question's row stores the language of its own code.
    code_language: CodeLanguage
    # What the topic covers, from the syllabus. It tells a question writer
    # where the topic starts and ends. Kept in the file only.
    covers: Annotated[str, StringConstraints(min_length=1)]


class CatalogSubject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    name_pt: Name
    name_en: Name
    short_pt: Short
    short_en: Short
    # A rough guide such as "1 to 2". Kept in the file only.
    typical_year: str
    # True for the subjects V1 launches with.
    launch: bool = False
    # In the order the topics are shown. Empty until the subject is
    # outlined.
    topics: list[CatalogTopic] = []

    @model_validator(mode="after")
    def no_two_topics_share_a_slug(self) -> Self:
        repeated = _repeated([topic.slug for topic in self.topics])
        if repeated:
            raise ValueError(
                f"{self.slug} has more than one topic with the slug: "
                + ", ".join(repeated)
            )
        return self

    def topic(self, slug: str) -> CatalogTopic | None:
        return next((t for t in self.topics if t.slug == slug), None)


class Catalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subjects: list[CatalogSubject]

    @model_validator(mode="after")
    def no_two_subjects_share_a_slug_or_a_badge(self) -> Self:
        for field in ("slug", "short_pt", "short_en"):
            values = [getattr(subject, field) for subject in self.subjects]
            repeated = _repeated(values)
            if repeated:
                raise ValueError(
                    f"{field} is used by more than one subject: "
                    + ", ".join(repeated)
                )
        return self

    def subject(self, slug: str) -> CatalogSubject | None:
        return next((s for s in self.subjects if s.slug == slug), None)


def _repeated(values: list[str]) -> list[str]:
    return sorted(value for value, n in Counter(values).items() if n > 1)


CATALOG_FILE_NAME = "catalog.yaml"


def load_catalog(path: Path) -> Catalog:
    """Read and validate the catalog file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Catalog.model_validate(data)
