# Implementation status

DriftLens analyzes Python and Markdown from immutable Git snapshots without
executing the target project. The analyzer has no third-party runtime dependencies.

## Supported behavior

- Public top-level parameter/default facts, including positional-only and
  keyword-only arguments; conservative removal and compatibility checks.
- Direct module-level argparse flags and supported optparse Boolean actions in
  public functions. Shared destinations use ordered explicit defaults;
  ambiguous registrations and dynamic overrides abstain.
- Bounded constants/imports, a constrained retry-count pattern and a declared
  cache-filename layout comparison.
- Source-mapped Markdown sentences/tables, scoped linking, old-support/new-
  contradiction checks, and suppression when documentation is corrected.
- Grouped JSON/Markdown findings, responsible diffs, commit-pinned source links
  and advisory GitHub annotations.
- Optional local Qwen extraction with validated quote, subject, schema and value.
- Optional behavioral candidates and source-cited model notes, kept separate
  from verified findings, annotations, build failures and recall.
- Snapshot resource limits, Git timeouts and explicit UTF-8 report handling.

## Run and verify

```sh
python3 -m unittest discover -v
python3 -m examples.demo
```

The current suite has 146 tests. The four deterministic scenarios expect finding
counts 1/0/0/1. CI checks Linux, macOS and Windows, distribution metadata and a
fresh installed CLI. See [verification](docs/VERIFICATION.md),
[installation](docs/GETTING_STARTED.md) and [release workflow](docs/PUBLISHING.md).

Evaluation is intentionally separated:

- [Development histories](examples/historical/README.md): 1/3 original positive
  labels detected; three real controls quiet.
- [External histories](examples/evaluation/README.md): 0/1 positive labels;
  11 controls quiet. Precision is undefined with no predictions.
- [Controlled source mutations](examples/controlled/README.md): 18/18 scenarios,
  with three injected changes detected and 15 controls quiet. These are synthetic.
- [Actual local-model checks](docs/LOCAL_AI.md): saved inference responses and
  clearly labeled model-assisted results.

## Limitations

General behavioral inference, arbitrary wrappers/callers, computed configuration,
re-export aliases, complex parsers and additional programming languages are not
verified. Literal defaults do not establish physical units or effective runtime
values. The cache rule assumes its supported declared types and local helper
shape; runtime overrides and filesystem normalization are outside its scope.
The yt-dlp/gdown behavioral histories remain unverified; review candidates do
not count as successful detections. See [details](docs/BEHAVIORAL_MISSES.md).
