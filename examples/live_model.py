"""Measure a real local-model contribution; never substitute a mocked verdict.

Run: python -m examples.live_model --output /tmp/driftlens-live-model.json
Requires a running Ollama server and the selected model already downloaded.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from driftlens.analyzer import analyze
from driftlens.model import Ollama, PROMPT_VERSION
from driftlens.reporting import write_json

DEFAULT_CASE = {
    'name': 'paraphrased-default',
    'before_docs': '`connect`: the default timeout equals 30.\n',
    'after_docs': '`connect`: the default timeout equals 30.\n',
    'after_default': 10, 'expected_findings': 1,
}


def verified(baseline, assisted, expected=1):
    """A model must add the expected supported finding, without warnings."""
    findings = assisted['findings']
    if expected == 0:
        return not baseline['findings'] and not findings and not baseline['warnings'] and not assisted['warnings']
    return (not baseline['findings'] and not baseline['warnings']
            and not assisted['warnings'] and assisted['metrics']['model_calls'] > 0
            and len(findings) == 1
            and findings[0]['before']['symbol'] == 'client.connect'
            and findings[0]['before']['name'] == 'timeout'
            and findings[0]['category'] == 'parameter_default_changed'
            and findings[0]['evidence_strength'] == 'model-extracted, deterministic fact comparison')


def run(model, case=None):
    case = DEFAULT_CASE if case is None else case
    if (not isinstance(case, dict)
            or not all(isinstance(case.get(k), str) for k in ('name', 'before_docs', 'after_docs'))
            or type(case.get('after_default')) is not int
            or type(case.get('expected_findings')) is not int
            or case['expected_findings'] not in (0, 1)):
        raise ValueError('Each case needs a name, before/after docs, integer after_default and expected_findings of 0 or 1')
    with tempfile.TemporaryDirectory(prefix='driftlens-live-') as temporary:
        repo = Path(temporary)
        env = {**os.environ, 'GIT_AUTHOR_NAME': 'DriftLens Demo',
               'GIT_AUTHOR_EMAIL': 'demo@example.invalid',
               'GIT_COMMITTER_NAME': 'DriftLens Demo',
               'GIT_COMMITTER_EMAIL': 'demo@example.invalid',
               'GIT_AUTHOR_DATE': '2026-10-31T00:00:00Z',
               'GIT_COMMITTER_DATE': '2026-10-31T00:00:00Z'}

        def git(*args):
            return subprocess.check_output(['git', '-C', str(repo), *args],
                                           env=env, stderr=subprocess.PIPE).decode().strip()

        git('init', '-q', '--initial-branch=main')
        git('config', 'core.autocrlf', 'false')
        # This paraphrase is intentionally outside the deterministic default grammar.
        commits = []
        for stage, default in (('before', 30), ('after', case['after_default'])):
            (repo / 'README.md').write_text(case[f'{stage}_docs'], encoding='utf-8', newline='\n')
            (repo / 'client.py').write_text(f'def connect(timeout={default}):\n    return timeout\n', encoding='utf-8', newline='\n')
            git('add', 'README.md', 'client.py')
            git('-c', 'commit.gpgsign=false', 'commit', '--allow-empty', '-qm', f'{stage}: timeout {default}')
            commits.append(git('rev-parse', 'HEAD'))
        baseline = analyze(repo, *commits)
        assisted = analyze(repo, *commits, model=model)
        return {'synthetic': True, 'name': case['name'], 'model': model.model,
                'prompt_version': PROMPT_VERSION, 'cache_enabled': False,
                'purpose': 'Live model contribution smoke test, not an accuracy benchmark.',
                'input': case, 'expected_findings': case['expected_findings'],
                'status': 'passed' if verified(baseline, assisted, case['expected_findings']) else 'failed',
                'last_ollama_response': getattr(model, 'last_response', None),
                'baseline': baseline, 'assisted': assisted}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='qwen2.5-coder:3b')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', type=Path, help='Run a JSON list of labeled synthetic cases')
    args = parser.parse_args(argv)
    try:
        if args.cases:
            cases = json.loads(args.cases.read_text(encoding='utf-8'))
            if not isinstance(cases, list) or not cases:
                raise ValueError('Cases must be a nonempty JSON list')
            results = [run(Ollama(args.model), case) for case in cases]
            result = {'synthetic': True, 'model': args.model, 'cache_enabled': False,
                      'status': 'passed' if all(r['status'] == 'passed' for r in results) else 'failed',
                      'cases': results,
                      'purpose': 'Small synthetic contribution/control suite, not historical accuracy.'}
        else:
            result = run(Ollama(args.model))
        write_json(result, args.output)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(2, f'Live model validation could not run: {exc}\n')
    results = result.get('cases', [result])
    print(json.dumps({'status': result['status'], 'output': str(args.output),
                      'cases': [{'name': r['name'], 'status': r['status'],
                                 'model_calls': r['assisted']['metrics']['model_calls'],
                                 'runtime_seconds': r['assisted']['metrics']['runtime_seconds']} for r in results]}))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
