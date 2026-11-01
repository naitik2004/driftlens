# Eight-minute presentation: Fuoriclasse / DriftLens

This is a rehearsal script, not a record of completed human rehearsal. Naitik now
delivers every segment alone. The original three-person team remains credited;
this script does not assert the other members are attending. Test the exact demo
laptop beforehand. The event allows eight minutes of presentation and four
minutes of Q&A.

## Before the panel

Open the current green main CI run, the report preview, a terminal in the checkout,
examples/cases.json, the live AI evidence table and the historical corpus README.
Start Ollama and confirm qwen2.5-coder:3b is installed. Use the commands in
LOCAL_AI.md if the local server is not running. Silence unrelated notifications.
Do not run the full test suite during the pitch; show its actual CI result.

## 0:00–0:45 — Naitik: problem and promise

“Code review usually checks the code that changed. It is easy to miss a sentence
in a different documentation file that became wrong. DriftLens connects that
sentence to the code change and shows maintainers the evidence.

“For example, a function's timeout changes from 30 to 10, but its documentation
still promises a default of 30. We check that the old code supported the claim,
the new code contradicts it, and the stale sentence still exists. We chose
Problem 5 because that link is the useful part for maintainers.”

## 0:45–2:45 — Naitik: deterministic live demonstration

Say: “This first demonstration uses an actual historical Black code change.”
Run the pinned A/B command in CACHE_LAYOUT.md, using the prepared bare cache.
It writes `/tmp/driftlens-black-live.md` and its JSON report. Open the report
preview alongside the pinned old/new code links.

“The README still describes a cache filename with two numeric fields. The code
now calls a local helper that joins five fields. Counting the declared separators
proves that layout cannot match, without evaluating the unknown values. The
Linux label matches exactly; Windows and macOS give two more stale sentences,
all grouped under this one code change.”

Show exact quote, line, old/new facts, helper/list dependencies and responsible
diff. Explain that runtime overrides and filesystem normalization are outside
this static contract. Later documentation C was not given to the detector.

Then briefly show the removed-flag example as an additional controlled fixture.
Do not call that synthetic example upstream history or a verified semantic rename.

## 2:45–3:45 — Naitik: two important non-findings

Run `python3 -m examples.demo` and show documentation-fixed and harmless-refactor reports.

“The first change updates the documentation too, so there is no unchanged stale
claim. The second changes formatting without changing the declared default, so
there is no contradictory fact. Both stay quiet. These controls protect
maintainers from noise. Zero findings means no new drift was established within
our supported scope, not that every sentence was proved correct.”

## 3:45–4:45 — Naitik: actual open-weight AI contribution

Run the small actual local smoke test; keep a clearly labeled earlier actual run
ready as a fallback. Do not label a fallback as live.

```sh
python3 -m examples.live_model --output /tmp/driftlens-panel-live.json
```

“Qwen2.5-Coder 3B runs locally through Ollama. The baseline cannot extract this
particular paraphrase. The model maps its prose to a structured default claim;
we validate its quote and subject and still require agreement with the old/new
static values. This is the difference between deterministic and model-extracted
findings in the report.

“In our small synthetic suite, AI added three verified findings over the baseline.
Five controls stayed quiet; three were filtered before any model call. That is
five actual requests across eight cases, not eight demonstrations of AI reasoning.”

Point to baseline/assisted counts, model_calls, evidence_strength and the actual
API response. Mention the initial rejected response if asked about reliability.

## 4:45–6:00 — Naitik: real histories and honest limits

Show examples/historical/README.md and one pinned A/B/C source example.

“Our corpus has three genuine drift histories and three negative controls.
The original Black Linux label is now detected; all three controls stay quiet.
The two extra platform sentences are reviewed predictions for that same code
change, not extra successful historical cases. Known-label recall is one of
three supplied positive labels. We left the labels unchanged.

“The yt-dlp behavior example and gdown folder cap remain unverified findings.
Opt-in review mode now retrieves those sentences with source evidence, without
counting candidates as detections. This rule was
developed using an already-known Black case, so we do not call it held-out
accuracy. We kept the misses, warnings and two additional reviewed locations
visible. Later C is used only after A/B detection to corroborate the result.”

If a later reviewed PR changes these results, rerun the corpus and update this
script and reports before changing that claim. Never silently replace a miss
with a different task or count the absence of predictions as perfect precision.

Show the separate external study briefly: 12 HTTPX/pipx cases, one genuine
delayed-fix positive missed, 11 controls quiet. Say: “That is 0/1 supplied-label
recall and undefined precision with no predictions. We preserved the frozen
baseline and did not tune on that new case.” Do not present this as broad
accuracy or independent human verification.

## 6:00–7:15 — Naitik: design decisions and trade-offs

Trace the code once: Git snapshots → AST facts → Markdown spans → scoped linking
→ supported-before/contradicted-after verification → reports. The optional model
is a constrained interpretation step; it cannot run target code or apply fixes.

“We chose Python and Markdown, a standard-library implementation, and advisory
findings. Exact links limit recall, but make evidence reviewable. We abstain on
ambiguous scope, unsupported aliases and runtime behavior. We intentionally
avoided adding a backend or graph database before establishing correctness.”

Explain that CI's advisory analysis is deterministic and needs no model server
or API key. Local model-enabled analysis is a separate mode. These checks reduce
risk but do not prove the absence of false positives or prompt injection.

## 7:15–8:00 — Naitik: delivery and close

Show the actual latest green main CI, MIT license, team declaration, PR history,
input examples and corresponding actual outputs. Open the v0.1.0 GitHub preview
and its checksum/install verification; PyPI is deferred. Name Qwen and the coding
assistants truthfully. Do not claim an organizer submission unless confirmed.

“DriftLens makes supported documentation contradictions traceable to the change
that caused them. Our next priority is broader linking measured against new,
independent histories, after fixing reproduced false positives. The repository includes
both what worked and what failed, so a maintainer can inspect the evidence.”

## Four-minute Q&A drill

If asked which other projects were tested: “We also injected controlled default
changes into private copies of backoff, retry and urllib3 source, with generated
Markdown claims. All three changes were detected and 15 controls stayed quiet.
These are functional tests, not newly discovered upstream bugs or extra
historical recall.” The full pinned study is in examples/controlled/README.md.

Naitik: answer aloud without an assistant, then check the guide:

1. Why is this different from grep and doctest?
2. Which exact line verifies old support and current contradiction?
3. What did Qwen add, and what happens if it returns a wrong type or verdict?
4. Why does Black match, why do the other two histories remain missed, and why are three sentences only one successful historical case?
5. How does a same-PR doc fix avoid a false alarm?
6. Why is zero findings not proof that documentation is correct?
7. What runs on GitHub, and what requires the local model?

Use JUDGES_GUIDE.md for explanations. Stop and inspect the source/test whenever
you cannot explain a claim. Complete a real eight-minute spoken run with a
stopwatch before marking rehearsal complete; the agent's technical checks do not
substitute for that run.
