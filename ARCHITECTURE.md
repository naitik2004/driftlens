# DriftLens architecture and implementation plan

> Design proposal. This document describes planned functionality, not an
> implemented or benchmarked system. Team, model choice, and event details are
> recorded in [HACKATHON.md](HACKATHON.md).

DriftLens identifies which documentation claim became false, shows the code
change that caused it, and abstains when the evidence is insufficient.

## Scope and detection principle

Start with Python source code and Markdown documentation. Use deterministic
analysis for concrete facts and the selected local Qwen2.5-Coder 3B Instruct
model, through Ollama, for interpreting prose. Model quality, latency, and memory
usage must be evaluated on the team's hardware before claiming suitability.

**New drift = previously supported claim + contradictory code change + claim
still present in current documentation.**

For example, a PR changes `connect(timeout=30)` to `connect(timeout=10)`, but
`docs/connections.md` still says “Connections time out after 30 seconds by
default.” A finding needs to establish that this sentence refers to this function,
was supported before the PR, and is contradicted afterward.

An explicit example such as `connect(timeout=30)` is not necessarily invalid when
the default changes. Likewise, a sentence already wrong before the PR is an
existing documentation issue, not newly introduced drift.

## Analysis pipeline

The CLI coordinates six stages: collect snapshots, extract code facts, index
documentation claims, link candidates, verify drift, and render findings.
The same analysis core will serve local use and GitHub Actions.

### 1. PR snapshot collector

Input: repository, target/base revision, and PR head revision.

- Resolve the merge base and PR head to immutable commit IDs.
- Retrieve source and documentation at both revisions.
- Extract changed files, diff hunks, and renamed paths.
- Preserve old and new line ranges and their corresponding commit IDs.
- Use the actual PR head rather than accidentally analyzing a synthetic merge
  commit supplied by a CI checkout.

Use Git directly. A three-dot diff compares a merge base with the selected head.
Read complete relevant functions and dependencies, not only changed lines.
Documentation must be searched across the repository, including files untouched
by the PR.

### 2. Code fact extractor

Use Python's built-in `ast` to extract public functions, parameters, literal
defaults, constants, and explicitly supported configuration patterns. Initially
support CLI flags defined through `argparse`.

Compare normalized facts between revisions so formatting-only edits do not
trigger findings. Identify removed symbols; treat renames as hypotheses until
mapping and compatibility evidence support them.

Example fact change:

```json
{
  "symbol": "client.connect",
  "kind": "parameter_default_changed",
  "parameter": "timeout",
  "before": 30,
  "after": 10,
  "source_file": "src/client.py",
  "old_line": 12,
  "new_line": 12
}
```

Dynamic defaults, unresolved imports, decorators, or environment overrides may
prevent a reliable conclusion. Represent unresolved values as unknown rather
than guessing. Syntax extraction alone does not establish runtime behavior.

### 3. Documentation claim index

Parse Markdown paragraphs, sentences, tables, and code blocks. Preserve:

- File, heading, exact original text, line range, and character offsets.
- Mentioned symbols, flags, configuration keys, values, and units.
- Version, platform, and conditional qualifiers.
- Table column headings alongside each row.

Example claim:

```json
{
  "file": "docs/connections.md",
  "line_start": 42,
  "line_end": 42,
  "quote": "Connections time out after 30 seconds by default.",
  "subject": "connection timeout",
  "property": "default",
  "value": 30,
  "unit": "seconds"
}
```

Retain original source offsets throughout processing. A line may contain several
sentences, so line numbers alone are insufficient for exact highlighting. Align
claims between old and current docs; use the current text to avoid reporting
sentences already corrected in the PR.

### 4. Code-to-documentation linker

Retrieve candidate claims using progressively broader evidence:

1. Exact function names, configuration keys, flags, and source links.
2. Heading context, module names, and lexical search.
3. Imported constants, public wrappers, and callers.
4. Optional semantic similarity for descriptions using different terminology.

Start with exact references and lexical ranking. Add embeddings only when
measured retrieval misses justify them. Similarity retrieves candidates; it does
not prove contradictions.

Keep evidence for each relationship. For example: a sentence mentions
`--timeout`, its CLI definition maps to `connect(timeout=...)`, and the changed
fact belongs to that parameter. Follow a bounded dependency graph, initially up
to two hops. An in-memory adjacency map is sufficient for the MVP.

### 5. Drift verifier

Use deterministic checks for resolved default changes, removed parameters,
removed flags, and supported configuration-key changes.

Use the local model for claim extraction and limited behavioral interpretation.
Give it an evidence bundle containing the exact passage and heading, relevant
before/after code, structured facts, and necessary dependency or test context.
Treat repository content as data, never as instructions to the model.

Require structured verdicts: `supported`, `contradicted`, or
`insufficient_evidence`. A new-drift finding requires support in the old revision
and contradiction in the new revision. If old support is uncertain, do not
present a newly introduced contradiction as established.

Validate output structure, quoted text, source locations, and cited facts against
the supplied snapshots. A quotation existing in a file is necessary but does not
by itself validate the reasoning. Abstain on unresolved semantic relationships.
LLM self-reported confidence is not a calibrated probability.

Start behavioral analysis with one constrained case, such as automatic retries.
Do not claim arbitrary prose or whole-program behavior can be verified reliably.

### 6. Findings and GitHub reporter

Produce a JSON artifact and a readable check summary containing:

- Exact documentation quote, path, lines, and character offsets.
- Finding category and explanation of the contradiction.
- Before/after facts and responsible diff hunk.
- Commit-pinned source and documentation links.
- Evidence strength, limitations, and an optional suggested correction.

Example report (illustrative, not an actual run):

> **Default timeout changed: 30 → 10 seconds**  
> Documentation: `docs/connections.md:42`  
> “Connections time out after 30 seconds by default.”  
> Evidence: `connect(timeout=30)` became `connect(timeout=10)` in
> `src/client.py:12`. Suggested correction: replace “30” with “10”.

Keep every finding in the summary, including findings in unchanged documentation
files. Add file annotations where supported; do not rely exclusively on inline
PR review comments. Deduplicate repeated runs using the head commit, claim, and
underlying fact change.

Start with advisory checks. Do not automatically post issues or comments to
external open-source projects. For fork PRs, account for restricted tokens and
unavailable secrets. Analyze repository text without executing untrusted code;
use a trusted reporting path if write permissions are needed. Never execute
untrusted PR code with privileged credentials.

## MVP scope and technology

- Python and Markdown only.
- Changed literal defaults, removed parameters, and removed CLI flags.
- Rename detection only when evidence supports the mapping and aliases are checked.
- One constrained behavioral detector after deterministic checks work.
- A local CLI, JSON report, and GitHub Actions integration.
- Python `ast`, Git subprocesses, and a Markdown parser with source mappings.
- JSON files or SQLite for storage and caching.
- Exact identifier matching and lexical retrieval before embeddings.
- The already selected Qwen2.5-Coder 3B Instruct Ollama model for semantic work.

A separate service, graph database, and agent framework are unnecessary for the
first version. Cache by commit or content hash plus analyzer/model/prompt version
so cached results cannot silently outlive their inputs. Tree-sitter is a later
option for other languages, each requiring language-specific extraction rules.

## False-positive controls

- Suppress a finding when the current PR already corrects the documentation.
- Separate pre-existing inaccuracies from new drift.
- Respect historical-version, platform, and conditional qualifiers.
- Check public aliases before declaring flags or parameters removed.
- Distinguish explicit example values from claims about defaults.
- Resolve module scope when names such as `timeout` occur in multiple places.
- Preserve units and distinguish defaults from effective values after overrides.
- Abstain when dependencies or dynamic behavior cannot be resolved.
- Group repeated claims about the same underlying change.
- Keep initial checks advisory and choose publication thresholds using measured
  precision, not model confidence alone.

## Historical evaluation

For each case identify A (before the code change), B (drift-introducing revision),
and C (later documentation correction). Run detection using A and B only; use C
afterward as evaluation evidence. Do not expose C, its commit message, or future
history to retrieval or the model.

Measure finding precision, known-case recall, sentence/table localization,
responsible-change attribution, warnings per PR, runtime, and model resource
usage. Include negative cases: harmless refactors, formatting changes, retained
aliases, explicit example values, and PRs that fix their docs correctly.

Later corrections are incomplete ground truth. Manually review unmatched
predictions instead of automatically counting them as false positives. Report
recall specifically over known labeled cases. Split development and evaluation by
repository where possible and avoid tuning on the held-out histories.

## Build sequence and demo

1. Create fixtures for changed defaults, removed flags, and unchanged behavior.
2. Implement snapshot collection, AST facts, Markdown spans, and exact linking.
3. Add before/after verification and JSON reporting.
4. Add GitHub Actions, check summaries, and commit-pinned links.
5. Add limited model-based verification and replay historical cases.

Follow the repository's PR-based workflow for subsequent implementation work.
No implementation, benchmark, or successful test run is claimed by this plan.

Demo three outcomes: drift detected, documentation already fixed, and harmless
refactor ignored. Show the exact sentence alongside old and new code, then show
that fixing the docs clears the finding.

## Reading material

Read in this order, building a small extractor before expanding scope:

1. [Python AST](https://docs.python.org/3/library/ast.html): functions, arguments,
   constants, visitors, and source locations for deterministic extraction.
2. [Git diff](https://git-scm.com/docs/git-diff): merge-base comparisons, rename
   detection, and diff hunks for attribution.
3. [Python doctest](https://docs.python.org/3/library/doctest.html): executable
   example validation and its distinction from explanatory-prose verification.
4. [Rustdoc documentation tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html):
   integrating executable documentation into development.
5. [mktestdocs](https://github.com/koaning/mktestdocs): running pytest against
   Markdown examples and docstrings.
6. [Doc Detective](https://docs.doc-detective.com/docs/get-started/introduction):
   validation of documented user workflows; compare with change-linked prose checks.
7. [GitHub Checks API](https://docs.github.com/en/rest/checks/runs): actionable
   check output and annotations.
8. [GitHub workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows):
   pull request events, fork behavior, and permission constraints.
9. [GitHub Open Source Survey](https://github.com/github/open-source-survey/blob/main/README.md):
   the 2024 survey material for problem motivation and presentation research.
10. [Tree-sitter](https://tree-sitter.github.io/tree-sitter/): a possible parsing
    foundation for later language support, not a substitute for semantic rules.

The central contribution is evidence linking: identifying the documentation
claim, showing why it was supported before, and identifying the code change that
contradicts it now.
