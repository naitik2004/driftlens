# Repository audit — 1 November 2026

Reviewed main `428e81204a1f3078dc108c7a4494d11756468e09`. The local
`codex/behavioral-drift-detector` tree at `5dbc3fc` is identical to that main
tree. This is a functional and delivery audit, not a security certification or
proof that every possible input is correct. No product fixes were made here.

## Confirmed errors, in recommended repair order

### 1. Retained argparse flags can be reported as removed

**Priority: high.** `driftlens/facts.py:208` extracts only direct module-level
expression calls. `changes()` at line 417 treats missing facts as removal even
when the new parser contains unsupported registrations.

Reproduction through real Git snapshots:

```python
# A
import argparse
p = argparse.ArgumentParser()
p.add_argument('--timeout', default=30)

# B: same option, moved under an unconditional branch
import argparse
p = argparse.ArgumentParser()
if True:
    p.add_argument('--timeout', default=30)
```

Keep README `Use --timeout to stop slow jobs.` unchanged. Actual: one
`flag_removed` finding. Expected: no finding; the flag still exists. A second
confirmed variant moves the registration to `q = p; q.add_argument(...)` and
also reports removal. Unsupported syntax must invalidate removal evidence,
rather than be interpreted as absence. Add both negative regressions.

### 2. Shadowed parser constructors are treated as argparse

**Priority: medium.** `driftlens/facts.py:187` records import spellings without
validating subsequent constructor rebinding. The stricter trusted-import guards
used by the filename rule are not applied here.

Both snapshots contain:

```python
from argparse import ArgumentParser
class ArgumentParser:
    def add_argument(self, *args, **kwargs): pass
p = ArgumentParser()
p.add_argument('--timeout', default=30)
```

B changes only `default=30` to `default=10`. README says
`` `--timeout` defaults to 30. `` Actual: one `flag_default_changed` finding.
Expected: abstain; this custom class implements no option or default at all.
Validate import bindings, local module shadowing and receiver bindings before
emitting parser facts; apply the same policy to optparse.

### 3. Constant resolution ignores function/class name bindings

**Priority: medium.** `driftlens/facts.py:94–114` counts assignments and
`ast.Name` stores, but a function definition binds its name without such a store.

```python
LIMIT = 30
def LIMIT(): return 99
def connect(timeout=LIMIT): pass
```

B changes only the first line to `LIMIT = 10`. README says
`` `connect` parameter `timeout` defaults to 30. `` Actual: one
`parameter_default_changed` finding. Expected: abstain; the default is a function
object in both revisions, so the old numeric claim was never supported. Include
definitions/imports and binding order in resolution, or conservatively reject
ambiguous names. Add a regression for this exact pre-existing inaccuracy.

### 4. Retry extraction mistakes a custom `range` for the built-in

**Priority: medium.** `driftlens/facts.py:401` rejects stores and some arguments
named `range`, but misses definitions and imports.

```python
def range(n): return [0]
def fetch():
    for _ in range(3):
        try: return remote()
        except IOError: pass
    raise IOError()
```

B changes `range(3)` to `range(5)`. README says
`` `fetch` performs at most 2 automatic retries for `IOError`. `` Actual: a
finding claiming the maximum changed from 2 to 4. The custom loop still makes
one attempt, so the old upper bound remains true. Reject shadowed built-ins,
including definitions, imports and positional-only arguments.

### 5. Git timeouts bypass the documented CLI error handling

**Priority: low.** `snapshots.git()` sets a 60-second subprocess timeout but
does not translate `subprocess.TimeoutExpired`; `cli.main()` does not catch it.
A controlled mock raising `TimeoutExpired('git', 60)` from
`driftlens.snapshots.subprocess.run` reproduced the uncaught exception from
`main(['--base', 'main'])`. Expected: a concise error and exit code 2, consistent
with README. Translate the exception into `SnapshotError` and test that path.
This was a mocked error-path check, not a real hanging Git operation.

## What is complete

| Area | Verified status |
| --- | --- |
| Snapshot collection | Immutable merge-base/head objects, rename map, hunks; ignores dirty target files and does not import target Python |
| Core detector | Top-level defaults/parameters, bounded constants, direct argparse/optparse, constrained retry and filename rules implemented; errors above qualify correctness claims |
| Markdown | Exact quotes, lines/offsets, ATX headings, paragraphs, simple tables and example/qualifier filtering within a documented subset |
| Reports | JSON, Markdown, grouped findings, source links and advisory annotations implemented |
| Optional AI | Fresh eight-case actual Ollama suite passed with five uncached calls; constrained schema validation and digest/prompt/evidence cache implemented |
| CLI/package | Local installation metadata and console entry point implemented; no runtime third-party dependencies |
| GitHub | PR #14 merged; main CI run 41244087665 successful; no open issues at audit time |
| Regression suite | Fresh run: all 105 tests pass in 21.910 seconds; new probes expose gaps outside that suite |
| Synthetic demos | Fresh execution of all four input cases: 1/0/0/1 expected findings |
| Repository artifacts | All 25 JSON files parsed; tracked Markdown relative-link scan found no missing local targets |
| Historical evidence | Fresh six-case replay passed: 1/3 labels, all three controls quiet; all findings identical to saved artifacts; Black retains four syntax warnings |

## Missing or unfinished work

1. Fix and regression-test the five confirmed errors above before broadening
   detection. Green CI does not exercise these failure cases.
2. Historical coverage remains one of three supplied positive labels. yt-dlp's
   implicit format-selection behavior and gdown's folder cap remain missed.
   Three Black sentences represent one code change, not three successful cases.
3. There is no independent held-out validation of the new Black rule. All manifest
   cases remain marked `evaluation`, although Black was used during development;
   narrative docs disclose that limitation. Split metadata should explicitly
   reflect the development use before any held-out metric is reported.
4. Precision is undefined for incompletely reviewed positive cases. Additional
   repositories and reviewed predictions are needed for a broader accuracy claim.
5. Public release work is not integrated: PR #15 is closed without merging.
   Main has no publishing workflow, and GitHub lists no releases. PR #15 records
   that PyPI name `driftlens` belongs to another project and proposes
   `driftlens-docs`; current index availability was not independently checked in
   this audit. Do not advertise `pip install driftlens` as this project's release.
6. Current CI tests source, runs demos, installs the package and checks help, but
   does not run the historical corpus, real Ollama inference, or a functional
   installed-CLI comparison from outside the checkout. Installed checks and
   manual live runs are evidence, rather than continuous guarantees.
7. Default historical replay needs separately fetched bare repositories. They
   are intentionally not shipped. A prepared local manifest/cache was used for
   this audit; the default cache path does not exist on this machine.
8. Large-repository resource handling remains limited: snapshots read every
   eligible blob into memory and spawn Git per blob; there are no repository-wide
   byte/file/time budgets. This is a scalability concern, not a reproduced outage.
9. Organizer submission, selected challenge/team membership, final frozen version
   and spoken rehearsal remain unverified external tasks.
10. Broad configuration analysis, public method traversal, general aliases and
    wrappers, semantic retrieval, other languages and full Markdown semantics
    remain outside the implemented scope. Architecture proposals are not delivery.

## Documentation discrepancies

- `docs/TEAM_PLAN.md:29` still calls 0/2 the current historical result.
- `docs/tasks/NAITIK.md:58` still says both positives are missed.
- `examples/historical/README.md:140` and the Black manifest's `review` and
  `label_subject_note` still describe cache paths/categories as unsupported.
  Refresh explanatory prose without changing the pinned labels or SHAs.
- `docs/PRESENTATION.md` closes by calling a supported real-history positive
  the next priority, despite demonstrating the new Black result earlier.
- Earlier verification artifacts intentionally preserve older counts; retain
  their provenance and distinguish them from stale present-tense status.

## Validation boundaries

The audit reviewed the tracked inventory, all core runtime modules, build and
workflow definitions, evaluation/replay logic, team/status/presentation material,
saved JSON and current GitHub delivery state. Fresh local synthetic Git probes
reproduced the findings above without running upstream project code. Main and
the reviewed checkout have identical tracked content. Fresh historical output
is at `/tmp/driftlens-audit-replay/`; fresh live AI output is at
`/tmp/driftlens-audit-model.json`. The live run passed all eight cases with five
uncached calls after approved localhost access; the initial sandbox-denied run
was an environment restriction. This audit did not rerun public-index
installation, organizer actions or a fresh clean installation; prior installed
evidence is identified separately. A link existence scan is not a full Markdown
renderer check or external URL crawl.

## Remediation follow-up

The follow-up branch fixes all five confirmed errors above. New Git-snapshot
regressions failed before the fixes and now pass. The full suite passes 120
tests; four demos, eight actual local-model cases and all six historical
experiments pass their existing expectations. Historical recall remains 1/3,
with all three controls quiet. All manifest cases now explicitly use the
development split; original expected labels and SHAs are unchanged.

Current status prose is reconciled. CI adds wheel/source metadata validation
and functional installed-CLI controls from outside the checkout. A manual
historical workflow and explicit replay cache option are provided. A fresh
wheel install and strict Twine checks passed locally. Source-distribution
contents now include development fixtures and helper modules. Configurable
snapshot file/byte limits and a collection time budget address the loading
concern; AST and model analysis still have no combined hard runtime budget. Proposed
driftlens-docs packaging and manual Trusted Publishing preparation are restored
from closed PR #15. No public upload has occurred.

Unfinished: safe support for the two semantic historical misses; genuinely new
held-out histories; broader precision evidence; hosted execution of new manual workflows; PyPI account setup/upload;
organizer confirmation and spoken rehearsal. The original audit observations
above describe the audited main commit and are retained as provenance.
