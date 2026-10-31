# Independent historical evaluation protocol

Status: **12 real external-repository cases replayed**: one verified delayed-fix
positive and 11 controls from HTTPX and pipx. Both the frozen detector and the
continuation miss the positive; all 11 controls produce zero findings and zero
warnings. Supplied-label recall is **0/1**, and precision is undefined because
there are no predictions. This is a small, purposive retrospective study, not a
random sample or independent human annotation. The controls include three
synchronized implementation/docs changes, three comment/docstring edits, one
logging-message correction and four Markdown-only edits. They are deliberately
easy non-drift controls and do not establish broad precision.

The positive is HTTPX's actual default pool change from 10 to 20 in
[`8c7729e`](https://github.com/encode/httpx/commit/8c7729e42c9ebf860e75820d5325741b85d64970).
The exact `(Defaults 10)` Markdown sentence survives A and B; later
[`68cf1ff`](https://github.com/encode/httpx/commit/68cf1ff88a7f6c0b084bb62455c043aa503713ef)
corrects it to 20. Source evidence includes the containing bullet and effective
`DEFAULT_LIMITS` constructor configuration. This is outside literal function
default extraction. No detector rule was tuned on this case after prediction.

[selection.json](selection.json) preserves the labels frozen before prediction
(SHA256 `ea3bd5d4955ee673b6848a4fc1dbf6c517be232f532291c029f8b5d430d5d171`).
[manifest.json](manifest.json) adds reviewed-patch hashes without changing those
labels. [frozen-baseline/](frozen-baseline/) and [outputs/](outputs/) retain every
raw report, including the miss. Later C was read by the replay only after A/B
analysis. C had been inspected during retrospective selection, so this is not a
blinded discovery exercise.

## Reproduce

```sh
mkdir -p /tmp/driftlens-evaluation-cache
git clone --bare https://github.com/encode/httpx.git /tmp/driftlens-evaluation-cache/httpx.git
git clone --bare https://github.com/pypa/pipx.git /tmp/driftlens-evaluation-cache/pipx.git
python3 -m examples.evaluation.replay --cache-dir /tmp/driftlens-evaluation-cache --output /tmp/driftlens-external-evaluation
```

Existing clones can be reused. The harness checks exact SHAs, ancestry, patch
hashes, changed paths, Markdown-only/comment controls, retained quotes and exact
localization before replay. It never imports or executes upstream projects.
Exit success means provenance/replay completed, **not** that accuracy passed.
The manual **External historical evaluation** workflow repeats this on GitHub.

For the frozen executable, archive commit
`caf6347b0ff74ee01f9e74c86f749ed96aaa4677` into a separate directory and run its
`examples.historical.replay` against a temporary manifest with absolute cache
paths. The saved frozen result used that exact executable. Benchmark selection
and human review are separate: no independent first-time user test is claimed.

Freeze the existing detector before choosing new labels: merged main
`caf6347b0ff74ee01f9e74c86f749ed96aaa4677`. The public-readiness follow-up changes
text I/O and installation/validation workflows, not the behavioral rules. Record
the exact executable version in every eventual result.

## Selection and review gate

1. Target 10–20 real cases across at least two new Python/Markdown repositories,
   including genuine delayed-fix positives and reviewed negative controls.
2. Exclude the current development repositories and their forks/renames:
   yt-dlp, Black, python-slugify and gdown. Distinct clone paths do not establish
   repository independence.
3. Pin A/B and, for delayed-fix positives, later C. Verify old supporting code,
   contradictory B code, the unchanged exact B Markdown quote and C's correction.
   Same-commit code/docs fixes are controls, never delayed-fix positives.
4. Save exact path, quote, line and Unicode offset, subject/category, source
   URLs, licenses, selection reasoning and rejected candidates. Docstrings/RST
   do not satisfy the current Markdown corpus requirement.
5. Freeze labels before running predictions. Give A/B only to the analyzer;
   inspect C after detection as corroboration. Do not tune the frozen detector
   on results and continue calling those cases held out.
6. Review every prediction, including unmatched ones. Report supplied-label
   recall and exact localization; report precision only for fully reviewed
   cases. Retain misses, warnings and cases without predictions.
7. If a case is used to develop a fix, move it into development and obtain new
   evaluation data. Record that change rather than silently recycling labels.

The target is a first external-repository study, not proof of broad accuracy or
independent human verification. A person outside the authorship team should
review the labels and first-use experience separately.

## Candidate search log — 1 November 2026

GitHub commit search and source/patch review produced these initial candidates.
They have not been supplied as a new accuracy benchmark:

| Repository / commit | Review result |
| --- | --- |
| HTTPX `47266d763bdef9dc99f9c9d09d49d441b87802e6` | Commit message describes coordinated redirect-default/docs changes; complete diff review is still required before labeling a negative control. |
| HTTPX `1c33a2854e5d18955c8766c5c01e6229716b5b7a` | Candidate synchronized encoding-default change; not a verified delayed correction. |
| HTTPX `30229f16527882305d75ff2877c5b8831f6dc638` | Candidate synchronized HTTP/2 default/docs change; not a verified delayed correction. |
| HTTPX `f8981f3d124f9b8db9073fd5c8afa11acb55a738` | Candidate synchronized proxy API/deprecation/docs change; no delayed positive established. |
| Rich `2567ed9bea808b4a0116a21d531b260ebe12bbae` | Rejected for this corpus: correction is in `rich/syntax.py` docstrings, not Markdown. |
| Rich `32def19a2a9f8bf9333a9b41ecbdc23b98b9765a` | Rejected as a delayed-doc positive: patch fixes code to match existing documentation; it does not establish a later Markdown correction. |
| tqdm `95efb20fae9a56022bde6c7ce8e6f74ba3b9e301` | Candidate described as typo in README/docstrings; no verified behavioral drift and no A/B/C chain. |
| tqdm `23c596fb331478cbc15d1854b61a3e63284da3a5` | Rejected as a drift positive: packaging encoding fix, not established stale behavior prose. |
| Typer `7202e86bf8314b63ccb998fab751f2140cd5b187` | Candidate synchronized Enum-default display bugfix/docs/tests; no delayed positive established. |

These original search entries remain candidates/rejections, not nine extra
evaluation cases. The 12 admitted cases and their reviews are explicitly listed
in manifest.json; rejected or unverified candidates are excluded.
