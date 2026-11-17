"""report: write content/REPORT.md from the bank and the pipeline log.

The report gives, for every subject that has topics: the number of
questions by topic and difficulty, the share of each difficulty band
against the spec's target (25% level 1 to 2, 50% level 3, 25% level 4
to 5), and the failure rate at each step of the pipeline.
"""

from collections import Counter
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from app.domain.question_doc import (
    DIFFICULTY_MAX,
    DIFFICULTY_MIN,
    QuestionDoc,
)
from app.enums import Locale
from app.services.catalog_file import Catalog, CatalogSubject
from app.services.question_files import read_question_files
from app.settings import get_settings
from content.tools import common, run_log
from content.tools.run_code import has_code_to_run
from content.tools.run_log import LogEntry, Step

REPORT_FILE_NAME = "REPORT.md"

LEVELS = range(DIFFICULTY_MIN, DIFFICULTY_MAX + 1)
# The difficulty bands of the spec's target spread: name, levels.
BANDS: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("Level 1 to 2", (1, 2)),
    ("Level 3", (3,)),
    ("Level 4 to 5", (4, 5)),
)

_STEP_NAMES = {
    Step.VALIDATE: "Validate",
    Step.RUN_CODE: "Run code",
    Step.DEDUPE: "Dedupe",
    Step.BLIND_SOLVE: "Blind solve",
    Step.PROMOTE: "Promote (failed means dropped)",
}


def build_report(
    docs: Sequence[QuestionDoc],
    entries: Sequence[LogEntry],
    catalog: Catalog,
    written_on: date,
) -> str:
    """The whole report, as Markdown."""
    subjects = [subject for subject in catalog.subjects if subject.topics]
    parts = [
        "# Question bank report",
        f"Written by `python -m content.tools report` on {written_on}, "
        "from `content/bank/` and `content/pipeline-log.jsonl`. Run the "
        "tool again instead of editing this file.",
        "## Totals",
        _totals_table(docs, subjects),
        "The target spread is 25% level 1 to 2, 50% level 3 and 25% level "
        '4 to 5. "Code run" counts the questions whose code the run-code '
        'tool executed and checked. "Key is longest" looks only at the '
        "questions in which one option is longer than the other three, in "
        "Portuguese, and gives the share of them whose longest option is "
        "the correct one: near 25% when length does not give the answer "
        "away.",
    ]
    for subject in subjects:
        parts += [
            f"## {subject.name_pt}",
            _topics_table(
                [doc for doc in docs if doc.subject == subject.slug], subject
            ),
        ]
    parts += [
        "## Pipeline",
        "Failure rate at each step, over every check the tools logged. A "
        "question that failed and was repaired is checked again, so it "
        "counts once per check. A question that fails Promote did not "
        "reach the bank.",
        _pipeline_table(entries, subjects),
    ]
    return "\n\n".join(parts) + "\n"


def _totals_table(
    docs: Sequence[QuestionDoc], subjects: Sequence[CatalogSubject]
) -> str:
    rows = []
    for subject in subjects:
        subject_docs = [doc for doc in docs if doc.subject == subject.slug]
        rows.append(_totals_row(subject.name_pt, subject_docs))
    in_report = {subject.slug for subject in subjects}
    rows.append(
        _totals_row("**Total**", [d for d in docs if d.subject in in_report])
    )
    return _table(
        [
            "Subject",
            "Questions",
            *(name for name, _ in BANDS),
            "With code",
            "Code run",
            "Key is longest",
            "Human-checked",
        ],
        rows,
    )


def _totals_row(name: str, docs: Sequence[QuestionDoc]) -> list[str]:
    with_a_longest = [doc for doc in docs if _has_a_longest_option(doc)]
    return [
        name,
        str(len(docs)),
        *_band_shares(docs),
        str(sum(1 for doc in docs if doc.code() is not None)),
        str(sum(1 for doc in docs if has_code_to_run(doc))),
        _share(
            sum(1 for doc in with_a_longest if _key_is_longest(doc)),
            len(with_a_longest),
        ),
        str(sum(1 for doc in docs if doc.verification.human_checked)),
    ]


def _topics_table(docs: Sequence[QuestionDoc], subject: CatalogSubject) -> str:
    rows = []
    for topic in subject.topics:
        topic_docs = [doc for doc in docs if doc.topic == topic.slug]
        rows.append(_topic_row(topic.name_pt, topic_docs))
    rows.append(_topic_row("**Total**", docs))
    return _table(
        [
            "Topic",
            "Questions",
            *(f"L{level}" for level in LEVELS),
            *(name for name, _ in BANDS),
        ],
        rows,
    )


def _topic_row(name: str, docs: Sequence[QuestionDoc]) -> list[str]:
    by_level = Counter(doc.difficulty_prior for doc in docs)
    return [
        name,
        str(len(docs)),
        *(str(by_level[level]) for level in LEVELS),
        *_band_shares(docs),
    ]


def _band_shares(docs: Sequence[QuestionDoc]) -> list[str]:
    return [
        _share(
            sum(1 for doc in docs if doc.difficulty_prior in levels), len(docs)
        )
        for _, levels in BANDS
    ]


def _has_a_longest_option(doc: QuestionDoc) -> bool:
    """True when one option is longer than the other three. Options such
    as 12, 23, 24 and 31 have no longest one.
    """
    lengths = [
        len(option.text) for option in doc.locales[Locale.PT_BR].options
    ]
    return lengths.count(max(lengths)) == 1


def _key_is_longest(doc: QuestionDoc) -> bool:
    options = doc.locales[Locale.PT_BR].options
    longest = max(len(option.text) for option in options)
    return all(
        len(option.text) < longest
        for option in options
        if option.key != doc.correct_key
    )


def _pipeline_table(
    entries: Sequence[LogEntry], subjects: Sequence[CatalogSubject]
) -> str:
    rows = []
    for subject in subjects:
        for step in Step:
            of_step = [
                entry
                for entry in entries
                if entry.subject == subject.slug and entry.step is step
            ]
            if not of_step:
                continue
            checked = sum(entry.checked for entry in of_step)
            failed = sum(len(entry.failed) for entry in of_step)
            rows.append(
                [
                    subject.name_pt,
                    _STEP_NAMES[step],
                    str(checked),
                    str(failed),
                    _share(failed, checked),
                ]
            )
    if not rows:
        return "No pipeline run is logged yet."
    return _table(
        ["Subject", "Step", "Checked", "Failed", "Failure rate"], rows
    )


def _share(part: int, whole: int) -> str:
    """part of whole as a percentage; a dash when there is nothing."""
    if whole == 0:
        return "-"
    return f"{round(100 * part / whole)}%"


def _table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


def command(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Where to write. Default: content/REPORT.md.",
        ),
    ] = None,
) -> None:
    """Write content/REPORT.md from the bank and the pipeline log."""
    lines, problems = read_question_files([common.bank_dir()])
    if problems:
        typer.echo(common.problem_list(problems), err=True)
        typer.echo(
            f"report: {common.count(len(problems), 'problem')} in the "
            "bank; the lines above are left out of the report.",
            err=True,
        )
    target = output or get_settings().content_dir / REPORT_FILE_NAME
    report = build_report(
        [line.doc for line in lines],
        run_log.read_entries(run_log.pipeline_log_path()),
        common.catalog(),
        date.today(),
    )
    target.write_text(report, encoding="utf-8")
    typer.echo(
        f"report: {common.count(len(lines), 'question')}; written to {target}."
    )
