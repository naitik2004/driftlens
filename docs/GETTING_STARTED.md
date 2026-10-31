# Install and run DriftLens

You need Git and Python 3.10 or newer. Ollama is optional; ordinary analysis
does not need a model server or API key. Distribution is through GitHub Releases;
PyPI is deferred. The unrelated PyPI package named `driftlens` is not this tool.

## Versioned GitHub installation

Download the wheel and `SHA256SUMS` from the
[v0.1.0 release](https://github.com/naitik2004/driftlens/releases/tag/v0.1.0).
Check its checksum against `SHA256SUMS`, then install that local wheel in a fresh
environment. You can also install the versioned wheel directly:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-deps https://github.com/naitik2004/driftlens/releases/download/v0.1.0/driftlens_docs-0.1.0-py3-none-any.whl
.venv/bin/driftlens --help
```

On Windows PowerShell, use `py -3 -m venv .venv` and replace the executable paths
with `.\.venv\Scripts\python.exe` and `.\.venv\Scripts\driftlens.exe`.
The release page identifies the exact source commit and known limitations.
The source-install alternative follows.

## macOS and Linux

```sh
git clone https://github.com/naitik2004/driftlens.git
cd driftlens
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m driftlens --help
```

## Windows PowerShell

Use `py -3` to select an installed Python 3.10+ interpreter. The commands below
invoke the venv directly, so PowerShell script activation is unnecessary.

```powershell
git clone https://github.com/naitik2004/driftlens.git
cd driftlens
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m driftlens --help
```

## Analyze your own repository

Save/commit your code change in a Python project with Markdown documentation.
Choose two existing commit IDs or branch names: BEFORE from before the change,
AFTER containing it. Inspect them with `git -C /path/to/project log --oneline`.
DriftLens compares their merge base to AFTER; uncommitted changes are ignored.

On macOS/Linux, from the DriftLens checkout:

```sh
.venv/bin/python -m driftlens --repo /path/to/project --base BEFORE --head AFTER --json report.json --summary report.md
```

On PowerShell, replace the path and revisions with your actual values:

```powershell
.\.venv\Scripts\python.exe -m driftlens --repo "C:\path\to\project" --base BEFORE --head AFTER --json report.json --summary report.md
```

Open `report.md` to review the exact claim, old/new facts, responsible diff and
limits. `report.json` contains machine-readable positions and evidence. Add
`--repository-url https://github.com/OWNER/REPO` for immutable source links.
Output files are UTF-8. Project Python/Markdown Git blobs must also be UTF-8.

Exit 0 means advisory analysis completed, even with findings. Add
`--fail-on-drift` for exit 1 on findings; exit 2 means an input or analysis error.
Zero findings does not verify every sentence. Check warnings and abstentions;
implicit behavior, many wrappers and indirect prose are outside supported scope.

For a controlled demonstration, run `.venv/bin/python -m examples.demo` on
macOS/Linux or `.\.venv\Scripts\python.exe -m examples.demo` on Windows. This
requires the source checkout and writes synthetic reports in `examples/outputs/`.
It does not measure effectiveness on your project.

## Troubleshooting

- **No Git executable:** install Git, reopen the terminal, check `git --version`.
- **Unknown revision/shallow history:** confirm the refs and fetch enough history
  for a merge base. A dirty editor buffer is not a Git revision.
- **No finding:** check the supported checks in README; a behavior may be outside
  scope, or the documentation may already have changed in the same revision.
- **Snapshot limit exceeded:** review the reported error and the CLI's
  `--max-files`, `--max-bytes`, `--max-file-bytes`, `--snapshot-timeout` options.
- **Local model unavailable:** leave off `--model` for deterministic analysis;
  model setup is separate in [LOCAL_AI.md](LOCAL_AI.md).

## Independent first-use check

Ask a person who has not worked on DriftLens to follow these instructions on
their own project. Record their OS/Python/Git versions, installed source commit,
commands, chosen revisions, whether they generated both reports, whether they
understood one finding, and where they needed assistance. Review the reported
evidence with them; do not upload private source without their consent.

Automated macOS/Windows checks are useful portability evidence. They do not
establish that an independent person successfully used the product.
