"""Immutable Git snapshots, rename mappings and responsible diff hunks."""
from dataclasses import dataclass
from pathlib import Path
import math
import re
import subprocess
import time


class SnapshotError(ValueError):
    pass


@dataclass(frozen=True)
class SnapshotLimits:
    max_files: int = 20_000
    max_bytes: int = 100 * 1024 * 1024
    max_file_bytes: int = 10 * 1024 * 1024
    timeout_seconds: float = 180

    def __post_init__(self):
        if (any(type(value) is not int or value <= 0 for value in
                (self.max_files, self.max_bytes, self.max_file_bytes))
                or type(self.timeout_seconds) not in (int, float)
                or not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0):
            raise SnapshotError('Snapshot limits must be positive finite numbers with integer file/byte limits')


def git(repo, *args):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        raise SnapshotError('Git operation timed out after 60 seconds') from exc
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


def snapshot(repo, commit, limits=None):
    limits = limits or SnapshotLimits()
    started = time.monotonic()
    files = {}
    blobs = []
    total_bytes = 0
    for entry in git(repo, "ls-tree", "-rzl", commit).split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, oid, raw_size = metadata.split()
        path = raw_path.decode("utf-8", "surrogateescape")
        # Symlinks and submodules are data, never followed.
        if mode not in (b"100644", b"100755") or not path.lower().endswith((".py", ".md", ".markdown")):
            continue
        size = int(raw_size)
        total_bytes += size
        if size > limits.max_file_bytes:
            raise SnapshotError(f'Snapshot file byte limit exceeded: {path}')
        blobs.append((path, oid))
        if len(blobs) > limits.max_files or total_bytes > limits.max_bytes:
            raise SnapshotError('Snapshot file count or total byte limit exceeded')
    # Preflight object sizes before loading any eligible content. Fail rather
    # than silently issuing an incomplete report after truncating the snapshot.
    for path, oid in blobs:
        if time.monotonic() - started > limits.timeout_seconds:
            raise SnapshotError('Snapshot collection timed out')
        blob = git(repo, "cat-file", "blob", oid.decode())
        try:
            files[path] = blob.decode("utf-8")
        except UnicodeDecodeError:
            raise SnapshotError(f"Cannot analyze non-UTF-8 file: {path}")
    if time.monotonic() - started > limits.timeout_seconds:
        raise SnapshotError('Snapshot collection timed out')
    return Snapshot(commit, files)


def collect(repo: Path, base: str, head: str, limits=None):
    target, tip = resolve(repo, base), resolve(repo, head)
    ancestor = git(repo, "merge-base", target, tip).decode().strip()
    old, new = snapshot(repo, ancestor, limits), snapshot(repo, tip, limits)
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
