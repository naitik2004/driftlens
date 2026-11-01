"""Controlled mutations on pinned public source; NOT historical bug discovery.

Copies eligible Git blobs into temporary fixtures, adds explicitly synthetic
Markdown claims and changes one literal default. Never executes upstream code.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from driftlens.analyzer import analyze
from driftlens.facts import Extractor
from driftlens.reporting import summary, write_json
from driftlens.snapshots import git, resolve, snapshot

DOC = 'docs/driftlens-controlled.md'
SCENARIOS = ('default-drift', 'docs-updated', 'harmless-refactor',
             'preexisting-inaccuracy', 'explicit-example', 'historical-qualifier')


def mutate_default(source, function, parameter, before, after):
    functions = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
                 and n.name == function]
    if len(functions) != 1:
        raise ValueError('Mutation requires one unambiguous top-level function')
    args = functions[0].args
    positional = args.posonlyargs + args.args
    pairs = list(zip(positional, [None] * (len(positional) - len(args.defaults)) + args.defaults))
    pairs += list(zip(args.kwonlyargs, args.kw_defaults))
    defaults = [node for arg, node in pairs if arg.arg == parameter and node is not None]
    if len(defaults) != 1:
        raise ValueError('Mutation requires one existing default')
    node = defaults[0]
    value = ast.literal_eval(node)
    if type(value) is not type(before) or value != before:
        raise ValueError('Pinned source default differs from the frozen case')
    # AST columns are UTF-8 byte offsets, not Python character offsets.
    lines = source.encode('utf-8').splitlines(keepends=True)
    start = sum(map(len, lines[:node.lineno - 1])) + node.col_offset
    end = sum(map(len, lines[:node.end_lineno - 1])) + node.end_col_offset
    raw = source.encode('utf-8')
    result = (raw[:start] + repr(after).encode('utf-8') + raw[end:]).decode('utf-8')
    ast.parse(result)
    return result


def claim(case, value):
    return f"`{case['symbol']}` `{case['parameter']}` defaults to {value!r}."


def documents(case, scenario):
    old = claim(case, case['before'])
    new = old
    if scenario == 'docs-updated':
        new = claim(case, case['after'])
    elif scenario == 'preexisting-inaccuracy':
        old = new = claim(case, case['after'])
    elif scenario == 'explicit-example':
        args = case['example_prefix']
        old = new = (f"For example, `{case['symbol']}({args}{case['parameter']}={case['before']!r})` "
                     'supplies an explicit argument.')
    elif scenario == 'historical-qualifier':
        old = new = 'Previously, ' + old
    return '# Synthetic controlled validation\n\n' + old + '\n', '# Synthetic controlled validation\n\n' + new + '\n'


def run_case(case, scenario, files):
    original = files[case['source_path']]
    changed = mutate_default(original, case['function'], case['parameter'], case['before'], case['after'])
    if scenario == 'harmless-refactor':
        changed = original + '\n# Controlled comment-only change.\n'
    before_doc, after_doc = documents(case, scenario)
    if DOC in files:
        raise ValueError('Synthetic documentation path already exists upstream')
    with tempfile.TemporaryDirectory(prefix='driftlens-controlled-') as temporary:
        root = Path(temporary)
        env = {**os.environ, 'GIT_AUTHOR_NAME': 'DriftLens Controlled Study',
               'GIT_COMMITTER_NAME': 'DriftLens Controlled Study',
               'GIT_AUTHOR_EMAIL': 'study@example.invalid', 'GIT_COMMITTER_EMAIL': 'study@example.invalid',
               'GIT_AUTHOR_DATE': '2026-10-31T00:00:00Z', 'GIT_COMMITTER_DATE': '2026-10-31T00:00:00Z'}

        def command(*args):
            return subprocess.check_output(['git', '-C', str(root), *args], env=env,
                                           stderr=subprocess.PIPE, timeout=60).decode().strip()

        command('init', '-q', '--initial-branch=main')
        command('config', 'core.autocrlf', 'false')
        empty_hooks = root / '.git' / 'controlled-empty-hooks'
        empty_hooks.mkdir()
        command('config', 'core.hooksPath', str(empty_hooks))
        for path, content in dict(files, **{DOC: before_doc}).items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode('utf-8'))
        command('add', '.')
        command('-c', 'commit.gpgsign=false', 'commit', '-qm', 'synthetic baseline')
        base = command('rev-parse', 'HEAD')
        (root / case['source_path']).write_bytes(changed.encode('utf-8'))
        (root / DOC).write_bytes(after_doc.encode('utf-8'))
        command('add', '.')
        command('-c', 'commit.gpgsign=false', 'commit', '-qm', 'controlled mutation')
        head = command('rev-parse', 'HEAD')
        # Fixture commit IDs do not exist on GitHub: deliberately omit repository_url.
        report = analyze(root, base, head)
    expected = 1 if scenario == 'default-drift' else 0
    exact = [f for f in report['findings'] if f['claim']['path'] == DOC
             and f['before']['symbol'] == case['symbol'] and f['before']['name'] == case['parameter']
             and f['category'] == 'parameter_default_changed'
             and f['claim']['quote'] == claim(case, case['before'])]
    passed = len(report['findings']) == expected and (expected == 0 or len(exact) == 1)
    report['controlled_study'] = {'synthetic': True, 'upstream_repository': case['source_url'],
                                  'upstream_commit': case['commit'], 'scenario': scenario,
                                  'generated_documentation': DOC,
                                  'note': 'Counterfactual local commits; not a real upstream bug or historical finding.'}
    return report, {'id': case['id'] + '-' + scenario, 'scenario': scenario,
                    'expected_findings': expected, 'actual_findings': len(report['findings']),
                    'passed': passed, 'warnings': report['warnings'],
                    'model_calls': report['metrics']['model_calls']}


def replay(manifest_path, cache_dir, output):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    output.mkdir(parents=True, exist_ok=True)
    rows, sources = [], []
    for case in manifest['repositories']:
        repo = cache_dir / (case['id'] + '.git')
        if len(case['commit']) != 40 or resolve(repo, case['commit']) != case['commit']:
            raise ValueError('Public snapshots must pin full commit SHAs')
        files = snapshot(repo, case['commit']).files
        extractor = Extractor(files)
        facts = [f for f in extractor.extract() if f.kind == 'parameter' and f.path == case['source_path']
                 and f.symbol == case['symbol'] and f.name == case['parameter']]
        if len(facts) != 1 or not facts[0].resolved or type(facts[0].value['default']) is not type(case['before']) or facts[0].value['default'] != case['before']:
            raise ValueError('Pinned declaration is not a resolved supported fact')
        sources.append({'id': case['id'], 'commit': case['commit'], 'eligible_files': len(files),
                        'source_sha256': hashlib.sha256(files[case['source_path']].encode('utf-8')).hexdigest(),
                        'fact': facts[0].json(),
                        'upstream_source': f"{case['source_url']}/blob/{case['commit']}/{case['source_path']}#L{facts[0].line}"})
        for scenario in SCENARIOS:
            report, row = run_case(case, scenario, files)
            write_json(report, output / (row['id'] + '.json'))
            (output / (row['id'] + '.md')).write_text(
                '**SYNTHETIC mutation of real upstream source; not a historical bug.**\n\n' + summary(report),
                encoding='utf-8', newline='\n')
            rows.append(row)
            print(json.dumps(row), flush=True)
    root = Path(__file__).resolve().parents[2]
    result = {'synthetic': True, 'scope': manifest['scope'],
              'executed_detector_commit': resolve(root, 'HEAD'),
              'runtime_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root / 'driftlens').glob('*.py'))},
              'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
              'repositories': sources, 'cases': rows, 'passed': sum(r['passed'] for r in rows),
              'total': len(rows), 'historical_recall': None,
              'limitations': ['Generated Markdown claims and counterfactual code changes are synthetic.',
                              'Cases intentionally exercise supported APIs, not representative repository accuracy.',
                              'No upstream Python, tests, setup scripts or installers were executed.',
                              'Original historical misses remain unchanged and are not replaced by these cases.']}
    write_json(result, output / 'evaluation.json')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).with_name('manifest.json'))
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.manifest, args.cache_dir, args.output)
    if result['passed'] != result['total']:
        raise SystemExit('Controlled cases failed; inspect saved reports. No labels were changed.')
    print(f"{result['passed']}/{result['total']} controlled cases passed; not historical recall.")


if __name__ == '__main__':
    main()
