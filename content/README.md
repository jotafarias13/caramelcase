# content

The question bank and the tools that check it. The files here are the source of truth for question text; the database is the source of truth for everything live (rating, statistics, status, reports).

| Path | Contents | Arrives in |
| --- | --- | --- |
| `catalog.yaml` | The 20 subjects, in catalog order. `python -m app.cli seed` copies them to the database as drafts | Here since milestone 2; topics join in milestone 3 |
| `prompts/` | Generation and blind-solve instructions | Milestone 3 |
| `tools/` | validate, strip-keys, run-code, dedupe, report | Milestone 3 |
| `bank/<subject>/<topic>.jsonl` | One question per line | Milestone 4 |
| `REPORT.md` | Counts and failure rates of the last pipeline run | Milestone 4 |
