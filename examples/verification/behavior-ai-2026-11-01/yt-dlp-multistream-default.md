# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `50865ca803a130308c064c2de5c7140754382993`  
Head: `91ebc64068d2957400dbfaadff23e995392b3963`

No new drift established within the supported analysis scope.

## Behavioral candidates requiring review

These are retrieval hints, not established drift findings. They do not trigger annotations or fail-on-drift.

**README.md:885** ([source](https://github.com/yt-dlp/yt-dlp/blob/91ebc64068d2957400dbfaadff23e995392b3963/README.md#L885))

<blockquote>For example, &#96;-f bestvideo+best+bestaudio&#96; will download and merge all 3 given formats.</blockquote>

Opt-in defaults changed while this merge example remains. Stream-selection behavior and CLI forwarding require verification; the example alone does not assert a default.

Unverified local-model notes (qwen2.5-coder:3b; review_required):

The quote in the README.md file has changed from allowing multiple video and audio streams to not allowing them. This change requires verification to ensure that the example still accurately represents the current behavior of the &#96;--video-multistreams&#96; and &#96;--audio-multistreams&#96; flags.

Verify the updated behavior of the &#96;--video-multistreams&#96; and &#96;--audio-multistreams&#96; flags by running the command &#96;youtube-dl -f bestvideo+best+bestaudio&#96; and checking if the output is as expected. Additionally, ensure that the &#96;--video-multistreams&#96; and &#96;--audio-multistreams&#96; flags are correctly parsed and handled in the &#96;youtube_dlc/options.py&#96; file.

Citation validation checks source text only; it does not establish the model’s interpretation.

youtube_dlc/options.py:439: --video-multistreams declared default True → False; resolved parser state: False.

youtube_dlc/options.py:447: --audio-multistreams declared default True → False; resolved parser state: False.

[base youtube_dlc/options.py:439](https://github.com/yt-dlp/yt-dlp/blob/50865ca803a130308c064c2de5c7140754382993/youtube_dlc/options.py#L439-L442)

<details><summary>Source evidence</summary>

<pre>    video_format.add_option(
        &#x27;--video-multistreams&#x27;,
        action=&#x27;store_true&#x27;, dest=&#x27;allow_multiple_video_streams&#x27;, default=True,
        help=&#x27;Allow multiple video streams to be merged into a single file (default)&#x27;)</pre>

</details>

[head youtube_dlc/options.py:439](https://github.com/yt-dlp/yt-dlp/blob/91ebc64068d2957400dbfaadff23e995392b3963/youtube_dlc/options.py#L439-L442)

<details><summary>Source evidence</summary>

<pre>    video_format.add_option(
        &#x27;--video-multistreams&#x27;,
        action=&#x27;store_true&#x27;, dest=&#x27;allow_multiple_video_streams&#x27;, default=False,
        help=&#x27;Allow multiple video streams to be merged into a single file&#x27;)</pre>

</details>

[base youtube_dlc/options.py:447](https://github.com/yt-dlp/yt-dlp/blob/50865ca803a130308c064c2de5c7140754382993/youtube_dlc/options.py#L447-L450)

<details><summary>Source evidence</summary>

<pre>    video_format.add_option(
        &#x27;--audio-multistreams&#x27;,
        action=&#x27;store_true&#x27;, dest=&#x27;allow_multiple_audio_streams&#x27;, default=True,
        help=&#x27;Allow multiple audio streams to be merged into a single file (default)&#x27;)</pre>

</details>

[head youtube_dlc/options.py:447](https://github.com/yt-dlp/yt-dlp/blob/91ebc64068d2957400dbfaadff23e995392b3963/youtube_dlc/options.py#L447-L450)

<details><summary>Source evidence</summary>

<pre>    video_format.add_option(
        &#x27;--audio-multistreams&#x27;,
        action=&#x27;store_true&#x27;, dest=&#x27;allow_multiple_audio_streams&#x27;, default=False,
        help=&#x27;Allow multiple audio streams to be merged into a single file&#x27;)</pre>

</details>

Abstentions: 0. Runtime: 51.051s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
- Only the first three behavioral candidates receive optional unverified model notes; citations do not prove the interpretation.
