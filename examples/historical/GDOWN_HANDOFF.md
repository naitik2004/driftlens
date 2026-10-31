# Satya → detector implementation: gdown folder limit

Status: provenance verified; **current detector misses this case**. This is an
implementation handoff for an existing corpus case, not another new example or a
claim that detector work is complete. Baseline: main `6047427`.

## Exact historical evidence

Public source: [wkentaro/gdown](https://github.com/wkentaro/gdown), MIT.

| Revision | Role |
|---|---|
| `373c16d983bcfafcd1ccd9f0fd826aa21d5c9365` | A: working old parser and client limit |
| `a7de85b30d77044c93dd7652c0194c60e51c401a` | Intermediate: removes constant/error; old references remain |
| `dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58` | B: replaces parser; README still stale |
| `5bb1faa88faa179ae114ab095515be3fd1324269` | C: later README correction |

A→B is two consecutive commits. Do not substitute the intermediate commit for A.
The replay verifies full SHAs, ancestry, retained text, removed code and exact
localization. It analyzes A/B before checking C. Discovery was retrospective:
C was inspected while selecting this case; this is not a blinded evaluation.

At [A, source lines 178–187](https://github.com/wkentaro/gdown/blob/373c16d983bcfafcd1ccd9f0fd826aa21d5c9365/gdown/download_folder.py#L178),
`MAX_NUMBER_FILES = 50` (line 22) feeds the guard:

```python
has_at_least_max_files = len(gdrive_file.children) == MAX_NUMBER_FILES
if not remaining_ok and has_at_least_max_files:
    # constructs a limit error message
    raise FolderContentsMaximumLimitError(message)
```

`remaining_ok` defaults to False; public `download_folder` forwards it at line
303. This is a default failure at the listing threshold, not proof that Google
Drive itself has a universal 50-file service limit.

At [B, replacement parser](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/gdown/download_folder.py#L210),
`_parse_embedded_folder_view` constructs the `embeddedfolderview` URL (216),
collects children (236–273), and the recursive caller traverses them (282–321).
Public `download_folder` calls that traversal at 144. The old constant and guard
are absent. This supports removal of the client cap; it does not prove unlimited
remote-service behavior. No upstream code or live folder download was executed.

The exact bullet survives in A and [B README line 21](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/README.md#L21):

> - Downloads folders recursively (up to 50 files per folder)

[C's documentation-only patch](https://github.com/wkentaro/gdown/commit/5bb1faa88faa179ae114ab095515be3fd1324269)
removes `(up to 50 files per folder)`. Its message explicitly attributes the
correction to the endpoint replacement. C corroborates the manual label; it must
not be supplied to inference or used as the detection rule.

## Expected result and ownership

Use the existing `gdown-folder-file-limit` label in `manifest.json`: path
`README.md`, line 21, Unicode character offset 925, exact bullet above, symbol
`gdown.download_folder.download_folder`, name `max_files_per_folder`, category
`folder_file_limit_changed`. The name denotes a reviewed concept, not an actual
function parameter. The category is a proposed behavioral category outside the
current detector. Agree any schema change explicitly; do not loosen localization
or relabel a miss just to pass the gate.

Ravichandra owns implementing a reusable bounded rule. Removing a constant alone
is insufficient evidence: require old numeric-limit enforcement, documentation
that describes that same operation and limit, and evidence the new operation no
longer enforces it. Abstain when the effective new bound is unresolved. Do not
special-case repository, SHA, URL, the number 50 or this exact README sentence.
If this behavior needs analysis beyond a safely bounded rule, report that limit.

Required implementation negatives: same effective bound renamed/inlined/moved;
unrelated numeric constants; docs updated with code; unchanged limit; conditional
bypass mistaken for universal removal. These are acceptance requirements for
Ravichandra, **not implemented or passing tests in this handoff**. The existing
real synchronized-removal control is useful but does not replace these tests.

## Reproduce and require the actual hit

Run from the repository root after cloning the four caches as described in the
corpus README. An absolute cache path can be substituted in the temporary
manifest. This uses existing replay and strict matching, with no detector changes:

```sh
python3 - <<'PY'
import json
from pathlib import Path
from examples.historical.replay import replay

source = Path('examples/historical/manifest.json').resolve()
manifest = json.loads(source.read_text())
manifest['cases'] = [c for c in manifest['cases'] if c['id'].startswith('gdown-')]
for case in manifest['cases']:
    case['repo'] = str((source.parent / case['repo']).resolve())
target = Path('/tmp/driftlens-gdown-acceptance-manifest.json')
target.write_text(json.dumps(manifest))
result = replay(target, Path('/tmp/driftlens-gdown-acceptance'))
rows = {r['id']: r for r in result['cases']}
positive = rows['gdown-folder-file-limit']
negative = rows['gdown-fuzzy-code-and-docs-together']
print(json.dumps(result, indent=2))
assert negative['predictions'] == 0, 'Synchronized-removal control regressed'
assert positive['known_hits'] == 1, 'Genuine stale folder-limit claim still missed'
assert positive['predictions'] == 1, 'Review additional predictions before accepting'
PY
```

Verified on the baseline using the existing local bare gdown cache: provenance
passes, positive **0 hits / 1 known label, 0 predictions**, negative **0
predictions**, no warnings. The acceptance command therefore **fails intentionally
on the missing hit**. Raw outputs: `outputs/gdown-folder-file-limit.json`,
`outputs/gdown-fuzzy-code-and-docs-together.json`; aggregate `outputs/evaluation.json`.
Full corpus remains **0/3** positives detected. Precision is undefined with no
predictions. No live Qwen inference is claimed by this deterministic evidence work.

Satya's evidence deliverable is complete. Detector success remains pending;
integration, false-positive review, full replay, model/demo checks and refreshed
presentation counts belong to the subsequent implementation/integration work.
