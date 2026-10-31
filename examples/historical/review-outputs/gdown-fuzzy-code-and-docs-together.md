# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `6a435009d5bf3f2ffc99f47d209e0e8b4173c1e9`  
Head: `b1c6e1ce257d4fa247304adcd181cdf8e7651c74`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 0.867s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
