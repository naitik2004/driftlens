# Behavioral review without fabricated detections

```sh
driftlens --repo /path/to/repo --base BEFORE --head AFTER --review-candidates --json report.json --summary report.md
```

Established findings still require the existing old-support/new-contradiction
checks. Opt-in `review_candidates` are a separate JSON array and Markdown
section. They have `status: needs_review`; they never become GitHub warning
annotations, never trigger `--fail-on-drift`, and never count toward recall or
precision. At most 50 candidates are returned. The default CLI behavior remains
the established-finding analysis.

Add `--model qwen2.5-coder:3b` with `--review-candidates` for optional local Qwen
notes on at most three candidates. These requests are uncached and bounded in
context/output size (8,192 context tokens; 900 generated tokens maximum). Source
excerpts are bounded to 80 lines and 6,000 characters each. The model must echo the exact claim and cite actual source
text at its supplied line; wrong quotes, invented locations and asserted
contradiction verdicts are rejected. Validated citations do not validate the
interpretation: notes remain unverified, and no candidate is promoted to a
finding. The report records actual model identity, prompt version and calls.
If inference fails, the source-backed candidate remains available with a warning.

Two retrieval patterns are supported:

- A retained merge example contains several `+` operands while related Boolean
  opt-in declarations change True → False. Any explicit override for the
  changing destinations suppresses speculation. Parser resolution is recorded
  honestly; compatibility wrappers can leave it unresolved.
- A retained numeric “up to N items per container” claim is associated with a
  removed module constant used in a `len` comparison and a uniquely scoped
  public operation calling that helper. Retained, renamed, inlined and
  same-module moved guards are suppressed. The replacement source is included
  for review. External service limits and arbitrary callees remain unresolved.

No repository name, commit, endpoint, expected quote or numeric threshold is
hardcoded into these runtime patterns. Current docs must retain the same old
claim. Historical/conditional qualifiers, unrelated values and corrected docs
are filtered. Source is parsed, never executed; future correction C is absent
from retrieval.

On the six development histories, the original yt-dlp merge sentence and gdown
folder-limit bullet are retrieved for review. That does **not** turn historical
recall from 1/3 into 3/3. The unresolved obligations are stream-selection and
forwarding semantics for yt-dlp, and the new effective bound for gdown. A removed
guard alone cannot justify “unlimited downloads.” Human review is still required.

Reproduce with the four bare caches described in the corpus README:

```sh
python3 -m examples.historical.replay --cache-dir /path/to/histories --review-candidates --output /tmp/driftlens-review-history
```

The replay separately records established hits and candidate counts. See
[review outputs](../examples/historical/review-outputs/) and
[the external study](../examples/evaluation/README.md). Neither is evidence of a
completed human review or a general behavior verifier.
