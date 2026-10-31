# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `14775800b1cf763a32e3543ab03154ddabce8f95`  
Head: `dd2ea2bbfa713e2882fe25ad6a17c4c2323dc90d`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 0.786s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
