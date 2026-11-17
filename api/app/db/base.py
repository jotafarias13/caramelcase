"""The base class of every table: a UUID key, created_at and updated_at.

Conventions every model in app/db/models/ follows:

- Timestamps are TIMESTAMP WITH TIME ZONE and hold UTC.
- An enum from app/enums.py is stored as its text value in a VARCHAR(32).
- A row that belongs to a user is deleted with the user (ON DELETE
  CASCADE). Subjects, topics and questions are never deleted.
- Value rules (ranges, allowed states) are checked in Python; the database
  enforces keys, uniqueness and NOT NULL.
- There are no ORM relationships: queries join explicitly.
"""

import enum
import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar

import sqlalchemy
from sqlalchemy import DateTime, Double, MetaData, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Names for keys, constraints and indexes, so that migrations can refer
# to each one.
NAMING_CONVENTION = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}

ENUM_LENGTH = 32


def utc_now() -> datetime:
    return datetime.now(UTC)


def _created_at_of_the_row(context: DefaultExecutionContext) -> datetime:
    """A new row's updated_at: the same instant as its created_at."""
    # SQLAlchemy does not annotate get_current_parameters.
    parameters = context.get_current_parameters()  # type: ignore[no-untyped-call]
    created_at: datetime = parameters["created_at"]
    return created_at


def _enum_values(enum_class: type[enum.Enum]) -> list[str]:
    """Store an enum by its value ("pt-BR"), not by its name ("PT_BR")."""
    return [str(member.value) for member in enum_class]


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # How a Python type in Mapped[...] becomes a column type.
    type_annotation_map: ClassVar[dict[Any, Any]] = {
        datetime: DateTime(timezone=True),
        float: Double(),
        # none_as_null: Python None is stored as SQL NULL, not JSON null.
        dict[str, Any]: JSONB(none_as_null=True),
        enum.Enum: sqlalchemy.Enum(
            enum.Enum,
            native_enum=False,
            length=ENUM_LENGTH,
            values_callable=_enum_values,
            validate_strings=True,
        ),
    }

    # sort_order puts id first and the two timestamps last in each table.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        sort_order=-1,
    )
    # Set in Python, so that a row has its timestamps as soon as it is
    # flushed. The server defaults cover rows inserted with plain SQL.
    # The two are equal until the row is first updated.
    created_at: Mapped[datetime] = mapped_column(
        default=utc_now, server_default=func.now(), sort_order=998
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=_created_at_of_the_row,
        onupdate=utc_now,
        server_default=func.now(),
        sort_order=999,
    )
