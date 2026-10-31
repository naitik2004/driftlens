# DriftLens

**1 finding(s)** across 1 code change(s). Advisory analysis.

Base: `6d10078e897855d5f0a940e85fbfdf4824329633`  
Head: `7bd5d2df2abeeeaf2dba15f9e288c34d21891448`

## client.parser no longer declares --timeout, which the unchanged documentation says is available.

**README.md:1-1**

<blockquote>The CLI supports &#96;--timeout&#96;.</blockquote>

Character offsets: 0–29 (end exclusive).

Remove or update the documented --timeout reference after reviewing migration behavior.

Evidence: deterministic.

<details><summary>Responsible change</summary>

<pre>@@ -1,3 +1,2 @@
 import argparse
 parser = argparse.ArgumentParser()
-parser.add_argument(&#x27;--timeout&#x27;, default=30)
</pre>

</details>

Abstentions: 0. Runtime: 0.064s.


## Scope and limitations

- Python top-level functions and direct module-level argparse definitions only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
