import optparse
import unittest

from driftlens.analyzer import analyze
from .helpers import Repository


class OptparseDefaultSemanticsTests(unittest.TestCase):
    def test_paired_flags_share_the_last_explicit_default(self):
        old = """import optparse
def options():
    parser = optparse.OptionParser()
    parser.add_option('--enable', action='store_true', dest='enabled', default=True)
    parser.add_option('--disable', action='store_false', dest='enabled')
    return parser
"""
        for default in (True, False):
            parser = optparse.OptionParser()
            parser.add_option('--enable', action='store_true', dest='enabled', default=default)
            parser.add_option('--disable', action='store_false', dest='enabled')
            self.assertIs(parser.parse_args([])[0].enabled, default)
        report = self.compare(old, old.replace('default=True', 'default=False'),
                              '`--enable` defaults to True.')
        self.assertEqual(len(report['findings']), 1)
        self.assertIs(report['findings'][0]['after']['value']['default'], False)

    def test_group_and_parser_share_defaults(self):
        old = """import optparse
def options():
    parser = optparse.OptionParser()
    group = optparse.OptionGroup(parser, 'Mode')
    group.add_option('--enable', action='store_true', dest='enabled', default=True)
    parser.add_option('--disable', action='store_false', dest='enabled')
    parser.add_option_group(group)
    return parser
"""
        self.assertEqual(len(self.compare(old, old.replace('default=True', 'default=False'),
                                         '`--enable` defaults to True.')['findings']), 1)

    def test_unknown_later_registration_cannot_preserve_a_known_default(self):
        old = """import optparse
def options(extra):
    parser = optparse.OptionParser()
    parser.add_option('--enable', action='store_true', dest='enabled', default=True)
    parser.add_option('--disable', action='store_false', dest='enabled', **extra)
    return parser
"""
        self.assertFalse(self.compare(old, old.replace('default=True', 'default=False'),
                                      '`--enable` defaults to True.')['findings'])

    def test_independent_parsers_do_not_share_destination_state(self):
        old = """import optparse
def options():
    first = optparse.OptionParser()
    second = optparse.OptionParser()
    first.add_option('--enable', action='store_true', dest='enabled', default=True)
    second.add_option('--other', action='store_true', dest='enabled', default=False)
    return first
"""
        report = self.compare(old, old.replace('default=True', 'default=False'),
                              '`--enable` defaults to True.')
        self.assertEqual(len(report['findings']), 1)

    def test_dynamic_last_default_abstains(self):
        old = """import optparse
def options(value):
    parser = optparse.OptionParser()
    parser.add_option('--enable', action='store_true', dest='enabled', default=True)
    parser.add_option('--disable', action='store_false', dest='enabled', default=value)
    return parser
"""
        self.assertFalse(self.compare(old, old.replace('default=True', 'default=False'),
                                      '`--enable` defaults to True.')['findings'])

    def test_same_spelling_on_independent_parsers_is_ambiguous(self):
        old = """import optparse
def options():
    first = optparse.OptionParser()
    second = optparse.OptionParser()
    first.add_option('--enable', action='store_true', dest='mode', default=True)
    second.add_option('--enable', action='store_true', dest='mode', default=False)
    return first
"""
        new = old.replace("dest='mode', default=False", "dest='mode', default=True")
        # The returned parser's default never changes. The old prose is already
        # inaccurate; two declarations cannot be collapsed into one fact key.
        self.assertFalse(self.compare(old, new, '`--enable` defaults to False.')['findings'])

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
