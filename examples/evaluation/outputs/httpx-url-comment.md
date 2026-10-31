# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `6f5865f8605b2cf15872388c3d9bc3623bbf265e`  
Head: `efc841a9e8e709f5cc40257927dd7461dc832330`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 3.422s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
