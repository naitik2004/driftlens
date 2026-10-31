"""Advisory summaries and workflow annotations; no network writes."""
import html
import json


def safe(text):
    return html.escape(str(text)).replace('`', '&#96;')


def summary(report):
    lines = ['# DriftLens', '', f"**{len(report['findings'])} finding(s)** across {report['metrics']['change_groups']} code change(s). Advisory analysis.", '', f"Base: `{report['base_commit']}`  ", f"Head: `{report['head_commit']}`", '']
    groups = {}
    for finding in report['findings']:
        groups.setdefault(finding['group_id'], []).append(finding)
    for findings in groups.values():
        lines += [f"## {safe(findings[0]['explanation'])}", '']
        for finding in findings:
            claim = finding['claim']
            location = f"{safe(claim['path'])}:{claim['line_start']}-{claim['line_end']}"
            link = finding['links']['documentation']
            lines += [f'**{location}**' + (f' ([source]({link}))' if link else ''), '', '<blockquote>' + safe(claim['quote']).replace('\n', '<br>') + '</blockquote>', '', f"Character offsets: {claim['start']}–{claim['end']} (end exclusive).", '', safe(finding['suggested_correction']), '', f"Evidence: {safe(finding['evidence_strength'])}.", '']
            for label in ('before', 'after'):
                if finding['links'][label]:
                    lines += [f"[{label.title()} code]({finding['links'][label]})", '']
            for hunk in finding['hunks']:
                lines += ['<details><summary>Responsible change</summary>', '', '<pre>' + safe(hunk['text']) + '</pre>', '', '</details>', '']
    if not report['findings']:
        lines += ['No new drift established within the supported analysis scope.', '']
    lines += [f"Abstentions: {len(report['abstentions'])}. Runtime: {report['metrics']['runtime_seconds']:.3f}s.", '']
    lines += [f'- Warning: {safe(w)}' for w in report['warnings']]
    lines += ['', '## Scope and limitations', '']
    lines += [f'- {safe(item)}' for item in report['limitations']]
    return '\n'.join(lines) + '\n'


def escape_command(text, property=False):
    text = str(text).replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    return text.replace(':', '%3A').replace(',', '%2C') if property else text


def annotations(report):
    for finding in report['findings'][:50]:
        claim = finding['claim']
        yield f"::warning file={escape_command(claim['path'], True)},line={claim['line_start']},endLine={claim['line_end']},title=DriftLens::{escape_command(finding['explanation'])}"


def write_json(report, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
