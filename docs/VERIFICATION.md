# Verification

## Automated checks

- Full suite: 146 tests, including mutation-generator regressions.
- Deterministic demos: default drift 1 finding; corrected docs 0; harmless
  refactor 0; removed CLI flag 1.
- CI: Linux, macOS and Windows, with Python 3.10/3.12/3.13 configurations.
- Distribution checks: wheel/source builds, strict metadata validation and
  isolated installed-CLI checks for drift, corrected docs, retained flags,
  paired defaults, ambiguous parsers and non-blocking review candidates.

The current workflow runs are available in
[GitHub Actions](https://github.com/naitik2004/driftlens/actions).

## Published release

[v0.1.0 preview](https://github.com/naitik2004/driftlens/releases/tag/v0.1.0)
is pinned to source `f9f45d30788ec0169cafb14e50c56c5bd40764b1`. Its source archive,
wheel and checksums were verified by anonymous download and a fresh install.
The wheel's runtime files match that Git commit byte for byte. Subsequent
repository changes add evaluation material and documentation; the runtime is
unchanged. See [machine-readable release evidence](../examples/verification/github-release-2026-11-01.json).
The release source's 141-test count predates the five evaluation-generator tests.

## Evaluation results

| Study | Observed result | Scope |
| --- | --- | --- |
| [Historical development corpus](../examples/historical/README.md) | 1/3 original positive labels; three quiet controls | Retrospective development cases |
| [External histories](../examples/evaluation/README.md) | 0/1 positive labels; 11 quiet controls | Purposive selection; no predictions, so precision undefined |
| [Controlled mutations](../examples/controlled/README.md) | 18/18 scenarios; three injected changes detected, 15 controls quiet | Generated Markdown and counterfactual edits on three real source snapshots |
| [Local Qwen default extraction](../examples/outputs/LIVE_AI.md) | Eight selected cases passed; three additional findings, five quiet controls | Synthetic inputs, five actual uncached requests |
| [Behavioral Qwen review](../examples/verification/behavior-ai-2026-11-01/evaluation.json) | Two source-cited unverified notes; three controls with no inference | Candidates remain outside finding/recall counts |

Historical labels, failures and raw outputs remain in `examples/`. Later
correction C is used after A/B analysis as corroboration, not detector input.
The extra Black platform sentences describe one underlying change, not three
successful historical cases. Legacy Python syntax-fixture warnings remain
visible. These small studies do not establish broad real-world accuracy or
independent human usability validation.

The [rejected initial behavioral response](../examples/verification/behavior-model-initial-failure-2026-11-01.json)
is retained. Its wrong claim quote was rejected; the corrected request keeps exact
quote and citation validation. Valid source citations do not prove the model's
interpretation. Historical verification records retain the versions and counts
observed when they were produced.
