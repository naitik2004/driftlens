# Naitik's agent assignment: continue this chat's work

Read docs/TEAM_PLAN.md and docs/JUDGES_GUIDE.md. Own live AI, reports, integration,
CI and the final presentation. Do not edit Ravichandra's extractor/analyzer or
Satya's evaluator while their branches are active.

Immediate issue: Qwen's integration is written and mocked tests pass, but a real
Ollama server was unavailable. Meaningful AI is mandatory; do not describe the
current synthetic deterministic demos as proof of AI use.

1. Install/start Ollama on the demonstration laptop using official instructions.
   Fetch qwen2.5-coder:3b, record model digest and hardware. The current tag is
   about 1.9 GB on Ollama; latency and memory must be measured, not assumed.
2. Run `python3 -m examples.live_model --output /tmp/driftlens-live-model.json`.
   It compares a deterministic baseline against actual uncached local inference
   on identical snapshots. Its sentence is deliberately outside today's regex
   grammar, so a passing run proves a narrow model-assisted extraction contribution.
   This is one synthetic smoke test, not an accuracy benchmark or proof that the
   whole product requires a model. A failed run exits nonzero and records failure.
3. If successful, save the ACTUAL output to examples/outputs/live-model.json in a
   separate PR, plus model digest, measured hardware/runtime and exact command.
   Never change the expected answer, inject a mocked verdict, or hide warnings
   just to get a pass. Add positive paraphrases and negatives to assess usefulness.
4. Inspect real returned JSON when inference fails; improve prompt/validation
   conservatively within model.py. Schema validation and deterministic old/new
   evidence remain mandatory. Check failure handling with regressions. Do not
   enable automatic LLM calls on the secretless GitHub runner or require an API key.
5. Fill current model/status declarations only after observed evidence; synchronize
   HACKATHON.md, README.md and IMPLEMENTATION.md without rewriting history.
6. Review and merge independent PRs one by one after tests and hosted CI pass.
   Verify install from a clean clone and reports pinned to actual input commits.
7. Confirm both organizer submissions, rehearse the guide with all members and
   freeze the final green commit before 6:30 AM IST on 1 November.

If local inference cannot be established promptly, ask event mentors about the
announced open-model server before midnight. Current adapter deliberately accepts
localhost only: remote support would require an explicit, constrained change and
its own tests. Do not switch to closed-model APIs or claim an unused open model.

Do not spend the night on a dashboard, login system, graph database, model training,
or rebranding DocDrift vs DriftLens. The project is DriftLens. Keep all subsequent
work on PR branches and fill the mandatory PR description truthfully.
