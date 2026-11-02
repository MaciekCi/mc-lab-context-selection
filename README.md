# What should AI actually read?

An offline evidence-selection demo and saved results from E008, by Maciej Ciezki. Original synthetic refunds, service bookings and invoice approvals. No real customer data, API credentials or external actions.

Read the [full report (PDF)](publishing/report.pdf), [Markdown](publishing/report.md) or [HTML](publishing/report.html). The report is the same final publication artifact; its private-workspace commands are separate from the public `demo.py` command below.

## Try it

Open `demo.html` in a browser to compare saved outputs. The explorer works offline and makes no API calls. It contains measured model answers, not a live AI service.

With Python 3.9 or newer, no packages to install:

```sh
python3 demo.py --case R-867 --strategy linked
python3 demo.py --case R-867 --strategy search --output prompt.txt
```

Inspect the selected source IDs and prompt. `whole` supplies all documents; `search` uses BM25 top five; `linked` brings the named record, its associated documents and the CURRENT policy, then fills to eight with BM25. It relies on structured titles/IDs; it is not general semantic retrieval. The public command never sends the prompt anywhere.

## What was measured

Three folders of 124 short documents each. Four development cases and 16 held-out cases per domain. Two solver models (`gpt-6-luna`, `gpt-6.1-sol`), low reasoning, 2048 output-token cap, default sampling, two attempts per held-out case. Five context approaches also include a Sol-generated question-blind reusable brief and brief plus linked search. There are 960 primary outputs, 120 development outputs, 48 smaller-folder diagnostic outputs and three briefing calls.

`results.json` contains actual counts, timings, usage and usage-priced charges. Primary success requires correct decision/value and all three required source references; decision-only counts are separate. A source ID in a briefing is a reference, not proof that all prose is entailed. No model judge is used. Shared input caching reflects actual billing. Standalone cost scenarios charge full brief preparation; those rows are not additive experiment spending.

## Reproduce or adapt

`context_data.build()` regenerates the exact synthetic folders and labels with a fixed seed. `context_engine.select`, `prompt` and `grade` provide the context assembly, common answer contract and deterministic scoring. The offline explorer includes all held-out first-attempt outputs for inspection. Source and export hashes are in `export-manifest.json`.

For a fresh model evaluation, keep development separate, freeze context selection and brief creation before held-out answers, shuffle/interleave approaches, repeat the tasks, and preserve all usage/errors. You must provide your own model access and spending controls. This export intentionally contains no credential-reading or paid-execution adapter. Model/API usage and any runner costs still apply if you add live inference. The original study used an atomic local budget gate; a provider dashboard alert alone is not a hard cap. Aliases and provider behavior may change, so a rerun need not reproduce identical answers or cost.

## Limits

This is a compact synthetic workflow case study, not production validation or a universal ranking of context methods/models. The 48 cases reuse 30 domain/rule patterns; repeats are not new independent tasks. The original uncertainty analysis clusters by those patterns. Folders are approximately 66 KB each, not million-token contexts. Basic keyword retrieval is only one simple baseline, not all retrieval systems. Real deployments still need document permissions, updates/versioning, file parsing, injection defenses, monitoring, and human review of consequential decisions.

MIT license for original work. See THIRD_PARTY.md. No live booking, payment, message or publication is performed by this code.
