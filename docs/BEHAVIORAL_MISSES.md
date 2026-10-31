# Why the two behavioral histories remain missed

This follow-up re-read the pinned A/B source without running either upstream
project. It adds no detector heuristic and leaves the original labels unchanged.
The hosted main replay also confirms both misses. A later correction is review
evidence, not a rule supplied to detection.

## yt-dlp: format selection spans parser and runtime behavior

At B `91ebc64068d2957400dbfaadff23e995392b3963`:

- `youtube_dlc/options.py:441–453` declares paired positive/negative flags sharing
  destinations for video and audio multistream behavior.
- `youtube_dlc/__init__.py:369–370` forwards parsed destination values into a
  parameter dictionary.
- `youtube_dlc/YoutubeDL.py:1216–1217` reads that dictionary inside a class method
  containing a nested format-selector parser and merge behavior.
- The retained README example uses `-f bestvideo+best+bestaudio`; it does not name
  the multistream flags or claim a literal default. Ordinary explicit examples
  are intentionally excluded from default-claim detection.

Recognizing the option's False default alone does not prove what that example
downloads. The missing proof requires resolving shared argparse/optparse-style
destination state, forwarding, the format expression and stream selection.
Treating every example near a changed Boolean as wrong would report valid
explicit overrides and unrelated format expressions.

An acceptable extension needs independently named positive fixtures plus
controls for explicit enabling flags, retained alias/negative-flag behavior,
single-stream expressions, wrappers that override defaults, and same-change
documentation corrections. It must distinguish an example's behavior from a
simple declared-default claim. No positive regression is claimed until such a
rule actually establishes both old support and new contradiction.

## gdown: removal of a client guard is not an effective new bound

At A `373c16d983bcfafcd1ccd9f0fd826aa21d5c9365`, a private recursive helper compares
the number of children to a module constant. It raises a dedicated limit error
unless a forwarded Boolean bypass is enabled. The public operation calls that
helper. At B `dda064d76f8f04b7ebb0fc4c7b2f9e9b063a2e58`, the helper uses another
parser and remote listing endpoint; the guard/constant and bypass parameter are
gone. README still says “up to 50 files per folder.”

This is good manual evidence for a removed client restriction. The current
static engine cannot establish the effective new limit through an arbitrary
remote-response parser and recursion, or link the unqualified feature bullet to
that complete operation. Looking only for a deleted constant would also flag
limits moved into helpers, inlined or renamed. Nothing here establishes an
unlimited remote-service guarantee.

The detailed [gdown acceptance handoff](../examples/historical/GDOWN_HANDOFF.md)
requires those negative cases and abstention when the new bound is unresolved.
That acceptance gate still fails and is not marked complete.

## Current decision

Keep both as visible development misses. Do not hardcode repository names,
numbers, endpoint strings or expected quotes into runtime rules. First collect
new independently selected histories, then evaluate a separately scoped
behavioral-analysis design with positive and adversarial controls. Existing
1/3 recall remains the reported result.
