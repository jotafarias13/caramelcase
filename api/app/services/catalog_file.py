"""Reading content/catalog.yaml: the subjects, in the order they are shown.

Topics join each subject in milestone 3.
"""

from collections import Counter
from pathlib import Path
from typing import Annotated, Self

import yaml
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

Slug = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", max_length=80)
]
Name = Annotated[str, StringConstraints(min_length=1, max_length=120)]
# The label on a subject's badge: "ed" is shown as "ed/".
Short = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9]+$", max_length=12)
]


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


def _repeated(values: list[str]) -> list[str]:
    return sorted(value for value, n in Counter(values).items() if n > 1)


def load_catalog(path: Path) -> Catalog:
    """Read and validate the catalog file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Catalog.model_validate(data)
