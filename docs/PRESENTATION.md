# Eight-minute presentation: Fuoriclasse / DriftLens

This is a rehearsal script, not a record of completed human rehearsal. Every
member must explain the whole pipeline and operate their segment without an
agent. Test the exact demo laptop beforehand. The event allows eight minutes of
presentation and four minutes of Q&A.

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

## 0:45–2:45 — Ravichandra: deterministic live demonstration

Say explicitly: “This first demonstration uses controlled synthetic Git histories.”

```sh
python3 -m examples.demo
```

Show the drift-detected report preview. Point to the exact quote and line, old
30/new 10 source facts, responsible diff and suggested correction. Explain that
the analyzer reads committed snapshots, not uncommitted editor content.

Then show the removed-flag report and the direct instruction regression:

```sh
python3 -m unittest tests.test_detector_extensions -q
```

“The slide's `Use --timeout` instruction is now recognized when that exact flag
was supported before and removed now. We report removal. We do not prove that a
new `--deadline` flag means the same thing or actually stops a slow job.”

Show one committed test/source snippet. Do not spend the segment scrolling a
whole file or presenting a test double as real model execution.

## 2:45–3:45 — Satya: two important non-findings

Show documentation-fixed and harmless-refactor reports from the same demo run.

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

## 4:45–6:00 — Satya: real histories and honest limits

Show examples/historical/README.md and one pinned A/B/C source example.

“We also investigated actual public history. We analyze A and B before using C,
the later correction, for validation. The current corpus has two genuine drift
cases and two negative controls. The detector misses both positives: one needs
nested optparse/example semantics; the other needs computed cache-path reasoning.
Both are outside the implementation's scope today.

“We retain that 0/2 result rather than present synthetic success as historical
accuracy. This is an unblinded, small retrospective study, not a held-out benchmark.
It tells us exactly where a future bounded extension needs evidence.”

If a later reviewed PR changes these results, rerun the corpus and update this
script and reports before changing that claim. Never silently replace a miss
with a different task or count the absence of predictions as perfect precision.

## 6:00–7:15 — Ravichandra: design decisions and trade-offs

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
input examples and corresponding actual outputs. Name Qwen and the coding
assistants truthfully. Do not claim an organizer submission unless confirmed.

“DriftLens makes supported documentation contradictions traceable to the change
that caused them. Our next priority is a safely supported real-history positive,
then broader linking measured against independent cases. The repository includes
both what worked and what failed, so a maintainer can inspect the evidence.”

## Four-minute Q&A drill

Ask each other, without an assistant:

1. Why is this different from grep and doctest?
2. Which exact line verifies old support and current contradiction?
3. What did Qwen add, and what happens if it returns a wrong type or verdict?
4. Why are both real-history positives missed? What would a safe extension need?
5. How does a same-PR doc fix avoid a false alarm?
6. Why is zero findings not proof that documentation is correct?
7. What runs on GitHub, and what requires the local model?

Use JUDGES_GUIDE.md for explanations. Stop and inspect the source/test whenever
someone cannot explain a claim. Complete a real eight-minute spoken run with a
stopwatch before marking rehearsal complete; the agent's technical checks do not
substitute for that run.
