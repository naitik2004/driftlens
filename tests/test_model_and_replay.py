from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from driftlens.analyzer import analyze
from driftlens.evaluate import evaluate
from driftlens.model import ModelError, Ollama
from .helpers import Repository


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.bundle = {'claim': {'quote': '`connect`: the default timeout equals 30.'},
                       'before': {'symbol': 'client.connect'}}
        self.verdict = {'quote': self.bundle['claim']['quote'], 'subject': 'client.connect',
                        'property': 'default', 'value': 30, 'before_verdict': 'supported',
                        'after_verdict': 'contradicted'}

    def test_schema_and_digest_cache(self):
        calls = []
        digest = ['digest-one']
        def request(url, timeout):
            calls.append(url)
            if isinstance(url, str):
                return BytesIO(json.dumps({'models': [{'name': 'qwen2.5-coder:3b', 'digest': digest[0]}]}).encode())
            body = json.loads(url.data)
            self.assertEqual(body['model'], 'qwen2.5-coder:3b')
            self.assertFalse(body['stream'])
            self.assertIn('UNTRUSTED', body['messages'][0]['content'])
            return BytesIO(json.dumps({'message': {'content': json.dumps(self.verdict)}}).encode())
        with tempfile.TemporaryDirectory() as tmp, patch('driftlens.model.urlopen', side_effect=request):
            model = Ollama(cache=tmp)
            self.assertEqual(model.interpret(self.bundle), self.verdict)
            self.assertEqual(model.interpret(self.bundle), self.verdict)
            self.assertEqual(model.calls, 1)
            self.assertEqual(model.cache_hits, 1)
            digest[0] = 'digest-two'
            model.interpret(self.bundle)
            self.assertEqual(model.calls, 2)
            self.bundle['head_commit'] = 'different-head'
            model.interpret(self.bundle)
            self.assertEqual(model.calls, 3)

    def test_invalid_response_types(self):
        for key, value in [('before_verdict', []), ('value', float('nan')), ('quote', 'invented'), ('property', 'behavior')]:
            with self.subTest(key=key), self.assertRaises(ModelError):
                Ollama.validate({**self.verdict, key: value}, self.bundle)

    def test_model_claim_still_needs_static_support(self):
        repo = Repository()
        self.addCleanup(repo.close)
        a = repo.commit({'client.py': 'def connect(timeout=30): pass', 'docs.md': self.bundle['claim']['quote']})
        b = repo.commit({'client.py': 'def connect(timeout=10): pass'})
        model = Ollama()
        with patch.object(model, 'interpret', return_value=self.verdict):
            self.assertEqual(len(analyze(repo.path, a, b, model=model)['findings']), 1)
        with patch.object(model, 'interpret', return_value={**self.verdict, 'value': 99}):
            self.assertFalse(analyze(repo.path, a, b, model=model)['findings'])


class ReplayTests(unittest.TestCase):
    def test_c_only_loaded_after_analysis(self):
        repo = Repository()
        self.addCleanup(repo.close)
        a = repo.commit({'client.py': 'def connect(timeout=30): pass', 'docs.md': '`connect` timeout defaults to 30.'})
        b = repo.commit({'client.py': 'def connect(timeout=10): pass'})
        c = repo.commit({'docs.md': '`connect` timeout defaults to 10.'})
        case = {'id': 'known', 'repo': str(repo.path), 'before': a, 'drift': b, 'correction': c,
                'expected': [{'path': 'docs.md', 'symbol': 'client.connect', 'category': 'parameter_default_changed'}]}
        calls = []
        from driftlens import evaluate as module
        real_analyze, real_snapshot = module.analyze, module.snapshot
        def tracked_analyze(*args, **kwargs):
            calls.append('analyze')
            self.assertEqual(args[1:], (a, b))
            return real_analyze(*args, **kwargs)
        def tracked_snapshot(*args, **kwargs):
            calls.append('correction')
            return real_snapshot(*args, **kwargs)
        with patch.object(module, 'analyze', side_effect=tracked_analyze), patch.object(module, 'snapshot', side_effect=tracked_snapshot):
            result = evaluate({'cases': [case]}, Path('.'))
        self.assertEqual(calls, ['analyze', 'correction'])
        self.assertEqual(result['known_case_recall'], 1)
        self.assertIsNone(result['cases'][0]['precision'])
        self.assertFalse(result['cases'][0]['correction_evidence'][0]['old_quote_still_present'])

    def test_split_leakage_rejected(self):
        cases = [{'repo': '.', 'split': 'development'}, {'repo': '.', 'split': 'evaluation'}]
        with self.assertRaises(ValueError):
            evaluate({'cases': cases}, Path('.'))
