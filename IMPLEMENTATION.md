# Implementation and verification status

## Implemented

DriftLens compares immutable merge-base/head Git snapshots and reads Python and
Markdown without importing or executing the analyzed project.

- AST facts for public top-level defaults/parameters, bounded constants/imports,
  direct argparse definitions and a constrained retry-count pattern.
- Direct optparse option/group facts with explicit defaults. Implicit/shared
  destinations and set_defaults overrides conservatively abstain.
- Exact Markdown spans, scoped linking, old support/new contradiction checks,
  same-PR documentation correction suppression and conservative exclusions.
- Removed CLI flags in direct `Use --flag` instructions, including backticks.
- A bounded cache filename rule: an old declared two-numeric-field format cannot
  match a new local literal dot-join with more fields. It follows one declared
  helper's structure, not its runtime values. See [CACHE_LAYOUT.md](docs/CACHE_LAYOUT.md).
- JSON/Markdown findings, grouped changes, exact paths/lines/offsets, before/after
  facts, responsible hunks and optional immutable source links.
- Optional local Qwen prose extraction with validated schema/quote/value and
  model/content/prompt-versioned caching.
- CLI, advisory GitHub Actions, MIT license, PR template and Python 3.10/3.12/3.13 CI.

## Latest detector continuation

Local suite: **105 tests passed**, including **21 filename-rule test methods**.
The first positive filename regression failed before implementation. Negatives
cover refactors, corrected docs, ambiguous owners, unknown or shadowed types,
unknown decorators, mutated joins, custom access hooks and unresolved helpers.

All four deterministic demos ran with expected counts **1/0/0/1**. The actual local
Qwen/control suite passed all eight cases with five uncached calls and three
additional findings over the model-off baseline. These synthetic checks are
separate from the historical evaluation.

The full six-case public-history replay now matches **1/3 original positive
labels**, with all three negative controls quiet. Black's exact existing Linux
label matches; Windows and macOS also yield matching stale sentences. These are
three sentences in one code-change group, not three successful historical cases.
The two extra locations were manually reviewed after A/B detection and corroborated
by later C. Labels were not changed. Four existing Black syntax-fixture warnings
remain visible. Positive labels are not exhaustive, so precision is undefined.

The new rule was developed using an already-known Black case. This is a
retrospective development result, not held-out accuracy. No future C content,
repository names, commit IDs or exact case text enter the detector. Actual reports
are in examples/historical/outputs/; [the corpus README](examples/historical/README.md)
explains provenance and limits.

Clean installation, installed historical CLI execution, PR checks and post-merge
main CI are checked before integration sign-off. Always inspect CI for the exact
latest commit rather than substituting an earlier green run.

## Remaining limits

The yt-dlp implicit example and gdown folder-limit cases are still missed.
General computed methods, arbitrary wrappers/callers, complex parsers, broad
configuration frameworks, implicit semantic links and languages beyond Python
remain unsupported. The filename rule assumes the supported declared typing and
library bindings; it does not prove runtime dispatch/subclass overrides or
filesystem normalization. Zero findings does not mean every sentence was verified.

Earlier 49/72/79/84-test and 0/2/0/3 corpus results describe prior versions;
retained verification artifacts preserve those observations. Ordinary CI needs
neither a model server nor API keys. Model weights retain their own license.

Organizer submissions and spoken team rehearsal remain unverified by the agent.
PR #1's empty original description and absent recorded pre-merge checks remain a
historical workflow gap; its post-merge CI passed. No history was rewritten.
