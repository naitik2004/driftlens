import contextlib
import io
import subprocess
import unittest
from unittest.mock import patch

from driftlens.analyzer import analyze
from driftlens.cli import main
from .helpers import Repository


class AuditRegressions(unittest.TestCase):
    def compare(self, old, new, docs, extra=None):
        repo = Repository()
        self.addCleanup(repo.close)
        a = repo.commit({'engine.py': old, 'README.md': docs})
        b = repo.commit({'engine.py': new, **(extra or {})})
        return analyze(repo.path, a, b)

    def test_retained_flag_in_unsupported_registration_abstains(self):
        prefix = 'import argparse\np = argparse.ArgumentParser()\n'
        old = prefix + 'p.add_argument("--timeout", default=30)\n'
        for registration in ('if True:\n    p.add_argument("--timeout", default=30)\n',
                             'q = p\nq.add_argument("--timeout", default=30)\n',
                             'configure(p)\n',
                             'p = custom_parser()\np.add_argument("--other")\n'):
            with self.subTest(registration=registration):
                self.assertFalse(self.compare(old, prefix + registration,
                                             'Use --timeout to stop slow jobs.')['findings'])

    def test_shadowed_argparse_constructor_abstains(self):
        for prefix in ('from argparse import ArgumentParser\nclass ArgumentParser:\n    pass\n',
                       'from .argparse import ArgumentParser\n'):
            old = prefix + 'p = ArgumentParser()\np.add_argument("--timeout", default=30)\n'
            self.assertFalse(self.compare(old, old.replace('default=30', 'default=10'),
                                         '`--timeout` defaults to 30.')['findings'])

    def test_project_shadowing_argparse_invalidates_removal(self):
        old = 'import argparse\np = argparse.ArgumentParser()\np.add_argument("--timeout")\n'
        self.assertFalse(self.compare(old, old.replace('p.add_argument("--timeout")', ''),
                                     'Use --timeout.', {'argparse.py': '# custom library\n'})['findings'])

    def test_rebound_constant_abstains(self):
        for binding in ('def LIMIT(): return 99', 'class LIMIT: pass', 'from settings import LIMIT'):
            with self.subTest(binding=binding):
                old = f'LIMIT = 30\n{binding}\ndef connect(timeout=LIMIT): pass\n'
                self.assertFalse(self.compare(old, old.replace('LIMIT = 30', 'LIMIT = 10'),
                                             '`connect` timeout defaults to 30.')['findings'])

    def test_shadowed_range_abstains(self):
        body = ('    for _ in range(3):\n        try: return remote()\n'
                '        except IOError: pass\n    raise IOError()\n')
        for prefix, signature in (('def range(n): return [0]\n', 'def fetch():'),
                                  ('from custom import range\n', 'def fetch():'),
                                  ('', 'def fetch(range, /):')):
            old = prefix + signature + '\n' + body
            self.assertFalse(self.compare(old, old.replace('range(3)', 'range(5)'),
                                         '`fetch` performs at most 2 automatic retries for `IOError`.')['findings'])

    def test_import_rebinding_public_function_abstains(self):
        old = 'def connect(timeout=30): pass\nfrom custom import connect\n'
        self.assertFalse(self.compare(old, old.replace('timeout=30', 'timeout=10'),
                                     '`connect` timeout defaults to 30.')['findings'])

    def test_optparse_shadowed_constructor_abstains(self):
        old = ('import optparse\nclass optparse: pass\ndef parseOpts():\n'
               '    p = optparse.OptionParser()\n'
               '    p.add_option("--quiet", action="store_true", dest="quiet", default=True)\n'
               '    return p\n')
        self.assertFalse(self.compare(old, old.replace('default=True', 'default=False'),
                                     '`--quiet` defaults to True.')['findings'])

    def test_git_timeout_has_cli_error_exit(self):
        stderr = io.StringIO()
        with patch('driftlens.snapshots.subprocess.run', side_effect=subprocess.TimeoutExpired('git', 60)), \
                contextlib.redirect_stderr(stderr):
            self.assertEqual(main(['--base', 'main']), 2)
        self.assertIn('timed out', stderr.getvalue())

    def test_attached_optparse_group_still_reports_explicit_default_change(self):
        old = ('import optparse\ndef parseOpts():\n'
               '    p = optparse.OptionParser()\n'
               '    group = optparse.OptionGroup(p, "Output")\n'
               '    group.add_option("--quiet", action="store_true", dest="quiet", default=True)\n'
               '    p.add_option_group(group)\n    return p\n')
        self.assertEqual(len(self.compare(old, old.replace('default=True', 'default=False'),
                                         '`--quiet` defaults to True.')['findings']), 1)
