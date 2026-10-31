import unittest
from driftlens.analyzer import analyze
from .helpers import Repository


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.addCleanup(self.repo.close)

    def compare(self, old, new, docs='`connect` timeout defaults to 30.'):
        a = self.repo.commit({'client.py': old, 'docs.md': docs})
        b = self.repo.commit({'client.py': new})
        return analyze(self.repo.path, a, b)

    def test_augmented_constant_abstains(self):
        old = 'TIMEOUT = 30\nTIMEOUT += 20\ndef connect(timeout=TIMEOUT): pass'
        self.assertFalse(self.compare(old, old.replace('TIMEOUT = 30', 'TIMEOUT = 10'))['findings'])

    def test_conditional_constant_override(self):
        old = 'TIMEOUT = 30\nif production:\n    TIMEOUT = 60\ndef connect(timeout=TIMEOUT): pass'
        self.assertFalse(self.compare(old, old.replace('TIMEOUT = 30', 'TIMEOUT = 10'))['findings'])

    def test_mutated_function_defaults(self):
        old = 'def connect(timeout=30): pass\nconnect.__defaults__ = (60,)'
        self.assertFalse(self.compare(old, old.replace('timeout=30', 'timeout=10'))['findings'])

    def test_body_override(self):
        old = 'def connect(timeout=30):\n    timeout = get_timeout()\n    return timeout'
        self.assertFalse(self.compare(old, old.replace('timeout=30', 'timeout=10'))['findings'])

    def test_last_flag_removed(self):
        old = 'import argparse\np = argparse.ArgumentParser()\np.add_argument("--timeout", default=30)'
        new = 'import argparse\np = argparse.ArgumentParser()'
        self.assertEqual(len(self.compare(old, new, 'The CLI supports `--timeout`.')['findings']), 1)

    def test_flag_abbreviation(self):
        old = 'import argparse\np = argparse.ArgumentParser()\np.add_argument("--time", default=30)'
        new = old.replace('--time', '--timeout')
        self.assertFalse(self.compare(old, new, 'The CLI supports `--time`.')['findings'])

    def test_renamed_documentation_exact_span(self):
        a = self.repo.commit({'client.py': 'def connect(timeout=30): pass', 'old.md': '`connect` timeout defaults to 30.'})
        b = self.repo.commit({'client.py': 'def connect(timeout=10): pass', 'old.md': None, 'new.md': '`connect` timeout defaults to 30.'})
        findings = analyze(self.repo.path, a, b)['findings']
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['claim']['path'], 'new.md')
        self.assertEqual(findings[0]['before_claim']['path'], 'old.md')

    def test_not_a_default_claim(self):
        self.assertFalse(self.compare('def connect(timeout=30): pass', 'def connect(timeout=10): pass', '`connect` timeout does not default to 30.')['findings'])

    def test_incompatible_retry_body(self):
        old = 'def connect():\n    for attempt in range(4):\n        try:\n            return send()\n        except ConnectionError:\n            break\n    raise ConnectionError()'
        self.assertFalse(self.compare(old, old.replace('range(4)', 'range(2)'), '`connect` performs up to 3 retries on ConnectionError.')['findings'])

    def test_multiple_parameter_claim_abstains(self):
        self.assertFalse(self.compare('def connect(timeout=30, retries=30): pass', 'def connect(timeout=10, retries=30): pass', '`connect` accepts timeout and retries defaults to 30.')['findings'])

    def test_hidden_html_comment_abstains(self):
        self.assertFalse(self.compare('def connect(timeout=30): pass', 'def connect(timeout=10): pass', '<!-- `connect` timeout defaults to 30. -->')['findings'])

    def test_conditional_function_redefinition(self):
        old = 'def connect(timeout=30): pass\nif production:\n    def connect(timeout=60): pass'
        self.assertFalse(self.compare(old, old.replace('timeout=30', 'timeout=10'))['findings'])

    def test_late_constant_definition(self):
        old = 'def connect(timeout=TIMEOUT): pass\nTIMEOUT = 30'
        self.assertFalse(self.compare(old, old.replace('30', '10'))['findings'])
