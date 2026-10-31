import json
from pathlib import Path
import unittest
from unittest.mock import patch

from examples.historical import replay as module
from .helpers import Repository


class HistoricalEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.addCleanup(self.repo.close)
        self.quote = '`connect` timeout defaults to 30.'
        a = self.repo.commit({'client.py': 'def connect(timeout=30): pass\n',
                              'README.md': self.quote + '\n'})
        b = self.repo.commit({'client.py': 'def connect(timeout=10): pass\n'})
        self.case = {'id': 'fixture', 'repo': str(self.repo.path),
                     'before': a, 'drift': b, 'source_url': 'https://example.invalid/repo',
                     'expected': [{'path': 'README.md', 'symbol': 'client.connect',
                                   'name': 'timeout', 'category': 'parameter_default_changed',
                                   'quote': self.quote, 'line_start': 1, 'start': 0}],
                     'evidence': {'code_path': 'client.py',
                                  'before_code': 'timeout=30', 'drift_code': 'timeout=10',
                                  'doc_path': 'README.md', 'quote': self.quote}}

    def test_reports_and_moved_correction_without_future_leakage(self):
        corrected = '`connect` timeout defaults to 10.'
        c = self.repo.commit({'README.md': None, 'docs/api.md': corrected})
        self.case['correction'] = c
        self.case['evidence'].update(correction_path='docs/api.md', correction_quote=corrected)
        manifest = self.repo.path / 'manifest.json'
        manifest.write_text(json.dumps({'cases': [self.case]}))
        output = self.repo.path / 'outputs'
        events = []
        real_analyze, real_read = module.analyze, module.read

        def analyze(*args, **kwargs):
            self.assertEqual(args[1:], (self.case['before'], self.case['drift']))
            self.assertNotIn('model', kwargs)
            events.append('analysis')
            return real_analyze(*args, **kwargs)

        def read(repo, revision, path):
            if revision == c:
                self.assertIn('analysis', events)
            return real_read(repo, revision, path)

        with patch.object(module, 'analyze', side_effect=analyze), \
                patch.object(module, 'read', side_effect=read):
            result = module.replay(manifest, output)
        self.assertEqual(result['known_case_recall'], 1)
        self.assertEqual(json.loads((output / 'fixture.json').read_text())['findings'][0]
                         ['claim']['quote'], self.quote)
        self.assertEqual(json.loads((output / 'evaluation.json').read_text()), result)

    def test_incorrect_localization_rejected(self):
        self.case['expected'][0]['start'] = 1
        with self.assertRaisesRegex(ValueError, 'localization'):
            module.verify(self.case, self.repo.path)

    def test_explicit_cache_directory_does_not_mutate_manifest(self):
        original = {'cases': [{**self.case, 'repo': '../missing/' + self.repo.path.name}]}
        manifest = self.repo.path / 'manifest.json'
        manifest.write_text(json.dumps(original))
        result = module.replay(manifest, self.repo.path / 'output', self.repo.path.parent)
        self.assertEqual(result['known_case_recall'], 1)
        self.assertEqual(json.loads(manifest.read_text()), original)

    def test_missing_old_support_rejected(self):
        self.case['evidence']['before_code'] = 'timeout=99'
        with self.assertRaisesRegex(ValueError, 'before_code'):
            module.verify(self.case, self.repo.path)

    def test_removed_code_evidence_must_be_absent_at_b(self):
        self.case['evidence']['absent_drift_code'] = 'timeout=10'
        with self.assertRaisesRegex(ValueError, 'removed code still present'):
            module.verify(self.case, self.repo.path)
        self.case['evidence']['absent_drift_code'] = 'timeout=30'
        module.verify(self.case, self.repo.path)

    def test_claim_must_remain_at_b_even_without_localization_labels(self):
        self.case['drift'] = self.repo.commit({'README.md': 'Updated documentation.\n'})
        self.case['expected'] = []
        with self.assertRaisesRegex(ValueError, 'claim not retained at B'):
            module.verify(self.case, self.repo.path)

    def test_before_may_precede_multiple_change_commits(self):
        self.case['drift'] = self.repo.commit({'unrelated.txt': 'Second commit in the change.\n'})
        module.verify(self.case, self.repo.path)

    def test_behavior_change_cannot_be_called_formatting(self):
        self.case['formatting_only'] = True
        with self.assertRaisesRegex(ValueError, 'AST'):
            module.verify(self.case, self.repo.path)

    def test_stale_docs_cannot_be_called_synchronized(self):
        self.case['synchronized'] = {'code_path': 'client.py', 'doc_path': 'README.md',
                                     'added_text': 'timeout=10'}
        with self.assertRaisesRegex(ValueError, 'code and docs together'):
            module.verify(self.case, self.repo.path)

    def test_synchronized_removal_checks_both_code_and_docs(self):
        self.case['expected'] = []
        self.case.pop('evidence')
        self.case['synchronized'] = {'code_path': 'client.py', 'doc_path': 'README.md',
                                     'removed_text': 'timeout'}
        with self.assertRaisesRegex(ValueError, 'code and docs together'):
            module.verify(self.case, self.repo.path)
        self.case['drift'] = self.repo.commit({'client.py': 'def connect(): pass\n',
                                               'README.md': '`connect` is available.\n'})
        module.verify(self.case, self.repo.path)

    def test_synchronized_direction_must_be_unambiguous(self):
        self.case['synchronized'] = {'code_path': 'client.py', 'doc_path': 'README.md',
                                     'removed_text': 'timeout', 'added_text': 'timeout'}
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            module.verify(self.case, self.repo.path)


if __name__ == '__main__':
    unittest.main()
