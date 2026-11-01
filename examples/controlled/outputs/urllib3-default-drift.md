**SYNTHETIC mutation of real upstream source; not a historical bug.**

# DriftLens

**1 finding(s)** across 1 code change(s). Advisory analysis.

Base: `f66eda3932adb686aec20405a306964145695d0b`  
Head: `4a7dde5412299a5c9e44882489f09bd0f56650be`

## urllib3.request: redirect default changed from True to False; the documentation still states the old value.

**docs/driftlens-controlled.md:3-3**

<blockquote>&#96;urllib3.request&#96; &#96;redirect&#96; defaults to True.</blockquote>

Character offsets: 35–81 (end exclusive).

Update the documented default from True to False.

Evidence: deterministic.

<details><summary>Responsible change</summary>

<pre>@@ -123,7 +123,7 @@ def request(
     headers: typing.Mapping[str, str] | None = None,
     preload_content: bool | None = True,
     decode_content: bool | None = True,
-    redirect: bool | None = True,
+    redirect: bool | None = False,
     retries: Retry | bool | int | None = None,
     timeout: Timeout | float | int | None = 3,
     json: typing.Any | None = None,
</pre>

</details>

Abstentions: 0. Runtime: 20.297s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
