# DriftLens

## Team

**Team name:** Fuoriclasse

- Satya Prakash
- Ravichandra Shinde
- Naitik Pandey

## Selected problem statement

**Problem 05: Automated Documentation Drift Detection**

DriftLens will analyze pull request code changes, identify documentation that
has become incorrect, and link the exact affected sentences to the responsible
code changes. The initial scope is Python defaults, function parameters, and
configuration options. Findings will include supporting evidence and uncertainty.

## Architecture and implementation plan

See [ARCHITECTURE.md](ARCHITECTURE.md) for the proposed analysis pipeline,
MVP scope, false-positive controls, historical evaluation strategy, build
sequence, and reading material. A Python/Markdown MVP is implemented; see
[IMPLEMENTATION.md](IMPLEMENTATION.md) for observed validation and remaining limits.

## Product AI model and justification

**Selected model:** Qwen2.5-Coder 3B Instruct, using the `qwen2.5-coder:3b`
Ollama tag, running locally on the demonstration laptop.

The open-weight, code-focused model will assess documentation prose against
extracted code changes, explain possible contradictions, and suggest corrections.
Its compact quantized distribution makes it a practical candidate for development
on an Apple M3 laptop with 8 GB of shared memory, subject to runtime testing.
Deterministic code analysis will supply facts and source references; the model
will perform the semantic comparison rather than serve only as a chatbot.

**Current status:** Installed and exercised through actual local inference on
31 October 2026. With prompt `driftlens-claim-v2`, Qwen added three verified
findings missed by the deterministic baseline in a small synthetic suite; five
controls remained quiet. Five uncached model calls were made across eight cases.
These selected cases are not a real-world accuracy benchmark. The first live
run failed and was correctly rejected; its actual output is retained too.
See [local AI evidence](docs/LOCAL_AI.md) and the reports in `examples/outputs/`.
The historical initial commit still records the original planned status.

Model reference: https://ollama.com/library/qwen2.5-coder:3b

## Development tools and workflow

- AI coding assistant used for this setup: OpenAI Codex.
- Product code license: MIT, included in LICENSE. Model weights retain their own license.
- The first commit contained only `HACKATHON.md`.
- All subsequent changes will go through pull requests with CI checks.
- PRs have added the required license, README, PR template, CI workflow,
  implementation, tests, and representative inputs with actual outputs in `examples/`.
- Only public project data will be used. The tool will not automatically post
  issues or comments to external open-source projects.

## Event

Hacktoberfest 2026 Hack Day, Newton School of Technology, Rishihood University.

- Repository submission deadline: 31 October 2026, 8:30 PM IST.
- Final repository freeze: 1 November 2026, 6:30 AM IST.
