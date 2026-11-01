# DriftLens project declaration

**Team:** Fuoriclasse

- Satya Prakash
- Ravichandra Shinde
- Naitik Pandey

**Problem statement:** 05 — Automated Documentation Drift Detection.

DriftLens connects supported stale Markdown claims to the Python code changes
that invalidated them. See [README.md](README.md) for installation and usage.

**Product model:** optional local Qwen2.5-Coder 3B through Ollama
(`qwen2.5-coder:3b`). It extracts constrained prose claims and can provide
unverified behavioral review notes. Static checks determine established findings.
The compact, code-focused model supports local inference on the 8 GB demo laptop.
See [model setup and evidence](docs/LOCAL_AI.md).

**Product license:** MIT. Upstream model and evaluation-data licenses are separate.

**AI coding assistant disclosed for repository work:** OpenAI Codex.
