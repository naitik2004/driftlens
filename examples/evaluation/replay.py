"""Reproduce the external-repository study without executing upstream code.

Exit success means the provenance checks and replay completed, not that every
positive was detected. Always read known_case_recall and per-case results.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

from examples.historical.replay import read, replay, require
from driftlens.reporting import write_json
from driftlens.snapshots import git, resolve


def reviewed_patch(repo, before, head):
    # Fix presentation settings so Git versions/configuration and abbreviated
    # object IDs do not change a reviewed patch's provenance fingerprint.
    return git(repo, 'diff', '--no-ext-diff', '--no-textconv', '--no-color',
               '--full-index', '--no-renames', '--diff-algorithm=myers',
               '--no-indent-heuristic', '--unified=3', '--src-prefix=a/',
               '--dst-prefix=b/', before, head)


def verify_controls(manifest_path, cache):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    require(10 <= len(manifest['cases']) <= 20, 'Study needs 10–20 pinned cases')
    require(len({c['source_url'] for c in manifest['cases']}) >= 2, 'Need two external repositories')
    excluded = {'https://github.com/yt-dlp/yt-dlp', 'https://github.com/psf/black',
                'https://github.com/un33k/python-slugify', 'https://github.com/wkentaro/gdown'}
    for case in manifest['cases']:
        require(case['source_url'] not in excluded, 'Development repository in evaluation')
        repo = cache / Path(case['repo']).name
        paths = git(repo, 'diff', '--name-only', case['before'], case['drift']).decode().splitlines()
        require(paths == case['changed_paths'], 'Changed paths differ from reviewed selection')
        if case.get('control_type') == 'markdown_only':
            require(paths and all(p.endswith('.md') for p in paths), 'Not a Markdown-only control')
        if case.get('control_type') == 'comment_only':
            for path in paths:
                require(path.endswith('.py'), 'Comment control changes non-Python source')
                require(ast.dump(ast.parse(read(repo, case['before'], path))) ==
                        ast.dump(ast.parse(read(repo, case['drift'], path))), 'Executable AST changed')
        patch = reviewed_patch(repo, case['before'], case['drift'])
        require(hashlib.sha256(patch).hexdigest() == case['reviewed_patch_sha256'], 'Reviewed patch changed')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).with_name('manifest.json'))
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = verify_controls(args.manifest, args.cache_dir.resolve())
    result = replay(args.manifest, args.output, args.cache_dir)
    root = Path(__file__).resolve().parents[2]
    runtime = root / 'driftlens'
    result['study'] = {'manifest_sha256': hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
                       'frozen_detector_commit': manifest['frozen_detector_commit'],
                       'executed_detector_commit': resolve(root, 'HEAD'),
                       'working_tree_modified': bool(git(root, 'status', '--porcelain').strip()),
                       'runtime_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(runtime.glob('*.py'))},
                       'selection': manifest['selection'],
                       'positive_cases': sum(bool(c['expected']) for c in manifest['cases']),
                       'negative_controls': sum(not c['expected'] for c in manifest['cases']),
                       'independent_human_review': False,
                       'precision': None}
    write_json(result, args.output / 'evaluation.json')
    print(json.dumps({'cases': len(result['cases']), 'known_case_recall': result['known_case_recall'],
                      'predictions': sum(c['predictions'] for c in result['cases']),
                      'note': 'Replay completion is not an accuracy pass.'}))


if __name__ == '__main__':
    main()
