# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `07b87da81140cf51e4a585e43d4fe9113f4c2ad5`  
Head: `d968ca7419e6f4e40685888c56d03bea50fd39d7`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 0.460s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
- Only the first three behavioral candidates receive optional unverified model notes; citations do not prove the interpretation.
