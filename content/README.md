# content

The question bank and the tools that check it. The files here are the source of truth for question text; the database is the source of truth for everything live (rating, statistics, status, reports).

| Path | Contents |
| --- | --- |
| `catalog.yaml` | The 20 subjects in catalog order, and the topics of the subjects outlined so far, each with its code language. `python -m app.cli seed` copies subjects and topics to the database |
| `bank/<subject>/<topic>.jsonl` | The question bank: one question per line, every one through the whole pipeline. `python -m app.cli import-content` copies it to the database |
| `work/<subject>/<topic>.jsonl` | Questions still in the pipeline. Not committed |
| `prompts/generate.md` | Instructions for the agent that writes, or repairs, the questions of one topic |
| `prompts/blind-solve.md` | Instructions for the agent that answers a stripped file |
| `tools/` | The pipeline's tools: `python -m content.tools` |
| `pipeline-log.jsonl` | What each step checked and what failed. Committed: it is the only record of the questions that were repaired or dropped |
| `REPORT.md` | Counts by subject, topic and difficulty, and the failure rate of each step. Written by the `report` tool |

## A question

A question is one JSON object on one line. Its format is `QuestionDoc` in `api/app/domain/question_doc.py`, the one definition that the tools and the importer share; `prompts/generate.md` shows a full line and says what each field is for. The limits (characters in a stem, an option, a reason, an explanation; lines of code) are settings in `api/app/settings.py`.

Beyond the spec's sample line, a question with code has a `code_check`:

| `code_check` | What `run-code` does |
| --- | --- |
| `output` | Runs the code. What it prints must be the text of the correct option, in both languages |
| `runs` | Runs the code, which must finish without an error |
| `skip` | Nothing: the code is a fragment or fails on purpose |

`verification` records what the pipeline found: `blind_key` and `blind_agrees` from the blind solve, `code_ran` from the code run, and `human_checked`, which the owner sets by hand. A question is in the bank only with `blind_agrees` true and, when its code is run, `code_ran` true.

## The tools

They run from the repository root, in the API's environment:

```sh
uv run --project api python -m content.tools --help
```

In the commands below, `tools` stands for `uv run --project api python -m content.tools`.

| Command | What it does |
| --- | --- |
| `tools validate <paths>` | Checks each line against the format and the catalog. `--verified` also requires every question to have passed the pipeline |
| `tools run-code <paths>` | Runs the code of each question as its `code_check` says and records `code_ran` |
| `tools dedupe <paths> --against content/bank` | Flags questions whose stem and code nearly repeat an earlier question of the subject. Code has its own, higher threshold, because short programs share their frame |
| `tools strip-keys <file>` | Writes `<topic>.stripped.jsonl`: the questions without key, reasons or explanation |
| `tools check-blind <file>` | Compares `<topic>.answers.jsonl` with the keys and records `blind_key` and `blind_agrees` |
| `tools promote <files>` | Moves the questions that passed everything to `bank/`; the others stay behind |
| `tools report` | Writes `REPORT.md` |

- Exit code 0 means every question passed, 1 means some failed (each is printed with its id and the reason), 2 means the tool could not work, for example on a file with a broken line.
- `--log` adds the result to `pipeline-log.jsonl`. Use it on the runs that count, once per step and round, and leave it out while trying things: the failure rates in the report are computed from the log.
- `--dry-run` on `run-code` and `check-blind` checks without writing to the question file.
- `run-code` needs a C compiler as `cc`. It compiles with warnings as errors and the address and undefined-behaviour sanitizers, runs Python in the tools' interpreter and SQL in an empty SQLite database, and runs everything five times, each Python run with another hash seed: output that changes between runs fails. It is not a sandbox: the code runs as you.

## The pipeline, for one topic

Generation and blind solving run in subagents; everything else is a tool. `F` is `content/work/<subject>/<topic>.jsonl`.

1. **Generate.** A subagent follows `prompts/generate.md`. Its task message names the subject, the topic, how many questions and the first id number: 1 for a new topic, otherwise one more than the highest number the topic ever used. It writes `F` and runs the checks itself, without `--log`. It changes nothing else in the repository and does not commit.
2. **Check.** `tools validate F --log`, then `tools run-code F --log`, then `tools dedupe F --against content/bank --log`.
3. **Blind solve.** `tools strip-keys F`, then `chmod 000 F`, and the same for whatever script the generator left in a scratch directory: while the solver works, no file with the keys can be opened. A fresh subagent follows `prompts/blind-solve.md`. Its task message names the stripped file and says that this file and the prompt are the only ones it opens, the reading that `CLAUDE.md` asks for before other work included: an agent that has seen `F` or the bank cannot be the solver. It writes `<topic>.answers.jsonl`. Then `chmod 644 F` and `tools check-blind F --log`.
4. **Repair, once.** If steps 2 and 3 printed failures, a subagent follows the repair section of `prompts/generate.md` with the failed ids and their reasons, as the tools printed them. Then steps 2 and 3 run again on `F`, with a new blind solver.
5. **Promote.** `tools promote F --log`. Questions that still fail are dropped: they stay in `content/work/`, and the log counts them.
6. **Report.** After the last topic of a run, `tools report`, and commit `bank/`, `pipeline-log.jsonl` and `REPORT.md` together.

A disagreement is never waved through: a question reaches the bank only by passing, and there is no way to promote one by hand short of editing its `verification`, which nobody does.

## Into the database

```sh
make import-content        # python -m app.cli import-content, in the api container
```

The importer checks the whole bank first and imports nothing if a line fails. Then it creates new questions (as `verified` in a launch subject, as `draft` elsewhere), rewrites questions whose content changed and adds 1 to their version, and retires questions that are no longer in the files. `--dry-run` shows the counts and saves nothing. `docs/RUNBOOK.md` has the details.

A test in `api/tests/test_content_bank.py` runs the same check on `content/bank/` in CI.
