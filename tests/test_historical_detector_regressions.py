import unittest

from driftlens.analyzer import analyze
from driftlens.facts import Extractor, UNKNOWN
from .helpers import Repository


class OptparseHistoricalTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.addCleanup(self.repo.close)
        self.option = '''import optparse
def parseOpts():
    parser = optparse.OptionParser()
    video = optparse.OptionGroup(parser, 'Video')
    video.add_option('--video-multistreams', action='store_true', dest='allow_video', default={default})
    return parser
'''

    def test_tracks_explicit_default_and_abstains_on_implicit_store_false(self):
        source = self.option.format(default='False').replace(
            '    return parser',
            "    video.add_option('--no-video-multistreams', action='store_false', dest='other')\n    return parser")
        facts = Extractor({'cli.py': source}).extract()
        flags = {f.name: f for f in facts if f.kind == 'flag'}
        self.assertEqual(flags['--video-multistreams'].value['default'], False)
        self.assertEqual(flags['--video-multistreams'].value['dest'], 'allow_video')
        self.assertEqual(flags['--video-multistreams'].value['action'], 'store_true')
        self.assertEqual(flags['--no-video-multistreams'].value['default'], UNKNOWN)
        self.assertFalse(flags['--no-video-multistreams'].resolved)

    def test_exact_flag_claim_links_old_and_new_static_defaults(self):
        a = self.repo.commit({'cli.py': self.option.format(default='True'),
                              'README.md': '`--video-multistreams` defaults to True.'})
        b = self.repo.commit({'cli.py': self.option.format(default='False')})
        report = analyze(self.repo.path, a, b)
        self.assertEqual(len(report['findings']), 1)
        finding = report['findings'][0]
        self.assertEqual(finding['before']['name'], '--video-multistreams')
        self.assertEqual(finding['before']['value']['default'], True)
        self.assertEqual(finding['after']['value']['default'], False)
        self.assertEqual(finding['claim']['quote'], '`--video-multistreams` defaults to True.')

    def test_dynamic_default_abstains(self):
        facts = Extractor({'cli.py': self.option.format(default='choose_default()')}).extract()
        flag = next(f for f in facts if f.kind == 'flag' and f.name == '--video-multistreams')
        self.assertFalse(flag.resolved)


class ComputedCachePathTests(unittest.TestCase):
    def test_method_computed_filename_is_not_claimed_as_resolved(self):
        repo = Repository()
        self.addCleanup(repo.close)
        a = repo.commit({'black.py': '''def get_cache_file(line_length, mode):
    return CACHE_DIR / f"cache.{line_length}.{mode.value}.pickle"
''', 'README.md': '`cache.<line-length>.<file-mode>.pickle` is the cache filename.'})
        b = repo.commit({'black.py': '''def get_cache_file(mode):
    return CACHE_DIR / f"cache.{mode.get_cache_key()}.pickle"

class FileMode:
    def get_cache_key(self):
        return ".".join([str(self.line_length), str(self.is_pyi)])
'''} )
        report = analyze(repo.path, a, b)
        self.assertEqual(report['findings'], [])


if __name__ == '__main__':
    unittest.main()
