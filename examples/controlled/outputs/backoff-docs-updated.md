**SYNTHETIC mutation of real upstream source; not a historical bug.**

# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `8ab114035865fb57aac6167cb3056aac14b14c7e`  
Head: `6d54f3d712ca9252d8692da71bbe9487f22cd005`

No new drift established within the supported analysis scope.

Abstentions: 1. Runtime: 4.567s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
