"""Run with an installed venv's Python -I, from outside the source checkout."""
import json
import html
from pathlib import Path
import subprocess
import sys
import tempfile

import driftlens


def main():
    checkout = Path(__file__).resolve().parents[1]
    if Path(driftlens.__file__).resolve().is_relative_to(checkout):
        raise RuntimeError('Run this check with an installed Python environment outside the checkout')
    with tempfile.TemporaryDirectory(prefix='driftlens-installed-') as tmp:
        repo = Path(tmp)

        def git(*args):
            return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE).decode().strip()

        git('init', '-q')
        git('config', 'user.name', 'DriftLens Install Check')
        git('config', 'user.email', 'check@example.invalid')
        git('config', 'core.autocrlf', 'false')
        claim = '`connect` timeout defaults to 30 — 日本語.'
        (repo / 'README.md').write_text('# Café\n\n' + claim + '\n', encoding='utf-8', newline='\n')
        revisions = []
        for timeout in (30, 10):
            (repo / 'client.py').write_text(f'def connect(timeout={timeout}): pass\n', encoding='utf-8', newline='\n')
            git('add', '.')
            git('-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture')
            revisions.append(git('rev-parse', 'HEAD'))
        output = repo / 'report.json'
        command = [sys.executable, '-I', '-m', 'driftlens', '--repo', str(repo),
                   '--base', revisions[0], '--head', revisions[1], '--json', str(output),
                   '--summary', str(repo / 'report.md'), '--fail-on-drift']
        result = subprocess.run(command, cwd=tmp, capture_output=True, text=True, timeout=60)
        if result.returncode != 1:
            raise AssertionError(f'Installed CLI returned {result.returncode}: {result.stderr}')
        report = json.loads(output.read_text(encoding='utf-8'))
        assert len(report['findings']) == 1 and not report['warnings']
        finding = report['findings'][0]
        assert finding['category'] == 'parameter_default_changed'
        assert finding['claim']['quote'] == claim
        assert claim in html.unescape((repo / 'report.md').read_text(encoding='utf-8'))
        assert finding['before']['value']['default'] == 30
        assert finding['after']['value']['default'] == 10
        assert report['base_commit'] == revisions[0] and report['head_commit'] == revisions[1]
        assert finding['hunks'] and report['metrics']['model_calls'] == 0
        (repo / 'README.md').write_text(claim.replace('30', '10') + '\n', encoding='utf-8', newline='\n')
        git('add', '.')
        git('-c', 'commit.gpgsign=false', 'commit', '-qm', 'fix docs')
        command[command.index('--head') + 1] = git('rev-parse', 'HEAD')
        result = subprocess.run(command, cwd=tmp, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stderr
        assert not json.loads(output.read_text(encoding='utf-8'))['findings']
        prefix = 'import argparse\np = argparse.ArgumentParser()\n'
        (repo / 'README.md').write_text('Use --timeout.\n', encoding='utf-8', newline='\n')
        for conditional in (False, True):
            registration = 'p.add_argument("--timeout")\n'
            if conditional:
                registration = 'if True:\n    ' + registration
            (repo / 'client.py').write_text(prefix + registration, encoding='utf-8', newline='\n')
            git('add', '.')
            git('-c', 'commit.gpgsign=false', 'commit', '-qm', 'retained flag')
            flag_revision = git('rev-parse', 'HEAD')
            command[command.index('--head' if conditional else '--base') + 1] = flag_revision
        result = subprocess.run(command, cwd=tmp, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stderr
        assert not json.loads(output.read_text(encoding='utf-8'))['findings']
    print(f'Installed CLI passed drift, corrected-doc and retained-flag controls: {driftlens.__file__}')


if __name__ == '__main__':
    main()
