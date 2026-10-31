# DriftLens

**0 finding(s)** across 0 code change(s). Advisory analysis.

Base: `373c16d983bcfafcd1ccd9f0fd826aa21d5c9365`  
Head: `dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58`

No new drift established within the supported analysis scope.

## Behavioral candidates requiring review

These are retrieval hints, not established drift findings. They do not trigger annotations or fail-on-drift.

**README.md:21** ([source](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/README.md#L21))

<blockquote>- Downloads folders recursively (up to 50 files per folder)</blockquote>

A referenced numeric client guard disappeared while this limit claim remains. The replacement implementation and external service may impose another bound; no unlimited-service claim is established.

[base gdown/download_folder.py:22](https://github.com/wkentaro/gdown/blob/373c16d983bcfafcd1ccd9f0fd826aa21d5c9365/gdown/download_folder.py#L22)

<details><summary>Source evidence</summary>

<pre>MAX_NUMBER_FILES = 50</pre>

</details>

[base gdown/download_folder.py:178](https://github.com/wkentaro/gdown/blob/373c16d983bcfafcd1ccd9f0fd826aa21d5c9365/gdown/download_folder.py#L178)

<details><summary>Source evidence</summary>

<pre>    has_at_least_max_files = len(gdrive_file.children) == MAX_NUMBER_FILES</pre>

</details>

[head gdown/download_folder.py:144](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/gdown/download_folder.py#L144-L149)

<details><summary>Source evidence</summary>

<pre>    gdrive_file = _download_and_parse_google_drive_link(
        sess=sess,
        folder_id=folder_id,
        quiet=quiet,
        verify=verify,
    )</pre>

</details>

[head gdown/download_folder.py:276](https://github.com/wkentaro/gdown/blob/dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58/gdown/download_folder.py#L276-L322)

<details><summary>Source evidence</summary>

<pre>def _download_and_parse_google_drive_link(
    sess: requests.Session,
    folder_id: str,
    quiet: bool = False,
    verify: bool | str = True,
) -&gt; _GoogleDriveFile:
    folder_name, children = _parse_embedded_folder_view(
        sess=sess, folder_id=folder_id, verify=verify
    )

    gdrive_file = _GoogleDriveFile(
        id=folder_id,
        name=folder_name,
        type=_GoogleDriveFile.TYPE_FOLDER,
    )

    for child_id, child_name, child_type in children:
        if child_type != _GoogleDriveFile.TYPE_FOLDER:
            if not quiet:
                print(
                    &quot;Processing file&quot;,
                    child_id,
                    child_name,
                )
            gdrive_file.children.append(
                _GoogleDriveFile(
                    id=child_id,
                    name=child_name,
                    type=child_type,
                )
            )
            continue

        if not quiet:
            print(
                &quot;Retrieving folder&quot;,
                child_id,
                child_name,
            )
        child = _download_and_parse_google_drive_link(
            sess=sess,
            folder_id=child_id,
            quiet=quiet,
            verify=verify,
        )
        gdrive_file.children.append(child)
    return gdrive_file</pre>

</details>

Abstentions: 0. Runtime: 0.745s.


## Scope and limitations

- Python top-level functions, direct module-level argparse, and direct optparse option groups in public function bodies only.
- Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.
- Static declared defaults do not prove effective runtime values or physical units.
- General computed return values and arbitrary called methods are not resolved.
- Filename checks bound one local literal dot-join; runtime type/dispatch overrides are not evaluated.
- Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code.
