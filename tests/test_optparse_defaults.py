import optparse
import unittest

from driftlens.analyzer import analyze
from .helpers import Repository


class OptparseDefaultSemanticsTests(unittest.TestCase):
    def compare(self, old, new, claim):
        repo = Repository()
        self.addCleanup(repo.close)
        before = repo.commit({'cli.py': old, 'README.md': claim})
        after = repo.commit({'cli.py': new})
        return analyze(repo.path, before, after)

    def test_implicit_boolean_actions_do_not_invent_defaults(self):
        for action in ('store_true', 'store_false'):
            parser = optparse.OptionParser()
            parser.add_option('--quiet', action=action, dest='quiet')
            self.assertIsNone(parser.parse_args([])[0].quiet)
        old = """import optparse
def parseOpts():
    parser = optparse.OptionParser()
    parser.add_option('--quiet', action='store_false', dest='quiet')
    return parser
"""
        report = self.compare(old, old.replace("action='store_false'", "action='store_true'"),
                              '`--quiet` defaults to True.')
        self.assertFalse(report['findings'])

    def test_shared_destination_overrides_do_not_create_new_drift(self):
        for default in (True, False):
            parser = optparse.OptionParser()
            parser.add_option('--yes', action='store_true', dest='mode', default=default)
            parser.add_option('--no', action='store_false', dest='mode', default=False)
            self.assertIs(parser.parse_args([])[0].mode, False)
        old = """import optparse
def parseOpts():
    parser = optparse.OptionParser()
    parser.add_option('--yes', action='store_true', dest='mode', default=True)
    parser.add_option('--no', action='store_false', dest='mode', default=False)
    return parser
"""
        self.assertFalse(self.compare(old, old.replace('default=True', 'default=False'),
                                      '`--yes` defaults to True.')['findings'])

    def test_set_defaults_override_abstains(self):
        parser = optparse.OptionParser()
        parser.add_option('--yes', action='store_true', dest='mode', default=True)
        parser.set_defaults(mode=False)
        self.assertIs(parser.parse_args([])[0].mode, False)
        old = """import optparse
def parseOpts():
    parser = optparse.OptionParser()
    parser.add_option('--yes', action='store_true', dest='mode', default=True)
    parser.set_defaults(mode=False)
    return parser
"""
        self.assertFalse(self.compare(old, old.replace('default=True', 'default=False'),
                                      '`--yes` defaults to True.')['findings'])
