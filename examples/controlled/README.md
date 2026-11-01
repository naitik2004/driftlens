# Controlled tests on three additional repositories

**18/18 scenarios passed locally**, using the unchanged DriftLens runtime from
`5e13b81b125166cad5f57c0a05add58406241e3a` (identical to the v0.1.0 runtime).
Three injected default changes were detected; 15 controls produced zero
findings. Every case had zero warnings and zero model calls. Full results are
in [outputs/evaluation.json](outputs/evaluation.json), with JSON and Markdown
reports for every case.

These are **synthetic controlled changes on real upstream source snapshots**.
The generator adds a Markdown test claim and modifies a literal default in a
temporary private copy. It does not claim to have discovered real upstream bugs.
Original historical results remain 1/3 development labels and 0/1 external
labels; these controlled cases are not added to those denominators.

| Repository | Actual source function / parameter | Injected default change | Cases passed |
| --- | --- | --- | --- |
| [litl/backoff](https://github.com/litl/backoff) | `backoff._decorator.on_exception` / `raise_on_giveup` | True → False | 6/6 |
| [invl/retry](https://github.com/invl/retry) | `retry.api.retry` / `delay` | 0 → 1 | 6/6 |
| [urllib3/urllib3](https://github.com/urllib3/urllib3) | `urllib3.request` / `redirect` | True → False | 6/6 |

Each repository has six scenarios:

1. Default changes while the generated documentation stays stale: one finding.
2. Documentation updates with the default: zero findings.
3. A comment-only edit leaves the default unchanged: zero findings.
4. The documentation was already inaccurate before the change: zero findings.
5. An example supplies an explicit argument: zero findings.
6. The sentence explicitly describes historical behavior: zero findings.

## Reproduce

Run from a source checkout with Python 3.14 and Git. No upstream package needs
installation, and Ollama is not needed.

```sh
mkdir -p /tmp/driftlens-more-repos
git clone --bare https://github.com/litl/backoff.git /tmp/driftlens-more-repos/backoff.git
git clone --bare https://github.com/invl/retry.git /tmp/driftlens-more-repos/retry.git
git clone --bare https://github.com/urllib3/urllib3.git /tmp/driftlens-more-repos/urllib3.git
python3 -m examples.controlled.replay --cache-dir /tmp/driftlens-more-repos --output /tmp/driftlens-controlled-results
```

Existing bare caches can be reused. [manifest.json](manifest.json) pins full
upstream SHAs and expected typed defaults. The runner verifies the supported
baseline fact, copies eligible Python/Markdown Git blobs, adds the explicitly
synthetic document and patches only the selected default using AST byte offsets.
Temporary fixture hooks and commit signing are disabled. It never imports,
executes, installs or tests upstream code. Reports intentionally omit public
links for synthetic commit IDs; provenance links point to the actual upstream
baseline source.

The manual **Controlled repository validation** workflow repeats the study and
uploads every report. A mismatch fails the run; labels are not adjusted to
turn failures into passes. This workflow is functional validation, not an
accuracy benchmark on historical bugs.

## Scope and selection limits

The APIs were intentionally selected because the frozen detector resolves their
literal defaults. Generated claims use exact implementation-symbol references.
Public re-export aliases, ordinary ambiguous prose, behavioral inference and
unsupported documentation formats are not covered by this study. Backoff and
retry primarily use reStructuredText README files, which are not silently
converted into historical Markdown claims. Their inspected historical candidates
were not admitted as new genuine positives.

The retry `3c27f5e3579e458eb617989acdaecc54a9312fe3` default-change candidate
has README.rst, not a verified retained Markdown claim. Backoff's
`a2a0132eed09d8e3e8329c09014e6689fd8ef4b1` logging correction also changes
README.rst and concerns behavior outside literal default checks. Neither is
counted as an accuracy success or a reviewed negative control here.

Upstream license notices at the pinned revisions are preserved in
[licenses/](licenses/), including the Apache 2.0 license for retry. The study is
developer-selected, not blinded or independently human reviewed. The existing
[real historical study](../historical/README.md) and
[external-repository study](../evaluation/README.md) remain separate.
