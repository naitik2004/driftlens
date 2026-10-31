# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `971e4d294d3ab0366fccd96c9343185f83bd681c`  
Head: `871b26dfc4defdd9f09350e6c16d969fb266069c`

No new drift established within the supported analysis scope.

Abstentions: 1. Runtime: 0.098s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
