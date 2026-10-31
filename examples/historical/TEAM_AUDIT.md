# Assignment audit before Satya follow-up

Checked on 1 November 2026 against main
`176cd70b1289b8936f96f3018846dadda6acd6e4`. The working checkout was clean,
GitHub's main SHA matched it, no PRs were open, and
[main CI was green](https://github.com/naitik2004/driftlens/actions/runs/41234997611).
All 79 baseline tests passed independently before this follow-up.

| Owner | Completed work verified | What remains |
| --- | --- | --- |
| Naitik | [PR #4](https://github.com/naitik2004/driftlens/pull/4) saved actual uncached Qwen2.5-Coder 3B inference, three additional verified findings in eight synthetic cases, five quiet controls, initial failed inference and hardware/model metadata. [PR #7](https://github.com/naitik2004/driftlens/pull/7) records integration checks. [PR #9](https://github.com/naitik2004/driftlens/pull/9) supplies presentation/submission preparation. [PR #10](https://github.com/naitik2004/driftlens/pull/10) conservatively fixes the false optparse defaults found after PR #8. These PRs are merged and their recorded checks passed. | Actual organizer submissions and spoken team rehearsal remain unverified. Final integration and any reruns after a new merge remain Naitik's assignment. This audit read committed live-inference artifacts; it did not rerun the model or redo that workstream. |
| Ravichandra | [PR #5](https://github.com/naitik2004/driftlens/pull/5) fixes the real slide wording, “Use --timeout to stop slow jobs.” Its Git-snapshot regression, preserved aliases/abbreviations, historical/negated text and synchronized-documentation negatives are in the passing suite. [PR #6](https://github.com/naitik2004/driftlens/pull/6) documents the supported scope. Both are merged with green checks. | The current corpus still has no successful real-history detection. Broader behavioral support is a detector task, not an evaluation fix. No analyzer changes are made here. |
| Satya | [PR #3](https://github.com/naitik2004/driftlens/pull/3) already delivered two genuine public A/B/C histories, two real controls, exact labels, licenses, raw outputs, replay checks and honest 0/2 recall. It is merged. [PR #8](https://github.com/naitik2004/driftlens/pull/8) also added optparse extraction outside the original evaluation ownership; its false defaults were corrected by PR #10. | Refresh evidence against current main, extend the independent candidate search, preserve rejected candidates and actual misses, and deliver the follow-up through a separate PR. Those are the only edits in this follow-up. |

The old “Ollama is unavailable” planning note is superseded by the merged actual
live-model outputs. Conversely, green synthetic tests and an operational model
do not establish real-history recall. The original PR #1 description/check-history
gap is recorded in `docs/VERIFICATION.md`; this follow-up does not rewrite it.

## Scope of this continuation

The original Satya assignment was substantially delivered already. This
continuation adds a third genuine positive from gdown and a synchronized-removal
control, preserving the earlier misses. The expanded result is still a detector
gap, not a reason to alter labels or implement heuristics outside ownership.
Read [SEARCH_LOG.md](SEARCH_LOG.md) for rejected candidates and
[README.md](README.md) for actual results and the source-level explanation.

Shared README, presentation, model integration, detector, CI and submission files
are unchanged. Integration should reconcile any shared text that still says
“two positives / 0 of 2” with the expanded corpus; this audit does not mark that
handoff complete or claim a successful historical hit.
