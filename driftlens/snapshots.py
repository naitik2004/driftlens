"""Immutable Git snapshots, rename mappings and responsible diff hunks."""
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess


class SnapshotError(ValueError):
    pass


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=60,
    )
    if result.returncode:
        raise SnapshotError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


@dataclass
class Snapshot:
    commit: str
    files: dict[str, str]


@dataclass
class Comparison:
    base: Snapshot
    head: Snapshot
    renames: dict[str, str]
    hunks: list[dict]


def resolve(repo, revision):
    # --end-of-options prevents revisions from becoming Git options.
    return git(repo, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}").decode().strip()


def snapshot(repo, commit):
    files = {}
    for entry in git(repo, "ls-tree", "-rz", commit).split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        path = raw_path.decode("utf-8", "surrogateescape")
        # Symlinks and submodules are data, never followed.
        if mode not in (b"100644", b"100755") or not path.lower().endswith((".py", ".md", ".markdown")):
            continue
        blob = git(repo, "cat-file", "blob", oid.decode())
        try:
            files[path] = blob.decode("utf-8")
        except UnicodeDecodeError:
            raise SnapshotError(f"Cannot analyze non-UTF-8 file: {path}")
    return Snapshot(commit, files)


def collect(repo: Path, base: str, head: str):
    target, tip = resolve(repo, base), resolve(repo, head)
    ancestor = git(repo, "merge-base", target, tip).decode().strip()
    old, new = snapshot(repo, ancestor), snapshot(repo, tip)
    entries = git(repo, "diff", "--name-status", "-z", "-M", ancestor, tip).split(b"\0")
    renames, changed = {}, []
    i = 0
    while i < len(entries) and entries[i]:
        status = entries[i].decode()
        before = entries[i + 1].decode("utf-8", "surrogateescape")
        i += 2
        after = before
        if status.startswith(("R", "C")):
            after = entries[i].decode("utf-8", "surrogateescape")
            i += 1
            renames[after] = before
        changed.append((before, after))
    hunks = []
    for before, after in changed:
        if not (before.endswith(".py") or after.endswith(".py")):
            continue
        diff = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--unified=3", ancestor, tip, "--", before, after).decode("utf-8", "replace")
        matches = list(re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*$", diff, re.M))
        for index, match in enumerate(matches):
            hunks.append({
                "old_path": before, "new_path": after,
                "old_start": int(match[1]), "old_count": int(match[2] or 1),
                "new_start": int(match[3]), "new_count": int(match[4] or 1),
                "text": diff[match.start():matches[index + 1].start() if index + 1 < len(matches) else len(diff)],
            })
    return Comparison(old, new, renames, hunks)
