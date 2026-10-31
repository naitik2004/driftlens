import unittest

from driftlens.analyzer import analyze
from .helpers import Repository


OLD = '''from pathlib import Path
from enum import Flag
CACHE_DIR = Path('cache')
class StorageMode(Flag):
    NORMAL = 0
    OTHER = 1
def locate_cache(width: int, mode: StorageMode):
    return CACHE_DIR / f"entry.{width}.{mode.value}.bin"
'''
NEW = '''from pathlib import Path
from dataclasses import dataclass
CACHE_DIR = Path('cache')
@dataclass
class StorageMode:
    width: int = 80
    def key(self):
        parts = [str(self.width), 'x', 'y']
        return '.'.join(parts)
def locate_cache(mode: StorageMode):
    return CACHE_DIR / f"entry.{mode.key()}.bin"
'''
DOCS = '* Linux: `/home/user/<version>/entry.<width>.<storage-mode>.bin`\n'


class CachePatternTests(unittest.TestCase):
    def compare(self, old=OLD, new=NEW, docs=DOCS, current_docs=None):
        repo = Repository()
        self.addCleanup(repo.close)
        a = repo.commit({'engine.py': old, 'README.md': docs})
        b = repo.commit({'engine.py': new, 'README.md': docs if current_docs is None else current_docs})
        return analyze(repo.path, a, b, repository_url='https://example.invalid/project')

    def test_numeric_filename_contradicted_by_longer_joined_key(self):
        report = self.compare()
        self.assertEqual(len(report['findings']), 1)
        f = report['findings'][0]
        self.assertEqual(f['category'], 'cache_path_changed')
        self.assertEqual(f['before']['symbol'], 'engine.locate_cache')
        self.assertEqual(f['before']['name'], 'mode')
        self.assertEqual(f['claim']['quote'], DOCS.strip())
        self.assertEqual(f['before']['value']['numeric_components'], 2)
        self.assertEqual(f['after']['value']['minimum_components'], 3)
        self.assertEqual(f['before_verdict'], 'supported')
        self.assertEqual(f['after_verdict'], 'contradicted')
        self.assertTrue(f['hunks'])
        self.assertIn('/blob/' + report['head_commit'], f['links']['documentation'])
        self.assertEqual(report['metrics']['model_calls'], 0)

    def test_docs_fixed_in_same_change(self):
        self.assertFalse(self.compare(current_docs=DOCS.replace('<width>.<storage-mode>', '<key>'))['findings'])

    def test_unchanged_numeric_filename(self):
        self.assertFalse(self.compare(new=OLD.replace("Path('cache')", "Path( 'cache' )"))['findings'])

    def test_equal_component_count_is_not_a_contradiction(self):
        self.assertFalse(self.compare(new=NEW.replace(
            "[str(self.width), 'x', 'y']", "[str(self.width), 'x']"))['findings'])

    def test_mutated_join_inputs_abstain(self):
        for operation in ('parts.pop()', "parts.append('z')", 'alias = parts'):
            with self.subTest(operation=operation):
                code = NEW.replace("        return '.'", f"        {operation}\n        return '.'")
                self.assertFalse(self.compare(new=code)['findings'])

    def test_dynamic_join_length_abstains(self):
        self.assertFalse(self.compare(new=NEW.replace(
            "[str(self.width), 'x', 'y']", '[str(x) for x in self.width]'))['findings'])

    def test_untyped_old_value_abstains(self):
        for old in (OLD.replace('width: int', 'width'), OLD.replace('{width}', '{width:04}'),
                    OLD.replace('{mode.value}', '{mode.value!r}')):
            with self.subTest(code=old):
                self.assertFalse(self.compare(old=old)['findings'])

    def test_unknown_decorator_abstains(self):
        self.assertFalse(self.compare(new=NEW.replace('@dataclass', '@custom_decorator'))['findings'])
        old = OLD.replace('def locate_cache', '    @custom_decorator\n    def helper(self): return None\ndef locate_cache')
        self.assertFalse(self.compare(old=old)['findings'])

    def test_temporal_and_conditional_claims_abstain(self):
        for prefix in ('Before version 2, ', 'Previously, ', 'If compatibility mode is enabled, ', '<span class="legacy">'):
            with self.subTest(prefix=prefix):
                self.assertFalse(self.compare(docs=prefix + DOCS)['findings'])

    def test_ambiguous_identical_filename_owners_abstain(self):
        extra = '\ndef other_cache(width: int, mode: StorageMode):\n    return CACHE_DIR / f"entry.{width}.{mode.value}.bin"\n'
        self.assertFalse(self.compare(old=OLD + extra)['findings'])

    def test_unknown_helper_or_separator_abstains(self):
        for new in (NEW.replace('mode.key()', 'external_key(mode)'),
                    NEW.replace("return '.'.join", "return '-'.join")):
            with self.subTest(code=new):
                self.assertFalse(self.compare(new=new)['findings'])

    def test_noninteger_enum_values_abstain(self):
        self.assertFalse(self.compare(old=OLD.replace('NORMAL = 0', "NORMAL = 'x.y'"))['findings'])

    def test_base_path_changes_abstain(self):
        self.assertFalse(self.compare(new=NEW.replace('return CACHE_DIR /', 'return OTHER_DIR /'))['findings'])

    def test_shadowed_numeric_type_or_import_abstains(self):
        for old in (OLD + '\nint = custom_type\n', OLD + '\nfrom custom import Flag\n',
                    OLD.replace('from enum import', 'from .enum import')):
            with self.subTest(code=old):
                self.assertFalse(self.compare(old=old)['findings'])

    def test_monkeypatched_helper_abstains(self):
        for code in (NEW + '\nStorageMode.key = custom_key\n',
                     NEW.replace('def locate_cache', '    key = custom_key\ndef locate_cache'),
                     NEW.replace('    def key(self):', '    def __getattribute__(self, name):\n        return external(name)\n    def key(self):')):
            with self.subTest(code=code):
                self.assertFalse(self.compare(new=code)['findings'])

    def test_module_reference_does_not_disambiguate_two_functions(self):
        extra = '\ndef other_cache(width: int, mode: StorageMode):\n    return CACHE_DIR / f"entry.{width}.{mode.value}.bin"\n'
        self.assertFalse(self.compare(old=OLD + extra, docs='# engine.py\n\n' + DOCS)['findings'])

    def test_parameter_rename_without_layout_change_is_ignored(self):
        self.assertFalse(self.compare(new=OLD.replace('width', 'columns'))['findings'])

    def test_multiple_helper_return_shapes_abstain(self):
        code = NEW.replace("        parts =", "        if self.width == 1:\n            return 'x.y'\n        parts =")
        self.assertFalse(self.compare(new=code)['findings'])

    def test_known_attr_dataclass_decorator(self):
        self.assertEqual(len(self.compare(new=NEW.replace('from dataclasses', 'from attr'))['findings']), 1)

    def test_rebound_class_annotation_abstains(self):
        for code in (NEW + '\nStorageMode = foreign_type\n', NEW + '\ndef StorageMode(): pass\n'):
            with self.subTest(code=code):
                self.assertFalse(self.compare(new=code)['findings'])

    def test_project_shadowing_trusted_modules_abstains(self):
        for name in ('enum', 'pathlib', 'dataclasses', 'attr'):
            with self.subTest(module=name):
                repo = Repository()
                self.addCleanup(repo.close)
                a = repo.commit({'engine.py': OLD, 'README.md': DOCS, name + '.py': '# local module\n'})
                b = repo.commit({'engine.py': NEW})
                self.assertFalse(analyze(repo.path, a, b)['findings'])
