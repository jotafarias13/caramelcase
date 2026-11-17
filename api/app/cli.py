"""The command line of the API: python -m app.cli <command>.

Run by hand, by make and, later, by cron. Each command opens its own
database session and commits once at the end.
"""

import asyncio
import json
import random
from typing import Annotated

import typer

from app.db.base import utc_now
from app.db.session import engine, session_maker
from app.services.catalog_file import CATALOG_FILE_NAME, load_catalog
from app.services.content_import import (
    ImportCounts,
    InvalidBankError,
    import_content,
)
from app.services.demo import (
    DemoUser,
    NoPublishedSubjectError,
    create_demo_user,
)
from app.services.magic_links import create_magic_link, link_url
from app.services.publishing import UnknownSubjectError, publish_subject
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


@cli.command("publish-subjects")
def publish_subjects_command(
    slugs: Annotated[
        list[str] | None,
        typer.Argument(help="The slugs of the subjects to publish."),
    ] = None,
    launch: Annotated[
        bool,
        typer.Option(
            "--launch", help="Publish the launch subjects of the catalog."
        ),
    ] = False,
) -> None:
    """Put subjects in front of students. Safe to run again.

    A subject becomes published, and so does each of its verified
    questions. Run it after the hand check of a subject, and again
    after importing more questions into a published one.
    """
    chosen = list(slugs or [])
    if launch:
        settings = get_settings()
        catalog = load_catalog(settings.content_dir / CATALOG_FILE_NAME)
        chosen += [s.slug for s in catalog.subjects if s.launch]
    if not chosen:
        typer.echo("Name at least one subject, or pass --launch.", err=True)
        raise typer.Exit(code=2)
    try:
        published = asyncio.run(_publish_subjects(chosen))
    except UnknownSubjectError as error:
        typer.echo(f"Nothing published: {error}.", err=True)
        raise typer.Exit(code=1) from error
    for slug, count in published.items():
        typer.echo(f"Published {slug}: {count} more questions.")


async def _publish_subjects(slugs: list[str]) -> dict[str, int]:
    try:
        async with session_maker() as session:
            published = {
                slug: await publish_subject(session, slug) for slug in slugs
            }
            await session.commit()
    finally:
        await engine.dispose()
    return published


@cli.command("demo-user")
def demo_user_command() -> None:
    """Create the demo user with three weeks of history, for a
    development database, and print a link that signs in as it.

    If the demo user exists, only the link is new.
    """
    settings = get_settings()
    if settings.environment == "production":
        typer.echo("The demo user is not for production.", err=True)
        raise typer.Exit(code=1)
    try:
        demo, link = asyncio.run(_demo_user())
    except NoPublishedSubjectError as error:
        typer.echo(
            f"No demo user: {error}. Run publish-subjects first.", err=True
        )
        raise typer.Exit(code=1) from error
    if demo.created:
        typer.echo(f"Created {demo.user.email} with {demo.sessions} sessions.")
    else:
        typer.echo(f"{demo.user.email} was already there.")
    minutes = settings.magic_link_expire_minutes
    typer.echo(f"Sign in as the demo user (valid for {minutes} min):")
    typer.echo(link)


async def _demo_user() -> tuple[DemoUser, str]:
    settings = get_settings()
    now = utc_now()
    try:
        async with session_maker() as session:
            # A fixed seed: the same history on every machine.
            demo = await create_demo_user(
                session, settings, now, random.Random(2026)
            )
            assert demo.user.email is not None
            token = await create_magic_link(
                session, demo.user.email, now, settings
            )
            await session.commit()
    finally:
        await engine.dispose()
    return demo, link_url(token, settings)


@cli.command("openapi")
def openapi_command() -> None:
    """Print the API's OpenAPI schema, which the web app's TypeScript
    types are generated from (make types).
    """
    # Imported here: the other commands do not need the web app.
    from app.main import app  # noqa: PLC0415

    typer.echo(json.dumps(app.openapi(), indent=2, sort_keys=True))


if __name__ == "__main__":
    cli()
