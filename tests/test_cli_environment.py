import json
import os
import unittest
from unittest.mock import patch

from driftlens.cli import main
from .helpers import Repository


class EventPrecedenceTests(unittest.TestCase):
    def test_explicit_revisions_do_not_inherit_an_unrelated_pr_head(self):
        repo = Repository()
        self.addCleanup(repo.close)
        before = repo.commit({'client.py': 'def connect(timeout=30): pass',
                              'docs.md': '`connect` timeout defaults to 30.'})
        after = repo.commit({'client.py': 'def connect(timeout=10): pass'})
        event = repo.path / 'event.json'
        output = repo.path / 'report.json'
        event.write_text(json.dumps({'pull_request': {
            'base': {'sha': before}, 'head': {'sha': 'unrelated-external-head'}}}))
        env = {'GITHUB_EVENT_NAME': 'pull_request', 'GITHUB_EVENT_PATH': str(event)}
        args = ['--repo', str(repo.path), '--json', str(output),
                '--summary', str(repo.path / 'summary.md')]
        with patch.dict(os.environ, env):
            self.assertEqual(main(args + ['--base', before]), 0)
            self.assertEqual(json.loads(output.read_text())['head_commit'], after)
            # An explicitly requested event still supplies its head; an invalid
            # external revision must fail, not silently fall back to local HEAD.
            self.assertEqual(main(args + ['--base', before, '--github-event', str(event)]), 2)
            event.write_text(json.dumps({'pull_request': {
                'base': {'sha': before}, 'head': {'sha': after}}}))
            self.assertEqual(main(args), 0)
            report = json.loads(output.read_text())
            self.assertEqual((report['base_commit'], report['head_commit']), (before, after))
