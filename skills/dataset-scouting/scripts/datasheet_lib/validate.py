"""Deterministic validation for datasheet structure and decision invariants."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .markdown import load_candidates, parse_criteria
from .model import (
    ACCESS_VALUES,
    CHANNELS,
    CHECK_NAMES,
    CHECK_VALUES,
    DOWNLOAD_SIZE_RE,
    FIELD_PRIORITIES,
    FIELD_STATUSES,
    RECOMMENDATION_VALUES,
    REVIEW_MARKER,
    SUMMARY_KEYS,
    Candidate,
    Criteria,
    first_token,
)


CITATION_RE = re.compile(r"\[(S\d+)\]")
SOURCE_ID_RE = re.compile(r"^S\d+$")
COVERAGE_RE = re.compile(r"^\s*(\d[\d,]*)\s*/\s*(\d[\d,]*)\s*$")
DATE_RE = r"\d{4}-\d{2}-\d{2}"
EVIDENCE_RE = re.compile(
    rf"^(claimed|route verified\s+{DATE_RE}|contents inspected\s+{DATE_RE}|unknown)\b",
    re.I,
)


@dataclass(frozen=True)
class Issue:
    severity: str
    candidate: str
    message: str


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def _coverage(value: str) -> tuple[int, int] | None:
    match = COVERAGE_RE.match(value)
    return (
        int(match.group(1).replace(",", "")),
        int(match.group(2).replace(",", "")),
    ) if match else None


def _threshold_met(found: int, total: int, threshold: str) -> bool:
    threshold = threshold.strip().casefold()
    if total <= 0:
        return False
    if threshold in {"all", "every", "100%"}:
        return found == total
    if threshold in {"any", "at least one"}:
        return found > 0
    percent = re.fullmatch(r"(\d+(?:\.\d+)?)\s*%", threshold)
    if percent:
        return found / total >= float(percent.group(1)) / 100
    ratio = COVERAGE_RE.match(threshold)
    if ratio and int(ratio.group(2).replace(",", "")):
        numerator = int(ratio.group(1).replace(",", ""))
        denominator = int(ratio.group(2).replace(",", ""))
        return found / total >= numerator / denominator
    decimal = re.fullmatch(r"(?:0(?:\.\d+)?|1(?:\.0+)?)", threshold)
    return found / total >= float(threshold) if decimal else False


def _evidence_level(value: str) -> str:
    normalized = value.replace("**", "").replace("`", "").strip().casefold()
    for token in ("contents inspected", "route verified", "claimed", "unknown"):
        if normalized.startswith(token):
            return token
    return ""


def validate_candidate(candidate: Candidate, criteria: Criteria) -> list[Issue]:
    issues: list[Issue] = []

    def error(message: str) -> None:
        issues.append(Issue("ERROR", candidate.name, message))

    def warning(message: str) -> None:
        issues.append(Issue("WARNING", candidate.name, message))

    if len(candidate.section_names) != len(set(candidate.section_names)):
        error("duplicate level-two section heading")
    if REVIEW_MARKER not in candidate.review_text:
        error("human Review marker is missing")

    for key in SUMMARY_KEYS:
        if key not in candidate.summary:
            error(f"missing Summary field: {key}")
        elif not candidate.summary[key].strip():
            error(f"empty Summary field: {key}; write an explicit unknown")
    for key in sorted(set(candidate.summary) - set(SUMMARY_KEYS)):
        error(f"unknown Summary field: {key}")

    download_size = (
        candidate.summary.get("Download size", "")
        .replace("**", "")
        .replace("`", "")
        .strip()
    )
    download_size_match = DOWNLOAD_SIZE_RE.match(download_size)
    per_sample_only = bool(
        download_size_match
        and re.match(
            r"^\s*(?:/\s*sample\b|per[-\s]+sample\b)",
            download_size[download_size_match.end():],
            re.I,
        )
    )
    explicit_unknown = re.match(r"^unknown\s+[—–-]\s+\S", download_size, re.I)
    if download_size and (not download_size_match or per_sample_only) and not explicit_unknown:
        error("Download size must start with a total size and unit, or 'unknown — <reason>'")

    for key in ("Metadata access", "Raw-data access"):
        value = first_token(candidate.summary.get(key, ""))
        if value and value not in ACCESS_VALUES:
            error(f"{key} must start with one of: {', '.join(sorted(ACCESS_VALUES))}")
    for key in ("Metadata evidence", "Raw-data evidence"):
        value = candidate.summary.get(key, "")
        cleaned = value.replace("**", "").replace("`", "").strip()
        if value and not EVIDENCE_RE.match(cleaned):
            error(f"{key} must start with claimed, route verified <date>, contents inspected <date>, or unknown")

    recommendation = first_token(candidate.summary.get("Recommendation", ""))
    if recommendation and recommendation not in RECOMMENDATION_VALUES:
        error("Recommendation must start with accept, reject, or unknown")

    check_names = [_norm(row.name) for row in candidate.checks]
    if len(check_names) != len(set(check_names)):
        error("duplicate row in Checks table")
    if set(check_names) != {_norm(name) for name in CHECK_NAMES}:
        error(f"Checks table must contain exactly: {', '.join(CHECK_NAMES)}")
    for row in candidate.checks:
        if first_token(row.result) not in CHECK_VALUES:
            error(f"{row.name} check result must start with pass, fail, or unknown")
        if not row.reason.strip():
            error(f"{row.name} check has no reason")

    field_names = [_norm(row.name) for row in candidate.fields]
    if len(field_names) != len(set(field_names)):
        error("duplicate field name in Fields table")
    for row in candidate.fields:
        if _norm(row.priority) not in FIELD_PRIORITIES:
            error(f"field '{row.name}' has invalid priority '{row.priority}'")
        if _norm(row.status) not in FIELD_STATUSES:
            error(f"field '{row.name}' has invalid status '{row.status}'")
        if _norm(row.status) in {"present", "absent"}:
            coverage = _coverage(row.coverage)
            if coverage is None and not row.coverage.casefold().startswith("not determinable"):
                error(f"field '{row.name}' needs n/N coverage or 'not determinable — reason'")
            elif coverage:
                found, total = coverage
                if total <= 0 or found > total:
                    error(f"field '{row.name}' has invalid coverage {row.coverage}")
                if _norm(row.status) == "present" and found == 0:
                    error(f"field '{row.name}' is present but coverage is zero")
        if _norm(row.status) == "present" and (not row.storage.strip() or not row.level.strip()):
            error(f"present field '{row.name}' needs Storage and Level")

    declared_fields = {
        _norm(row.name): row for row in criteria.fields if "ignore" not in row.priority
    }
    candidate_fields = {_norm(row.name): row for row in candidate.fields}
    for name, declared in declared_fields.items():
        row = candidate_fields.get(name)
        if row is None:
            error(f"field of interest not addressed: {declared.name}")
        elif "must" in declared.priority and _norm(row.priority) != "must-have":
            error(f"field '{declared.name}' must be marked must-have")

    technical_names = [_norm(row.item) for row in candidate.technical]
    if len(technical_names) != len(set(technical_names)):
        error("duplicate item in Technical details table")
    for item in criteria.technical_items:
        if _norm(item) not in technical_names:
            error(f"technical item not addressed: {item}")
    for row in candidate.technical:
        if not row.value.strip():
            error(f"technical item '{row.item}' has no value or explicit unknown")

    research_channels = [_norm(row.channel) for row in candidate.research]
    if len(research_channels) != len(set(research_channels)):
        error("duplicate channel in Research table")
    for row in candidate.research:
        if _norm(row.channel) not in CHANNELS:
            error(f"unknown Research channel: {row.channel}")
        if not row.outcome.strip():
            error(f"Research channel '{row.channel}' has no outcome")

    source_ids = [row.ident for row in candidate.sources]
    if len(source_ids) != len(set(source_ids)):
        error("duplicate source ID")
    for source in candidate.sources:
        if not SOURCE_ID_RE.match(source.ident):
            error(f"invalid source ID: {source.ident}")
        if not source.description.strip() or not source.location.strip():
            error(f"source {source.ident} needs a description and location")
        if source.retrieved and not re.fullmatch(DATE_RE, source.retrieved.strip()):
            error(f"source {source.ident} has invalid retrieval date: {source.retrieved}")

    review_start = candidate.text.rfind("## Review")
    cited = set(CITATION_RE.findall(candidate.text[:review_start]))
    for source_id in sorted(cited - candidate.source_ids, key=lambda value: int(value[1:])):
        error(f"citation {source_id} is not defined in Sources")

    metadata_result = candidate.check_result("Metadata")
    required_result = candidate.check_result("Required fields")
    raw_result = candidate.check_result("Raw data")
    metadata_evidence = _evidence_level(candidate.summary.get("Metadata evidence", ""))
    raw_evidence = _evidence_level(candidate.summary.get("Raw-data evidence", ""))
    metadata_route = first_token(candidate.summary.get("Metadata route", ""))
    raw_route = first_token(candidate.summary.get("Raw-data route", ""))

    if metadata_result == "pass":
        if metadata_route in {"", "unknown"}:
            error("Metadata pass requires a populated Metadata route")
        if metadata_evidence not in {"route verified", "contents inspected"}:
            error("Metadata pass requires route-verified or contents-inspected evidence")
    if required_result == "pass":
        if metadata_evidence != "contents inspected":
            error("Required fields pass requires contents-inspected metadata evidence")
        for declared in criteria.fields:
            if "must" not in declared.priority:
                continue
            row = candidate_fields.get(_norm(declared.name))
            if row is None or _norm(row.status) != "present":
                error(f"Required fields pass but must-have '{declared.name}' is not present")
                continue
            coverage = _coverage(row.coverage)
            if coverage is None:
                error(f"Required fields pass but '{declared.name}' has no countable coverage")
            elif not _threshold_met(*coverage, declared.threshold):
                error(
                    f"Required fields pass but '{declared.name}' coverage {row.coverage} "
                    f"is below {declared.threshold}"
                )
    if raw_result == "pass":
        if raw_route in {"", "unknown"}:
            error("Raw data pass requires a populated Raw-data route")
        if raw_evidence != "contents inspected":
            error("Raw data pass requires contents-inspected evidence")
    if recommendation == "accept":
        for check_name in CHECK_NAMES:
            if candidate.check_result(check_name) != "pass":
                error(f"accept recommendation while {check_name} check is not pass")

    accepted_or_tier_one = recommendation == "accept" or bool(
        re.match(r"^\s*(?:tier\s*)?1\b", candidate.summary.get("Tier", ""), re.I)
    )
    if accepted_or_tier_one:
        for channel in ("publication", "supplements"):
            if channel not in research_channels:
                error(f"accept or tier-1 candidate must record Research channel '{channel}'")

    for source_id in sorted(candidate.source_ids - cited, key=lambda value: int(value[1:])):
        warning(f"source {source_id} is not cited")
    return issues


def validate_datasheet(
    datasheet_dir: str, review_baseline: str | None = None
) -> tuple[list[Candidate], Criteria, list[Issue]]:
    candidates = load_candidates(datasheet_dir)
    criteria = parse_criteria(datasheet_dir)
    issues: list[Issue] = []

    identities = [candidate.ident.casefold() for candidate in candidates]
    for ident in sorted({value for value in identities if identities.count(value) > 1}):
        issues.append(Issue("ERROR", "datasheet", f"duplicate candidate identifier: {ident}"))
    for candidate in candidates:
        issues.extend(validate_candidate(candidate, criteria))

    if review_baseline:
        baseline = {candidate.name: candidate for candidate in load_candidates(review_baseline)}
        current = {candidate.name: candidate for candidate in candidates}
        for name, before in baseline.items():
            after = current.get(name)
            if after is None:
                issues.append(Issue("ERROR", name, "candidate from Review baseline is missing"))
            elif before.review_text != after.review_text:
                issues.append(Issue("ERROR", name, "human Review block changed byte-for-byte"))
    return candidates, criteria, issues


def format_issues(issues: list[Issue]) -> str:
    lines: list[str] = []
    current = None
    for issue in issues:
        if issue.candidate != current:
            if lines:
                lines.append("")
            lines.append(issue.candidate)
            current = issue.candidate
        lines.append(f"  {issue.severity:<7} {issue.message}")
    return "\n".join(lines)
