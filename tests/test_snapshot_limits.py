import contextlib
import io
import unittest
from unittest.mock import patch

from driftlens.cli import main
from driftlens.snapshots import SnapshotError, SnapshotLimits, snapshot
from .helpers import Repository


class SnapshotLimitTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.addCleanup(self.repo.close)
        self.commit = self.repo.commit({'a.py': '# 12345\n', 'README.md': 'example\n',
                                       'ignored.txt': 'x' * 1000})

    def test_normal_snapshot_and_ineligible_files(self):
        result = snapshot(self.repo.path, self.commit, SnapshotLimits(max_bytes=16))
        self.assertEqual(set(result.files), {'a.py', 'README.md'})

    def test_file_and_byte_limits_preflight(self):
        for limits in (SnapshotLimits(max_files=1), SnapshotLimits(max_bytes=15),
                       SnapshotLimits(max_file_bytes=7)):
            with self.subTest(limits=limits), self.assertRaisesRegex(SnapshotError, 'limit exceeded'):
                snapshot(self.repo.path, self.commit, limits)

    def test_collection_time_budget(self):
        with patch('driftlens.snapshots.time.monotonic', side_effect=[0, 181]), \
                self.assertRaisesRegex(SnapshotError, 'timed out'):
            snapshot(self.repo.path, self.commit)

    def test_cli_limit_failure_does_not_write_report(self):
        output = self.repo.path / 'report.json'
        with contextlib.redirect_stderr(io.StringIO()):
            code = main(['--repo', str(self.repo.path), '--base', self.commit,
                         '--max-files', '1', '--json', str(output)])
        self.assertEqual(code, 2)
        self.assertFalse(output.exists())

    def test_invalid_limits(self):
        for kwargs in ({'max_files': 0}, {'max_bytes': -1}, {'timeout_seconds': 0},
                       {'timeout_seconds': float('nan')}, {'timeout_seconds': float('inf')}):
            with self.subTest(kwargs=kwargs), self.assertRaises(SnapshotError):
                SnapshotLimits(**kwargs)
