"""Run a question's SQL in an empty SQLite database and print its rows.

run-code starts this file as its own process: python sql_runner.py
<file>. It imports nothing from the project.

Each statement runs in order. A statement that returns rows prints one
line per row, the columns separated by "|" and NULL written as NULL, the
way the sqlite3 shell does. Foreign keys are enforced, as in the SQL the
course teaches. An error stops the run with exit code 1.
"""

import sqlite3
import sys
from pathlib import Path


def statements_of(sql: str) -> list[str]:
    """Split the text into statements, each ending at its own semicolon.

    Not every semicolon ends a statement: there are semicolons inside
    strings and inside a trigger's body. sqlite3.complete_statement knows
    the difference.
    """
    statements = []
    current = ""
    for char in sql:
        current += char
        if char == ";" and sqlite3.complete_statement(current):
            statements.append(current.strip())
            current = ""
    if current.strip():
        # The last statement has no semicolon.
        statements.append(current.strip())
    return statements


def cell(value: object) -> str:
    return "NULL" if value is None else str(value)


def main(sql_file: str) -> int:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    for statement in statements_of(Path(sql_file).read_text(encoding="utf-8")):
        try:
            cursor = connection.execute(statement)
        except sqlite3.Error as error:
            print(f"{type(error).__name__}: {error}", file=sys.stderr)
            return 1
        if cursor.description is not None:
            for row in cursor:
                print("|".join(cell(value) for value in row))
    connection.commit()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
