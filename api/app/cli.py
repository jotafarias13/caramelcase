"""The command line of the API: python -m app.cli <command>.

Run by hand, by make and, later, by cron. Each command opens its own
database session and commits once at the end.
"""

import asyncio

import typer

from app.db.session import engine, session_maker
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
    """Write the plans, feature flags and subjects. Safe to run again."""
    counts = asyncio.run(_seed())
    typer.echo(
        f"Seeded: {counts.plans} plans, {counts.flags} feature flags, "
        f"{counts.subjects} subjects."
    )


async def _seed() -> SeedCounts:
    try:
        async with session_maker() as session:
            counts = await seed_all(session, get_settings())
            await session.commit()
    finally:
        await engine.dispose()
    return counts


if __name__ == "__main__":
    cli()
