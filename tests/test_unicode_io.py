import json
import html
import os
from pathlib import Path
import subprocess
import sys
import unittest

from .helpers import Repository


class UnicodeIOTests(unittest.TestCase):
    def test_cli_report_uses_utf8_with_non_utf8_default_locale(self):
        repo = Repository()
        self.addCleanup(repo.close)
        quote = '`connect` timeout defaults to 30 — 日本語.'
        a = repo.commit({'client.py': 'def connect(timeout=30): pass\n',
                         'docs/日本語.md': '# Café\n\n' + quote + '\n'})
        b = repo.commit({'client.py': 'def connect(timeout=10): pass\n'})
        output, summary = repo.path / 'report.json', repo.path / 'report.md'
        env = {**os.environ, 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0', 'LC_ALL': 'C'}
        result = subprocess.run([sys.executable, '-m', 'driftlens', '--repo', str(repo.path),
                                 '--base', a, '--head', b, '--json', str(output), '--summary', str(summary)],
                                cwd=Path(__file__).resolve().parents[1], env=env,
                                capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
        report = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(report['findings'][0]['claim']['quote'], quote)
        self.assertEqual(report['findings'][0]['claim']['path'], 'docs/日本語.md')
        self.assertIn(quote, html.unescape(summary.read_text(encoding='utf-8')))
