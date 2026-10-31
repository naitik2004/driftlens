# Implementation and verification status

## Current implementation

DriftLens is an executable Python/Markdown documentation drift detector with a
CLI and advisory GitHub Actions integration. It reads immutable merge-base/head
Git snapshots without importing or executing the analyzed project's code.

Implemented capabilities:

- AST facts for public top-level function parameters/defaults, bounded simple
  constants/imports, direct module-level argparse definitions, and one constrained
  retry-count pattern.
- Direct optparse option/group facts in public function bodies, with explicit
  defaults only. Implicit/shared destinations and set_defaults overrides abstain.
- Exact Markdown sentence/table spans, scoped linking, unchanged-claim alignment,
  old support/new contradiction checks, and conservative abstention.
- Removed CLI options in direct `Use --flag` instructions, with optional backticks.
  This proves removal, not a semantic rename or the promised flag behavior.
- JSON, Markdown summaries, grouped findings, responsible diff hunks, source
  locations, optional commit-pinned links and advisory workflow annotations.
- Optional local Qwen claim extraction with schema/quote/value validation and
  content/model/prompt-versioned caching.
- Synthetic demos, real A/B/C replay with later corrections withheld from
  detection, MIT license, PR template and Python 3.10/3.12/3.13 CI.

## Integration run: 1 November 2026

Runtime source checked: `36ee68ffd98273de68fd0386a3ca1829998ed822` (PRs #1–#6).
The verification PR changes documentation, the PR template and a verification
record; it does not change detector behavior. See [the verification record](docs/VERIFICATION.md)
for the latest completed checks and remaining human tasks.

Observed locally on Python 3.14.6:

- **72 tests passed**, including the direct CLI instruction regressions.
- All four deterministic synthetic demos passed: drift 1 finding, docs fixed 0,
  harmless refactor 0, removed flag 1. Each made zero model calls.
- Generated JSON/Markdown were checked for expected counts, exact claim offsets,
  old support/new contradiction, source paths, diff evidence and evidence mode.
- The eight-case actual local Qwen suite passed: three verified findings added
  over the baseline, five quiet controls, five uncached calls. Three controls
  never reached the model. The first model-enabled case took 6.05 seconds in this
  run; the other model-enabled cases took 2.58–2.74 seconds. No broad accuracy or
  latency guarantee is made.
- A fresh tracked-files-only clone built and installed into a new virtual
  environment. From outside the checkout, the installed CLI correctly detected
  the direct removed-flag example without AI and a paraphrased default with one
  actual Qwen call, with no warnings.

The independent upstream-history replay completed all four pinned experiments
with the same 0/2 positive-label recall and quiet negative controls. Source main
CI passed across Python 3.10/3.12/3.13. See the verification record for provenance
and the latest GitHub Actions runs for verification-PR/final-main status.

## Historical effectiveness and limits

The bundled retrospective corpus contains two genuine drift cases and two real
negative controls. Its saved baseline misses both positive labels: nested
optparse/example semantics in yt-dlp and computed cache-path behavior in Black
are outside current support. Both controls stay quiet. This is **0/2 supplied
positive labels detected**, not successful real-history detection. It is an
unblinded scope study, not a held-out accuracy benchmark. See
[the corpus and labels](examples/historical/README.md).

The linker requires exact scope references. Methods, nested functions, complex
parser setups, arbitrary wrappers/aliases, broad configuration frameworks,
implicit prose links, general behavioral reasoning and additional languages
remain unsupported. Zero findings does not mean documentation was verified.

## Evidence provenance

Earlier 49-, 51-, 55- and 60-test results described earlier versions. Current
integration tests are counted above. Original 31 October actual model outputs,
including the initially rejected response, remain in examples/outputs/; their
recorded times describe those runs, not the newer verification run. The local AI
guide distinguishes real calls from unit-test doubles and model-internal prompt
reuse from DriftLens's optional verdict cache.

Coding assistants used during development are disclosed in PR descriptions.
Ordinary CI requires neither a running model nor an API key. The first
implementation PR has an empty description and no recorded pre-merge PR checks;
its post-merge CI passed. That historical workflow gap has not been rewritten or
represented as a successful pre-merge review.

## Subsequent optparse integration correction

PR #8 was merged externally during review. Its implicit Boolean defaults and
per-option treatment of shared destinations produced reproduced false positives.
The correction removes inferred Boolean defaults and conservatively leaves
implicit/shared/overridden defaults unresolved. Three failing-before/passing-after
Git-snapshot regressions were added, and the prior test that asserted an invented
implicit True default was corrected. The valid explicit-default positive remains.

The correction run passed 79 tests, all four deterministic demos, and all eight
actual local Qwen/control cases. The baseline 72-test record above describes the
earlier source commit. Historical recall remains an explicit limitation.
