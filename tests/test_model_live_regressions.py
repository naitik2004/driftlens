from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from driftlens.model import Ollama
from examples.live_model import DEFAULT_CASE, run, verified
from .test_live_model_demo import ExtractedClaim


class ModelEvidenceTests(unittest.TestCase):
    def test_preserves_actual_validated_api_response(self):
        bundle = {'claim': {'quote': 'original'}, 'before': {'symbol': 'client.connect'}}
        verdict = {'quote': 'original', 'subject': 'client.connect', 'property': 'default',
                   'value': 30, 'before_verdict': 'supported', 'after_verdict': 'contradicted'}
        response = {'model': 'qwen2.5-coder:3b', 'done': True, 'eval_count': 42,
                    'message': {'content': json.dumps(verdict)}}
        model = Ollama()
        with patch('driftlens.model.urlopen', return_value=BytesIO(json.dumps(response).encode())):
            self.assertEqual(model.interpret(bundle), verdict)
        self.assertEqual(model.last_response, response)
        self.assertEqual(model.calls, 1)

    def test_controls_do_not_turn_abstention_or_stale_docs_into_drift(self):
        cases = json.loads((Path(__file__).parents[1] / 'examples/model-cases.json').read_text())
        for case in cases:
            if case['expected_findings'] != 0:
                continue
            with self.subTest(case=case['name']):
                result = run(ExtractedClaim(), case)
                self.assertEqual(result['status'], 'passed')
                changed = deepcopy(result['assisted'])
                changed['warnings'].append('unavailable model')
                self.assertFalse(verified(result['baseline'], changed, expected=0))

    def test_rejects_invalid_case_labels_and_inputs(self):
        for key, value in [('expected_findings', 2), ('expected_findings', True),
                           ('after_default', '10\nraise RuntimeError()'), ('before_docs', None)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                run(ExtractedClaim(), {**DEFAULT_CASE, key: value})

    def test_first_live_run_errors_cannot_become_findings(self):
        for mistake in ({'value': '30'},
                        {'before_verdict': 'contradicted', 'after_verdict': 'supported'}):
            with self.subTest(mistake=mistake):
                class MisinterpretedClaim(ExtractedClaim):
                    def interpret(self, bundle):
                        return {**super().interpret(bundle), **mistake}
                result = run(MisinterpretedClaim())
                self.assertEqual(result['status'], 'failed')
                self.assertFalse(result['assisted']['findings'])
                self.assertTrue(result['assisted']['abstentions'])
