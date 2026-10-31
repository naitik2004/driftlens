# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `8d9dfb54fccb4b45c7ffedf67033714e74ea4961`  
Head: `8c7729e42c9ebf860e75820d5325741b85d64970`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 2.406s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
