import json
import unittest
from unittest.mock import patch
from driftlens.analyzer import analyze
from driftlens.cli import event_revisions, main
from driftlens.markdown import parse
from driftlens.model import ModelError, Ollama
from driftlens.reporting import annotations, summary
from .helpers import Repository


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.addCleanup(self.repo.close)

    def run_case(self, old, new, docs='`connect` timeout defaults to 30 seconds.', new_docs=None, extra=None):
        a = self.repo.commit({'client.py': old, 'docs/usage.md': docs, **(extra or {})})
        update = {'client.py': new}
        if new_docs is not None:
            update['docs/usage.md'] = new_docs
        b = self.repo.commit(update)
        return analyze(self.repo.path, a, b, 'https://github.com/example/driftlens')

    def test_default_evidence_and_offsets(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', '# API\n\nIntro. `connect` timeout defaults to 30 seconds. Next.\n')
        self.assertEqual(len(report['findings']), 1)
        finding = report['findings'][0]
        claim = finding['claim']
        doc = (self.repo.path / claim['path']).read_text()
        self.assertEqual(doc[claim['start']:claim['end']], claim['quote'])
        self.assertEqual(claim['quote'], '`connect` timeout defaults to 30 seconds.')
        self.assertIn(report['head_commit'], finding['links']['documentation'])
        self.assertIn('-def connect(timeout=30)', finding['hunks'][0]['text'])

    def test_corrected_docs(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', new_docs='`connect` timeout defaults to 10 seconds.')
        self.assertFalse(report['findings'])

    def test_preexisting_error(self):
        self.assertFalse(self.run_case('def connect(timeout=20): pass', 'def connect(timeout=10): pass')['findings'])

    def test_formatting_only(self):
        self.assertFalse(self.run_case('def connect(timeout=30): pass', 'def connect( timeout = 30 ):\n    pass\n')['findings'])

    def test_explicit_examples(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', '```python\nconnect(timeout=30)\n```\n\nFor example, `connect(timeout=30)`.')
        self.assertFalse(report['findings'])

    def test_qualifiers(self):
        for text in ('On Windows, `connect` timeout defaults to 30.', 'Previously `connect` timeout defaults to 30.', 'If enabled, `connect` timeout defaults to 30.'):
            with self.subTest(text=text):
                self.assertFalse(self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', text)['findings'])

    def test_dynamic_default(self):
        self.assertFalse(self.run_case('def connect(timeout=30): pass', 'def connect(timeout=get_timeout()): pass')['findings'])

    def test_decorator(self):
        self.assertFalse(self.run_case('@override\ndef connect(timeout=30): pass', '@override\ndef connect(timeout=10): pass')['findings'])

    def test_ambiguous_names(self):
        self.assertFalse(self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', extra={'other.py': 'def connect(timeout=30): pass'})['findings'])

    def test_qualified_symbol(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', '`client.connect` timeout defaults to 30.', extra={'other.py': 'def connect(timeout=30): pass'})
        self.assertEqual(len(report['findings']), 1)

    def test_removed_last_parameter(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(): pass', '`connect` accepts the `timeout` parameter.')
        self.assertEqual(len(report['findings']), 1)
        self.assertEqual(report['findings'][0]['category'], 'parameter_removed')

    def test_kwargs_compatibility(self):
        self.assertFalse(self.run_case('def connect(timeout=30): pass', 'def connect(**kwargs): pass', '`connect` accepts the `timeout` parameter.')['findings'])

    def test_whole_function_alias(self):
        self.assertFalse(self.run_case('def connect(timeout=30): pass', 'def open_connection(timeout=10): pass\nconnect = open_connection', '`connect` accepts the `timeout` parameter.')['findings'])

    def test_table(self):
        docs = '# connect\n\n| Parameter | Default | Description |\n|---|---|---|\n| timeout | 30 | Timeout in seconds |\n'
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', docs)
        self.assertEqual(len(report['findings']), 1)
        self.assertEqual(report['findings'][0]['claim']['columns'], ('Parameter', 'Default', 'Description'))

    def test_grouping_and_stable_ids(self):
        docs = '`connect` timeout defaults to 30.\n\n`connect` timeout defaults to 30.'
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass', docs)
        repeated = analyze(self.repo.path, report['base_commit'], report['head_commit'])
        self.assertEqual(report['metrics']['change_groups'], 1)
        self.assertEqual(len(report['findings']), 2)
        self.assertEqual([f['id'] for f in report['findings']], [f['id'] for f in repeated['findings']])

    def test_imported_constant_hunk(self):
        a = self.repo.commit({'client.py': 'from settings import TIMEOUT\ndef connect(timeout=TIMEOUT): pass', 'settings.py': 'TIMEOUT = 30', 'docs.md': '`connect` timeout defaults to 30.'})
        b = self.repo.commit({'settings.py': 'TIMEOUT = 10'})
        report = analyze(self.repo.path, a, b)
        self.assertEqual(len(report['findings']), 1)
        self.assertEqual(report['findings'][0]['hunks'][0]['new_path'], 'settings.py')

    def test_cli_aliases(self):
        old = 'import argparse\np = argparse.ArgumentParser()\np.add_argument("--timeout", "-t", default=30)\np.add_argument("--verbose", action="store_true")'
        report = self.run_case(old, old.replace('"--timeout", ', ''), 'The CLI supports `--timeout`.\n\nThe CLI supports `-t`.')
        self.assertEqual(len(report['findings']), 1)
        self.assertEqual(report['findings'][0]['before']['name'], '--timeout')

    def test_cli_default(self):
        old = 'import argparse\np = argparse.ArgumentParser()\np.add_argument("--timeout", default=30)'
        self.assertEqual(len(self.run_case(old, old.replace('30', '10'), '`--timeout` defaults to 30.')['findings']), 1)

    def test_cli_override(self):
        old = 'import argparse\np = argparse.ArgumentParser()\np.add_argument("--timeout", default=30)\np.set_defaults(timeout=60)'
        self.assertFalse(self.run_case(old, old.replace('default=30', 'default=10'), '`--timeout` defaults to 30.')['findings'])

    def test_syntax_warning(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(', '`connect` accepts timeout.')
        self.assertFalse(report['findings'])
        self.assertTrue(report['warnings'])

    def test_retry_pattern(self):
        old = 'def connect():\n    for attempt in range(4):\n        try:\n            return send()\n        except ConnectionError:\n            pass\n    raise ConnectionError()\n'
        report = self.run_case(old, old.replace('range(4)', 'range(2)'), '`connect` performs up to 3 automatic retries on ConnectionError.')
        self.assertEqual(len(report['findings']), 1)
        self.assertEqual(report['findings'][0]['category'], 'retry_limit_changed')

    def test_dirty_worktree(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass')
        (self.repo.path / 'client.py').write_text('raise RuntimeError("must not execute")')
        self.assertEqual(len(analyze(self.repo.path, report['base_commit'], report['head_commit'])['findings']), 1)

    def test_never_execute_code(self):
        marker = self.repo.path / 'executed'
        prefix = f'open({str(marker)!r}, "w").write("bad")\n'
        self.run_case(prefix + 'def connect(timeout=30): pass', prefix + 'def connect(timeout=10): pass')
        self.assertFalse(marker.exists())

    def test_merge_base(self):
        a = self.repo.commit({'client.py': 'def connect(timeout=30): pass', 'docs.md': '`connect` timeout defaults to 30.'})
        branch = self.repo.git('branch', '--show-current')
        self.repo.git('checkout', '-qb', 'feature')
        b = self.repo.commit({'client.py': 'def connect(timeout=10): pass'})
        self.repo.git('checkout', branch)
        target = self.repo.commit({'docs.md': 'Changed only on target.'})
        report = analyze(self.repo.path, target, b)
        self.assertEqual(report['base_commit'], a)
        self.assertEqual(len(report['findings']), 1)

    def test_cli_exit_and_artifacts(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass')
        path = self.repo.path / 'report.json'
        args = ['--repo', str(self.repo.path), '--base', report['base_commit'], '--json', str(path), '--summary', str(self.repo.path / 'summary.md')]
        self.assertEqual(main(args), 0)
        self.assertEqual(main(args + ['--fail-on-drift']), 1)
        self.assertEqual(len(json.loads(path.read_text())['findings']), 1)

    def test_pr_head(self):
        path = self.repo.path / 'event.json'
        path.write_text(json.dumps({'pull_request': {'base': {'sha': 'base'}, 'head': {'sha': 'actual-head'}}}))
        self.assertEqual(event_revisions(path), ('base', 'actual-head'))

    def test_unicode_offsets(self):
        source = '# API\n\nCafé. `connect` timeout defaults to 30.\n'
        for claim in parse('docs.md', source):
            self.assertEqual(source[claim.start:claim.end], claim.quote)
        self.assertEqual(parse('docs.md', source)[1].line_start, 3)

    def test_fabricated_model_evidence(self):
        bundle = {'claim': {'quote': 'original'}, 'before': {'symbol': 'client.connect'}}
        output = {'quote': 'fabricated', 'subject': 'client.connect', 'property': 'default', 'value': 30, 'before_verdict': 'supported', 'after_verdict': 'contradicted'}
        with self.assertRaises(ModelError):
            Ollama.validate(output, bundle)

    def test_local_model_endpoint(self):
        with self.assertRaises(ModelError):
            Ollama(url='https://remote.example')

    def test_model_failure_advisory(self):
        a = self.repo.commit({'client.py': 'def connect(timeout=30): pass', 'docs.md': '`connect`: the default timeout equals 30.'})
        b = self.repo.commit({'client.py': 'def connect(timeout=10): pass'})
        model = Ollama()
        with patch.object(model, 'interpret', side_effect=ModelError('offline')):
            report = analyze(self.repo.path, a, b, model=model)
        self.assertFalse(report['findings'])
        self.assertIn('offline', report['warnings'])

    def test_annotation_escape(self):
        report = self.run_case('def connect(timeout=30): pass', 'def connect(timeout=10): pass')
        report['findings'][0]['claim']['path'] = 'a,b\n::error.md'
        annotation = next(annotations(report))
        self.assertIn('a%2Cb%0A%3A%3Aerror.md', annotation)
        self.assertEqual(len(annotation.splitlines()), 1)
        self.assertIn('Responsible change', summary(report))
