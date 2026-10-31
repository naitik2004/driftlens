# Bounded historical candidate search

This follow-up searched local bare public Git histories on 1 November 2026.
Commands used `git log`, `git show`, `git diff` and the existing deterministic
analyzer. Upstream code, tests, installers and downloads described by the
projects were never executed. This is retrospective candidate discovery, not a
random sample or held-out accuracy benchmark. Search stopped after obtaining
one additional verified positive and one real control; no successful new
detector hit was found.

The existing yt-dlp, Black and python-slugify cases were reviewed before searching
additional histories in python-dotenv, python-tabulate, Mistune and gdown.
Searching a repository does not mean its whole history was exhaustively reviewed.

| Candidate and inspected public evidence | Decision | Reason |
| --- | --- | --- |
| gdown: [endpoint change](https://github.com/wkentaro/gdown/commit/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58), then [README correction](https://github.com/wkentaro/gdown/commit/5bb1faa88faa179ae114ab095515be3fd1324269) | Added genuine positive | Old code enforces 50, B replaces the listing mechanism and removes that cap, the same README bullet remains, and C removes the parenthetical later. Actual detector output is empty. |
| gdown: [remove fuzzy](https://github.com/wkentaro/gdown/commit/b1c6e1ce257d4fa247304adcd181cdf8e7651c74) | Added negative control | Python/CLI options and all README uses change together. It is not delayed documentation drift. Complete seven-file diff and all predictions were reviewed. |
| gdown: [correct no_cookies example](https://github.com/wkentaro/gdown/commit/2b134e38ecda4da583ba3427d4dad96711a3eb13) | Not admitted as positive | README used `no_cookies=True`, but the inspected pre-correction `download_folder` already accepts `use_cookies`, not `no_cookies`. A bounded history search of that module did not establish an accurate A followed by a breaking B. A corrected typo alone is insufficient. |
| gdown: [correct cached_download example](https://github.com/wkentaro/gdown/commit/39a64de608583543b1425e44d9c88c3641bbb63c) | Not admitted as positive | A README example correction from `output` to `path` was found, but an accurate earlier claim and introducing code change were not established. Do not count every correction as drift. |
| Black: [include .py in docs](https://github.com/psf/black/commit/52ab313a6c506620eb96595a03b4a02554c138f2) | Not admitted as positive | The inspected pre-correction constant already includes `.py`; earlier `3d96b7f1` also uses `\.pyi?$`. No A in which the supplied omission was accurate was established. This does not prove every historical inclusion claim was reviewed. |
| python-dotenv: [UTF-8 default change](https://github.com/theskumar/python-dotenv/commit/b158aa721cdf625c72f79f3583e5cc1f0cea2950) | Not admitted as positive | An actual default change exists, but the earlier README encoding paragraph had already been removed by [the README rewrite](https://github.com/theskumar/python-dotenv/commit/2e0ea4873ba39192db97fcafdb16ae03ffcaf951). The required stale claim is not retained at B. |
| python-dotenv: [clarify override default](https://github.com/theskumar/python-dotenv/commit/08937a1911c042ed3fc7cbeeb4d1d5a73d2674ed) | Not admitted as positive | The change explains existing behavior; the inspected function still defaults `override=False`. No contradictory code change is established. |
| python-tabulate: [latex_booktabs refactor](https://github.com/astanin/python-tabulate/commit/71f92b4fb51279c91287d500870298f3d16a2c77) | Not admitted as positive | A removed `booktabs` parameter was found, but no retained README availability claim was established. The inspected README is reStructuredText, outside the Markdown input boundary as well. |
| Mistune: [escape default change](https://github.com/lepture/mistune/commit/0f5313c52c4beaee623d05e62eb05d10c7cbf281) | Not admitted as positive | The explicit `escape` parameter is added over prior `**kwargs`. Relevant documentation at that revision is not a retained Markdown API claim; Markdown test fixtures are not API documentation. |

These rejected candidates are excluded from the recall denominator. Their
rejection does not classify them as true negatives in a benchmark. Only the
manifest's explicitly reviewed negative controls have that role.

## Reproduction boundary

Bare caches were placed outside the committed corpus. The existing three
repositories used `/private/tmp/driftlens-verification-cache`; additional search
repositories used `/private/tmp/driftlens-satya-history-cache`. A temporary copy
of the manifest substituted only those repository paths. Committed labels,
revisions and expectations were unchanged. The public clone commands in the
README reproduce without relying on these machine-local paths.
