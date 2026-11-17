# content

The question bank and the tools that check it. The files here are the source of truth for question text; the database is the source of truth for everything live (rating, statistics, status, reports).

| Path | Contents | Arrives in |
| --- | --- | --- |
| `catalog.yaml` | Subjects and topics | Milestone 2 (subjects), milestone 3 (topics) |
| `prompts/` | Generation and blind-solve instructions | Milestone 3 |
| `tools/` | validate, strip-keys, run-code, dedupe, report | Milestone 3 |
| `bank/<subject>/<topic>.jsonl` | One question per line | Milestone 4 |
| `REPORT.md` | Counts and failure rates of the last pipeline run | Milestone 4 |
