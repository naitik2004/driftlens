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
sequence, and reading material. This is a design plan; implementation and
benchmark results remain future work.

## Product AI model and justification

**Selected model:** Qwen2.5-Coder 3B Instruct, using the `qwen2.5-coder:3b`
Ollama tag, planned for local execution.

The open-weight, code-focused model will assess documentation prose against
extracted code changes, explain possible contradictions, and suggest corrections.
Its compact quantized distribution makes it a practical candidate for development
on an Apple M3 laptop with 8 GB of shared memory, subject to runtime testing.
Deterministic code analysis will supply facts and source references; the model
will perform the semantic comparison rather than serve only as a chatbot.

**Current status:** Selected for implementation; not installed, integrated, or
benchmarked yet. This initial repository declaration does not claim working AI
functionality. Actual model usage and results will be documented through PRs.

Model reference: https://ollama.com/library/qwen2.5-coder:3b

## Development tools and workflow

- AI coding assistant used for this setup: OpenAI Codex.
- Product license selected: MIT; the license file will be added through a PR.
- This first commit contains only `HACKATHON.md`.
- All subsequent changes will go through pull requests with CI checks.
- Subsequent PRs will add the required license, README, PR template, CI workflow,
  implementation, tests, and representative inputs with actual outputs in `examples/`.
- Only public project data will be used. The tool will not automatically post
  issues or comments to external open-source projects.

## Event

Hacktoberfest 2026 Hack Day, Newton School of Technology, Rishihood University.

- Repository submission deadline: 31 October 2026, 8:30 PM IST.
- Final repository freeze: 1 November 2026, 6:30 AM IST.
