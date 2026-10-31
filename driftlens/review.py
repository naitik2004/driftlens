"""Source-backed review candidates, kept separate from established drift.

Retrieval is deliberately not verification. In particular a removed client guard
does not prove a new remote-service limit, and changed flags do not prove an
example's behavior. Nothing here executes analyzed source or reads future C.
"""
import ast
import re

from .facts import module_name
from .markdown import qualified


def nodes(files):
    for path, source in files.items():
        if not path.endswith('.py'):
            continue
        try:
            yield path, source, ast.parse(source)
        except (SyntaxError, ValueError, RecursionError):
            continue


def location(path, node, source):
    lines = source.splitlines(keepends=True)[node.lineno - 1:node.end_lineno]
    text = ''.join(lines).rstrip('\r\n')
    if len(lines) > 80 or len(text) > 6000:
        return None
    return {'path': path, 'line': node.lineno, 'end_line': node.end_lineno,
            'quote': text}


def candidate_claims(comparison, old_claims, new_claims):
    old = {(c.path, c.heading, c.quote, c.kind, c.columns) for c in old_claims}
    return [c for c in new_claims if c.kind == 'sentence' and not qualified(c)
            and (comparison.renames.get(c.path, c.path), c.heading, c.quote, c.kind, c.columns) in old]


def collect_candidates(comparison, before_facts, after_facts, old_claims, new_claims):
    claims = candidate_claims(comparison, old_claims, new_claims)
    candidates = []
    after_index = {f.key(): f for f in after_facts}
    flags = []
    for before in before_facts:
        after = after_index.get(before.key())
        if (before.kind == 'flag' and after and before.value.get('action') == 'store_true'
                and before.value.get('default') is True and after.value.get('default') is False):
            flags.append((before, after))
    destinations = {(f.path, f.symbol, f.value.get('dest')) for pair in flags for f in pair}
    changed_aliases = {alias for f in before_facts + after_facts if f.kind == 'flag'
                       and (f.path, f.symbol, f.value.get('dest')) in destinations
                       for alias in f.value.get('aliases', [])}
    for claim in claims:
        # A merge example is a retrieval hint, never a default assertion.
        commands = re.findall(r'`([^`\n]+)`', claim.quote)
        if not re.search(r'\b(?:merge|combine)\b', claim.quote, re.I):
            continue
        relevant = []
        for before, after in flags:
            terms = set(re.findall(r'[a-z]+', before.name.lower())) - {'no', 'allow', 'enable', 'multiple', 'streams', 'multistreams'}
            for command in commands:
                if (command.count('+') >= 2 and any(term in command.lower() for term in terms)
                        and not any(re.search(r'(?<!\S)' + re.escape(alias) + r'(?:=|(?=\s|$))', command) for alias in changed_aliases)):
                    relevant.append({'before': before.json(), 'after': after.json(),
                                     'default_resolved': before.resolved and after.resolved})
                    break
        if relevant:
            evidence = []
            for change in relevant:
                for side, snapshot in (('before', comparison.base), ('after', comparison.head)):
                    fact = change[side]
                    text = ''.join(snapshot.files[fact['path']].splitlines(keepends=True)[fact['line'] - 1:fact['end_line']]).rstrip('\r\n')
                    if len(text) <= 6000 and fact['end_line'] - fact['line'] < 80:
                        evidence.append({'revision': 'base' if side == 'before' else 'head',
                                         'path': fact['path'], 'line': fact['line'], 'end_line': fact['end_line'],
                                         'quote': text})
            candidates.append({'status': 'needs_review', 'kind': 'merge_example_after_flag_change',
                               'claim': claim.json(), 'changes': relevant,
                               'reason': 'Opt-in defaults changed while this merge example remains. Stream-selection behavior and CLI forwarding require verification; the example alone does not assert a default.',
                               'evidence': evidence, 'limitations': ['Not an established contradiction; unresolved parser construction, aliases or runtime dependencies may preserve the example.']})
            if len(candidates) >= 50:
                return candidates

    new_trees = {p: (s, t) for p, s, t in nodes(comparison.head.files)}
    for path, source, tree in nodes(comparison.base.files):
        target = next((p for p, old in comparison.renames.items() if old == path), path)
        if target not in new_trees:
            continue
        new_source, new_tree = new_trees[target]
        old_functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        new_functions = {n.name: n for n in new_tree.body if isinstance(n, ast.FunctionDef)}
        for statement in tree.body:
            if not (isinstance(statement, ast.Assign) and len(statement.targets) == 1
                    and isinstance(statement.targets[0], ast.Name)
                    and re.search(r'(?:MAX|LIMIT|CAP)', statement.targets[0].id)
                    and isinstance(statement.value, ast.Constant)
                    and type(statement.value.value) is int and statement.value.value > 0):
                continue
            name, value = statement.targets[0].id, statement.value.value
            if any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(new_tree)):
                continue
            guards = [(fn, n) for fn in old_functions.values() for n in ast.walk(fn)
                      if isinstance(n, ast.Compare)
                      and any(isinstance(a, ast.Name) and a.id == name for a in ast.walk(n))
                      and any(isinstance(a, ast.Call) and isinstance(a.func, ast.Name)
                              and a.func.id == 'len' for a in ast.walk(n))]
            if not guards:
                continue
            # A renamed, inlined or moved same-module guard is not a removal.
            constants = {n.targets[0].id: n.value.value for n in new_tree.body
                         if isinstance(n, ast.Assign) and len(n.targets) == 1
                         and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant)}
            if any(isinstance(n, ast.Compare)
                   and any(isinstance(a, ast.Call) and isinstance(a.func, ast.Name) and a.func.id == 'len' for a in ast.walk(n))
                   and any((isinstance(a, ast.Constant) and type(a.value) is int and a.value == value)
                           or (isinstance(a, ast.Name) and type(constants.get(a.id)) is int and constants[a.id] == value)
                           for a in ast.walk(n)) for n in ast.walk(new_tree)):
                continue
            for claim in claims:
                match = re.search(r'\b(?:up to|at most|maximum of)\s+(\d+)\s+(\w+)\s+per\s+(\w+)', claim.quote, re.I)
                if not match or int(match[1]) != value:
                    continue
                container = match[3].lower().rstrip('s')
                owners = [fn for fn in old_functions.values() if not fn.name.startswith('_')
                          and container in fn.name.lower() and fn.name in new_functions
                          and any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                                  and n.func.id in {guard_fn.name for guard_fn, _ in guards}
                                  for n in ast.walk(fn))]
                if len(owners) != 1:
                    continue
                owner = owners[0]
                evidence = []
                replacements = [n for n in ast.walk(new_functions[owner.name])
                                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                                and n.func.id in {fn.name for fn, _ in guards}]
                replacement_helpers = [new_functions[fn.name] for fn, _ in guards if fn.name in new_functions]
                for revision, source_path, node, content in (
                        [('base', path, statement, source)]
                        + [('base', path, guard, source) for _, guard in guards]
                        + [('head', target, node, new_source) for node in replacements + replacement_helpers]):
                    excerpt = location(source_path, node, content)
                    if excerpt:
                        evidence.append(dict(revision=revision, **excerpt))
                candidates.append({'status': 'needs_review', 'kind': 'removed_numeric_guard',
                                   'claim': claim.json(), 'symbol': module_name(path) + '.' + owner.name,
                                   'before_limit': value,
                                   'reason': 'A referenced numeric client guard disappeared while this limit claim remains. The replacement implementation and external service may impose another bound; no unlimited-service claim is established.',
                                   'changes': [],
                                   'evidence': evidence,
                                   'limitations': ['Retrieval candidate only; absence of this guard does not prove a new effective bound.']})
                if len(candidates) >= 50:
                    return candidates
    return candidates
