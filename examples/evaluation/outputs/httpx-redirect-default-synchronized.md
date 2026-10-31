# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `0b4a83257bef85559d91b466e4ac94a216a25485`  
Head: `47266d763bdef9dc99f9c9d09d49d441b87802e6`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 5.164s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
