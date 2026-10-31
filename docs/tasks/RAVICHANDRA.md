# Detector continuation status

The user explicitly asked Naitik's chat to take over this workstream. The new
bounded filename-layout rule was implemented there, with 105 passing tests and
21 rule-specific methods. Black's original historical Linux label now matches;
all three platform sentences are reported in one change group. Full corpus:
1/3 original positive labels, all three controls quiet. See
[the proof and limits](../CACHE_LAYOUT.md). PR/final-main checks and installed
execution are required before sign-off. The original assignment follows.

# Paste this assignment into Ravichandra's coding agent

You are working on Fuoriclasse's DriftLens for Problem 5. Read docs/TEAM_PLAN.md,
README.md and the existing implementation before editing. Work in your own clone
on codex/detector-correctness, based on current origin/main after the planning PR.
Do not reimplement the working MVP.

You own only driftlens/facts.py, driftlens/markdown.py, driftlens/analyzer.py and
new tests/test_detector_extensions.py. Report changes needed elsewhere to Naitik.
Preserve analyze(repo, base, head, repository_url=None, model=None), its report
schema and the model interpret(bundle) contract. No new runtime dependency.

Priority 1: reproduce the actual Problem 5 slide scenario. A module-level argparse
flag changes from --timeout to --deadline while README still says
"Use --timeout to stop slow jobs." The current removal detector recognizes
supports/accepts/available/takes but may miss this imperative sentence. Make a
small, conservative fix backed by old parser facts and retained current docs.
Report removal rather than inventing proof of a semantic rename.

Before editing, add a failing end-to-end regression through real Git snapshots.
Include negatives: same PR updates docs, historical/negated mentions, retained
--timeout alias, long-option abbreviation compatibility, code examples, and
pre-existing inaccurate prose. Keep prior 49 tests green.

Priority 2 only after Priority 1 passes: use Satya's independently selected public
histories to identify ONE high-value blocker, e.g. a Markdown linking limitation
or a public class method. Reproduce the miss before implementing. A supported,
small extension beats broad heuristics. Do not build whole-program analysis,
embeddings, a graph store or claim general behavioral reasoning.

Commands: python3 -m unittest discover -v; python3 -m examples.demo; git diff --check.
Generated synthetic output runtime differences alone do not need committing.

Deliver a PR with: exact before/after reproduction, supported scope, negatives,
full test results, actual product model usage in this PR, and the coding assistant
actually used. No direct main push or automatic merge. Return the PR URL, test
count, limitations and a two-minute explanation you personally understand.
