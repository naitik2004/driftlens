# DriftLens architecture

DriftLens compares immutable Git revisions and reports supported documentation
claims invalidated by a Python change. It reads source as data and never imports
or executes the analyzed project.

## Analysis pipeline

1. [snapshots.py](driftlens/snapshots.py) resolves merge-base/head commits, reads
   Python and Markdown blobs, and collects changed hunks and renamed paths.
   Collection has configurable file, byte and time limits.
2. [facts.py](driftlens/facts.py) extracts conservative AST facts: public
   function parameters/defaults, direct argparse declarations, supported optparse
   Boolean actions, bounded constants/imports, retry patterns and cache layouts.
   Shared optparse destinations use the last explicit default. Unknown parser
   state, duplicate spellings, decorators and rebindings cause abstention.
3. [markdown.py](driftlens/markdown.py) indexes ATX headings, paragraphs and simple
   tables with exact Unicode character offsets and line ranges. Code examples
   are not treated as default assertions.
4. [analyzer.py](driftlens/analyzer.py) links scoped references and requires old
   support, a contradictory code change, and the unchanged current claim.
   Corrected documentation, pre-existing inaccuracies, historical qualifiers
   and unresolved relationships are excluded or recorded as abstentions.
5. [reporting.py](driftlens/reporting.py) renders grouped JSON/Markdown findings,
   responsible hunks and optional commit-pinned links. Workflow text is escaped.
   Findings are advisory unless `--fail-on-drift` is selected.

## Optional local model

[model.py](driftlens/model.py) uses local Ollama/Qwen to extract constrained prose
claims. Schema, exact quote, subject, literal type and old/new facts are checked
before a finding is emitted. Optional caching includes the model digest, prompt
and evidence. Model weights and Ollama are not bundled with the Python package.
See [local setup](docs/LOCAL_AI.md).

With `--review-candidates`, [review.py](driftlens/review.py) retrieves possible
behavioral issues separately from established findings. Optional
[review_model.py](driftlens/review_model.py) adds bounded model notes with
validated source citations. These interpretations remain unverified and do not
trigger annotations, build failures or accuracy hits. See
[behavioral review](docs/BEHAVIOR_REVIEW.md).

## Boundaries and evaluation

The engine verifies supported static declarations, not general runtime behavior,
physical units, remote-service limits or arbitrary dependencies. Warnings and
abstentions remain visible; zero findings does not prove documentation correct.

[Implementation](IMPLEMENTATION.md) describes supported scope. Evaluation keeps
[historical cases](examples/historical/README.md), the
[external study](examples/evaluation/README.md), and
[synthetic controlled mutations](examples/controlled/README.md) separate.
