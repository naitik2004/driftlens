"""Replay pinned public histories; read upstream Git objects without executing code."""
import argparse
import ast
import json
from pathlib import Path

from driftlens.analyzer import analyze
from driftlens.evaluate import evaluate
from driftlens.reporting import write_json
from driftlens.snapshots import git, resolve


def read(repo, revision, path):
    return git(repo, 'show', f'{revision}:{path}').decode('utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(case, repo):
    """Check provenance and labels before replay, without reading correction C."""
    a, b = case['before'], case['drift']
    for revision in (a, b):
        require(len(revision) == 40 and resolve(repo, revision) == revision,
                'Cases must pin full commit SHAs')
    require(a != b, 'A and B must differ')
    git(repo, 'merge-base', '--is-ancestor', a, b)
    evidence = case.get('evidence')
    if evidence:
        for revision, key in ((a, 'before_code'), (b, 'drift_code')):
            require(evidence[key] in read(repo, revision, evidence['code_path']),
                    f'{case["id"]}: missing {key}')
        require(evidence['quote'] in read(repo, a, evidence['doc_path']),
                f'{case["id"]}: claim not present at A')
    for label in case['expected']:
        source = read(repo, b, label['path'])
        start, quote = label['start'], label['quote']
        require(source[start:start + len(quote)] == quote and
                source.count('\n', 0, start) + 1 == label['line_start'],
                f'{case["id"]}: incorrect exact localization')
    if case.get('formatting_only'):
        paths = git(repo, 'diff', '--name-only', a, b).decode().splitlines()
        require(bool(paths) and all(p.endswith('.py') for p in paths),
                'Formatting control must change only Python files')
        for path in paths:
            require(ast.dump(ast.parse(read(repo, a, path))) ==
                    ast.dump(ast.parse(read(repo, b, path))),
                    'Formatting control changes the Python AST')
    if case.get('synchronized'):
        item = case['synchronized']
        for key in ('code_path', 'doc_path'):
            require(item['added_text'] not in read(repo, a, item[key]) and
                    item['added_text'] in read(repo, b, item[key]),
                    'Synchronized control must add code and docs together')


def replay(manifest_path, output):
    manifest = json.loads(manifest_path.read_text())
    for case in manifest['cases']:
        repo = (manifest_path.parent / case['repo']).resolve()
        verify(case, repo)
        # C, its patch, message and later source are never arguments to analysis.
        report = analyze(repo, case['before'], case['drift'],
                         repository_url=case['source_url'])
        write_json(report, output / f'{case["id"]}.json')
        if case.get('correction'):
            c, evidence = case['correction'], case['evidence']
            require(len(c) == 40 and resolve(repo, c) == c,
                    'Correction must pin a full commit SHA')
            require(c != case['drift'], 'Correction must be later than B')
            git(repo, 'merge-base', '--is-ancestor', case['drift'], c)
            corrected = read(repo, c, evidence['correction_path'])
            require(evidence['correction_quote'] in corrected and
                    evidence['quote'] not in corrected,
                    f'{case["id"]}: correction does not replace the stale claim')
    # Use the existing metric contract; it independently analyzes only A/B.
    result = evaluate(manifest, manifest_path.parent)
    write_json(result, output / 'evaluation.json')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path,
                        default=Path(__file__).with_name('manifest.json'))
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).with_name('outputs'))
    args = parser.parse_args()
    try:
        result = replay(args.manifest, args.output)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f'Historical replay: {exc}\n')
    print(f'{len(result["cases"])} cases; known-label recall: {result["known_case_recall"]}')


if __name__ == '__main__':
    main()
