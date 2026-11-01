**SYNTHETIC mutation of real upstream source; not a historical bug.**

# DriftLens

**1 finding(s)** across 1 code change(s). Advisory analysis.

Base: `8ab114035865fb57aac6167cb3056aac14b14c7e`  
Head: `e6d28ffd0a63ac2951318a4024f910a8c442e053`

## backoff._decorator.on_exception: raise_on_giveup default changed from True to False; the documentation still states the old value.

**docs/driftlens-controlled.md:3-3**

<blockquote>&#96;backoff._decorator.on_exception&#96; &#96;raise_on_giveup&#96; defaults to True.</blockquote>

Character offsets: 35–104 (end exclusive).

Update the documented default from True to False.

Evidence: deterministic.

<details><summary>Responsible change</summary>

<pre>@@ -130,7 +130,7 @@ def on_exception(wait_gen: _WaitGenerator,
                  on_success: Union[_Handler, Iterable[_Handler], None] = None,
                  on_backoff: Union[_Handler, Iterable[_Handler], None] = None,
                  on_giveup: Union[_Handler, Iterable[_Handler], None] = None,
-                 raise_on_giveup: bool = True,
+                 raise_on_giveup: bool = False,
                  logger: _MaybeLogger = &#x27;backoff&#x27;,
                  backoff_log_level: int = logging.INFO,
                  giveup_log_level: int = logging.ERROR,
</pre>

</details>

Abstentions: 0. Runtime: 4.842s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
