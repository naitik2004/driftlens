"""Build isolated synthetic Git histories and save actual analyzer outputs."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from driftlens.analyzer import analyze
from driftlens.reporting import summary, write_json


def main():
    root = Path(__file__).parent
    cases = json.loads((root / 'cases.json').read_text(encoding='utf-8'))
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='driftlens-demo-') as temporary:
            repo = Path(temporary)
            env = {**os.environ, 'GIT_AUTHOR_NAME': 'DriftLens Demo', 'GIT_AUTHOR_EMAIL': 'demo@example.invalid',
                   'GIT_COMMITTER_NAME': 'DriftLens Demo', 'GIT_COMMITTER_EMAIL': 'demo@example.invalid',
                   'GIT_AUTHOR_DATE': '2026-10-31T00:00:00Z', 'GIT_COMMITTER_DATE': '2026-10-31T00:00:00Z'}
            def git(*args):
                return subprocess.check_output(['git', '-C', str(repo), *args], env=env, stderr=subprocess.PIPE).decode().strip()
            git('init', '-q', '--initial-branch=main')
            git('config', 'core.autocrlf', 'false')
            commits = []
            for stage in ('before', 'after'):
                (repo / 'client.py').write_text(case[f'{stage}_code'], encoding='utf-8', newline='\n')
                (repo / 'README.md').write_text(case[f'{stage}_docs'], encoding='utf-8', newline='\n')
                git('add', 'client.py', 'README.md')
                git('-c', 'commit.gpgsign=false', 'commit', '-qm', stage)
                commits.append(git('rev-parse', 'HEAD'))
            report = analyze(repo, *commits)
            if len(report['findings']) != case['expected_findings']:
                raise AssertionError(f"Demo {case['name']} did not match its expected outcome")
            report['demo'] = {'synthetic': True, 'name': case['name'], 'input': 'examples/cases.json'}
            output = root / 'outputs' / case['name']
            write_json(report, output.with_suffix('.json'))
            output.with_suffix('.md').write_text(summary(report), encoding='utf-8', newline='\n')
            print(f"{case['name']}: {len(report['findings'])} finding(s)")


if __name__ == '__main__':
    main()
