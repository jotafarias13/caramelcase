"""The migrations, run through the alembic command line as a deploy does."""

from app.db import models  # noqa: F401  registers every table on Base
from app.db.base import Base
from tests.support.commands import alembic, output_of
from tests.support.database import run_sql, table_names

ALEMBIC_TABLE = "alembic_version"


async def test_upgrade_creates_every_table_and_downgrade_removes_them(
    scratch_database: str,
) -> None:
    upgrade = alembic("upgrade", "head", database_url=scratch_database)

    assert upgrade.returncode == 0, output_of(upgrade)
    assert await table_names(scratch_database) == {
        *Base.metadata.tables,
        ALEMBIC_TABLE,
    }

    downgrade = alembic("downgrade", "base", database_url=scratch_database)

    assert downgrade.returncode == 0, output_of(downgrade)
    assert await table_names(scratch_database) == {ALEMBIC_TABLE}


async def test_models_and_migrations_agree(database: str) -> None:
    """Fails when a model changed and no migration was written for it.

    Write one with: uv run alembic revision --autogenerate -m "..."
    """
    check = alembic("check", database_url=database)

    assert check.returncode == 0, output_of(check)


async def test_the_check_notices_a_column_the_migrations_lack(
    scratch_database: str,
) -> None:
    """The test above is only worth something if the check can fail."""
    upgrade = alembic("upgrade", "head", database_url=scratch_database)
    assert upgrade.returncode == 0, output_of(upgrade)
    # The state a forgotten migration leaves: the model has the column,
    # the database does not.
    await run_sql(scratch_database, "ALTER TABLE users DROP COLUMN course")

    check = alembic("check", database_url=scratch_database)

    assert check.returncode != 0
    assert "course" in output_of(check)
