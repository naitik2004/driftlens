# Paste this assignment into Satya's coding agent

You are working on Fuoriclasse's DriftLens for Problem 5. Read docs/TEAM_PLAN.md,
README.md, driftlens/evaluate.py and its tests. Work in a separate clone on
codex/historical-evidence, based on current origin/main after the planning PR.

Own only driftlens/evaluate.py, new tests/test_historical_evaluation.py, and
examples/historical/. Do not modify the analyzer, core model, shared README or CI.
Preserve the evaluation API. Coordinate a detector failure by sending Naitik and
Ravichandra its exact reproduction; do not silently fix outside your ownership.

The organizers evaluate real histories, so this is a core deliverable, not polish.
Find public Python projects documenting APIs/flags in Markdown. Inspect actual Git
history for A (before code change), B (code changed while docs remained stale), C
(later documentation correction). Verify each SHA and the exact source and docs.
Do not invent commit IDs, relabel a synthetic repo as historical, or use a same-PR
doc update as a genuine drift case. If only a negative example is found, say so.

First target: one genuine positive plus real negative controls (formatting-only
or docs fixed together). Stretch: 2–3 positive histories across two repositories.
Record candidates that fail our support boundaries too; do not cherry-pick only
hits or claim broad accuracy from a few cases. Timebox initial search to 45 minutes.
If no candidate is verified, report that explicitly and supply the inspected
candidates; never manufacture evidence to fill the deliverable.

Under examples/historical/, add a README explaining sources, public URLs, licenses,
A/B/C SHAs, review reasoning, reproduction commands, and expected exact sentence,
path, symbol, parameter/flag and category. Store manifest labels and actual JSON
outputs. Supply a small fetch script only if needed; fetch into an explicit cache
outside the committed corpus. Never execute upstream code or add a whole cloned
repository to our repo. The analyzer only reads Git objects.

Run A/B without supplying C, its patch/message or future code to retrieval/model.
Only then inspect C as validation. Use the existing replay harness. Distinguish
known-label recall from precision: set fully_reviewed only after reviewing every
prediction and expected label. Include exact localization labels; explain any
miss. If changing metrics, add meaningful regression tests without changing the
existing contract. Do not claim AI evaluation: the current harness is deterministic.

Run full tests plus your replay. Submit a small PR, all template sections filled,
actual model/assistant disclosures, actual output and limitations. No direct main
push or automatic merge. Return PR URL, counts, reproductions and one case you can
explain from source code without an assistant.
