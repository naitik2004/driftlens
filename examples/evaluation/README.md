# Independent historical evaluation protocol

Status: **not a completed benchmark**. No new positive label, prediction or
10–20-case result is claimed by this directory.

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

These are search candidates and rejections, not nine evaluation cases. Continue
source review and selection before creating a runnable labeled manifest. No
labels were manufactured to reach the requested target.
