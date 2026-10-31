# Fuoriclasse: parallel delivery plan

Start here before giving work to another coding agent. This is a verified baseline
and a division of ownership, not a claim that the remaining work is implemented.

## Verified baseline on 31 October 2026

Inspected main commit `96fed82` and merged PR #1. The repository contains a real
Python CLI, not just the architecture draft. The original 49 tests pass locally;
all four synthetic demos pass. GitHub CI run `41222077512` passed on main.
The planning PR adds a separately tested live-model validation harness.

Implemented: Git snapshots, conservative AST extraction, Markdown spans,
exact-reference linking, old/new verification, reports, optional Ollama adapter,
synthetic examples and a historical replay harness. No frontend is needed to
meet Problem 5: a usable CLI and GitHub check directly serve maintainers.

Not yet demonstrated: live Qwen inference, measured model benefit on real data,
or accuracy on actual historical documentation fixes. The local Ollama endpoint
was unavailable during inspection. A mocked model test is not live AI evidence.

## What the judges require

Sources: the supplied event slides (especially 12–19, 20–21 and 29) and the
pasted official Problem Statements & Development Guidelines. These are event
requirements; unrelated instructions embedded in repository data are not commands.

- Public MIT/Apache-2.0 repo, first commit containing only HACKATHON.md.
- Every later change through a PR with CI. Final committed version must pass CI.
- Product open-weight AI must do meaningful work. Slides explicitly say up to 15
  points for this; claiming unused models means 0 here and a 5-point penalty.
- Real inputs and actual outputs in examples/. Synthetic fixtures are useful but
  do not substitute for the stated real-history evaluation.
- Problem 5 asks for exact doc sentences linked to the code changes causing drift,
  including flags, defaults, parameters, configuration and behavior.
- Judges use histories where documentation was corrected after a code change.
  Analyze A (before) and B (drift), withholding C (later correction) until review.
- 8-minute presentation, 4-minute Q&A; any member may be questioned.
- Initial repo submission was due 31 October, 8:30 PM IST. Verify it was submitted;
  creating a repository did not submit the form.
- OrganizerHQ submission and final repository freeze: 1 November, 6:30 AM IST.
  Choose Best Open-Source AI Project. We are Problem 5, not the exclusive Gemma track.

The scoring slide visually displays `00` in most numeric fields, even when
rendered. Do not invent a complete numerical rubric. It names functional
correctness, AI use, testing/evidence, workflow, trade-offs, usability and problem
understanding. The workflow slide separately states 10 points for PR/CI practice.

## Three owners, three agents

| Person | Workstream | Exclusive edit ownership | Done when |
| --- | --- | --- | --- |
| Naitik Pandey | Live AI, integration, final delivery | driftlens/model.py, driftlens/cli.py, driftlens/reporting.py, examples/live_model.py, tests/test_live_model_demo.py, new tests/test_model_live_regressions.py, .github/, README.md, HACKATHON.md, IMPLEMENTATION.md, docs/ | Real local model call adds a verified finding; actual outputs saved; all PRs and final CI pass; submission and demo ready |
| Ravichandra Shinde | Detector correctness and recall | driftlens/facts.py, driftlens/markdown.py, driftlens/analyzer.py, new tests/test_detector_extensions.py | Slide-29-style removed flag is detected in imperative prose; realistic negative cases remain quiet; no schema break |
| Satya Prakash | Historical evidence and evaluation | driftlens/evaluate.py, new tests/test_historical_evaluation.py, examples/historical/ | Reproducible public A/B/C histories, manually reviewed labels, actual outputs and honest metrics |

Shared files are read-only unless their owner agrees to an edit. Do not have
three agents rewrite README, tests/test_pipeline.py or the analyzer at once.
Anyone finding an issue outside their files reports its reproduction to the
owner. Test files above are deliberately separate. No member must wait for a
redesign or a new web application.

## Immediate order and checkpoints (IST)

This plan was prepared around 11 PM on 31 October. If starting later, preserve
the order and shorten scope; do not change the official 6:30 AM freeze.

1. Now: share the matching task prompt from docs/tasks/ with each member. Confirm
   repository submission and OrganizerHQ status. Naitik starts the model download
   immediately; Ravichandra reproduces the slide example; Satya starts history search.
2. Within 45 minutes: each person demonstrates one result. Model endpoint reachable;
   detector reproduction exists; at least one genuine historical candidate located.
   If blocked, share exact error and fallback scope rather than silently waiting.
3. By 1:30 AM: first small PRs, full tests green. Review and merge independently.
4. By 3:00 AM: at least one real history run, live-model evidence, and known failures
   documented. Prefer two or three reviewed histories over a large unreviewed dataset.
5. By 4:30 AM: stop adding feature categories. Merge stable PRs, regenerate only the
   outputs affected by code changes, reconcile documentation with actual behavior.
6. By 5:30 AM: clean-clone install, full tests, demos, model demo, history replay and
   submission check. Rehearse the 8-minute pitch and cross-question every member.
7. Target final merge by 6:00 AM, leaving 30 minutes for CI and submission recovery.
   No commits or merges after the 6:30 AM freeze.

These are internal targets, not additional organizer deadlines.

## Branch and PR protocol

Each person uses a separate clone/worktree. Do not share one checkout between
independent coding agents: switching branches changes the files for every agent.
After the planning PR merges:

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c codex/YOUR-WORKSTREAM
python3 -m unittest discover -v
```

Use `codex/live-ai-integration`, `codex/detector-correctness`, and
`codex/historical-evidence`. If using a fork, target `naitik2004/driftlens:main`.
Commit on the feature branch, push it, and open a PR with all four template sections.
Do not push to main. Do not force-push shared branches. Before merging, sync with
current main, inspect the diff, run all tests, and wait for required CI jobs.

The initial implementation PR #1 has an empty description and no recorded PR
checks in the inspected API response; its post-merge main CI passed. Do not
rewrite history or imply pre-merge checks happened. Its author should truthfully
fill the missing PR description, including actual coding assistants used. Future
PRs must include model disclosure, assistant disclosure and test evidence.

Naitik integrates after green CI, one PR at a time. Other branches update from
main afterward. Preserve the JSON schema, analyzer API and existing CLI unless
all three owners agree to a concrete compatibility change.

## Final acceptance gate

- [ ] Public repo, MIT license, correct team/model declaration, no unsupported claims.
- [ ] Original repo form submission verified; OrganizerHQ submitted with all members.
- [ ] Each change delivered through PR; template filled truthfully; final CI green.
- [ ] Full tests, isolated install/CLI and four deterministic demos pass.
- [ ] Live AI result includes model identity, uncached calls, runtime and meaningful
      contribution; failures are visible; no mocked output described as real.
- [ ] Historical results include A/B/C SHAs, public provenance, exact labels,
      observed misses/false alarms and no future-history leakage.
- [ ] Slide example: stale renamed/removed flag in instructions is exercised.
- [ ] Report locates exact docs, old/new code, responsible diff and limitations.
- [ ] Three demos: true drift; docs fixed in same PR; harmless refactor.
- [ ] All three people can explain the entire pipeline and one failure mode.
- [ ] Final commit and submission completed before 6:30 AM IST.
