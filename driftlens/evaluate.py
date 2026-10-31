"""Replay labeled A/B histories without exposing later C evidence to analysis.

Run: python -m driftlens.evaluate manifest.json --output evaluation.json
Unmatched predictions require manual review; they are not automatic false positives.
"""
import argparse
import json
from pathlib import Path
from .analyzer import analyze
from .reporting import write_json
from .snapshots import resolve, snapshot


def matches(finding, expected):
    actual = {'path': finding['claim']['path'], 'quote': finding['claim']['quote'],
              'symbol': finding['before']['symbol'], 'name': finding['before']['name'],
              'category': finding['category'], 'line_start': finding['claim']['line_start'],
              'start': finding['claim']['start']}
    return all(key in actual and actual[key] == value for key, value in expected.items())


def evaluate(manifest, directory):
    results = []
    repository_splits = {}
    for case in manifest['cases']:
        repo = (directory / case['repo']).resolve()
        split = case.get('split', 'evaluation')
        if repo in repository_splits and repository_splits[repo] != split:
            raise ValueError('Development and evaluation splits must use different repositories')
        repository_splits[repo] = split
    for case in manifest['cases']:
        repo = (directory / case['repo']).resolve()
        # No C snapshot, message or future history is supplied to the analyzer.
        report = analyze(repo, case['before'], case['drift'])
        unmatched = list(report['findings'])
        hits = 0
        for label in case['expected']:
            if not label or not {'path', 'symbol', 'category'} <= label.keys():
                raise ValueError('Labels require path, symbol and category')
            found = next((f for f in unmatched if matches(f, label)), None)
            if found:
                unmatched.remove(found)
                hits += 1
        correction_evidence = []
        if case.get('correction'):
            later = snapshot(repo, resolve(repo, case['correction']))
            for finding in report['findings']:
                claim = finding['claim']
                correction_evidence.append({'finding_id': finding['id'],
                    'old_quote_still_present': claim['quote'] in later.files.get(claim['path'], ''),
                    'note': 'Later text changes are review evidence, not ground truth.'})
        results.append({'id': case['id'], 'split': case.get('split', 'evaluation'),
                        'known_labels': len(case['expected']), 'known_hits': hits,
                        'predictions': len(report['findings']), 'unmatched_for_review': unmatched,
                        'correction_evidence': correction_evidence,
                        'runtime_seconds': report['metrics']['runtime_seconds'],
                        'warnings': report['warnings'],
                        'precision': hits / len(report['findings']) if case.get('fully_reviewed') and report['findings'] else None})
    labels, hits = sum(r['known_labels'] for r in results), sum(r['known_hits'] for r in results)
    return {'cases': results, 'known_case_recall': hits / labels if labels else None,
            'warnings_per_case': sum(len(r['warnings']) for r in results) / len(results) if results else 0,
            'model_resource_usage': None,
            'limitations': ['Recall is over supplied labels only.', 'Precision is reported only for explicitly fully reviewed cases.',
                            'This deterministic replay does not measure model quality or hardware resource usage.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.manifest.read_text()), args.manifest.parent)
        write_json(result, args.output)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f'DriftLens evaluation: {exc}\n')


if __name__ == '__main__':
    main()
