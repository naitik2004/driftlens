# PR #8 integration review: hold for correction

Reviewed PR head `bf48230110f68a47902f673202e07c15cb57e288` in an isolated
worktree. Main was not changed. The PR's green tests do not cover the two
false-positive cases below. Both were reproduced through actual temporary Git
snapshots and PR #8's analyzer, alongside Python's own optparse behavior.

## Blocker: unspecified defaults are invented

In Python optparse, an unspecified destination default is None. The PR currently
marks implicit store_true as False and store_false as True, both resolved.
This differs from actual optparse behavior and invents source evidence.

Minimal runtime check:

```python
import optparse
for action in ('store_true', 'store_false'):
    parser = optparse.OptionParser()
    parser.add_option('--quiet', action=action, dest='quiet')
    print(action, parser.parse_args([])[0].quiet)
# Both print None.
```

End-to-end false positive reproduced:

- A: public parseOpts creates OptionParser and adds --quiet with
  action='store_false', dest='quiet', without an explicit default.
- B: only the action changes to store_true.
- Both actual no-argument defaults are None.
- Unchanged Markdown: `--quiet` defaults to True.
- PR #8 reports one flag_default_changed finding, claiming True → False.
  The documentation was already inaccurate at A; the PR did not introduce that drift.

Correct implicit-value semantics or conservative abstention are required. Do not
fix this by changing the expected finding to one or coercing the runtime value.

## Blocker: defaults belong to destinations, not individual options

Reproduced with two direct options on one parser:

```python
parser.add_option('--yes', action='store_true', dest='mode', default=True)
parser.add_option('--no', action='store_false', dest='mode', default=False)
```

The effective default of mode is False. At B, change only --yes's explicit
True default to False; the effective default remains False. With unchanged
Markdown `--yes` defaults to True., the analyzer emits one false default-change
finding. The claim was already wrong before the change.

Resolve destination defaults in declaration order, including conservative
handling of unknown overrides, or abstain when shared destination semantics are
not established. Add both cases as negative Git-snapshot regressions before
integration. The existing test expecting implicit store_false=True needs correction.

Reference: [Python optparse default values](https://docs.python.org/3/library/optparse.html#default-values).

## Handoff and status

Satya authored this PR; its own description requests Ravichandra's detector
review. The extractor is Ravichandra's assigned ownership area. Corrections and
regressions belong in that detector branch, then Naitik reruns integration.
The integration agent did not merge a known false-positive regression into main.
The PR also still reports 0/2 genuine historical labels detected, so it must not
be presented as closing the real-history detection gap.
