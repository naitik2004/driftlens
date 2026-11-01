import ast
import unittest

from examples.controlled.replay import mutate_default


class ControlledMutationTests(unittest.TestCase):
    def test_changes_only_selected_default_with_utf8_columns(self):
        source = "def api(π='é', delay=0):\n    return delay\n\ndef other(delay=0):\n    return delay\n"
        changed = mutate_default(source, 'api', 'delay', 0, 1)
        self.assertEqual(changed, source.replace("π='é', delay=0", "π='é', delay=1"))
        ast.parse(changed)

    def test_changes_keyword_only_boolean_default(self):
        source = 'def api(*, enabled: bool = True):\n    return enabled\n'
        self.assertEqual(mutate_default(source, 'api', 'enabled', True, False), source.replace('= True', '= False'))

    def test_rejects_wrong_typed_baseline(self):
        with self.assertRaises(ValueError):
            mutate_default('def api(value=0): pass\n', 'api', 'value', False, True)

    def test_does_not_execute_dynamic_defaults(self):
        with self.assertRaises(ValueError):
            mutate_default('def api(value=run_external_code()): pass\n', 'api', 'value', 0, 1)

    def test_rejects_required_or_ambiguous_targets(self):
        for source in ('def api(value): pass\n', 'def api(value=0): pass\ndef api(value=0): pass\n'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                mutate_default(source, 'api', 'value', 0, 1)


if __name__ == '__main__':
    unittest.main()
