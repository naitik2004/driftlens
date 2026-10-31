"""Conservative AST facts and a bounded, two-hop constant resolver."""
import ast
import math
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
            stores = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
                    stores[node.id] = stores.get(node.id, 0) + 1
            self.constants[path] = {k: v[0] for k, v in assignments.items() if len(v) == 1 and stores.get(k) == 1}
            self.imports[path] = imports

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
            counts = {}
            for node in tree.body:
                name = getattr(node, "name", None)
                if name:
                    counts[name] = counts.get(name, 0) + 1
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            counts[target.id] = counts.get(target.id, 0) + 1
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
            # Recognize only direct argparse.ArgumentParser instances. Attribute
            # calls on arbitrary objects do not establish public CLI flags.
            parsers = set()
            constructors = set()
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "argparse":
                            constructors.add((alias.asname or "argparse") + ".ArgumentParser")
                if isinstance(node, ast.ImportFrom) and node.module == "argparse":
                    constructors.update(a.asname or a.name for a in node.names if a.name == "ArgumentParser")
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

    def optparse_facts(self, path, tree, module):
        """Read direct OptionGroup.add_option calls inside one public function."""
        facts = []
        parsers, groups = set(), set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                parsers.update(f"{a.asname or a.name}.OptionParser" for a in node.names if a.name == "optparse")
                groups.update(f"{a.asname or a.name}.OptionGroup" for a in node.names if a.name == "optparse")
            elif isinstance(node, ast.ImportFrom) and node.module == "optparse":
                parsers.update(a.asname or a.name for a in node.names if a.name == "OptionParser")
                groups.update(a.asname or a.name for a in node.names if a.name == "OptionGroup")
        for function in (n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and not n.name.startswith("_") and not n.decorator_list):
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
                resolved = action in ("store_true", "store_false")
                if default_node is None:
                    value = action == "store_false" if resolved else UNKNOWN
                else:
                    resolved = resolved and value != UNKNOWN
                dest_node = kwargs.get("dest")
                dest = dest_node.value if isinstance(dest_node, ast.Constant) and isinstance(dest_node.value, str) else None
                resolved = resolved and dest is not None and not any(k.arg is None for k in call.keywords)
                for option in options:
                    facts.append(Fact(path, symbol, "flag", option,
                                      {"default": value, "aliases": sorted(options), "dest": dest, "action": action},
                                      statement.lineno, statement.end_lineno, resolved, deps))
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
        if any(isinstance(n, ast.Name) and n.id == "range" and isinstance(n.ctx, ast.Store) for n in ast.walk(self.trees[path])) or any(a.arg == "range" for a in node.args.args + node.args.kwonlyargs):
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
        elif prior.kind in ("parameter", "flag"):
            a, b = prior.value.get("default", UNKNOWN), current.value.get("default", UNKNOWN)
            if a != UNKNOWN and b != UNKNOWN and (type(a) != type(b) or a != b):
                result.append((prior, current, f"{prior.kind}_default_changed"))
    return result
