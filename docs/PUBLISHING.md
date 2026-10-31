# Publishing DriftLens

Proposed distribution name: **driftlens-docs**. The existing PyPI project named
`driftlens` is unrelated; installing it does not install this tool. The Python
module and executable for this project remain `driftlens`. Install distributions
with overlapping module names in separate virtual environments.

## One-time account setup

Confirm the distribution name before the first upload. Name availability checks
are not reservations. On both PyPI and TestPyPI, verify your email and enable 2FA.
Add a pending GitHub publisher from the account Publishing page:

- PyPI: https://pypi.org/manage/account/publishing/
- TestPyPI: https://test.pypi.org/manage/account/publishing/

| Field | Value |
|---|---|
| Project name | `driftlens-docs` |
| Owner | `naitik2004` |
| Repository | `driftlens` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` on PyPI; `testpypi` on TestPyPI |

Use matching GitHub environments. No API token belongs in repository files or
chat. Trusted Publishing obtains a short-lived token during the release job.

On 1 November 2026, the repository's `pypi` and `testpypi` GitHub environments
were created and restricted to the `main` branch. This completes the GitHub-side
environment step, not the PyPI/TestPyPI publisher registration or publication.
The readiness branch's hosted validation run passed with its upload job skipped;
see [the recorded evidence](../examples/verification/public-readiness-2026-11-01.json).

## Validate and publish

Merge the reviewed release configuration into main. In GitHub Actions, run
**Publish Python package** with `publish` unchecked for validation only. It runs tests,
demos, builds both distributions, checks metadata, tests wheel installation
outside the checkout and retains distributions without an upload.

After account setup, run it from **main**, selecting `testpypi` and checking
`publish`. Only this explicit upload mode uses Trusted Publishing. Other branches
can validate but cannot publish. An unchecked run is not publication evidence.

After successful TestPyPI upload, use a fresh virtual environment:

```sh
python3 -m venv /tmp/driftlens-testpypi
/tmp/driftlens-testpypi/bin/python -m pip install --no-deps --index-url https://test.pypi.org/simple/ driftlens-docs==0.1.0
/tmp/driftlens-testpypi/bin/driftlens --help
```

Only after verifying that install, run the workflow on main with `pypi` and
`publish` checked. Verify:

```sh
python3 -m venv /tmp/driftlens-pypi
/tmp/driftlens-pypi/bin/python -m pip install --no-deps driftlens-docs==0.1.0
/tmp/driftlens-pypi/bin/driftlens --help
```

A successful build or workflow configuration is not a published release. Verify
the public index and clean installation before announcing availability. PyPI
versions cannot be replaced: bump `project.version` for subsequent releases.
Runtime dependencies are currently empty. Git must be installed to analyze Git
histories; Ollama and a downloaded model are optional for model-assisted mode.

## Local release check

```sh
python3 -m pip install build twine
python3 -m build
python3 -m twine check --strict dist/*
```

References: [new project setup](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
and [existing publisher setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).
