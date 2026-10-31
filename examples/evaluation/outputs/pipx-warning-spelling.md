# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `de9dd7fa5463e84142fde95f112897982f589159`  
Head: `ce3c37b1f81dc2cdc987638f087073048a269ef0`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 0.829s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
