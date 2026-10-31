# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `0634553cb01815693815e43f0bf85e841f9c90ca`  
Head: `820f761e1cf30036609f6bdaacae781effd5abaa`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 1.432s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
