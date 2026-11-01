**SYNTHETIC mutation of real upstream source; not a historical bug.**

# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `3841de7b02d7a4604071d2276b751cd82412bad0`  
Head: `f7d76795917298be89d88b2d9bf63a3b56122aad`

No new drift established within the supported analysis scope.

Abstentions: 1. Runtime: 4.351s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
