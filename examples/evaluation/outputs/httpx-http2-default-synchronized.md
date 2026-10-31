# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `12d00b238e837a96271d7b07b8c3b456bd82fe0c`  
Head: `30229f16527882305d75ff2877c5b8831f6dc638`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 3.489s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
