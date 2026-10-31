# Submission and Naitik demo handoff

Prepared from the implemented repository. **No submission has been made or
confirmed by this document.** Account confirmation and human rehearsal remain
open. Use this text in the actual event form; do not treat a prepared draft as a
submitted project.

## Copy-ready project fields

**Project name:** DriftLens

**Team name:** Fuoriclasse

**Repository:** https://github.com/naitik2004/driftlens

**Problem statement:** 05 — Automated Documentation Drift Detection

**Challenge:** Best Open-Source AI Project. Do not select the exclusive Gemma
track for this Problem 5/Qwen project.

**Members:** Naitik Pandey; Satya Prakash; Ravichandra Shinde.

**Technologies:** Python, Git, Python AST, Markdown, GitHub Actions, Ollama,
Qwen2.5-Coder 3B Q4_K_M.

**Product code license:** MIT. Model weights retain their separate license.

**Short description:**

DriftLens detects supported documentation contradictions introduced by Python
pull requests. It links exact Markdown sentences to old/new code facts and the
responsible diff, with advisory JSON and Markdown reports. Local Qwen helps
interpret constrained prose, while static evidence verifies the result.

**Longer description:**

DriftLens compares immutable Git snapshots and asks whether an unchanged
documentation claim was supported before a code change but contradicted after it.
It handles supported function defaults, removed parameters, direct argparse
options and a tightly constrained retry pattern. Reports preserve exact document
positions, before/after facts and diff evidence. An optional local Qwen model
extracts structured claims from otherwise unresolved prose, with schema, quote
and value validation. Unsupported or ambiguous evidence is left unverified.

The repository includes a CLI, advisory GitHub Actions workflow, MIT license,
79-test correction result, four deterministic demos, actual local-model outputs
and reproducible public-history experiments. AI added three verified findings in
a developer-selected synthetic suite. Both genuine historical drift cases in the
current corpus remain missed because they exercise unsupported patterns. The
project does not claim broad historical accuracy or general behavioral reasoning.

## What the form cannot verify automatically for us

1. Confirm the earlier repository-link form actually received the repo URL.
2. In OrganizerHQ, open the event and the team's submission; create one if absent.
3. Check repo, team, description, technologies and Best Open-Source AI Project.
4. Add all three members using their actual event accounts; GitHub names alone
   do not prove membership in OrganizerHQ.
5. Submit/save, then open the confirmation or submitted-project page and retain
   its URL and status. Check again before 6:30 AM IST on 1 November.
6. Choose the final green commit with the team. Do not assume this draft or a
   green GitHub run has frozen or submitted the project.

## Your personal presentation segments

The full speaker schedule is in [PRESENTATION.md](PRESENTATION.md).

**Opening, 45 seconds:** Explain the timeout 30 → 10 example and the three checks:
old code supported the sentence, new code contradicts it, same sentence remains.

**AI demonstration, 60 seconds:** Run this from the checkout with Ollama running:

```sh
python3 -m examples.live_model --output /tmp/driftlens-panel-live.json
```

Show baseline versus assisted finding counts, model_calls and evidence_strength.
Say: “Qwen interprets constrained prose; static analysis checks that interpretation
against old and new code before reporting drift.” The suite's three positive
paraphrases need the model; three of five controls are filtered without inference.
A completed request alone is not proof of contribution; the report must pass.

**Closing, 45 seconds:** Show actual green main CI, MIT license, PR history and
inputs/outputs. State the real-history limitation and the next bounded extension.
Do not claim organizer submission until confirmed.

If inference fails, read the warning and show a clearly labeled earlier actual
run. Do not call that fallback live or substitute a test double.

## Human completion check

Speak your segments aloud, then do one eight-minute run with both teammates and
a stopwatch. Each person should explain one finding end to end and answer a
question outside their ownership area. The agent's successful terminal runs do
not establish that this rehearsal or understanding has happened.
