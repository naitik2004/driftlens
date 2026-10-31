# Real historical replay

This corpus contains **two genuine stale-documentation histories and two real
negative controls**. Both positives are outside the current detector's supported
patterns. They are useful scope failures, not evidence of successful detection.
This is deterministic evaluation: no model is loaded and upstream code is never
imported or executed.

## Reproduce

From the DriftLens checkout, put bare Git histories in an explicit sibling cache
outside this repository. No upstream working trees or dependencies are needed:

```sh
mkdir -p ../driftlens-history-cache
git clone --bare https://github.com/yt-dlp/yt-dlp.git ../driftlens-history-cache/yt-dlp.git
git clone --bare https://github.com/psf/black.git ../driftlens-history-cache/black.git
git clone --bare https://github.com/un33k/python-slugify.git ../driftlens-history-cache/python-slugify.git
python3 -m examples.historical.replay
python3 -m unittest discover -v
```

Existing caches can be updated with `git -C PATH fetch origin`. The manifest pins
full SHAs, so later upstream changes do not change the selected snapshots.
`--output /tmp/driftlens-history-results` keeps regenerated artifacts separate.
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
| yt-dlp-multistream-default | 0/1 | 0 | 0 | 28.182 |
| black-cache-filename | 0/1 | 0 | 4 | 7.834 |
| yt-dlp-whitespace-control | 0/0 | 0 | 0 | 28.690 |
| slugify-code-and-docs-together | 0/0 | 0 | 0 | 0.322 |

**Known-label recall: 0/2 (0%).** Both genuine drift labels were missed.
Both negative controls produced zero findings. All four reports record zero model
calls. Precision is undefined because there are no predictions; no broad
accuracy or AI-benefit claim is made. The four Black warnings concern upstream
Python-2/invalid-syntax test fixtures, not the changed `black.py` source.

Raw reports and the harness metrics are in [outputs/](outputs/). The independent
harness replay measures its own runtime, so its durations differ from the saved
individual reports. Correction evidence is empty when there are no predictions;
positive A/B/C verification is recorded by the manifest, source links and replay
checks rather than inferred from that empty field.

## Method and interpretation

A is B's immediate parent in every case. Each positive has an unchanged exact
claim at A and B, old supporting source, contradictory source at B, and a later
correction C descended from B. Only A/B are passed to the analyzer. C's source,
patch and message never enter detection or model retrieval. Correction commits
were used to discover candidates, so this is a retrospective, unblinded case
study, not a held-out accuracy benchmark. The runner checks C only after saving
the detector report.

Labels in `manifest.json` include exact B path, quote, one-based line number,
zero-based Unicode start offset, subject, parameter/flag and category. The two
positive labels intentionally represent manually verified drift beyond current
support. `cache_path_changed` is a manual behavioral label, not a new detector
category. Unsupported subjects do not have to exist in extracted facts.

Positive cases have `fully_reviewed: false`: only the named claims are labeled;
the corpus does not assert exhaustive coverage of all stale text. Negative
controls have their entire changed diff and every prediction reviewed. Empty
predictions have undefined precision, not 100% precision. Report known-label
recall over supplied labels only. Do not describe zero findings as verified docs.
The stored analyzer warnings remain visible.

The reports were generated on Python 3.14.6 from analyzer version 0.1.0, based on
team main `d0acb94ab8835d296e5d261c973582c0888ac160`. Runtime is machine-dependent.
The evaluator's limitations text is updated to avoid claiming no corpus exists;
its API, matching and metric definitions are unchanged.

## Cases and public evidence

### yt-dlp-multistream-default

The video/audio defaults change from True to False. The unchanged example omits the opt-in flags and still promises all three formats; the later docs add both flags. Optparse inside parseOpts and behavioral examples are outside current support.

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

Label subject: `youtube_dlc.options.parseOpts`, name `--video-multistreams`, category `flag_default_changed`. parseOpts is the actual callable defining the optparse option; the extractor currently emits no flag fact for it.

### black-cache-filename

The old filename uses line length and an integer flag. B switches to a multi-part mode key including target versions. The old path remains in README; C corrects it after docs have moved. Computed return values and cache-path behavior are outside current support.

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

Label subject: `black.get_cache_file`, name `mode`, category `cache_path_changed`. cache_path_changed is a manual behavioral category outside the current detector categories; it does not add a detector feature.

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

For yt-dlp, the option definitions and `YoutubeDL.build_format_selector`
both change multiple-stream defaults from True to False. With no opt-in flags,
the old promise of merging all three formats is therefore stale. The later fix
adds both opt-in flags to that same example. The detector recognizes direct
module-level argparse definitions, not nested optparse groups, and deliberately
skips explicit examples; no warning or abstention is emitted for this miss.

For Black, A builds `cache.<line-length>.<integer-mode>.pickle`; B uses a mode
key containing target-version, line-length and formatting-option components.
The documented filename remains unchanged. C fixes the documentation in its
new location years later. The harness's `old_quote_still_present` field alone
cannot establish a correction after a doc move: this runner also checks the
explicit corrected path and replacement text. Computed filename behavior is
outside the supported default/removal checks.

## Search ledger and limits

The initial search inspected histories in yt-dlp, Black and python-slugify and
stopped after finding the above bounded corpus. It did not perform an exhaustive
search or use a 45-minute timebox as a claim of search coverage.

| Candidate | Decision |
| --- | --- |
| yt-dlp multistream defaults and later example correction | Included genuine positive; optparse and example semantics unsupported |
| Black cache format and later docs correction | Included genuine positive; computed cache-path behavior unsupported |
| Black default include-list correction (`52ab313a`) | Excluded: no verified earlier supported-claim/code-change pair |
| python-slugify `word_boundaries` rename (`683364ea`) | Excluded: no matching Markdown claim or later correction found |
| python-slugify Unicode opt-in addition (`d968ca74`) | Included as synchronized code/docs negative, not historical drift |
| yt-dlp single trailing-space removal (`4eacbc17`) | Included as formatting-only negative; identical Python ASTs |

This corpus measures neither AI contribution nor broad project accuracy. It
contains no detected real-history positive. These cases should not be used to
tune a detector and then called held-out evaluation; repository overlap between
development and evaluation must remain explicit. Source snippets retain the
upstream notices in `licenses/`.

## Satya's explanation for the team

“I checked actual Git snapshots instead of making a synthetic repository. In
yt-dlp the two multistream defaults changed from True to False, but the README
example still promised all three formats without enabling either option. A later
commit added the missing flags. DriftLens returned no finding because its static
extractor does not support that optparse setup and it excludes examples. That is
a verified limitation, and I saved the raw result rather than counting it as a
success.”
