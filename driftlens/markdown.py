"""Small source-mapped Markdown block/sentence parser for the MVP subset.

Unsupported constructs remain text. Fenced and indented code are never prose.
Offsets are zero-based Unicode character offsets into the original document.
"""
from dataclasses import asdict, dataclass
import re


@dataclass
class Claim:
    path: str
    heading: str
    quote: str
    line_start: int
    line_end: int
    start: int
    end: int
    kind: str
    columns: tuple = ()

    def json(self):
        return asdict(self)


def parse(path, source):
    lines = source.splitlines(keepends=True)
    offsets, offset = [], 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    claims, headings, fence, table_columns = [], [], None, ()
    paragraph = []
    in_comment = False

    def emit(start, end, kind, columns=()):
        raw = source[start:end]
        left = len(raw) - len(raw.lstrip())
        right = len(raw.rstrip())
        start, end = start + left, start + right
        if end <= start:
            return
        claims.append(Claim(path, " / ".join(headings), source[start:end],
                            source.count("\n", 0, start) + 1,
                            source.count("\n", 0, end - 1) + 1,
                            start, end, kind, columns))

    def flush():
        if paragraph:
            start, end = paragraph[0][0], paragraph[-1][1]
            raw = source[start:end]
            # Sentence boundaries only outside inline code; preserve exact spans.
            ticks, cursor = False, 0
            for match in re.finditer(r"`+|[.!?](?=\s|$)", raw):
                if match[0].startswith("`"):
                    ticks = not ticks
                elif not ticks:
                    emit(start + cursor, start + match.end(), "sentence")
                    cursor = match.end()
            emit(start + cursor, end, "sentence")
            paragraph.clear()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if in_comment or "<!--" in line:
            flush()
            in_comment = "-->" not in line
            continue
        fence_match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence_match:
            flush()
            marker = fence_match[1]
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            continue
        if fence or line.startswith(("    ", "\t")):
            flush()
            emit(offsets[i], offsets[i] + len(line), "code")
            continue
        heading = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            flush()
            level = len(heading[1])
            headings = headings[:level - 1] + [heading[2]]
            table_columns = ()
            continue
        if not stripped:
            flush()
            table_columns = ()
            continue
        if "|" in line:
            flush()
            if re.fullmatch(r"[\s|:\-]+", line):
                continue
            if i + 1 < len(lines) and re.fullmatch(r"[\s|:\-]+", lines[i + 1]) and "-" in lines[i + 1]:
                table_columns = tuple(c.strip() for c in stripped.strip("|").split("|"))
                continue
            if table_columns:
                emit(offsets[i], offsets[i] + len(line), "table", table_columns)
                continue
        if re.match(r"^\s*(?:[-*+] |\d+\. )", line):
            flush()
        paragraph.append((offsets[i], offsets[i] + len(line)))
    flush()
    return claims


def index(files):
    return [claim for path, source in files.items()
            if path.lower().endswith((".md", ".markdown")) for claim in parse(path, source)]


def tokens(text):
    return set(re.findall(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|--?[\w-]+", text))


def qualified(claim):
    return bool(re.search(
        r"\b(?:if|when|unless|except|previously|formerly|historically|legacy|deprecated|"
        r"windows|linux|macos|darwin|unix|version|versions|overrid\w*|environment|"
        r"before|until|since|prior|used to|v\d+(?:\.\d+)*)\b|\$\{",
        claim.heading + " " + claim.quote, re.I))


def explicit_example(claim):
    # A code sample with explicit values says nothing about defaults.
    return claim.kind == "code" or bool(re.search(r"\b(?:example|e\.g\.|for instance)\b", claim.heading + " " + claim.quote, re.I))
