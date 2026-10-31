# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `ab64f7c41fc0fbe638dd586fecf0689c847109bb`  
Head: `b16901311568a8bdb90e69cc3f83b593749976bc`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 3.584s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
