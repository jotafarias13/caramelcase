"""The command line of the API: python -m app.cli <command>.

Run by hand, by make and, later, by cron. Each command opens its own
database session and commits once at the end.
"""

import asyncio
from typing import Annotated

import typer

from app.db.session import engine, session_maker
from app.services.content_import import (
    ImportCounts,
    InvalidBankError,
    import_content,
)
from app.services.seed import SeedCounts, seed_all
from app.settings import get_settings

cli = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    # Plain tracebacks: the pretty ones can print local variables.
    pretty_exceptions_enable=False,
)


@cli.callback()
def main() -> None:
    """Commands of the CaramelCase API."""


@cli.command()
def seed() -> None:
    """Write the plans, feature flags, subjects and topics. Safe to run
    again.
    """
    counts = asyncio.run(_seed())
    typer.echo(
        f"Seeded: {counts.plans} plans, {counts.flags} feature flags, "
        f"{counts.subjects} subjects, {counts.topics} topics."
    )


async def _seed() -> SeedCounts:
    try:
        async with session_maker() as session:
            counts = await seed_all(session, get_settings())
            await session.commit()
    finally:
        await engine.dispose()
    return counts


@cli.command("import-content")
def import_content_command(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Show what would change and save nothing."
        ),
    ] = False,
) -> None:
    """Bring the questions in line with content/bank. Safe to run again.

    New questions are created, changed ones get their new text and a
    higher version, and questions no longer in the files are retired.
    """
    try:
        counts = asyncio.run(_import_content(dry_run))
    except InvalidBankError as error:
        for problem in error.problems:
            typer.echo(problem, err=True)
        typer.echo(f"Nothing imported: {error}.", err=True)
        raise typer.Exit(code=1) from error

    start = "Dry run, nothing saved. Would import" if dry_run else "Imported"
    typer.echo(
        f"{start}: {counts.created} created, {counts.updated} updated, "
        f"{counts.unchanged} unchanged, {counts.retired} retired."
    )
    if counts.left_retired:
        typer.echo(
            "In the files but retired in the database, and left retired: "
            + ", ".join(counts.left_retired)
        )


async def _import_content(dry_run: bool) -> ImportCounts:
    try:
        async with session_maker() as session:
            counts = await import_content(session, get_settings())
            if dry_run:
                await session.rollback()
            else:
                await session.commit()
    finally:
        await engine.dispose()
    return counts


if __name__ == "__main__":
    cli()
