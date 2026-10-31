# Actual local Qwen evidence

Observed on 31 October 2026, Apple M3 / 8 GB RAM. These are synthetic cases,
not historical project evaluation. Each baseline uses the same snapshots as its
assisted run. No DriftLens verdict cache was used.

| Case | Expected | Baseline | With Qwen | Model calls | Analyzer seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| paraphrased-default | 1 | 0 | 1 | 1 | 1.872 |
| default-amounts-to | 1 | 0 | 1 | 1 | 2.661 |
| value-before-default | 1 | 0 | 1 | 1 | 2.708 |
| preexisting-inaccuracy | 0 | 0 | 0 | 1 | 2.612 |
| docs-fixed-together | 0 | 0 | 0 | 0 | 0.077 |
| explicit-example | 0 | 0 | 0 | 0 | 0.085 |
| negated-claim | 0 | 0 | 0 | 1 | 2.667 |
| unchanged-default | 0 | 0 | 0 | 0 | 0.069 |

Three verified findings were added by model extraction; all five controls stayed
quiet. Three controls never reached the model. Five actual uncached requests
were made. This small developer-selected suite does not establish general
precision, recall, robustness, or freedom from prompt injection.

The first live run used prompt v1 and failed: the model returned a string value
and reversed old/new verdicts. The analyzer abstained. Prompt v2 clarifies scalar
types and revision direction; unchanged cases then passed. No label or static
verification rule was weakened.

Model: `qwen2.5-coder:3b`, `Q4_K_M`.
Model digest: `f72c60cabf6237b07f6e632b2c48d533cef25eda2efbd34bed21c5e9c01e6225`.
Ollama 0.40.13; configured context 4096; one parallel request.

Ollama reported approximately 2.16 GB of model allocation while loaded. A single
runner RSS sample was 2,095,088 KiB. This is not peak memory; GPU/shared pages may
overlap with process memory, so these values must not be added as physical RAM.

## Inputs and full outputs

- [Labeled input cases](../model-cases.json)
- [Standalone successful smoke test](live-model.json)
- [All eight actual suite results](live-model-suite.json)
- [Initial rejected real response](live-model-initial-failure.json)
- [Model, runtime and hardware metadata](live-model-environment.json)

Each successful model-assisted case retains the actual validated API response,
including generated JSON, timestamps, token counts and Ollama timing. Synthetic
commit IDs belong to temporary fixture histories, not public GitHub commits.

## Reproduce

Start Ollama with the same model installed, then run from the source checkout:

```sh
python3 -m examples.live_model --output /tmp/live-model.json
python3 -m examples.live_model --cases examples/model-cases.json \
  --output /tmp/live-model-suite.json
```

See [the local AI guide](../../docs/LOCAL_AI.md) for laptop setup, limitations
and failure interpretation. Runtime and generated text can vary on another run.
