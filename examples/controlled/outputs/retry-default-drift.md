**SYNTHETIC mutation of real upstream source; not a historical bug.**

# DriftLens

**1 finding(s)** across 1 code change(s). Advisory analysis.

Base: `6b38743ed1a77add6d152574fc6a5e4477909d7b`  
Head: `39f4c4646f2b2e66ecac7f83edb4de7ba7cd23a2`

## retry.api.retry: delay default changed from 0 to 1; the documentation still states the old value.

**docs/driftlens-controlled.md:3-3**

<blockquote>&#96;retry.api.retry&#96; &#96;delay&#96; defaults to 0.</blockquote>

Character offsets: 35–75 (end exclusive).

Update the documented default from 0 to 1.

Evidence: deterministic.

<details><summary>Responsible change</summary>

<pre>@@ -51,7 +51,7 @@ def __retry_internal(f, exceptions=Exception, tries=-1, delay=0, max_delay=None,
                 _delay = min(_delay, max_delay)
 
 
-def retry(exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1, jitter=0, logger=logging_logger):
+def retry(exceptions=Exception, tries=-1, delay=1, max_delay=None, backoff=1, jitter=0, logger=logging_logger):
     &quot;&quot;&quot;Returns a retry decorator.
 
     :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
</pre>

</details>

Abstentions: 0. Runtime: 0.943s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
