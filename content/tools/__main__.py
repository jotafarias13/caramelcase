"""The command line of the content tools: python -m content.tools.

Exit codes: 0 when every question passed, 1 when a question failed the
check, 2 when the tool could not do its work.
"""

import typer

from content.tools import (
    check_blind,
    common,
    dedupe,
    promote,
    report,
    run_code,
    strip_keys,
    validate,
)

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    # Plain tracebacks: the pretty ones can print local variables.
    pretty_exceptions_enable=False,
    help="The content pipeline's tools. See content/README.md.",
)

# In the order the pipeline runs them.
app.command("validate")(validate.command)
app.command("run-code")(run_code.command)
app.command("dedupe")(dedupe.command)
app.command("strip-keys")(strip_keys.command)
app.command("check-blind")(check_blind.command)
app.command("promote")(promote.command)
app.command("report")(report.command)


def main() -> None:
    try:
        app()
    except common.ToolError as error:
        typer.echo(str(error), err=True)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
