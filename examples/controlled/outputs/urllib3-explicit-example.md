**SYNTHETIC mutation of real upstream source; not a historical bug.**

# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `b87142932716271c80e9ba27e4ef156096f48eaa`  
Head: `81a95b22d5a0d31a41841bd22c073cc7ea7f5a05`

No new drift established within the supported analysis scope.

Abstentions: 0. Runtime: 18.002s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
