# Implement the evidence-linked DriftLens MVP

DriftLens previously contained only a project declaration and design. This change
adds a Python CLI that compares immutable Git snapshots, finds unchanged Markdown
claims contradicted by supported Python fact changes, and reports exact spans,
before/after facts and responsible diff hunks. It abstains on unresolved evidence
and keeps checks advisory by default.

Includes source-mapped Markdown parsing, bounded constant resolution, removed
parameter/flag checks, a constrained retry detector, optional local Ollama claim
extraction, versioned caching, JSON/Markdown reporting, GitHub workflows and an
A/B/C historical replay harness. See IMPLEMENTATION.md for supported scope.

Validation: 49 tests pass on Python 3.12.6; four demos match expected outcomes;
wheel installation and the installed CLI were verified outside the checkout.
Live Ollama inference, hardware measurements, historical labeled evaluation and
hosted CI remain unverified. No benchmark or general semantic-verification claim
is made. The advisory workflow bootstraps after this implementation reaches the
base branch.
