# DriftLens

Find the documentation claim a Python change made false, with the before/after
facts and responsible diff. DriftLens reads Git objects without importing or
executing analyzed repository code.

A finding requires **old support + a contradictory code change + the same claim
still present in current documentation**. Findings are advisory by default.

## Package release status

PyPI publication is being prepared under the proposed name `driftlens-docs`.
It is not yet verified as published. The PyPI package named `driftlens` is an
unrelated project. Continue using the source installation below until release
verification is complete. See [publishing setup](docs/PUBLISHING.md).

## Quick start

First-time setup, Windows PowerShell commands, report interpretation and
troubleshooting: [getting started](docs/GETTING_STARTED.md).

Python 3.10+ and Git are required. The analyzer has no third-party runtime dependencies.
From this checkout:

```sh
python3 -m driftlens --repo /path/to/repository --base main --head feature \
  --json report.json --summary report.md
```

Or install the CLI in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
driftlens --repo /path/to/repository --base main --head feature
```

Use commits or branch names for `--base` and `--head`. The base is resolved to the
merge base with the head; dirty working files are ignored. Fetch enough history
before analyzing a shallow clone. Add `--repository-url https://github.com/OWNER/REPO`
for commit-pinned source links. Exit codes: 0 for completed advisory analysis,
1 for findings when `--fail-on-drift` is explicitly supplied, 2 for input/analysis
errors. Explicit revision arguments take precedence over an inherited GitHub PR
event; use `--github-event` to explicitly fill missing revisions from an event.
Warnings and abstentions remain visible in reports; zero findings does
not mean every documentation claim was verified.

Snapshot collection preflights up to 20,000 eligible files, 100 MiB total and
10 MiB per file. Configure `--max-files`, `--max-bytes` and `--max-file-bytes`
for larger repositories. `--snapshot-timeout` defaults to 180 seconds per
snapshot and is checked between Git operations; each Git operation also has a
60-second timeout. These are collection limits, not a hard deadline for AST or
model analysis. Exceeding a limit exits 2 without issuing a partial report.

## Run the demos and tests

```sh
python3 -m examples.demo
python3 -m unittest discover -v
```

The demo creates isolated, synthetic Git histories in temporary directories and
writes actual results to [examples/outputs](examples/outputs). Its inputs are in
[examples/cases.json](examples/cases.json). The four expected outcomes are:

- `drift-detected`: a default changes from 30 to 10; one finding.
- `documentation-fixed`: the same change updates its docs; no finding.
- `harmless-refactor`: only formatting/comments change; no finding.
- `removed-flag`: a documented argparse option disappears; one finding.

The synthetic commit IDs in these reports are local fixture IDs, not public
GitHub commits. Runtime varies by machine. These fixtures are regression tests,
not a historical accuracy benchmark.

## Supported checks

- Literal scalar defaults on public, top-level Python functions, including
  positional-only and keyword-only parameters.
- Removed named parameters within an existing function; `**kwargs` compatibility
  causes abstention.
- Removed argparse flags and changed explicit defaults in direct, module-level
  `ArgumentParser` / `add_argument` definitions. Retained aliases and potentially
  compatible long-option abbreviations are respected.
- Direct optparse options/groups in public function bodies with explicit scalar
  defaults and a single declaration per destination. Implicit defaults, shared
  destinations and set_defaults overrides abstain; no Boolean defaults are inferred.
- Declared cache filename layouts: two typed numeric fields versus a new local
  fixed-list dot-joined key with more fields. Exact unique template linking and
  mutation/type guards apply; [bounded rule details](docs/CACHE_LAYOUT.md).
- Simple module constants and `from module import CONSTANT` dependencies with a
  maximum of two resolution hops. Constant changes carry the dependency's diff.
- One constrained retry pattern: a literal `range(N)` loop around `try: return
  call()` / `except NamedError: pass`, followed by a raise. Documentation must
  explicitly name the function, exception and maximum retry count.
- Markdown sentences, ATX headings and simple pipe tables, with original Unicode
  character offsets (zero-based, end-exclusive) and one-based line numbers.

Exact symbol/parameter or flag references, or an unambiguous declared filename
template, link documentation to facts. Unchanged
Markdown files are searched too. A table's header supplies its column semantics.
Identical old/current claims and heading context establish continuity; modified
or newly added passages are conservatively left unverified.

The JSON contains findings, old/current claim spans, structured facts, dependency
locations, relevant diff hunks, stable IDs, change-group IDs, optional links,
abstentions, warnings and runtime counters. Repeated claims are grouped in the
readable summary while each exact location remains in JSON.

## Optional local model

The integration targets `qwen2.5-coder:3b` through Ollama's local `/api/chat`
endpoint. Set up and start Ollama separately, then:

```sh
ollama pull qwen2.5-coder:3b
python3 -m driftlens --base main --head feature --model \
  --cache .driftlens-cache --json report.json
```

The model only interprets otherwise unresolved default prose already linked by
exact references. It receives the exact passage, heading, immutable revisions,
structured facts, old/new code, dependency lines and diff hunks. Repository text
is explicitly untrusted data. JSON schema, cited quote, subject, property,
literal value and verdicts are validated; static old/new facts must still agree.
Model self-confidence is never treated as evidence. Failures produce warnings and
abstentions, not invented findings. No repository code or model-suggested command
is executed.

The optional cache includes analyzer version, prompt/schema, complete evidence
and the installed model's digest, so changing the model behind a tag invalidates
cached results. A digest lookup failure disables that analysis with a warning.
Only localhost HTTP endpoints are accepted.

**Live local inference has been demonstrated.** On an Apple M3 with 8 GB RAM,
Qwen added three verified findings missed by the deterministic baseline; all five
controls stayed quiet in a developer-selected synthetic suite. Five uncached
requests were made across eight cases; three controls were filtered before any
model call. Model-enabled case runtimes were 1.87–2.71 seconds on this run. This
is not a real-history accuracy benchmark. The initial failed run is retained.
See [commands, hardware and actual evidence](docs/LOCAL_AI.md). Unit tests still
use explicitly identified test doubles; they are separate from these live runs.
The deterministic pipeline and hosted CI work without Ollama.

API reference: [Ollama chat](https://docs.ollama.com/api/chat).

## GitHub Actions

[CI](.github/workflows/ci.yml) runs tests, demos and packaging checks on Python
3.10, 3.12 and 3.13, validates wheel/source metadata, and checks installed
finding and corrected-doc behavior outside the checkout. The [advisory drift workflow](.github/workflows/driftlens.yml)
uses `pull_request`, reads the actual PR head from the event, and runs the analyzer
from a separate trusted base checkout. It reads the target checkout only as Git
objects. No model, secrets, PR comments or write token are required.

The first implementation PR displays a bootstrap message because the base branch
does not yet have an analyzer. Subsequent PRs get a job summary, up to 50 workflow
annotations, and a complete JSON artifact keyed by head SHA. Findings in unchanged
docs stay in the summary even when GitHub cannot display them inline. Reruns
replace the active workflow run for that PR and use stable finding IDs.

The CI test job intentionally tests proposed project code in an unprivileged
runner; the separate drift job does not execute analyzed target code. Do not
convert this workflow to privileged `pull_request_target` execution of PR code.
See [GitHub PR event behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request).

## Historical evaluation

Create a JSON manifest with a `cases` array. Each case contains `id`, `repo`
(relative to the manifest), `before` (A), `drift` (B), optional `correction` (C),
`split` (`development` or `evaluation`), and `expected` labels. Each label requires
`path`, `symbol` and `category`; add `quote`, `name`, `line_start` and `start` to
measure exact localization. Set `fully_reviewed: true` only when every prediction
and expected finding for that case has been manually reviewed.

```json
{
  "cases": [{
    "id": "timeout-change",
    "repo": "../sample-repo",
    "before": "BEFORE_COMMIT",
    "drift": "DRIFT_COMMIT",
    "correction": "LATER_DOC_FIX_COMMIT",
    "split": "evaluation",
    "expected": [{
      "path": "docs/connections.md",
      "symbol": "client.connect",
      "name": "timeout",
      "category": "parameter_default_changed"
    }]
  }]
}
```

```sh
python3 -m driftlens.evaluate manifest.json --output evaluation.json
```

Only A/B go to detection. C is opened afterward as review evidence. Unmatched
predictions remain available for manual review instead of being automatically
counted as false positives. The harness reports known-label recall, per-case
runtime and warnings, and precision only for fully reviewed cases. It rejects
repository overlap between development/evaluation splits. A small real-history
[corpus and reproducible replay](examples/historical/README.md) now contains three
genuine drift cases and three negative controls. The bounded filename detector
matches **1/3 original positive labels**; all three controls stay quiet. Black's
Linux claim matches exactly, plus two manually reviewed Windows/macOS references
in the same code-change group. No labels or revisions were changed. The other
two positive cases remain missed. This is retrospective development on a known
case, not held-out accuracy or a broad precision claim.
[Live AI measurements](docs/LOCAL_AI.md) use separate synthetic inputs.

## Boundaries and project status

This is a conservative MVP, not a whole-program verifier. It abstains on dynamic
defaults, decorated functions, reassigned parameters, unsupported runtime configuration,
ambiguous scopes, historical/platform/conditional qualifiers, examples and
uncertain alias relationships. Defaults are declared Python values; physical
units and effective values after external overrides are not independently
proven. General method evaluation, nested functions, complex argparse setup, arbitrary config
frameworks, public wrapper/caller traversal, implicit prose links, general symbol
renames and arbitrary behavioral claims are not supported. Code blocks are
indexed but never used as default assertions. Complex Markdown extensions and
setext heading semantics are outside this parser's subset.

The design and future expansion are in [ARCHITECTURE.md](ARCHITECTURE.md).
[HACKATHON.md](HACKATHON.md) records the original team/event declaration; its
initial implementation status is historical. Current validation and remaining
external work are recorded in [IMPLEMENTATION.md](IMPLEMENTATION.md).

MIT licensed. Development proceeds on feature branches through pull requests.

## Current integration status

The audit follow-up passed **120 tests**, all four deterministic demos, the
eight-case actual local Qwen suite, and the six-case historical replay. It fixes
five reproduced errors involving parser registration, shadowed bindings and Git
timeouts. CI also checks a functional installed CLI outside the checkout.
The historical result is **1/3 supplied positive labels**, with three quiet
controls. Three Black platform sentences form one underlying change group.
See [the filename proof and runnable historical demo](docs/CACHE_LAYOUT.md).
These checks do not establish broad real-world accuracy. Submission confirmation
and spoken team rehearsal are still human tasks; see [the verification record](docs/VERIFICATION.md).

## Team execution and presentation

See [the three-person work plan](docs/TEAM_PLAN.md), the copyable
[agent assignments](docs/tasks/), and the [presentation and Q&A guide](docs/JUDGES_GUIDE.md).

To verify a real local-model contribution separately from deterministic fixtures:

```sh
python3 -m examples.live_model --output /tmp/driftlens-live-model.json
```

This requires a running Ollama server with the selected model downloaded. It
compares model-off and model-on results for identical synthetic snapshots, saves
the actual reports, and exits nonzero unless an uncached model call adds the
expected evidence-backed finding without warnings. A successful run is a narrow
contribution smoke test, not a historical accuracy benchmark. Unit tests use an
explicit test double and do not establish live-model execution.

Local setup, observed results and failure interpretation: [Local AI guide](docs/LOCAL_AI.md).


## Direct CLI instructions: Problem 5 example

When a module-level argparse definition changes from `--timeout` to `--deadline`
and the current README still says either of these, DriftLens reports
`flag_removed` for `--timeout`:

- Use --timeout to stop slow jobs.
- Use `--timeout` to stop slow jobs.

The supported instruction starts the sentence with `Use` (case-insensitive),
followed by the exact flag, optionally wrapped in backticks. The flag must be
supported by the old parser facts, absent from the current parser facts, and
linked to the same unchanged passage and heading context in both snapshots.
The existing module/parser scope and diff-evidence checks still apply.

A replacement flag is not required: removing `--timeout` without adding another
option also qualifies. A replacement does not establish a semantic rename; the
finding proves removal of the documented option, not that `--deadline` has the
same meaning or that either option actually stops slow jobs. This check is
fully deterministic and makes no model calls.

Corrected documentation, retained aliases, potentially compatible long-option
abbreviations, historical/conditional/negated mentions, code examples and
pre-existing inaccuracies are filtered or left unverified. Unrelated flag
mentions and harmless documentation-only edits do not establish a code removal.
Edits elsewhere in a document do not hide an unchanged stale instruction.
Other instruction forms, indirect references, complex parser setup and general
natural-language or behavioral reasoning remain outside this extension.

Reproduce the exact example and both flag spellings with:

```sh
python3 -m unittest tests.test_detector_extensions -v
```
