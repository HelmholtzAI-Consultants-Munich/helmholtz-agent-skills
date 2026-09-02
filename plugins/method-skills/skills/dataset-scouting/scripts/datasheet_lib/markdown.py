"""Strict Markdown parsing and scaffolding for candidate datasheets."""

from __future__ import annotations

import re
from pathlib import Path

from .model import (
    CHECK_NAMES,
    REVIEW_MARKER,
    SUMMARY_KEYS,
    Candidate,
    CheckRow,
    Criteria,
    CriteriaField,
    FieldRow,
    ResearchRow,
    SourceRow,
    TechnicalRow,
)


class DatasheetError(Exception):
    """A readable operational or format error."""


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)
SUMMARY_RE = re.compile(r"^-\s+\*\*(?P<name>[^*]+?):\*\*\s*(?P<value>.*)$")
ALIGNMENT_RE = re.compile(r"^:?-{3,}:?$")

TABLE_HEADERS = {
    "Checks": ["Check", "Result", "Reason", "Sources"],
    "Fields": ["Field", "Priority", "Status", "Coverage", "Storage", "Level", "Sources", "Note"],
    "Technical details": ["Item", "Value", "Sources", "Channels checked"],
    "Research": ["Channel", "Outcome", "Sources"],
    "Sources": ["ID", "Description", "Location", "Retrieved"],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise DatasheetError(f"{path} is not valid UTF-8 at byte {exc.start}") from exc
    except OSError as exc:
        raise DatasheetError(f"cannot read {path}: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise DatasheetError(f"cannot write {path}: {exc}") from exc


def slugify(identifier: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", identifier).strip("-") or "candidate"


def candidate_scaffold(identifier: str) -> str:
    summary = "\n".join(f"- **{name}:**" for name in SUMMARY_KEYS)
    checks = "\n".join(f"| {name} |  |  |  |" for name in CHECK_NAMES)
    return f"""# {identifier}

## Summary

{summary}

## Checks

| Check | Result | Reason | Sources |
|---|---|---|---|
{checks}

## Fields

| Field | Priority | Status | Coverage | Storage | Level | Sources | Note |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Technical details

| Item | Value | Sources | Channels checked |
|---|---|---|---|
|  |  |  |  |

## Research

| Channel | Outcome | Sources |
|---|---|---|
|  |  |  |

## Sources

| ID | Description | Location | Retrieved |
|---|---|---|---|
|  |  |  |  |

## Gaps

## Research notes

## Review
{REVIEW_MARKER}

- **Decision:** pending
- **Notes:**
"""


def scaffold_candidates(datasheet_dir: str, identifiers: list[str]) -> list[str]:
    root = Path(datasheet_dir)
    if root.exists() and not root.is_dir():
        raise DatasheetError(f"{root} exists and is not a directory")
    candidate_dir = root / "candidates"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    messages = []
    for identifier in identifiers:
        path = candidate_dir / f"{slugify(identifier)}.md"
        if path.exists():
            messages.append(f"skip (exists): {path}")
            continue
        write_text(path, candidate_scaffold(identifier))
        messages.append(f"created: {path}")
    return messages


def _sections(text: str) -> tuple[dict[str, str], list[str]]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    names: list[str] = []
    for index, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        names.append(name)
        sections[name] = sections.get(name, "") + ("\n" if name in sections else "") + text[start:end].strip()
    return sections, names


def _summary(section: str) -> dict[str, str]:
    values: dict[str, str] = {}
    active: str | None = None
    for line in section.splitlines():
        match = SUMMARY_RE.match(line)
        if match:
            active = match.group("name").strip()
            values[active] = match.group("value").strip()
        elif active and line.strip():
            values[active] = f"{values[active]}\n{line.strip()}".strip()
    return values


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        raise DatasheetError(f"malformed Markdown table row: {line[:100]}")
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line[1:-1]:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def escape_table_cell(value: str) -> str:
    return " ".join(value.split()).replace("\\", "\\\\").replace("|", "\\|")


def _table(section_name: str, section: str) -> list[list[str]]:
    expected = TABLE_HEADERS[section_name]
    rows = [split_table_row(line) for line in section.splitlines() if line.strip().startswith("|")]
    if not rows:
        return []
    if rows[0] != expected:
        raise DatasheetError(f"## {section_name} headers are {rows[0]!r}; expected {expected!r}")
    out: list[list[str]] = []
    for row in rows[1:]:
        if all(ALIGNMENT_RE.match(cell.replace(" ", "")) for cell in row):
            continue
        if len(row) != len(expected):
            raise DatasheetError(f"## {section_name} row has {len(row)} cells; expected {len(expected)}")
        if any(cell for cell in row):
            out.append(row)
    return out


def parse_candidate(path: Path) -> Candidate:
    text = read_text(path)
    first = next((line for line in text.splitlines() if line.strip()), "")
    if not first.startswith("# "):
        raise DatasheetError(f"{path}: first non-empty line must be '# <candidate>'")
    title = first[2:].strip()
    sections, names = _sections(text)
    required = ["Summary", *TABLE_HEADERS, "Gaps", "Review"]
    missing = [name for name in required if name not in sections]
    if missing:
        raise DatasheetError(f"{path}: missing section(s): {', '.join('## ' + x for x in missing)}")

    review_matches = list(re.finditer(r"^##\s+Review\s*$", text, re.M))
    review_text = text[review_matches[-1].start():] if review_matches else ""
    return Candidate(
        path=path,
        text=text,
        title=title,
        summary=_summary(sections["Summary"]),
        checks=[CheckRow(*row) for row in _table("Checks", sections["Checks"])],
        fields=[FieldRow(*row) for row in _table("Fields", sections["Fields"])],
        technical=[TechnicalRow(*row) for row in _table("Technical details", sections["Technical details"])],
        research=[ResearchRow(*row) for row in _table("Research", sections["Research"])],
        sources=[SourceRow(*row) for row in _table("Sources", sections["Sources"])],
        gaps=sections["Gaps"],
        research_notes=sections.get("Research notes", ""),
        review_text=review_text,
        section_names=names,
    )


def load_candidates(datasheet_dir: str) -> list[Candidate]:
    root = Path(datasheet_dir)
    candidate_dir = root / "candidates"
    if not root.is_dir():
        raise DatasheetError(f"datasheet directory does not exist: {root}")
    if not candidate_dir.is_dir():
        raise DatasheetError(f"candidate directory does not exist: {candidate_dir}")
    paths = sorted(candidate_dir.glob("*.md"))
    if not paths:
        raise DatasheetError(f"no candidate Markdown files in {candidate_dir}")
    candidates = []
    for path in paths:
        try:
            candidates.append(parse_candidate(path))
        except DatasheetError as exc:
            raise DatasheetError(f"{path.name}: {exc}") from exc
    return candidates


def _criteria_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^#{{1,6}}\s*{re.escape(heading)}\b.*?$(.*?)(?=^#{{1,6}}\s|\Z)",
        text,
        re.M | re.S | re.I,
    )
    return match.group(1) if match else ""


def parse_criteria(datasheet_dir: str) -> Criteria:
    path = Path(datasheet_dir) / "criteria.md"
    if not path.is_file():
        raise DatasheetError(f"criteria file does not exist: {path}")
    text = read_text(path)
    fields: list[CriteriaField] = []
    for line in _criteria_section(text, "Fields of interest").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_table_row(line)
        if len(cells) < 3 or cells[0].casefold() == "field":
            continue
        if all(ALIGNMENT_RE.match(cell.replace(" ", "")) for cell in cells):
            continue
        name, priority, threshold = (cell.strip("*` ") for cell in cells[:3])
        if name and not name.startswith("<"):
            fields.append(CriteriaField(name, priority.casefold(), threshold))

    technical_items = []
    for line in _criteria_section(text, "Technical details").splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            item = re.split(r"\s+[—–]\s+", stripped[2:], maxsplit=1)[0].strip("*` ")
            if item and not item.startswith("<"):
                technical_items.append(item)
    return Criteria(fields=fields, technical_items=technical_items)
