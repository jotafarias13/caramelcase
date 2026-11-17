"""Run the API's command lines as a deploy does: in their own process."""

import os
import subprocess
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[2]


def alembic(*args: str, database_url: str) -> subprocess.CompletedProcess[str]:
    """Run `alembic <args>` against one database."""
    return _run_module("alembic", *args, database_url=database_url)


def cli(
    *args: str, database_url: str, content_dir: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Run `python -m app.cli <args>` against one database, reading the
    content from content_dir when it is given.
    """
    return _run_module(
        "app.cli", *args, database_url=database_url, content_dir=content_dir
    )


def output_of(result: subprocess.CompletedProcess[str]) -> str:
    """Everything the command printed, for an assertion message."""
    return f"{result.stdout}\n{result.stderr}"


def _run_module(
    module: str,
    *args: str,
    database_url: str,
    content_dir: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "DATABASE_URL": database_url}
    if content_dir is not None:
        env["CONTENT_DIR"] = str(content_dir)
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=API_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
