# Bounded cache filename layout detection

This detector continuation implements one part of Ravichandra's workstream at
the user's request. It adds no runtime dependency and never imports analyzed
code. It does not implement general method execution or whole-program typing.

## The rule

1. A public top-level function returns a pathlib Path join with a simple f-string.
   Its old dynamic filename fields are a declared built-in int parameter and an
   integer-valued local enum.Flag parameter's value. Default formatting is required.
2. A current Markdown inline path contains that exact old filename template.
   Placeholders use the integer argument name and enum type name, normalized to
   lower-case hyphenated names. The template must have an unambiguous owner, or
   the documentation must identify the function explicitly.
3. At the new revision, the same function returns the same base/prefix/suffix,
   but its typed local receiver calls one declared method. That method's sole
   return is `'.'.join(parts)`, with one unmodified literal list of N items.
4. N exceeds the old number of numeric fields. Each successful join contributes
   at least N-1 literal dots, so unknown field values cannot reduce the declared
   string to the old two-field numeric layout. Values are not executed or guessed.
5. The unchanged old/current documentation claim, responsible diff, original
   declaration, enum evidence and helper/list/return locations accompany the finding.

This compares a **declared typed string-layout contract**. It does not prove all
runtime dispatch, subclass overrides, filesystem normalization or arbitrary
monkeypatching. Known rebindings, custom access hooks, unknown decorators,
project-shadowed trusted modules and mutated/ambiguous join inputs abstain.
Recognized unparameterized dataclass decorators are limited to the imported
standard dataclasses decorator and legacy attr.dataclass; arbitrary decorators
are not interpreted. General computed return values remain unsupported.

Platform labels do not alter the common basename, and inline template
placeholders such as `<version>` are not historical-version assertions. Actual
temporal/conditional qualifiers remain exclusions. Runtime examples remain excluded.

## Genuine Black history

The original unmodified manifest label identifies:

- A: `a9d8af466a65b7d88ea35e0ff4c460175098260e`
- B: `36d3c516d3c09fc5f05c420900dd6b854e3c8bbd`
- Later C: `137766332565267cad23aea28bcfef4569439edd`

A declares `cache.{line_length}.{mode.value}.pickle`. B declares
`cache.{mode.get_cache_key()}.pickle`; the local helper joins five parts. The
unchanged README still describes two numeric fields. The exact Linux label at
README.md:886 matches, along with the Windows and macOS sentences at 884/885.
There are **three sentence findings, one underlying code-change group**.

Only A/B enter detection. C is read afterward: its moved documentation contains
three `cache.<mode-key>.pickle` paths. This corroborates the two extra platform
locations too, but does not supply the detection rule. Repository names, commit
IDs, concrete field values and exact case quotes are not hardcoded in the detector.
The synthetic tests use different function, enum, prefix and suffix names.

The six-case retrospective corpus now matches **1/3 original positive labels**;
all three negative controls stay quiet. Labels/SHAs were not changed. Two other
positive histories remain missed. The two extra Black sentences are preserved
for manual review rather than counted automatically as false positives or used
to inflate known-label recall. Positive labels are not exhaustive; no general
precision, held-out accuracy or 100% effectiveness claim is made.

## Actual commands

Clone the public histories as described in examples/historical/README.md. On the
prepared demonstration laptop the verified Black bare cache is at
`/tmp/driftlens-verification-cache/black.git`; substitute your own cache elsewhere.

```sh
python3 -m driftlens --repo /tmp/driftlens-verification-cache/black.git \
  --base a9d8af466a65b7d88ea35e0ff4c460175098260e \
  --head 36d3c516d3c09fc5f05c420900dd6b854e3c8bbd \
  --repository-url https://github.com/psf/black \
  --json /tmp/driftlens-black-live.json --summary /tmp/driftlens-black-live.md
python3 -m unittest tests.test_cache_patterns -v
```

The three source links point to actual immutable upstream commits. Cached fixture
commit IDs used by the separate synthetic demos are not public upstream history.

## Negative tests

Tests retain quiet outcomes for docs fixed with code, unchanged/renamed layouts,
equal component counts, mutated or dynamically sized lists, untyped numeric
values, unknown decorators/helpers/separators, rebound classes/methods/imports,
project module shadowing, custom attribute hooks, temporal/conditional claims,
ambiguous owners and changed base paths. Legacy attr.dataclass has a positive
syntax-only test; analyzed projects do not need to be installed.

All 105 tests passed locally, including 21 rule-specific test methods. Ordinary
four-case demos and the actual eight-case Qwen/control suite also passed. Full
historical replay results are in examples/historical/outputs/. Latest PR/main CI
and clean-installed execution are checked before integration sign-off.
