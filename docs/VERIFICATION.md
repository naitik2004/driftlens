# Integration verification — 1 November 2026

## Later optparse correction

PR #8 was merged during integration review. Three false-positive cases were
reproduced: invented implicit Boolean defaults, conflicting shared-destination
defaults, and set_defaults overrides. The correction now abstains on those cases.
The valid explicit single-destination positive remains covered.

Correction validation: **79 tests passed**, all four deterministic demos passed,
all eight actual Qwen/control cases passed, and the four-case historical replay
completed again with unchanged labels and **0/2** historical positives detected.
The [correction record](../examples/verification/optparse-defaults-2026-11-01.json)
retains these results. Earlier 72-test results below describe the original
source version and are not the current test count. The correction also passed a
fresh clone/install and both installed-CLI checks outside the checkout. Its PR
and post-merge main CI must pass before integration sign-off.


This records checks actually run on merged runtime source
`36ee68ffd98273de68fd0386a3ca1829998ed822` (PRs #1–#6), not a claim that all
submission or presentation tasks are complete. The verification PR changes only
documentation, the PR template and the machine-readable record.

## Observed technical checks

| Check | Actual result |
| --- | --- |
| Complete test suite, Python 3.14.6 | 72 passed |
| Synthetic default drift | 1 finding, zero model calls |
| Documentation fixed together | 0 findings, zero model calls |
| Harmless refactor | 0 findings, zero model calls |
| Removed CLI flag | 1 finding, zero model calls |
| Actual local Qwen suite | All 8 labeled cases passed; 3 added findings; 5 quiet controls; 5 uncached calls |
| JSON/Markdown evidence | Exact quote offsets, source paths, old/new verdicts, responsible hunks and deterministic labels checked |
| Model evidence | Actual returned model identity, completed responses, typed values and model-extracted evidence labels checked |
| Fresh clone and isolated wheel install | Passed; installed package import resolved to venv site-packages outside the checkout |
| Installed deterministic CLI | Removed direct-instruction flag detected, no model call, no warnings |
| Installed model-enabled CLI | Paraphrased default detected with one actual Qwen call, no warnings |
| Independent public-history replay | All 4 experiments completed; 0/2 positive labels detected; both controls quiet |
| Source main CI | Passed on Python 3.10/3.12/3.13: run 41232713350 |
| Required repository files | Present; MIT license and public visibility verified |
| Team declaration | Fuoriclasse; Satya Prakash, Ravichandra Shinde, Naitik Pandey; Problem 5 |
| First commit | Contains only HACKATHON.md |
| Runtime/model artifacts | Ignored and untracked; no weights or runtime binaries in Git |
| Focused literal credential patterns | No matches in tracked text files; this was not a comprehensive security audit |
| Teammate integration | PRs #3, #5 and #6 merged; no open teammate PRs at the check |

The PR checks and the post-merge main checks for this verification update are
available in GitHub Actions; check the latest commit rather than treating an
older green run as final evidence.

## Actual results, not broader claims

The live suite uses developer-selected synthetic cases. Three controls are
filtered before the model runs. The first model-enabled case took 6.05 seconds
in this run; other model-enabled cases took 2.58–2.74 seconds. No general AI
accuracy or latency claim follows from eight cases.

The independent historical replay downloaded bare public histories for yt-dlp,
Black and python-slugify into a temporary cache and used the committed full SHAs
and labels. The manifest's repository paths were redirected to that cache; labels
and revisions were not changed. Upstream code was read as Git objects, never
imported or executed. The replay verified A/B provenance and exact localization,
ran detection without C, and checked the later correction afterward.

Both historical drift cases remain missed: nested optparse/example semantics
and computed cache-path behavior are outside current support. Four warnings
come from Black's invalid/Python-2 test fixtures. Zero predictions does not give
100% precision, and a successful replay command does not mean successful drift
detection. See [the corpus](../examples/historical/README.md).

The [machine-readable verification summary](../examples/verification/integration-2026-11-01.json)
retains the observed counts, response timestamps, call counts, runtime and warning
summary. Original complete model and historical artifacts remain under examples/.
Fresh raw rerun reports and test logs were also retained locally in
`/tmp/driftlens-integration-20261101/` and
`/tmp/driftlens-integration-live-20261101.json`; those temporary paths are not
portable repository artifacts.

## Workflow correction and historical exception

The PR template had lost the required product-model and coding-assistant
sections. This verification PR restores the four organizer-requested sections
while retaining test/evidence checks and limitations.

Main's first-parent history contains the initial declaration followed by PR
merge commits. However, PR #1's description is empty and no pre-merge PR checks
were recorded in its inspected API response; its post-merge CI passed. This
historical gap has not been rewritten, hidden or counted as pre-merge compliance.
The author should add truthful model/assistant/test disclosure if still missing.

## Human tasks still open

- [ ] Verify the repo-link form was actually submitted before its original deadline.
- [ ] Verify OrganizerHQ submission exists, selects Best Open-Source AI Project,
      includes the correct repo and all three members, and is submitted by 6:30 AM IST.
- [ ] Perform an actual eight-minute spoken rehearsal with the three speakers.
- [ ] Have each member operate the demo and answer questions about the full pipeline.
- [ ] After any further code merge, rerun affected checks, the complete final-main
      test suite and final-main CI; do not reuse this record for changed runtime code.

No event-account confirmation or observed spoken rehearsal was available to the
integration agent. Those tasks remain unverified. The prepared script is
[PRESENTATION.md](PRESENTATION.md); detailed Q&A is in JUDGES_GUIDE.md.
