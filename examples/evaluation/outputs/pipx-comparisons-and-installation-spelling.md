# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `5fd768690b178adccf53511634d734e0e7765f4c`  
Head: `946cd61fe6e3290448a1622737cca30b28b5ea82`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 1.435s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
