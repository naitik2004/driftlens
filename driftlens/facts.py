"""Conservative AST facts and a bounded, two-hop constant resolver."""
import ast
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath

UNKNOWN = {"unknown": True}


@dataclass
class Fact:
    path: str
    symbol: str
    kind: str
    name: str
    value: object
    line: int
    end_line: int
    resolved: bool = True
    dependencies: tuple = ()

    def key(self):
        return self.path, self.symbol, self.kind, self.name

    def json(self):
        return asdict(self)


def module_name(path):
    parts = list(PurePosixPath(path).with_suffix("").parts)
    if parts and parts[0] == "src":
        parts.pop(0)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def bindings(tree):
    """Conservative binding inventory, including bindings without Name stores."""
    counts = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            counts[node.id] += 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            counts[node.name] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                counts[alias.asname or (alias.name.split('.')[0] if isinstance(node, ast.Import) else alias.name)] += 1
        elif isinstance(node, ast.arg):
            counts[node.arg] += 1
        elif isinstance(node, ast.ExceptHandler) and node.name:
            counts[node.name] += 1
    return counts


def uncertain_parser_use(tree, names, registrations, direct_body, allow_return=False):
    """Unknown registrations, aliases and escapes cannot prove option absence."""
    if not names:
        return False
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    direct_calls = {s.value for s in direct_body if isinstance(s, ast.Expr)}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or node.id not in names or not isinstance(node.ctx, ast.Load):
            continue
        parent = parents.get(node)
        if allow_return and isinstance(parent, ast.Return):
            continue
        if not isinstance(parent, ast.Attribute) or not isinstance(parent.ctx, ast.Load):
            return True
        call = parents.get(parent)
        if not isinstance(call, ast.Call) or call.func is not parent:
            return True
        if parent.attr in registrations and call not in direct_calls:
            return True
        if parent.attr not in registrations | {'parse_args', 'parse_known_args', 'print_help', 'format_help'}:
            return True
    return False


def imported_names(tree, module, member):
    names = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and not node.level and node.module == module:
            names.update(a.asname or a.name for a in node.names if a.name == member)
        elif isinstance(node, ast.Import):
            names.update((a.asname or a.name) + '.' + member for a in node.names if a.name == module)
    if not names:
        return set()
    counts = bindings(tree)
    mutated = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del)):
            root = node.value
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name):
                mutated.add(root.id)
    return {name for name in names if counts[name.split('.')[0]] == 1
            and name.split('.')[0] not in mutated and not counts['*']}


def local_class(tree, name):
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == name]
    if len(classes) != 1 or classes[0] not in tree.body or classes[0].keywords:
        return None
    if sum(isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name for n in ast.walk(tree)) != 1:
        return None
    if any(isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, (ast.Store, ast.Del)) for n in ast.walk(tree)):
        return None
    if any(isinstance(n, ast.alias) and (n.asname or n.name.split('.')[0]) == name for n in ast.walk(tree)):
        return None
    for member in classes[0].body:
        if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in member.decorator_list:
            if not isinstance(decorator, ast.Name) or decorator.id not in ('classmethod', 'staticmethod'):
                return None
            if any((isinstance(n, ast.Name) and n.id == decorator.id and isinstance(n.ctx, (ast.Store, ast.Del)))
                   or (isinstance(n, ast.alias) and (n.asname or n.name) == decorator.id)
                   or (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == decorator.id) for n in ast.walk(tree)):
                return None
    return classes[0]


def slug(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).replace('_', '-').lower()


class Extractor:
    def __init__(self, files):
        self.trees, self.errors, self.constants, self.imports = {}, [], {}, {}
        self.modules = {module_name(p): p for p in files if p.endswith(".py")}
        for path, source in files.items():
            if not path.endswith(".py"):
                continue
            try:
                tree = ast.parse(source)
            except (SyntaxError, ValueError) as exc:
                self.errors.append(f"{path}: {exc}")
                continue
            self.trees[path] = tree
            assignments, imports = {}, {}
            for node in tree.body:
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for target in targets:
                        if isinstance(target, ast.Name):
                            assignments.setdefault(target.id, []).append(node)
                elif isinstance(node, ast.ImportFrom):
                    package = module_name(path).split(".")
                    if not path.endswith("__init__.py"):
                        package = package[:-1]
                    prefix = package[:len(package) - node.level + 1] if node.level else []
                    module = ".".join(prefix + ([node.module] if node.module else []))
                    for alias in node.names:
                        imports[alias.asname or alias.name] = (self.modules.get(module), alias.name)
            stores = bindings(tree)
            self.constants[path] = {k: v[0] for k, v in assignments.items() if len(v) == 1 and stores.get(k) == 1}
            self.imports[path] = {k: v for k, v in imports.items() if stores[k] == 1}

    def value(self, path, node, hops=0, seen=()):
        if node is None:
            return UNKNOWN, ()
        try:
            value = ast.literal_eval(node)
            if type(value) in (str, int, float, bool, type(None)) and not (type(value) == float and not math.isfinite(value)):
                return value, ()
        except (ValueError, TypeError, SyntaxError):
            pass
        if isinstance(node, ast.Name) and hops <= 2 and (path, node.id) not in seen:
            seen = (*seen, (path, node.id))
            target = self.constants.get(path, {}).get(node.id)
            if target is not None:
                value, deps = self.value(path, target.value, hops + 1, seen)
                return value, ((path, target.lineno), *deps)
            imported = self.imports.get(path, {}).get(node.id)
            if imported and imported[0] and hops < 2:
                value, deps = self.value(imported[0], ast.Name(id=imported[1]), hops + 1, seen)
                return value, deps
        return UNKNOWN, ()

    def extract(self):
        facts = []
        for path, tree in self.trees.items():
            module = module_name(path)
            # Avoid claiming runtime facts for monkey-patched/reassigned names.
            counts = bindings(tree)
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                    symbol = f"{module}.{node.name}"
                    safe = not node.decorator_list and counts.get(node.name) == 1 and sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == node.name for n in ast.walk(tree)) == 1
                    # Conditional rebindings or mutations of function defaults
                    # invalidate an otherwise simple top-level definition.
                    for other in ast.walk(tree):
                        if isinstance(other, ast.Name) and other.id == node.name and isinstance(other.ctx, (ast.Store, ast.Del)):
                            safe = False
                        if isinstance(other, ast.Attribute) and isinstance(other.value, ast.Name) and other.value.id == node.name and isinstance(other.ctx, (ast.Store, ast.Del)):
                            safe = False
                    facts.append(Fact(path, symbol, "owner", "function", {"kwargs": node.args.kwarg is not None}, node.lineno, node.end_lineno, safe))
                    args = node.args
                    positional = args.posonlyargs + args.args
                    defaults = [None] * (len(positional) - len(args.defaults)) + args.defaults
                    parameters = list(zip(positional, defaults)) + list(zip(args.kwonlyargs, args.kw_defaults))
                    for arg, default in parameters:
                        value, deps = self.value(path, default)
                        if any(p == path and line >= node.lineno for p, line in deps):
                            value = UNKNOWN
                        facts.append(Fact(path, symbol, "parameter", arg.arg,
                                          {"default": value, "has_default": default is not None,
                                           "kwargs": args.kwarg is not None},
                                          node.lineno, node.end_lineno,
                                          safe and not any(isinstance(n, ast.Name) and n.id == arg.arg and isinstance(n.ctx, (ast.Store, ast.Del)) for n in ast.walk(node)), deps))
                    retries = self.retry_count(path, node)
                    if retries is not None:
                        facts.append(Fact(path, symbol, "retries", "retries", retries, node.lineno, node.end_lineno, safe))
                    pattern = self.cache_pattern(path, node) if safe else None
                    if pattern:
                        facts.append(pattern)
            # Recognize only direct argparse.ArgumentParser instances. Attribute
            # calls on arbitrary objects do not establish public CLI flags.
            parsers = set()
            constructors = imported_names(tree, 'argparse', 'ArgumentParser') if 'argparse' not in self.modules else set()
            for node in tree.body:
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and ast.unparse(node.value.func) in constructors:
                    parsers.update(t.id for t in node.targets if isinstance(t, ast.Name))
            unsafe_parser = any(isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                                and ast.unparse(n.value.func) in constructors and
                                any(k.arg in (None, "parents", "conflict_handler", "argument_default") for k in n.value.keywords)
                                for n in tree.body)
            unsafe_parser = unsafe_parser or any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                and isinstance(n.func.value, ast.Name) and n.func.value.id in parsers
                                and n.func.attr in ("set_defaults", "add_subparsers", "add_argument_group", "add_mutually_exclusive_group")
                                for n in ast.walk(tree))
            binding_counts = bindings(tree)
            unsafe_parser = unsafe_parser or any(binding_counts[name] != 1 for name in parsers)
            unsafe_parser = unsafe_parser or uncertain_parser_use(tree, parsers, {'add_argument'}, tree.body)
            for parser in parsers:
                definitions = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == parser for t in n.targets)]
                owner = definitions[0]
                facts.append(Fact(path, f"{module}.{parser}", "owner", "parser", {}, owner.lineno, owner.end_lineno, not unsafe_parser and len(definitions) == 1))
            for stmt in tree.body:
                node = stmt.value if isinstance(stmt, ast.Expr) else None
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name) and node.func.value.id in parsers
                        and node.func.attr == "add_argument"):
                    continue
                flags = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.startswith("-")]
                kwargs = {k.arg: k.value for k in node.keywords}
                value, deps = self.value(path, kwargs.get("default"))
                for flag in flags:
                    facts.append(Fact(path, f"{module}.{node.func.value.id}", "flag", flag,
                                      {"default": value, "aliases": sorted(flags)}, stmt.lineno, stmt.end_lineno,
                                      not unsafe_parser and None not in kwargs, deps))
            facts.extend(self.optparse_facts(path, tree, module))
        return facts

    def cache_pattern(self, path, function):
        """Bound a declared numeric filename against a local literal dot-join.

        Values are not evaluated: a join of N items has at least N-1 separators.
        """
        tree = self.trees[path]
        if any(name in self.modules for name in ('pathlib', 'enum', 'dataclasses', 'attr')):
            return None
        body = [n for n in function.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                                                and isinstance(n.value.value, str))]
        if len(body) != 1 or not isinstance(body[0], ast.Return):
            return None
        expression = body[0].value
        if not (isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Div)
                and isinstance(expression.left, ast.Name) and isinstance(expression.right, ast.JoinedStr)):
            return None
        base = self.constants[path].get(expression.left.id)
        if not (base and isinstance(base.value, ast.Call)
                and ast.unparse(base.value.func) in imported_names(tree, 'pathlib', 'Path')):
            return None
        pieces = expression.right.values
        if not (len(pieces) in (3, 5) and isinstance(pieces[0], ast.Constant) and isinstance(pieces[-1], ast.Constant)
                and isinstance(pieces[0].value, str) and isinstance(pieces[-1].value, str)
                and re.fullmatch(r'[\w-]+\.', pieces[0].value) and re.fullmatch(r'\.[\w-]+', pieces[-1].value)):
            return None
        fields = [p for p in pieces if isinstance(p, ast.FormattedValue)]
        if any(p.conversion != -1 or p.format_spec is not None for p in fields):
            return None
        annotations = {a.arg: a.annotation for a in function.args.posonlyargs + function.args.args + function.args.kwonlyargs}
        value = {'prefix': pieces[0].value, 'suffix': pieces[-1].value, 'base_expression': ast.unparse(base.value)}
        dependencies = ()
        if len(pieces) == 5:
            if not (len(fields) == 2 and isinstance(pieces[2], ast.Constant) and pieces[2].value == '.'):
                return None
            number, enum = fields[0].value, fields[1].value
            if not (isinstance(number, ast.Name) and isinstance(annotations.get(number.id), ast.Name)
                    and annotations[number.id].id == 'int' and isinstance(enum, ast.Attribute)
                    and enum.attr == 'value' and isinstance(enum.value, ast.Name)):
                return None
            if any((isinstance(n, ast.Name) and n.id == 'int' and isinstance(n.ctx, (ast.Store, ast.Del)))
                   or (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == 'int')
                   or (isinstance(n, ast.alias) and (n.asname or n.name) == 'int') for n in ast.walk(tree)):
                return None
            receiver = enum.value.id
            annotation = annotations.get(receiver)
            cls = local_class(tree, annotation.id) if isinstance(annotation, ast.Name) else None
            if not (cls and not cls.decorator_list and len(cls.bases) == 1
                    and ast.unparse(cls.bases[0]) in imported_names(tree, 'enum', 'Flag')):
                return None
            members = [n for n in cls.body if isinstance(n, ast.Assign)]
            if not members or any(not isinstance(n.value, ast.Constant) or type(n.value.value) is not int for n in members):
                return None
            if any(isinstance(n, ast.FunctionDef) and (n.name == 'value' or n.name.startswith('__')) for n in cls.body):
                return None
            value.update(numeric_components=2,
                         component_types=['int', cls.name + '.value (enum.Flag)'],
                         template=value['prefix'] + '<' + slug(number.id) + '>.<' + slug(cls.name) + '>' + value['suffix'])
            dependencies = tuple((path, n.lineno) for n in [cls, *members])
        else:
            if len(fields) != 1:
                return None
            call = fields[0].value
            if not (isinstance(call, ast.Call) and not call.args and not call.keywords and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)):
                return None
            receiver, method_name = call.func.value.id, call.func.attr
            annotation = annotations.get(receiver)
            cls = local_class(tree, annotation.id) if isinstance(annotation, ast.Name) else None
            decorators = imported_names(tree, 'dataclasses', 'dataclass') | imported_names(tree, 'attr', 'dataclass')
            if not cls or cls.bases or any(ast.unparse(d) not in decorators for d in cls.decorator_list):
                return None
            if any(isinstance(n, ast.FunctionDef) and n.name.startswith('__') for n in cls.body):
                return None
            methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name]
            if len(methods) != 1 or methods[0].decorator_list:
                return None
            method = methods[0]
            if (len(method.args.args) != 1 or method.args.posonlyargs or method.args.kwonlyargs
                    or method.args.vararg or method.args.kwarg):
                return None
            returns = [n for n in ast.walk(method) if isinstance(n, ast.Return)]
            if len(returns) != 1 or method.body[-1] is not returns[0]:
                return None
            join = returns[0].value
            if not (isinstance(join, ast.Call) and not join.keywords and len(join.args) == 1 and isinstance(join.args[0], ast.Name)
                    and isinstance(join.func, ast.Attribute) and join.func.attr == 'join'
                    and isinstance(join.func.value, ast.Constant) and join.func.value.value == '.'):
                return None
            name = join.args[0].id
            lists = [n for n in method.body if isinstance(n, ast.Assign) and len(n.targets) == 1
                     and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name and isinstance(n.value, ast.List)]
            references = [n for n in ast.walk(method) if isinstance(n, ast.Name) and n.id == name]
            if len(lists) != 1 or len(references) != 2 or any(isinstance(n, ast.Starred) for n in lists[0].value.elts):
                return None
            if any(isinstance(n, (ast.Attribute, ast.Name)) and isinstance(n.ctx, (ast.Store, ast.Del))
                   and (n.attr if isinstance(n, ast.Attribute) else n.id) == method_name for n in ast.walk(tree)):
                return None
            value.update(minimum_components=len(lists[0].value.elts), helper=cls.name + '.' + method_name)
            dependencies = ((path, method.lineno), (path, lists[0].lineno), (path, returns[0].lineno))
        return Fact(path, module_name(path) + '.' + function.name, 'cache_path', receiver,
                    value, function.lineno, function.end_lineno, True, dependencies)

    def optparse_facts(self, path, tree, module):
        """Read direct OptionGroup.add_option calls inside one public function."""
        facts = []
        parsers = imported_names(tree, 'optparse', 'OptionParser') if 'optparse' not in self.modules else set()
        groups = imported_names(tree, 'optparse', 'OptionGroup') if 'optparse' not in self.modules else set()
        counts = bindings(tree)
        for function in (n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and not n.name.startswith("_") and not n.decorator_list and counts[n.name] == 1):
            parser_names, group_names = set(), set()
            for statement in function.body:
                if not isinstance(statement, ast.Assign) or len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
                    continue
                target = statement.targets[0].id
                value = statement.value
                if not isinstance(value, ast.Call):
                    continue
                constructor = ast.unparse(value.func)
                if constructor in parsers:
                    parser_names.add(target)
                elif constructor in groups and value.args and isinstance(value.args[0], ast.Name) and value.args[0].id in parser_names:
                    group_names.add(target)
            symbol = f"{module}.{function.name}"
            function_facts, destination_counts = [], {}
            overridden = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                             and n.func.attr == "set_defaults" and isinstance(n.func.value, ast.Name)
                             and n.func.value.id in parser_names | group_names for n in ast.walk(function))
            # Group construction/attachment are known parser escapes; exclude
            # their arguments while retaining all option registrations.
            check_tree = ast.Module(body=[s for s in function.body if not (
                isinstance(s, ast.Assign) and isinstance(s.value, ast.Call)
                and ast.unparse(s.value.func) in groups) and not (
                isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
                and isinstance(s.value.func, ast.Attribute)
                and isinstance(s.value.func.value, ast.Name)
                and s.value.func.value.id in parser_names
                and s.value.func.attr == 'add_option_group'
                and len(s.value.args) == 1 and not s.value.keywords
                and isinstance(s.value.args[0], ast.Name)
                and s.value.args[0].id in group_names)], type_ignores=[])
            overridden = overridden or uncertain_parser_use(check_tree, parser_names | group_names,
                                                            {'add_option', 'add_option_group'}, function.body, True)
            overridden = overridden or any(bindings(function)[name] != 1 for name in parser_names | group_names)
            unknown_options = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                  and n.func.attr == 'add_option' for n in ast.walk(function)) and not parser_names
            if overridden or unknown_options:
                facts.append(Fact(path, symbol, 'owner', 'function', {}, function.lineno, function.end_lineno, False))
            for statement in function.body:
                if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
                    continue
                call = statement.value
                if not (isinstance(call.func, ast.Attribute) and call.func.attr == "add_option"
                        and isinstance(call.func.value, ast.Name) and call.func.value.id in group_names | parser_names):
                    continue
                options = [a.value for a in call.args if isinstance(a, ast.Constant)
                           and isinstance(a.value, str) and a.value.startswith("-")]
                if not options:
                    continue
                kwargs = {k.arg: k.value for k in call.keywords if k.arg}
                action_node, default_node = kwargs.get("action"), kwargs.get("default")
                action = action_node.value if isinstance(action_node, ast.Constant) else None
                value, deps = self.value(path, default_node) if default_node is not None else (UNKNOWN, ())
                resolved = action in ("store_true", "store_false") and value != UNKNOWN
                dest_node = kwargs.get("dest")
                dest = dest_node.value if isinstance(dest_node, ast.Constant) and isinstance(dest_node.value, str) else None
                destination_counts[dest] = destination_counts.get(dest, 0) + 1
                resolved = resolved and dest is not None and not any(k.arg is None for k in call.keywords)
                for option in options:
                    function_facts.append(Fact(path, symbol, "flag", option,
                                      {"default": value, "aliases": sorted(options), "dest": dest, "action": action},
                                      statement.lineno, statement.end_lineno, resolved, deps))
            # shortcut: implicit/shared/overridden defaults abstain, until destination state is modeled.
            for fact in function_facts:
                fact.resolved = fact.resolved and not overridden and destination_counts[fact.value["dest"]] == 1
            facts.extend(function_facts)
        return facts

    def retry_count(self, path, node):
        """Only: for _ in range(N): try: return call() except E: pass; raise E.

        This proves an upper bound, not successful retrying of all exceptions.
        """
        body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
        if len(body) != 2 or not isinstance(body[0], ast.For) or not isinstance(body[1], ast.Raise):
            return None
        loop = body[0]
        if loop.orelse or not isinstance(loop.iter, ast.Call) or not isinstance(loop.iter.func, ast.Name) or loop.iter.func.id != "range" or len(loop.iter.args) != 1 or loop.iter.keywords:
            return None
        # Restrict retry counts to literals, avoiding dependency/rebinding claims.
        if not isinstance(loop.iter.args[0], ast.Constant):
            return None
        if bindings(self.trees[path])['range']:
            return None
        count, _ = self.value(path, loop.iter.args[0])
        if type(count) != int or not 1 <= count <= 1000 or len(loop.body) != 1:
            return None
        attempt = loop.body[0]
        if not isinstance(attempt, ast.Try) or attempt.orelse or attempt.finalbody or len(attempt.body) != 1:
            return None
        ret = attempt.body[0]
        if not isinstance(ret, ast.Return) or not isinstance(ret.value, ast.Call) or not attempt.handlers:
            return None
        if any(len(h.body) != 1 or not isinstance(h.body[0], ast.Pass) or h.type is None for h in attempt.handlers):
            return None
        return {"maximum": count - 1, "exceptions": [ast.unparse(h.type) for h in attempt.handlers]}


def changes(before, after, renames):
    old = {f.key(): f for f in before}
    new = {}
    for fact in after:
        path = renames.get(fact.path, fact.path)
        symbol = fact.symbol
        if path != fact.path:
            symbol = module_name(path) + symbol[len(module_name(fact.path)):]
        new[path, symbol, fact.kind, fact.name] = fact
    result = []
    for key, prior in old.items():
        current = new.get(key)
        if not prior.resolved or (current and not current.resolved):
            continue
        if current is None:
            # A missing whole function/parser may be a re-export/alias or rename.
            # Only prove parameter/flag removal within a still-existing owner.
            siblings = [f for k, f in new.items() if k[:2] == key[:2]]
            if not siblings or any(not f.resolved for f in siblings):
                continue
            if prior.kind == "parameter" and any(isinstance(f.value, dict) and f.value.get("kwargs") for f in siblings):
                continue
            if prior.kind == "flag" and any(f.kind == "flag" and f.name.startswith(prior.name) for f in siblings):
                # argparse long-option abbreviations may preserve this spelling.
                continue
            if prior.kind in ("parameter", "flag"):
                result.append((prior, None, f"{prior.kind}_removed"))
        elif prior.kind == "retries":
            if prior.value != current.value and prior.value["exceptions"] == current.value["exceptions"]:
                result.append((prior, current, "retry_limit_changed"))
        elif prior.kind == 'cache_path':
            if (prior.value.get('numeric_components') and current.value.get('minimum_components', 0) > prior.value['numeric_components']
                    and all(prior.value[k] == current.value[k] for k in ('prefix', 'suffix', 'base_expression'))):
                result.append((prior, current, 'cache_path_changed'))
        elif prior.kind in ("parameter", "flag"):
            a, b = prior.value.get("default", UNKNOWN), current.value.get("default", UNKNOWN)
            if a != UNKNOWN and b != UNKNOWN and (type(a) != type(b) or a != b):
                result.append((prior, current, f"{prior.kind}_default_changed"))
    return result
