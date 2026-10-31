"""End-to-end detector regressions using committed Git snapshots."""
import unittest

from driftlens.analyzer import analyze
from .helpers import Repository


class ImperativeFlagRemovalTests(unittest.TestCase):
    old_code = ('import argparse\n'
                'parser = argparse.ArgumentParser()\n'
                'parser.add_argument("--timeout", type=int)\n')
    new_code = old_code.replace('--timeout', '--deadline')
    instruction = 'Use --timeout to stop slow jobs.'

    def setUp(self):
        self.repo = Repository()
        self.addCleanup(self.repo.close)

    def compare(self, docs=None, current_docs=None, old_code=None, new_code=None):
        docs = self.instruction if docs is None else docs
        base = self.repo.commit({'jobs.py': self.old_code if old_code is None else old_code,
                                 'README.md': docs})
        head = self.repo.commit({'jobs.py': self.new_code if new_code is None else new_code,
                                 'README.md': docs if current_docs is None else current_docs})
        return analyze(self.repo.path, base, head)

    def test_slide_instruction_reports_flag_removal(self):
        report = self.compare()
        self.assertEqual(len(report['findings']), 1)
        finding = report['findings'][0]
        self.assertEqual(finding['category'], 'flag_removed')
        self.assertEqual(finding['before']['name'], '--timeout')
        self.assertIsNone(finding['after'])
        self.assertEqual(finding['claim']['quote'], self.instruction)
        self.assertEqual(finding['before_claim']['quote'], self.instruction)
        self.assertEqual(finding['claim']['start'], 0)
        self.assertEqual(finding['claim']['end'], len(self.instruction))
        self.assertIn('-parser.add_argument("--timeout"', finding['hunks'][0]['text'])
        self.assertIn('+parser.add_argument("--deadline"', finding['hunks'][0]['text'])
        self.assertNotIn('rename', finding['explanation'].lower())
        self.assertEqual(report['metrics']['model_calls'], 0)

    def test_docs_corrected_in_same_pr(self):
        self.assertFalse(self.compare(current_docs='Use --deadline to stop slow jobs.')['findings'])

    def test_historical_mentions(self):
        for docs in ('Previously, use --timeout to stop slow jobs.',
                     'In version 1, use --timeout to stop slow jobs.',
                     'We used to use --timeout to stop slow jobs.'):
            with self.subTest(docs=docs):
                self.assertFalse(self.compare(docs=docs)['findings'])

    def test_negated_mentions(self):
        for docs in ('Do not use --timeout to stop slow jobs.',
                     'Never use --timeout to stop slow jobs.',
                     'Do not use --timeout; use --deadline to stop slow jobs.'):
            with self.subTest(docs=docs):
                self.assertFalse(self.compare(docs=docs)['findings'])

    def test_retained_timeout_alias(self):
        code = self.new_code.replace('"--deadline"', '"--deadline", "--timeout"')
        self.assertFalse(self.compare(new_code=code)['findings'])

    def test_long_option_abbreviation_compatibility(self):
        code = self.old_code.replace('--timeout', '--timeout-seconds')
        self.assertFalse(self.compare(new_code=code)['findings'])

    def test_code_examples(self):
        for docs in ('```sh\nUse --timeout to stop slow jobs.\n```\n',
                     '    Use --timeout to stop slow jobs.\n',
                     'For example, use --timeout to stop slow jobs.'):
            with self.subTest(docs=docs):
                self.assertFalse(self.compare(docs=docs)['findings'])

    def test_preexisting_inaccurate_prose(self):
        code = self.old_code.replace('--timeout', '--duration')
        self.assertFalse(self.compare(old_code=code)['findings'])

    def test_instruction_must_target_removed_flag(self):
        docs = 'Do not use --timeout; use --deadline to stop slow jobs.'
        self.assertFalse(self.compare(docs=docs)['findings'])

    def test_backtick_option_instruction(self):
        report = self.compare(docs='Use `--timeout` to stop slow jobs.')
        self.assertEqual(len(report['findings']), 1)
        self.assertEqual(report['findings'][0]['category'], 'flag_removed')

    def test_other_option_is_the_imperative_target(self):
        self.assertFalse(self.compare(docs='Use --deadline instead of --timeout.')['findings'])

    def test_use_in_descriptive_prose_is_not_an_instruction(self):
        self.assertFalse(self.compare(docs='We use --timeout to stop slow jobs.')['findings'])
