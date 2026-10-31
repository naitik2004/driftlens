# Real historical replay

This corpus contains **three genuine stale-documentation histories and three real
negative controls**. Black is now detected by a bounded declared-layout rule. The other two
positives remain misses, and are retained as scope failures.
This is deterministic evaluation: no model is loaded and upstream code is never
imported or executed.

Implementation handoff for the existing gdown miss: [exact evidence and acceptance gate](GDOWN_HANDOFF.md).

## Reproduce

From the DriftLens checkout, put bare Git histories in an explicit sibling cache
outside this repository. No upstream working trees or dependencies are needed:

```sh
mkdir -p ../driftlens-history-cache
git clone --bare https://github.com/yt-dlp/yt-dlp.git ../driftlens-history-cache/yt-dlp.git
git clone --bare https://github.com/psf/black.git ../driftlens-history-cache/black.git
git clone --bare https://github.com/un33k/python-slugify.git ../driftlens-history-cache/python-slugify.git
git clone --bare https://github.com/wkentaro/gdown.git ../driftlens-history-cache/gdown.git
python3 -m examples.historical.replay
python3 -m unittest discover -v
```

Existing caches can be updated with `git -C PATH fetch origin`. The manifest pins
full SHAs, so later upstream changes do not change the selected snapshots.
`--output /tmp/driftlens-history-results` keeps regenerated artifacts separate.
Use `--cache-dir /absolute/cache` to select a directory containing the four
`NAME.git` histories without editing the manifest. A manual GitHub Actions
workflow, `Historical replay (manual)`, fetches/cache these public histories,
checks the known Black label and all negative controls, and retains artifacts.
It is separate from ordinary fast CI and makes no held-out accuracy claim.
The replay verifies A/B ancestry, exact quote offsets and code evidence, writes
individual actual reports, then verifies C and runs the existing metric harness.
The latter analyzes A/B again, so total replay time exceeds the sum of individual
report runtimes. Missing Git objects or failed evidence checks exit nonzero.
A successful replay means the experiment completed; it does not mean recall is 1.

The harness alone can also be run directly:

```sh
python3 -m driftlens.evaluate examples/historical/manifest.json --output /tmp/driftlens-evaluation.json
```

## Observed results

| Case | Supplied labels found | Findings | Warnings | Saved report runtime (s) |
| --- | --- | --- | --- | --- |
| yt-dlp-multistream-default | 0/1 | 0 | 0 | 46.245 |
| black-cache-filename | 1/1 | 3 | 4 | 8.306 |
| yt-dlp-whitespace-control | 0/0 | 0 | 0 | 28.940 |
| slugify-code-and-docs-together | 0/0 | 0 | 0 | 0.328 |
| gdown-folder-file-limit | 0/1 | 0 | 0 | 0.563 |
| gdown-fuzzy-code-and-docs-together | 0/0 | 0 | 0 | 0.597 |

Known-label recall is **1/3 (33.3%)** in `outputs/evaluation.json`; all three
negative controls still produce zero findings. Black's exact existing Linux label
is matched. The Windows/macOS sentences are also reported, for three sentence
findings in one underlying change group. They were manually reviewed after
A/B detection and corroborated by C; original labels were not expanded to inflate
recall. Positive labels are not exhaustive, so precision remains undefined.

The bounded rule compares an old declared two-numeric-field filename against a
new local helper that joins five parts. It does not execute the helper or guess
its values. See [the rule and negative tests](../../docs/CACHE_LAYOUT.md),
[readable actual output](outputs/black-cache-filename.md), and
[reviewed locations](outputs/black-cache-filename.review.json).
The yt-dlp example and gdown limit still remain misses.

Raw reports and the harness metrics are in [outputs/](outputs/). The independent
harness replay measures its own runtime, so its durations differ from the saved
individual reports. Correction evidence is empty when there are no predictions;
positive A/B/C verification is recorded by the manifest, source links and replay
checks rather than inferred from that empty field.

## Method and interpretation

A is B's immediate parent in the original four cases and the new synchronized
removal control. The gdown limit change spans two consecutive commits; A is
before both, avoiding an intermediate source state with dangling references to
the removed limit constant. Each positive has an unchanged exact
claim at A and B, old supporting source, contradictory source at B, and a later
correction C descended from B. Only A/B are passed to the analyzer. C's source,
patch and message never enter detection or model retrieval. Correction commits
were used to discover candidates, so this is a retrospective, unblinded case
study, not a held-out accuracy benchmark. The runner checks C only after saving
the detector report.

Labels in `manifest.json` include exact B path, quote, one-based line number,
zero-based Unicode start offset, subject, parameter/flag and category. The three
positive labels represent manually verified drift. Black is now supported by the
bounded `cache_path_changed` rule; the other two subjects remain outside supported
patterns. Original labels and SHAs are unchanged. All six cases are marked
`development`: they have been inspected during development and provide no held-out
accuracy estimate. Unsupported subjects need not exist in extracted facts.

Positive cases have `fully_reviewed: false`: only the named claims are labeled;
the corpus does not assert exhaustive coverage of all stale text. Negative
controls have their entire changed diff and every prediction reviewed. Empty
predictions have undefined precision, not 100% precision. Report known-label
recall over supplied labels only. Do not describe zero findings as verified docs.
The stored analyzer warnings remain visible.

The current reports were regenerated on Python 3.14.6 / analyzer 0.1.0 by the
filename-layout continuation, based on main
`b4f881698e12d26673fd0be9945c97ea6a2884c6`. Earlier corpus results are preserved in
Git history. Runtime is machine-dependent.
The evaluator's limitations text is updated to avoid claiming no corpus exists;
its API, matching and metric definitions are unchanged.

## Cases and public evidence

### yt-dlp-multistream-default

The video/audio defaults change from True to False. The unchanged example omits the opt-in flags and still promises all three formats; the later docs add both flags. Direct optparse groups are now extracted, but this behavioral example still does not state a literal default or name the changed flag.

- A (2021-01-05): [`50865ca803a130308c064c2de5c7140754382993`](https://github.com/yt-dlp/yt-dlp/commit/50865ca803a130308c064c2de5c7140754382993).
- B (2021-01-05): [`91ebc64068d2957400dbfaadff23e995392b3963`](https://github.com/yt-dlp/yt-dlp/commit/91ebc64068d2957400dbfaadff23e995392b3963).
- C (2021-07-19): [`dce87436778a3448a3db098617eabe5541f6f229`](https://github.com/yt-dlp/yt-dlp/commit/dce87436778a3448a3db098617eabe5541f6f229).
- License at B: [Unlicense](https://github.com/yt-dlp/yt-dlp/blob/91ebc64068d2957400dbfaadff23e995392b3963/LICENSE); notice copied to `licenses/yt-dlp.txt`.

Exact B claim, [README.md:885](https://github.com/yt-dlp/yt-dlp/blob/91ebc64068d2957400dbfaadff23e995392b3963/README.md#L885), Unicode offset 58525:

> For example, `-f bestvideo+best+bestaudio` will download and merge all 3 given formats.

[A support](https://github.com/yt-dlp/yt-dlp/blob/50865ca803a130308c064c2de5c7140754382993/youtube_dlc/options.py#L441):

```python
action='store_true', dest='allow_multiple_video_streams', default=True,
```

[B contradiction](https://github.com/yt-dlp/yt-dlp/blob/91ebc64068d2957400dbfaadff23e995392b3963/youtube_dlc/options.py#L441):

```python
action='store_true', dest='allow_multiple_video_streams', default=False,
```

[Later correction](https://github.com/yt-dlp/yt-dlp/blob/dce87436778a3448a3db098617eabe5541f6f229/README.md#L1105):

> For example, `-f bestvideo+best+bestaudio --video-multistreams --audio-multistreams` will download and merge all 3 given formats.

Label subject: `youtube_dlc.options.parseOpts`, name `--video-multistreams`, category `flag_default_changed`. The extractor now emits a fact for direct optparse calls in the function body. The report remains a miss because this sentence contains no exact option reference and does not state a literal default. Do not infer a finding from the format selector alone.

### black-cache-filename

The old filename uses line length and an integer flag. B switches to a multi-part mode key including target versions. The old path remains in README; C corrects it after docs have moved. The bounded declared-layout detector now matches this known case; arbitrary computed behavior remains unsupported.

- A (2019-02-06): [`a9d8af466a65b7d88ea35e0ff4c460175098260e`](https://github.com/psf/black/commit/a9d8af466a65b7d88ea35e0ff4c460175098260e).
- B (2019-02-06): [`36d3c516d3c09fc5f05c420900dd6b854e3c8bbd`](https://github.com/psf/black/commit/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd).
- C (2026-10-22): [`137766332565267cad23aea28bcfef4569439edd`](https://github.com/psf/black/commit/137766332565267cad23aea28bcfef4569439edd).
- License at B: [MIT](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/LICENSE); notice copied to `licenses/black.txt`.

Exact B claim, [README.md:886](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/README.md#L886), Unicode offset 35239:

> * Linux: `/home/<username>/.cache/black/<version>/cache.<line-length>.<file-mode>.pickle`

[A support](https://github.com/psf/black/blob/a9d8af466a65b7d88ea35e0ff4c460175098260e/black.py#L3602):

```python
return CACHE_DIR / f"cache.{line_length}.{mode.value}.pickle"
```

[B contradiction](https://github.com/psf/black/blob/36d3c516d3c09fc5f05c420900dd6b854e3c8bbd/black.py#L3701):

```python
return CACHE_DIR / f"cache.{mode.get_cache_key()}.pickle"
```

[Later correction](https://github.com/psf/black/blob/137766332565267cad23aea28bcfef4569439edd/docs/usage_and_configuration/file_collection_and_discovery.md#L18):

> - Linux: `/home/<username>/.cache/black/<version>/cache.<mode-key>.pickle`

Label subject: `black.get_cache_file`, name `mode`, category `cache_path_changed`.
The original label is unchanged and now matches. The rule does not calculate the
version string, instance state or final key. It proves a five-item dot-join lower
bound, contradicting the old declared two-numeric-field template. Exact Linux
localization is retained, and the two extra platform references are reviewed
separately rather than used to inflate known-label recall.

### yt-dlp-whitespace-control

The entire commit removes one trailing space after a dictionary entry in youtube_dl/extractor/rtlnl.py. Python ASTs are identical; no Markdown changes.

- A (2020-09-08): [`e182ba877bff741a96e511eac53f25fe3e015e8c`](https://github.com/yt-dlp/yt-dlp/commit/e182ba877bff741a96e511eac53f25fe3e015e8c).
- B (2020-09-08): [`4eacbc172264cb8121e44e39ac40f9e959a7b4e2`](https://github.com/yt-dlp/yt-dlp/commit/4eacbc172264cb8121e44e39ac40f9e959a7b4e2).
- License at B: [Unlicense](https://github.com/yt-dlp/yt-dlp/blob/4eacbc172264cb8121e44e39ac40f9e959a7b4e2/LICENSE); notice copied to `licenses/yt-dlp.txt`.

### slugify-code-and-docs-together

The new opt-in allow_unicode=False parameter and CLI flag are documented in the same commit, including the README signature and Unicode examples. Existing defaults stay unchanged; this is a synchronized feature addition, not a default-change control.

- A (2022-02-16): [`07b87da81140cf51e4a585e43d4fe9113f4c2ad5`](https://github.com/un33k/python-slugify/commit/07b87da81140cf51e4a585e43d4fe9113f4c2ad5).
- B (2022-02-22): [`d968ca7419e6f4e40685888c56d03bea50fd39d7`](https://github.com/un33k/python-slugify/commit/d968ca7419e6f4e40685888c56d03bea50fd39d7).
- License at B: [MIT](https://github.com/un33k/python-slugify/blob/d968ca7419e6f4e40685888c56d03bea50fd39d7/LICENSE); notice copied to `licenses/python-slugify.txt`.

For yt-dlp, `--video-multistreams` and `--audio-multistreams` change from
True to False. The exact-reference policy permits a flag claim only when the
claim contains that option string. The stale example omits it and requires
deriving format-selector behavior from defaults, so the detector does not force
a finding. The separate conditional sentences mentioning
`--no-video-multistreams` and `--no-audio-multistreams` remain accurate.

For Black, A builds `cache.<line-length>.<integer-mode>.pickle`; B returns
`cache.{mode.get_cache_key()}.pickle`. Resolving the latter requires following
`get_cache_key`, evaluating a sorted enum comprehension and instance attributes,
then joining computed components. The new bounded rule does not resolve the values of that call chain. It instead
proves that the declared five-part dot-join cannot match the old two-numeric-field
string layout. It now detects all three retained platform sentences. C corrects the
documentation in its new location; the replay verifies that path explicitly.

The defaults-semantics correction regenerated these outputs and reran the full
replay without changing the pinned revisions or labels. The corpus grew from 0/2 to 0/3 before the detector extension; the new filename
rule now matches 1/3 original labels without changing the manifest.


### gdown-folder-file-limit

A enforces a 50-file limit in the old folder-listing implementation. The next two
commits remove the limit machinery and replace the listing endpoint while the
README bullet remains unchanged. C later removes the stale parenthetical.

- A: [`373c16d983bcfafcd1ccd9f0fd826aa21d5c9365`](https://github.com/wkentaro/gdown/commit/373c16d983bcfafcd1ccd9f0fd826aa21d5c9365).
- B: [`dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58`](https://github.com/wkentaro/gdown/commit/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58).
- C: [`5bb1faa88faa179ae114ab095515be3fd1324269`](https://github.com/wkentaro/gdown/commit/5bb1faa88faa179ae114ab095515be3fd1324269).
- License at B: [MIT](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/LICENSE), copied to `licenses/gdown.txt`.

The exact stale [README.md:21](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/README.md#L21) bullet is:

> - Downloads folders recursively (up to 50 files per folder)

[A's source](https://github.com/wkentaro/gdown/blob/373c16d983bcfafcd1ccd9f0fd826aa21d5c9365/gdown/download_folder.py#L22)
declares `MAX_NUMBER_FILES = 50`; lines 178–186 check the returned child count
and raise the limit error by default. [B's source](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/gdown/download_folder.py#L210)
uses `/embeddedfolderview` and enumerates the returned anchors instead. The
replay requires the old limit identifier to be absent at B. The intermediate
`a7de85b30d77044c93dd7652c0194c60e51c401a` removes its declaration while the old
parser still references it; that intermediate is not presented as a supported A.

After the A/B report is saved, the runner checks C's replacement bullet:

> - Downloads folders recursively

Label `folder_file_limit_changed` is a manual behavioral category. Its subject is
the real public function `gdown.download_folder.download_folder`;
`max_files_per_folder` names the reviewed concept, not a Python parameter.
The detector cannot derive a folder-service cap from this implementation and
produces zero findings and zero warnings. Static source plus the later correction
establish the reviewed documentation change; no claim about current Google Drive
service capacity or measured runtime behavior is made.

### gdown-fuzzy-code-and-docs-together

- A: [`6a435009d5bf3f2ffc99f47d209e0e8b4173c1e9`](https://github.com/wkentaro/gdown/commit/6a435009d5bf3f2ffc99f47d209e0e8b4173c1e9).
- B: [`b1c6e1ce257d4fa247304adcd181cdf8e7651c74`](https://github.com/wkentaro/gdown/commit/b1c6e1ce257d4fa247304adcd181cdf8e7651c74).
- License: the same gdown MIT notice above.

The complete seven-file diff removes `fuzzy` from the download API and CLI, and
updates every README usage in that same commit. The replay checks removal from
both `gdown/download.py` and `README.md`. It is a synchronized removal negative,
not a delayed-fix positive. The actual report has zero findings and zero warnings.

## Follow-up audit and rejected candidates

[TEAM_AUDIT.md](TEAM_AUDIT.md) records what each teammate already completed before
this continuation. [SEARCH_LOG.md](SEARCH_LOG.md) preserves rejected candidates,
bounded searches and the no-upstream-execution boundary. This continuation changes
only the historical workstream and does not claim to close the detector's
successful-real-history gap. Shared integration/presentation summaries need their
case counts reconciled by the integration owner after review.

## Detector continuation

This rule was developed against the already-known Black case, so its success is
a retrospective development result, not held-out evaluation. The underlying
source change is counted once among the original three labels. Two extra
platform references are retained and reviewed, not silently discarded or called
false positives. C was read only for after-the-fact corroboration, never as input
to the detector. Runtime type/dispatch overrides and filesystem normalization are
not evaluated by this declared-layout rule.
