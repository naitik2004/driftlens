import unittest

from driftlens.analyzer import analyze
from driftlens.cli import main
from driftlens.reporting import annotations, summary
from .helpers import Repository


OLD = '''MAX_ITEMS = 17
def _list_tree():
    tree = retrieve()
    reached = len(tree.children) == MAX_ITEMS
    if reached:
        raise ValueError('limit')
    return tree

def export_folder():
    return _list_tree()
'''
NEW = '''def _list_tree():
    return retrieve_new()

def export_folder():
    return _list_tree()
'''
CLAIM = 'Exports folders recursively (up to 17 files per folder)'


class BehavioralReviewTests(unittest.TestCase):
    def compare(self, old=OLD, new=NEW, claim=CLAIM, new_claim=None, enabled=True):
        repo = Repository()
        self.addCleanup(repo.close)
        a = repo.commit({'exporter.py': old, 'README.md': claim})
        files = {'exporter.py': new}
        if new_claim is not None:
            files['README.md'] = new_claim
        b = repo.commit(files)
        return repo, a, b, analyze(repo.path, a, b, 'https://github.com/example/exporter', review_candidates=enabled)

    def test_removed_guard_surfaces_evidence_without_claiming_a_new_bound(self):
        _, _, _, report = self.compare()
        self.assertEqual(report['findings'], [])
        candidate, = report['review_candidates']
        self.assertEqual(candidate['before_limit'], 17)
        self.assertEqual(candidate['symbol'], 'exporter.export_folder')
        self.assertEqual(candidate['status'], 'needs_review')
        self.assertIn('external service', candidate['reason'])
        self.assertIn('/blob/', candidate['evidence'][0]['link'])
        self.assertEqual(list(annotations(report)), [])
        rendered = summary(report)
        self.assertIn('not established drift findings', rendered)
        self.assertIn(CLAIM, rendered)

    def test_review_is_opt_in_and_does_not_fail_builds(self):
        repo, a, b, report = self.compare(enabled=False)
        self.assertNotIn('review_candidates', report)
        self.assertEqual(main(['--repo', str(repo.path), '--base', a, '--head', b,
                               '--review-candidates', '--fail-on-drift',
                               '--summary', str(repo.path / 'report.md')]), 0)

    def test_retained_renamed_inlined_and_moved_guards_are_suppressed(self):
        for source in (OLD, OLD.replace('MAX_ITEMS', 'BOUND'),
                       OLD.replace('MAX_ITEMS = 17\n', '').replace('MAX_ITEMS', '17'),
                       NEW + '\ndef enforce(tree):\n    if len(tree.children) == 17:\n        raise ValueError()\n'):
            with self.subTest(source=source):
                self.assertEqual(self.compare(new=source)[3]['review_candidates'], [])

    def test_updated_historical_unrelated_and_preexisting_claims_are_suppressed(self):
        cases = [dict(new_claim='Exports folders recursively.'),
                 dict(claim='Previously, ' + CLAIM), dict(claim=CLAIM.replace('17', '99')),
                 dict(claim=CLAIM.replace('folder', 'bucket')),
                 dict(old=NEW)]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.compare(**kwargs)[3]['review_candidates'], [])

    def test_merge_example_is_a_candidate_and_explicit_overrides_are_suppressed(self):
        old = '''import optparse
def options():
    parser = optparse.OptionParser()
    parser.add_option('--video-multistreams', action='store_true', dest='video', default=True)
    parser.add_option('--no-video-multistreams', action='store_false', dest='video')
    return parser
'''
        new = old.replace('default=True', 'default=False')
        claim = 'For example, `-f bestvideo+best+bestaudio` will merge all three formats.'
        report = self.compare(old, new, claim)[3]
        self.assertEqual(report['findings'], [])
        self.assertEqual(len(report['review_candidates']), 1)
        for override in (' --video-multistreams', ' --no-video-multistreams'):
            self.assertEqual(self.compare(old, new, claim.replace('bestaudio`', 'bestaudio' + override + '`'))[3]['review_candidates'], [])
        self.assertEqual(self.compare(old, new, claim.replace('+best+bestaudio', '+bestaudio'))[3]['review_candidates'], [])

    def test_one_explicit_stream_override_suppresses_cross_flag_speculation(self):
        old = '''import optparse
def options():
    parser = optparse.OptionParser()
    parser.add_option('--video', action='store_true', dest='video', default=True)
    parser.add_option('--no-video', action='store_false', dest='video')
    parser.add_option('--audio', action='store_true', dest='audio', default=True)
    return parser
'''
        claim = 'For example, `-f bestvideo+best+bestaudio --no-video` will merge two formats.'
        self.assertEqual(self.compare(old, old.replace('default=True', 'default=False'), claim)[3]['review_candidates'], [])

    def test_evidence_preserves_original_line_endings(self):
        old, new = OLD.replace('\n', '\r\n'), NEW.replace('\n', '\r\n')
        report = self.compare(old, new)[3]
        evidence = report['review_candidates'][0]['evidence']
        self.assertTrue(any('\r\n' in e['quote'] for e in evidence))
        for excerpt in evidence:
            self.assertIn(excerpt['quote'], old if excerpt['revision'] == 'base' else new)

    def test_large_helpers_do_not_expand_review_evidence_without_bound(self):
        new = NEW.replace('    return retrieve_new()', '    pass\n' * 100 + '    return retrieve_new()')
        candidate, = self.compare(new=new)[3]['review_candidates']
        self.assertTrue(candidate['evidence'])
        for excerpt in candidate['evidence']:
            self.assertLessEqual(len(excerpt['quote']), 6000)
            self.assertLessEqual(excerpt['end_line'] - excerpt['line'] + 1, 80)


if __name__ == '__main__':
    unittest.main()
