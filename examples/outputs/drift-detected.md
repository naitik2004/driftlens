# DriftLens

**1 finding(s)** across 1 code change(s). Advisory analysis.

Base: `2e1beea79cbabc7bfaecbd72ab27c236032e5833`  
Head: `f6c03ce47e8583b5a4ea5355e1e5d5796485f094`

## client.connect: timeout default changed from 30 to 10; the documentation still states the old value.

**README.md:4-4**

<blockquote>The &#96;connect&#96; timeout defaults to 30 seconds.</blockquote>

Character offsets: 52–97 (end exclusive).

Update the documented default from 30 to 10.

Evidence: deterministic.

<details><summary>Responsible change</summary>

<pre>@@ -1,2 +1,2 @@
-def connect(timeout=30):
+def connect(timeout=10):
     return timeout
</pre>

</details>

Abstentions: 1. Runtime: 0.092s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
