import copy
import json
import unittest
from unittest.mock import patch

from driftlens.model import ModelError, Ollama
from driftlens.review_model import review, validate
from . import test_behavior_review as fixtures


class BehavioralModelTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {'kind': 'removed_numeric_guard', 'claim': {'quote': 'Up to 17 files per folder.'},
                          'reason': 'A guard changed.', 'changes': [], 'limitations': ['Effective bound unresolved.'],
                          'evidence': [{'revision': 'base', 'path': 'client.py', 'line': 4, 'end_line': 5,
                                        'quote': 'MAX_ITEMS = 17\nif len(items) == MAX_ITEMS:'}]}
        self.verdict = {'quote': self.candidate['claim']['quote'], 'assessment': 'review_required',
                        'reason': 'A numeric guard changed; the new effective bound needs review.',
                        'suggested_action': 'Check the replacement parser and service constraints.',
                        'citations': [{'revision': 'base', 'path': 'client.py', 'line': 4, 'quote': 'MAX_ITEMS = 17'}]}

    def test_validates_actual_citation_and_matching_line(self):
        validate(self.verdict, self.candidate)
        for mutation in ({'line': 5}, {'path': 'invented.py'}, {'revision': 'head'},
                         {'quote': ''}, {'quote': 'MAX_ITEMS = 99'}, {'line': True}):
            output = copy.deepcopy(self.verdict)
            output['citations'][0].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ModelError):
                validate(output, self.candidate)

    def test_rejects_changed_claim_and_false_verified_verdict(self):
        for mutation in ({'quote': 'Different claim'}, {'assessment': 'contradicted'},
                         {'citations': []}, {'confidence': 0.99}, {'reason': 'a' * 1201}):
            output = dict(self.verdict, **mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ModelError):
                validate(output, self.candidate)

    def test_transport_counts_request_and_preserves_unverified_status(self):
        body = {'done': True, 'model': 'test-double', 'message': {'content': json.dumps(self.verdict)}}
        with patch('driftlens.review_model.urlopen') as opener:
            opener.return_value.__enter__.return_value.read.return_value = json.dumps(body).encode()
            model = Ollama()
            output = review(model, self.candidate)
        self.assertEqual(model.calls, 1)
        self.assertEqual(output['assessment'], 'review_required')
        self.assertIn('unverified', output['verification'])
        self.assertEqual(model.last_response, body)

    def test_citation_can_start_inside_its_real_line_but_not_on_another(self):
        output = copy.deepcopy(self.verdict)
        output['citations'][0].update(line=5, quote='len(items) == MAX_ITEMS')
        validate(output, self.candidate)
        output['citations'][0]['line'] = 4
        with self.assertRaises(ModelError):
            validate(output, self.candidate)

    def test_model_notes_never_promote_candidate_to_a_finding(self):
        from driftlens.analyzer import analyze
        fixture = fixtures.BehavioralReviewTests(methodName='test_removed_guard_surfaces_evidence_without_claiming_a_new_bound')
        try:
            repo, a, b, _ = fixture.compare()
            class Model:
                calls, cache_hits = 0, 0
                def review(self, candidate):
                    self.calls += 1
                    return {'model': 'test-double', 'assessment': 'review_required',
                            'reason': 'Unverified test-double notes', 'suggested_action': 'Inspect the code'}
            report = analyze(repo.path, a, b, model=Model(), review_candidates=True)
            self.assertEqual(report['findings'], [])
            self.assertEqual(report['metrics']['model_calls'], 1)
            self.assertEqual(report['review_candidates'][0]['model_review']['assessment'], 'review_required')
        finally:
            fixture.doCleanups()

    def test_oversized_model_bundle_is_rejected_without_a_request(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['evidence'][0]['quote'] = 'x' * 15000
        model = Ollama()
        with patch('driftlens.review_model.urlopen') as opener, self.assertRaises(ModelError):
            review(model, candidate)
        opener.assert_not_called()
        self.assertEqual(model.calls, 0)


if __name__ == '__main__':
    unittest.main()
