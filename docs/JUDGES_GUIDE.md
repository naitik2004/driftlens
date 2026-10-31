# DriftLens: understand it, demonstrate it, defend it

## The explanation every member should know

Documentation makes claims about code. A pull request can change code while
leaving its explanation untouched. DriftLens finds the exact stale sentence and
shows the old fact, new fact and responsible change.

Example: `connect(timeout=30)` becomes `connect(timeout=10)`, but README still
says "The connect timeout defaults to 30 seconds." We need three pieces of proof:
the old code agreed, the new code disagrees, and the sentence is still there.
Without all three, the system does not assert newly introduced drift.

A **PR** is a proposed change on a branch. **CI** runs automated checks for that
change. An **AST** is Python's parsed syntax tree: it lets us read a declared
parameter default without importing or executing the code. A **Git snapshot** is
the content at a particular commit, independent of uncommitted editor changes.
An **abstention** means evidence was insufficient, not that documentation is correct.

## Follow one finding through the actual code

1. `cli.py`: accepts repo/base/head, optional model and output options.
2. `snapshots.py`: resolves immutable commits and their merge base; reads Python
   and Markdown from Git objects; collects renamed paths and changed-code hunks.
3. `facts.py`: Python ast extracts declared function defaults, parameters, simple
   constants, direct argparse flags and one tightly restricted retry pattern.
4. `markdown.py`: keeps exact original passage, heading, line and character offsets.
5. `analyzer.py`: compares facts, links exact symbol/flag references, checks the
   same claim in the old snapshot and filters examples/qualifiers/ambiguity.
6. `model.py`, when enabled: asks local Qwen to extract a constrained claim from
   unresolved prose. The response must match the supplied quote/symbol/schema;
   the literal and old/new values still have to agree with static evidence.
7. `reporting.py`: produces JSON, readable Markdown, pinned source links and
   advisory workflow annotations. No automatic posts to external projects.

Know where to open each file. Read one test and one output yourself; do not just
memorize the architecture diagram. Names in ARCHITECTURE.md are proposals;
README.md and tested code define what is actually supported.

## What is implemented versus still unproven

The inspected MVP has 49 passing original tests and four passing synthetic demos.
This planning branch adds a tested live-model contribution harness. Main's hosted
CI passed after PR #1. These facts do not establish real-world accuracy.

Live local inference was subsequently observed: prompt v2 produced three
model-assisted findings that the baseline missed, and five synthetic controls
stayed quiet. See [actual evidence](LOCAL_AI.md). The first live run failed and
was rejected; do not claim the model is always reliable. Historical replay tooling
exists, but no real A/B/C corpus was bundled at the inspected baseline. Update
that claim only after Satya's evidence is reviewed.
The GitHub workflow runs deterministic analysis without Qwen; local model-enabled
analysis is a separate product mode. Explain that distinction directly.

## Eight-minute presentation allocation

| Time | Speaker | Show and explain |
| --- | --- | --- |
| 0:00–0:45 | Naitik | Maintainer problem and the 30-to-10 timeout example |
| 0:45–2:45 | Ravichandra | Live real finding: sentence, old/new code, responsible diff |
| 2:45–3:45 | Satya | Docs fixed together and harmless refactor: no new drift |
| 3:45–4:45 | Naitik | Actual Qwen contribution with model-off/model-on comparison |
| 4:45–6:00 | Satya | Real historical A/B/C example, measured results and misses |
| 6:00–7:15 | Ravichandra | AST + exact linking + verification; abstention and trade-offs |
| 7:15–8:00 | Naitik | GitHub integration, green CI, honest limits and next extension |

Only present a live-model/historical result if it actually exists. If not, disclose
that gap; do not replace it with a mocked or relabeled synthetic demonstration.
Pre-open terminal, code diff, report and Actions results. Use local saved evidence
as a clearly labeled fallback if venue internet fails. Do not claim a recorded
run is a live run. Keep the spoken pitch below eight minutes during rehearsal.

## Commands to rehearse

```sh
python3 -m unittest discover -v
python3 -m examples.demo
cat examples/outputs/drift-detected.md
cat examples/outputs/documentation-fixed.md
cat examples/outputs/harmless-refactor.md
python3 -m examples.live_model --output /tmp/driftlens-live-model.json
```

For a real PR/history, substitute verified commits and the public upstream URL:

```sh
python3 -m driftlens --repo /path/to/public-project --base VERIFIED_A --head VERIFIED_B \
  --repository-url https://github.com/OWNER/REPO --json /tmp/report.json --summary /tmp/report.md
```

The default synthetic demo does not need a model. Live model validation needs
Ollama plus Qwen already installed. The live harness exits 1 if contribution is
not demonstrated; warnings in the saved report explain why.

## Questions judges are likely to ask

**Why not just use grep?** Grep finds words. We compare parsed facts in two code
snapshots, preserve exact doc positions and require support-before/contradiction-after.
Current linkage still uses exact references; indirect semantic retrieval is limited.

**Why not doctest?** Doctest executes examples. Our target is descriptive prose
and tables whose claims became wrong because of a code change.

**Where exactly does AI help?** Today it extracts a literal default claim from
otherwise unresolved, already-linked prose; static evidence constrains the result.
Show an actual uncached model-assisted report. Do not claim arbitrary reasoning.

**Is AI necessary for every finding?** No. Deterministic checks handle concrete
patterns cheaply; AI extends a limited prose interpretation path. Measure its
incremental contribution and be honest about the small evaluation scope.

**How do you stop hallucinations?** Validate the schema and exact quote/subject,
require a literal from the passage and agreement with known old/new facts, and
abstain on uncertainty. These reduce errors; they are not a proof of zero errors.

**Why not report every possible issue?** Maintainers pay a cost for false alarms.
We prefer verifiable findings and explicit abstention to unsupported accusations.

**How do you know it was caused by this PR?** The claim must exist in A and B;
A's extracted fact agrees, B's fact differs, and a relevant diff hunk is attached.
Pre-existing inaccuracies are not classified the same way.

**What if docs are fixed in the same PR?** A corrected current sentence should
not yield the old unchanged claim, so the stale-claim check is suppressed.

**What if zero findings appear?** It means no drift was established in supported
scope, not that all documentation is correct. Read warnings and abstentions.

**What about untrusted code or prompt instructions in README?** We read Git objects
and parse syntax, not import the target. Repository data is marked untrusted for
the model; model output cannot execute commands. This is not a general sandbox.

**What is unsupported?** At baseline: methods/nested functions, broad config
frameworks, arbitrary wrappers/aliases, implicit prose links, many Markdown
extensions, general behavior and languages beyond Python. Check later merged PRs
before claiming a new capability.

**What does the model license allow?** The product code is MIT; model weights have
their own license. Qwen2.5-Coder 3B is open-weight with a Qwen Research license on
the inspected Ollama page. Do not call its weights MIT or assume every Qwen size
shares the same license.

**How did you evaluate without cheating?** Detect using A/B only; inspect later C
only afterward. Report actual manually reviewed labels, misses, false alarms,
runtime and exact localization. Four synthetic successes are not 100% real-world
accuracy. Avoid using future correction text in model prompts.

**Who built and understands it?** Explain the actual three ownership areas, name
coding assistants truthfully, and have every person trace one full finding.

## Rehearsal drill

Each member gets two minutes, without an agent, to explain the full pipeline.
Then another member changes a default, fixes its docs, or introduces ambiguous
scope and asks what the tool should do. Open the code and test to check the answer.
Any claim you cannot demonstrate gets removed or qualified before presentation.
