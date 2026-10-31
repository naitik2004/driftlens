# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `e182ba877bff741a96e511eac53f25fe3e015e8c`  
Head: `4eacbc172264cb8121e44e39ac40f9e959a7b4e2`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 34.052s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
- Only the first three behavioral candidates receive optional unverified model notes; citations do not prove the interpretation.
