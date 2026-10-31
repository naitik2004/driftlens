"""Harness tests use an injected model; these are not live inference evidence."""
from copy import deepcopy
import unittest

from examples.live_model import run, verified


class ExtractedClaim:
    model = 'test-double-not-a-real-model'
    calls = 0
    cache_hits = 0

    def interpret(self, bundle):
        self.calls += 1
        return {'quote': bundle['claim']['quote'], 'subject': bundle['before']['symbol'],
                'property': 'default', 'value': 30, 'before_verdict': 'supported',
                'after_verdict': 'contradicted'}


class LiveDemoTests(unittest.TestCase):
    def test_fixture_requires_model_and_checks_actual_contribution(self):
        result = run(ExtractedClaim())
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['baseline']['metrics']['finding_count'], 0)
        assisted = result['assisted']
        self.assertEqual(assisted['metrics']['model_calls'], 1)
        for mutate in (
            lambda r: r['metrics'].update(model_calls=0),
            lambda r: r['warnings'].append('Model unavailable'),
            lambda r: r['findings'][0].update(evidence_strength='deterministic'),
            lambda r: r['findings'][0]['before'].update(symbol='unrelated.connect'),
            lambda r: r['findings'].clear(),
        ):
            with self.subTest(mutation=mutate):
                changed = deepcopy(assisted)
                mutate(changed)
                self.assertFalse(verified(result['baseline'], changed))


if __name__ == '__main__':
    unittest.main()
