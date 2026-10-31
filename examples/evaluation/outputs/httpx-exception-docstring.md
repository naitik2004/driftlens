# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `35de3dfeb6215070ce6ae1974cbba10318f0e99e`  
Head: `317653585cd781c59fc3f5dde20292a47f765a0e`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 3.208s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
