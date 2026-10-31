import argparse
import json
import os
from pathlib import Path
import sys
from .analyzer import analyze
from .model import Ollama
from .reporting import annotations, summary, write_json
from .snapshots import SnapshotError, SnapshotLimits


def event_revisions(event_path):
    event = json.loads(Path(event_path).read_text())
    pr = event.get('pull_request')
    if not pr:
        raise ValueError('GitHub event does not contain pull_request revisions')
    return pr['base']['sha'], pr['head']['sha']


def main(argv=None):
    parser = argparse.ArgumentParser(description='Find new Python/Markdown documentation drift using immutable Git revisions.')
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--base', help='Target/base revision; comparison starts at the merge base')
    parser.add_argument('--head', help='Actual PR head revision (default HEAD outside PR events)')
    parser.add_argument('--github-event', type=Path)
    parser.add_argument('--repository-url', help='HTTPS repository URL for commit-pinned links')
    parser.add_argument('--json', dest='json_path', type=Path)
    parser.add_argument('--summary', type=Path)
    parser.add_argument('--github-annotations', action='store_true')
    parser.add_argument('--fail-on-drift', action='store_true', help='Exit 1 on findings; advisory by default')
    parser.add_argument('--model', nargs='?', const='qwen2.5-coder:3b', help='Enable optional local Ollama interpretation')
    parser.add_argument('--ollama-url', default='http://127.0.0.1:11434')
    parser.add_argument('--cache', type=Path)
    limits = SnapshotLimits()
    parser.add_argument('--max-files', type=int, default=limits.max_files,
                        help='Maximum eligible files per snapshot (default 20000)')
    parser.add_argument('--max-bytes', type=int, default=limits.max_bytes,
                        help='Maximum eligible bytes per snapshot (default 100 MiB)')
    parser.add_argument('--max-file-bytes', type=int, default=limits.max_file_bytes,
                        help='Maximum bytes per eligible file (default 10 MiB)')
    parser.add_argument('--snapshot-timeout', type=float, default=limits.timeout_seconds,
                        help='Collection budget per snapshot in seconds (default 180)')
    args = parser.parse_args(argv)
    try:
        event_path = args.github_event or os.environ.get('GITHUB_EVENT_PATH')
        base, head = args.base, args.head
        use_environment = not base and not head and os.environ.get('GITHUB_EVENT_NAME') == 'pull_request'
        if event_path and (not base or not head) and (args.github_event or use_environment):
            event_base, event_head = event_revisions(event_path)
            base, head = base or event_base, head or event_head
        if not base:
            parser.error('--base is required outside a GitHub pull_request event')
        model = Ollama(args.model, args.ollama_url, args.cache) if args.model else None
        snapshot_limits = SnapshotLimits(args.max_files, args.max_bytes, args.max_file_bytes,
                                         args.snapshot_timeout)
        report = analyze(args.repo, base, head or 'HEAD', args.repository_url, model, snapshot_limits)
        if args.json_path:
            write_json(report, args.json_path)
        rendered = summary(report)
        if args.summary:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(rendered)
        if args.github_annotations:
            print('\n'.join(annotations(report)))
        elif not args.summary:
            print(rendered, end='')
        print(f"DriftLens: {len(report['findings'])} finding(s), {len(report['abstentions'])} abstention(s), {len(report['warnings'])} warning(s).", file=sys.stderr)
        return 1 if args.fail_on_drift and report['findings'] else 0
    except (SnapshotError, ValueError, OSError, KeyError) as exc:
        print(f'DriftLens: {exc}', file=sys.stderr)
        return 2
