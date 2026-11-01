**SYNTHETIC mutation of real upstream source; not a historical bug.**

# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `d51c0e91f5d7a6cdab2c8e18c2e2987241485e26`  
Head: `68c023cb0590e0e66774284d3fe0ed180f682060`

No new drift established within the supported analysis scope.

Abstentions: 1. Runtime: 17.838s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
