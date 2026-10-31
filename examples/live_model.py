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
from driftlens.model import Ollama
from driftlens.reporting import write_json


def verified(baseline, assisted):
    """A model must add the expected supported finding, without warnings."""
    findings = assisted['findings']
    return (not baseline['findings'] and not baseline['warnings']
            and not assisted['warnings'] and assisted['metrics']['model_calls'] > 0
            and len(findings) == 1
            and findings[0]['before']['symbol'] == 'client.connect'
            and findings[0]['before']['name'] == 'timeout'
            and findings[0]['category'] == 'parameter_default_changed'
            and findings[0]['evidence_strength'] == 'model-extracted, deterministic fact comparison')


def run(model):
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
        # This paraphrase is intentionally outside the deterministic default grammar.
        passage = '`connect`: the default timeout equals 30.\n'
        (repo / 'README.md').write_text(passage)
        commits = []
        for default in (30, 10):
            (repo / 'client.py').write_text(f'def connect(timeout={default}):\n    return timeout\n')
            git('add', 'README.md', 'client.py')
            git('-c', 'commit.gpgsign=false', 'commit', '-qm', f'timeout {default}')
            commits.append(git('rev-parse', 'HEAD'))
        baseline = analyze(repo, *commits)
        assisted = analyze(repo, *commits, model=model)
        return {'synthetic': True, 'model': model.model, 'cache_enabled': False,
                'purpose': 'Live model contribution smoke test, not an accuracy benchmark.',
                'input': {'documentation': passage, 'before_default': 30, 'after_default': 10},
                'status': 'passed' if verified(baseline, assisted) else 'failed',
                'baseline': baseline, 'assisted': assisted}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='qwen2.5-coder:3b')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = run(Ollama(args.model))
        write_json(result, args.output)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f'Live model validation could not run: {exc}\n')
    print(json.dumps({'status': result['status'], 'output': str(args.output),
                      'model_calls': result['assisted']['metrics']['model_calls'],
                      'runtime_seconds': result['assisted']['metrics']['runtime_seconds']}))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
