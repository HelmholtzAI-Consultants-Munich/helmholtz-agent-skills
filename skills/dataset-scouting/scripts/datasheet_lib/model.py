"""Typed datasheet records and the small controlled vocabulary they use."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


REVIEW_MARKER = "<!-- Human-owned. The agent never edits below this line. -->"

SUMMARY_KEYS = [
    "Identifiers",
    "Publication",
    "Modality",
    "Sample count",
    "Download size",
    "Metadata route",
    "Metadata access",
    "Metadata evidence",
    "Raw-data route",
    "Raw-data access",
    "Raw-data evidence",
    "Access and contacts",
    "Tier",
    "Recommendation",
]

DOWNLOAD_SIZE_RE = re.compile(
    r"^\s*(?P<size>(?:[~≈]\s*)?"
    r"(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:[.,]\d+)?)\s*"
    r"(?:[KMGTPE]?i?B))\b",
    re.I,
)

CHECK_NAMES = ["Metadata", "Required fields", "Raw data"]
ACCESS_VALUES = {"direct", "on request", "off-repository", "unavailable", "unknown"}
CHECK_VALUES = {"pass", "fail", "unknown"}
RECOMMENDATION_VALUES = {"accept", "reject", "unknown"}
FIELD_PRIORITIES = {"must-have", "nice-to-have", "observed", "ignore"}
FIELD_STATUSES = {"present", "absent", "not checked"}
CHANNELS = {
    "record",
    "related-records",
    "publication",
    "supplements",
    "literature-search",
    "off-repository",
    "web",
    "user",
}


@dataclass(frozen=True)
class CheckRow:
    name: str
    result: str
    reason: str
    sources: str


@dataclass(frozen=True)
class FieldRow:
    name: str
    priority: str
    status: str
    coverage: str
    storage: str
    level: str
    sources: str
    note: str


@dataclass(frozen=True)
class TechnicalRow:
    item: str
    value: str
    sources: str
    channels_checked: str


@dataclass(frozen=True)
class ResearchRow:
    channel: str
    outcome: str
    sources: str


@dataclass(frozen=True)
class SourceRow:
    ident: str
    description: str
    location: str
    retrieved: str


@dataclass
class Candidate:
    path: Path
    text: str
    title: str
    summary: dict[str, str]
    checks: list[CheckRow]
    fields: list[FieldRow]
    technical: list[TechnicalRow]
    research: list[ResearchRow]
    sources: list[SourceRow]
    gaps: str
    research_notes: str
    review_text: str
    section_names: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def ident(self) -> str:
        for separator in (" — ", " – ", " - "):
            if separator in self.title:
                return self.title.split(separator, 1)[0].strip()
        return self.title.strip()

    @property
    def source_ids(self) -> set[str]:
        return {source.ident for source in self.sources}

    @property
    def human_decision(self) -> str:
        import re

        match = re.search(r"^-\s+\*\*Decision:\*\*\s*(.*)$", self.review_text, re.M)
        return match.group(1).strip() if match else "unknown"

    def check_result(self, name: str) -> str:
        for row in self.checks:
            if row.name.casefold() == name.casefold():
                return first_token(row.result)
        return "unknown"


@dataclass(frozen=True)
class CriteriaField:
    name: str
    priority: str
    threshold: str


@dataclass(frozen=True)
class Criteria:
    fields: list[CriteriaField]
    technical_items: list[str]


def first_token(value: str) -> str:
    """Return the normalized controlled token before citations or explanation."""
    value = value.replace("**", "").replace("`", "").strip().casefold()
    controlled = ACCESS_VALUES | CHECK_VALUES | RECOMMENDATION_VALUES | FIELD_PRIORITIES | FIELD_STATUSES
    for token in sorted(controlled, key=len, reverse=True):
        if value == token or value.startswith(token + " ") or value.startswith(token + " —"):
            return token
    return value.split(None, 1)[0] if value else ""
