# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `940d61b239d0f387405f56005b13ad5aed3216b0`  
Head: `1c33a2854e5d18955c8766c5c01e6229716b5b7a`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 3.703s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
