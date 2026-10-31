"""Link exact claims and verify supported-before / contradicted-after facts."""
from dataclasses import asdict
import hashlib
import json
import re
import time
from urllib.parse import quote, urlparse

from . import __version__
from .facts import Extractor, UNKNOWN, changes
from .markdown import explicit_example, index, qualified, tokens
from .model import ModelError
from .snapshots import collect


def same_value(a, b):
    return type(a) is type(b) and a == b


def values(text):
    # Backticks and quotes preserve strings; bare words include None/booleans.
    result = []
    for match in re.finditer(r"`([^`]+)`|\"([^\"]+)\"|'([^']+)'|(?<![\w.])-?\d+(?:\.\d+)?(?!\w|\.\d)|\b(?:True|False|None)\b", text):
        token = next((x for x in match.groups() if x is not None), match[0])
        if re.fullmatch(r"-?\d+", token):
            result.append(int(token))
        elif re.fullmatch(r"-?\d+\.\d+", token):
            result.append(float(token))
        elif token in ("True", "False", "None"):
            result.append({"True": True, "False": False, "None": None}[token])
        else:
            result.append(token)
    return result


def default_value(claim, fact):
    text = claim.quote
    if claim.kind == "table":
        cells = [c.strip() for c in text.strip().strip("|").split("|")]
        columns = [c.lower().strip(" `") for c in claim.columns]
        if "default" not in columns or len(cells) != len(columns):
            return UNKNOWN
        extracted = values(cells[columns.index("default")])
        return extracted[0] if len(extracted) == 1 else UNKNOWN
    # Restrict to explicit, affirmative default statements.
    if re.search(r"\b(?:not|never|no longer|can|could|may|should)\b", text, re.I):
        return UNKNOWN
    patterns = [r"\bdefaults?\s+(?:to|is|of|value\s+is)\s+(.+)",
                r"\bby default\b", r"\bdefault\s*[:=]\s*(.+)"]
    matches = [re.search(p, text, re.I) for p in patterns]
    matches = [m for m in matches if m]
    if not matches:
        return UNKNOWN
    extracted = values(text)
    # Exclude identifier mentions; keep literal candidates only.
    excluded = {fact.name, fact.symbol, fact.symbol.rsplit(".", 1)[-1]}
    extracted = [v for v in extracted if not (isinstance(v, str) and v in excluded)]
    return extracted[0] if len(extracted) == 1 else UNKNOWN


def linked(claim, fact, all_facts):
    context = claim.heading + " " + claim.quote
    mentions = tokens(context)
    if fact.kind == "flag":
        # Flags also need module/path scope if multiple parsers expose that flag.
        candidates = {(f.path, f.symbol) for f in all_facts if f.kind == "flag" and f.name == fact.name}
        return fact.name in mentions and (len(candidates) == 1 or fact.path in context or fact.symbol in mentions)
    short = fact.symbol.rsplit(".", 1)[-1]
    candidates = {f.symbol for f in all_facts if f.kind == "owner" and f.symbol.rsplit(".", 1)[-1] == short}
    owner = fact.symbol in mentions or (short in mentions and len(candidates) == 1)
    if fact.kind == "parameter":
        named_parameters = {f.name for f in all_facts if f.symbol == fact.symbol and f.kind == "parameter" and f.name in mentions}
        if len(named_parameters) > 1:
            return False
    return owner and (fact.kind == "retries" or fact.name in mentions)


def relevant_hunks(comparison, before, after):
    locations = [(before.path, before.line, before.end_line, "old")]
    if after:
        locations.append((after.path, after.line, after.end_line, "new"))
    locations += [(p, n, n, "old") for p, n in before.dependencies]
    if after:
        locations += [(p, n, n, "new") for p, n in after.dependencies]
    return [h for h in comparison.hunks if any(
        h[f"{side}_path"] == p and h[f"{side}_start"] <= end
        and h[f"{side}_start"] + max(1, h[f"{side}_count"]) > start
        for p, start, end, side in locations)]


def source_excerpt(snapshot, fact):
    if not fact:
        return None
    return "".join(snapshot.files[fact.path].splitlines(keepends=True)[fact.line - 1:fact.end_line])


def commit_link(repository_url, commit, path, start, end=None):
    if not repository_url:
        return None
    return f"{repository_url.rstrip('/')}/blob/{commit}/{quote(path, safe='/')}#L{start}" + (f"-L{end}" if end and end != start else "")


def analyze(repo, base, head, repository_url=None, model=None):
    started = time.perf_counter()
    if repository_url:
        parsed = urlparse(repository_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("Repository URL must be an HTTPS repository URL")
    comparison = collect(repo, base, head)
    old_extractor, new_extractor = Extractor(comparison.base.files), Extractor(comparison.head.files)
    before_facts, after_facts = old_extractor.extract(), new_extractor.extract()
    old_claims, new_claims = index(comparison.base.files), index(comparison.head.files)
    old_claim_index = {(c.path, c.heading, c.quote, c.kind, c.columns): c for c in old_claims}
    report = {"schema_version": 1, "analyzer_version": __version__,
              "base_commit": comparison.base.commit, "head_commit": comparison.head.commit,
              "findings": [], "abstentions": [], "warnings": old_extractor.errors + new_extractor.errors,
              "limitations": ["Python top-level functions and direct module-level argparse definitions only.",
                              "Exact scope references required; unresolved aliases, wrappers and qualifiers abstain.",
                              "Static declared defaults do not prove effective runtime values or physical units.",
                              "Markdown subset: ATX headings, paragraphs, simple pipe tables and fenced code."]}
    failed_paths = {w.split(":", 1)[0] for w in report["warnings"]}
    for before, after, category in changes(before_facts, after_facts, comparison.renames):
        if before.path in failed_paths or (after and after.path in failed_paths):
            continue
        hunks = relevant_hunks(comparison, before, after)
        if not hunks:
            continue
        for claim in new_claims:
            if explicit_example(claim) or not linked(claim, after or before, after_facts + before_facts):
                continue
            old_path = comparison.renames.get(claim.path, claim.path)
            old_claim = old_claim_index.get((old_path, claim.heading, claim.quote, claim.kind, claim.columns))
            reason = None
            if old_claim is None:
                reason = "No unchanged claim with matching scope in the base snapshot"
            elif qualified(claim):
                reason = "Historical, platform or conditional qualifier requires more evidence"
            elif not linked(old_claim, before, before_facts):
                reason = "Base claim could not be linked to the same fact"
            if reason:
                report["abstentions"].append({"claim": claim.json(), "symbol": before.symbol, "reason": reason})
                continue
            evidence = "deterministic"
            documented = UNKNOWN
            if category.endswith("default_changed"):
                documented = default_value(claim, before)
                supported = same_value(documented, before.value["default"])
                contradicted = after is not None and not same_value(documented, after.value["default"])
            elif category.endswith("removed"):
                # Presence in a real parameter/flag reference table is supported;
                # prose must explicitly state availability, not mention history.
                supported = (claim.kind == "table" and any(re.search(r"parameter|flag|option|argument", c, re.I) for c in claim.columns)) or bool(re.search(r"\b(?:accepts?|supports?|available|takes?)\b", claim.quote, re.I))
                # An imperative establishes availability of its exact option,
                # not the behavior promised by the rest of the instruction.
                # The old parser fact and unchanged claim are already verified.
                if before.kind == "flag" and claim.kind == "sentence":
                    option = re.escape(before.name)
                    instruction = rf"^Use\s+(?:`{option}`|{option})(?=\s|[.,;:!?]|$)"
                    supported = supported or bool(re.search(instruction, claim.quote, re.I))
                if re.search(r"\b(?:not|never|no longer|unsupported|removed)\b", claim.quote, re.I):
                    supported = False
                contradicted = True
            else:
                # Limited structural detector: maximum automatic retries for the
                # explicitly named exception type, not arbitrary behavior.
                match = re.search(r"(?:at most|up to|maximum(?: of)?)\s+`?(\d+)`?\s+(?:automatic\s+)?retr(?:ies|y)", claim.quote, re.I)
                documented = int(match[1]) if match else UNKNOWN
                exceptions_named = all(e in tokens(claim.quote) for e in before.value["exceptions"])
                supported = exceptions_named and same_value(documented, before.value["maximum"])
                contradicted = not same_value(documented, after.value["maximum"])
            if not supported and model and after and not category.endswith("removed"):
                bundle = {"base_commit": comparison.base.commit, "head_commit": comparison.head.commit,
                          "claim": claim.json(), "before": before.json(), "after": after.json(),
                          "before_code": source_excerpt(comparison.base, before),
                          "after_code": source_excerpt(comparison.head, after), "hunks": hunks,
                          "dependencies_before": [{"path": p, "line": n, "text": comparison.base.files[p].splitlines()[n - 1]} for p, n in before.dependencies],
                          "dependencies_after": [{"path": p, "line": n, "text": comparison.head.files[p].splitlines()[n - 1]} for p, n in after.dependencies]}
                try:
                    verdict = model.interpret(bundle)
                    # Model claims never override deterministic disagreement. It
                    # may extract a literal only when a default marker is present.
                    expected_property = "default" if category.endswith("default_changed") else "maximum_retries"
                    literal_present = any(same_value(v, verdict["value"]) for v in values(claim.quote))
                    before_value = before.value.get("default", before.value.get("maximum"))
                    after_value = after.value.get("default", after.value.get("maximum"))
                    supported = (documented == UNKNOWN and expected_property == "default"
                                 and bool(re.search(r"\bdefaults?\b", claim.quote, re.I))
                                 and not re.search(r"\b(?:not|never|no longer|can|could|may|should)\b", claim.quote, re.I)
                                 and verdict["property"] == expected_property and literal_present
                                 and same_value(verdict["value"], before_value)
                                 and verdict["before_verdict"] == "supported"
                                 and verdict["after_verdict"] == "contradicted")
                    contradicted = not same_value(verdict["value"], after_value)
                    evidence = "model-extracted, deterministic fact comparison"
                except ModelError as exc:
                    report["warnings"].append(str(exc))
            if not (supported and contradicted):
                report["abstentions"].append({"claim": claim.json(), "symbol": before.symbol,
                                            "reason": "Cannot establish both old support and new contradiction"})
                continue
            underlying = json.dumps([before.key(), category, before.value, after.value if after else None], sort_keys=True)
            group_id = hashlib.sha256(underlying.encode()).hexdigest()[:16]
            identity = json.dumps([comparison.head.commit, claim.path, claim.start, claim.quote, group_id])
            after_owner = next((f for f in after_facts if f.kind == "owner" and f.symbol == before.symbol and f.path == before.path), None) if after is None else None
            finding = {"id": hashlib.sha256(identity.encode()).hexdigest()[:20], "group_id": group_id,
                       "category": category, "claim": claim.json(), "before_claim": old_claim.json(),
                       "before": before.json(), "after": after.json() if after else None,
                       "after_owner": after_owner.json() if after_owner else None,
                       "before_verdict": "supported", "after_verdict": "contradicted", "evidence_strength": evidence,
                       "hunks": hunks,
                       "explanation": explain(before, after, category),
                       "suggested_correction": correction(before, after, category),
                       "links": {"documentation": commit_link(repository_url, comparison.head.commit, claim.path, claim.line_start, claim.line_end),
                                 "before": commit_link(repository_url, comparison.base.commit, before.path, before.line, before.end_line),
                                 "after": commit_link(repository_url, comparison.head.commit, after.path, after.line, after.end_line) if after else (commit_link(repository_url, comparison.head.commit, after_owner.path, after_owner.line, after_owner.end_line) if after_owner else None)},
                       "limitations": ["Static source evidence; runtime overrides are not evaluated."]}
            report["findings"].append(finding)
    report["findings"] = list({f["id"]: f for f in report["findings"]}.values())
    report["warnings"] = sorted(set(report["warnings"]))
    report["metrics"] = {"runtime_seconds": round(time.perf_counter() - started, 6),
                         "claims_indexed": len(new_claims), "facts_indexed": len(after_facts),
                         "finding_count": len(report["findings"]),
                         "change_groups": len({f["group_id"] for f in report["findings"]}),
                         "model_calls": model.calls if model else 0, "model_cache_hits": model.cache_hits if model else 0}
    return report


def explain(before, after, category):
    if category.endswith("removed"):
        return f"{before.symbol} no longer declares {before.name}, which the unchanged documentation says is available."
    key = "maximum" if category == "retry_limit_changed" else "default"
    return f"{before.symbol}: {before.name} {key} changed from {before.value[key]!r} to {after.value[key]!r}; the documentation still states the old value."


def correction(before, after, category):
    if category.endswith("removed"):
        return f"Remove or update the documented {before.name} reference after reviewing migration behavior."
    key = "maximum" if category == "retry_limit_changed" else "default"
    return f"Update the documented {key} from {before.value[key]!r} to {after.value[key]!r}."
