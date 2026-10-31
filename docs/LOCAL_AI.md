# Running and explaining local AI

DriftLens uses Qwen2.5-Coder 3B through Ollama. The model interprets constrained
prose claims; deterministic old/new source facts remain the verification boundary.
It does not execute target code, apply fixes or publish external PR comments.

## This laptop

The runtime is installed locally at `.local/ollama/ollama`; downloaded model files
are under `.local/ollama/models`. Both are ignored by Git. They are local setup
artifacts, not part of the distributable Python package. No global PATH change is
required. A fresh clone needs its own Ollama installation and model download.

From this checkout, start the server in a terminal if it is not already running:

```sh
OLLAMA_MODELS="$PWD/.local/ollama/models" \
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_CONTEXT_LENGTH=4096 OLLAMA_NUM_PARALLEL=1 \
  .local/ollama/ollama serve
```

Leave that terminal open. If it reports the port is in use, check the existing
server instead of starting a second one. In another terminal:

```sh
.local/ollama/ollama list
.local/ollama/ollama ps
python3 -m examples.live_model --output /tmp/driftlens-live-model.json
python3 -m examples.live_model --cases examples/model-cases.json \
  --output /tmp/driftlens-model-suite.json
```

If using a normal Ollama app installation, use `ollama` in place of the local
binary and start the app. Keep the adapter's default localhost endpoint. Download
weights once with `ollama pull qwen2.5-coder:3b`; inference after the download is
local. Do not include model weights or runtime binaries in commits.

## Reading the evidence

The standalone smoke test exits 0 only when a real uncached call adds the expected
finding, its quoted evidence matches old/new facts, and both reports have no
warnings. The suite runs three paraphrases plus five controls. Every case saves
its baseline, model-assisted report, expected outcome and last validated Ollama
response. API response timestamps, token counts and durations come from Ollama.
Reports also contain analyzer wall-clock runtime. There is no fabricated fallback.

The control cases exercise pre-existing incorrect docs, docs fixed together,
explicit examples, negation and unchanged defaults. Some are rejected before the
model is invoked. Report call counts per case; do not claim every control tests
model reasoning. All cases are synthetic and selected by the developers. They
are a contribution demonstration, not a real-world precision/recall benchmark.

`model_calls` counts requests attempted; by itself it does not establish success.
Inspect warnings, finding evidence strength, status and the saved API response.
Cache is disabled in these live tests. Ollama may reuse prompt/KV computation
internally; that is distinct from DriftLens replaying a cached verdict.

## If a run fails

Read the saved `warnings` and `abstentions`. A connection error means no local
server is listening or network access was denied. A model-not-found response
means the selected weights are absent from that server's configured model store.
A schema/quote mismatch is a rejected model response, not a finding. A timeout is
an inconclusive failed run. Do not change expected labels or inject a test double
to produce a successful demo artifact.

If the demonstration fails during judging, show a clearly labeled earlier actual
run and disclose the live failure. Deterministic analysis still works, but it does
not establish the mandatory meaningful AI contribution.

References: [Ollama macOS](https://docs.ollama.com/macos),
[chat API](https://docs.ollama.com/api/chat),
[model tag](https://ollama.com/library/qwen2.5-coder:3b).

## Observed run on 31 October 2026

[Results table and complete actual outputs](../examples/outputs/LIVE_AI.md)
record successful local inference with `driftlens-claim-v2`. The baseline missed
three paraphrases; the model-assisted run established all three. Five controls
stayed quiet, including three rejected without inference. There were five actual
requests across eight cases, with no DriftLens verdict cache. Model-enabled cases
took 1.87–2.71 seconds in this warm-model run; aggregate analyzer time was 12.75
seconds across all eight. These times are observations, not performance promises.

The first cold run took 10.88 seconds and failed: Qwen returned a string quantity
and reversed old/new verdicts. Its real output is included. We clarified types
and revision direction in the prompt, kept the cases and static verification
unchanged, and observed the successful run afterward. Model reliability remains
a limitation; one small suite is not a real-history benchmark.

The installed tag digest is
`f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225`.
Runtime: Ollama 0.40.13; hardware: Apple M3, 8 GB RAM; configured context: 4096.
Ollama reported about 2.16 GB of model allocation and one runner RSS sample was
2,095,088 KiB. Neither is peak memory; shared/GPU memory may overlap. Full metadata
and the verified runtime archive checksum are retained in the environment output.

## Behavioral review notes

`--review-candidates --model qwen2.5-coder:3b` optionally explains up to three
source-backed candidates. These notes remain unverified even when citations
validate. The review request uses an 8,192-token context and bounded output,
separately from the earlier default-extraction measurements above. No new peak
memory or broad accuracy claim is made for this path. Actual real-history
requests, controls and the rejected first gdown quote are retained in the final
verification evidence. See [BEHAVIOR_REVIEW.md](BEHAVIOR_REVIEW.md).
