#!/usr/bin/env python3
"""Check skill directories against the Agent Skills format and Anthropic's limits.

Run over this repo's own skills:

    python3 scripts/lint_skills.py

Or over any directory containing skill folders:

    python3 scripts/lint_skills.py path/to/skills

The limits come from Anthropic's Agent Skills spec and are the ones that cause a
rejection at upload time.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # no PyYAML: fall back to the parser below
    yaml = None

NAME_MAX = 64
DESCRIPTION_MAX = 1024
NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
RESERVED_WORDS = ("anthropic", "claude")
XML_TAG = re.compile(r"<[a-zA-Z/][^>]*>")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
# Markdown links to files in the skill, e.g. [format](./references/datasheet-format.md).
LOCAL_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)\s]+)")
JUNK_NAMES = {".DS_Store", "__MACOSX", "__pycache__"}


class SkillError(Exception):
    """A skill directory that will not load, or will be rejected on upload."""


def _scalar(raw: str) -> object:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return {"true": True, "false": False, "null": None}.get(raw.lower(), raw)


def _mini_yaml(block: str) -> dict:
    """Parse the small YAML subset that SKILL.md frontmatter actually uses.

    Handles top-level plain, quoted and block scalars, and skips nested mappings such as
    `metadata:`. Anything it does not recognise raises rather than being guessed at.
    Used only when PyYAML is unavailable, so this runs on a bare Python install.
    """
    lines = block.splitlines()
    result: dict[str, object] = {}
    index = 0

    def consume_indented() -> list[str]:
        nonlocal index
        chunk: list[str] = []
        while index < len(lines) and (not lines[index].strip() or lines[index][:1] in " \t"):
            chunk.append(lines[index].strip())
            index += 1
        return chunk

    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line[:1] in " \t":
            raise SkillError(f"frontmatter line {index + 1}: unexpected indentation")
        if ":" not in line:
            raise SkillError(f"frontmatter line {index + 1}: expected 'key: value'")
        key, _, rest = line.partition(":")
        key, rest = key.strip(), rest.strip()
        index += 1

        if rest.startswith((">", "|")):  # block scalar
            chunk = [part for part in consume_indented() if part]
            joined = " ".join(chunk) if rest.startswith(">") else "\n".join(chunk)
            result[key] = joined.strip()
        elif rest:  # scalar, possibly continued on indented lines
            continuation = [part for part in consume_indented() if part]
            value = _scalar(rest)
            result[key] = " ".join([str(value), *continuation]) if continuation else value
        else:  # nested mapping we do not need
            consume_indented()
            result[key] = None

    return result


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        raise SkillError("SKILL.md must open with a YAML frontmatter block delimited by ---")
    if yaml is None:
        return _mini_yaml(match.group(1))
    try:
        loaded = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise SkillError(f"frontmatter is not valid YAML: {error}") from error
    if not isinstance(loaded, dict):
        raise SkillError("frontmatter must be a mapping of keys to values")
    return loaded


def check_name(name: object, directory: Path) -> list[str]:
    problems: list[str] = []
    if not isinstance(name, str) or not name:
        return ["frontmatter must declare a non-empty 'name'"]
    if len(name) > NAME_MAX:
        problems.append(f"name is {len(name)} characters; the limit is {NAME_MAX}")
    if not NAME_PATTERN.fullmatch(name):
        problems.append(f"name {name!r} must use only lowercase letters, numbers and hyphens")
    for word in RESERVED_WORDS:
        if word in name.lower():
            problems.append(f"name may not contain the reserved word {word!r}")
    if name != directory.name:
        problems.append(
            f"name {name!r} does not match its directory {directory.name!r}; "
            "harnesses key on the directory, so the two must agree"
        )
    return problems


def check_description(description: object) -> list[str]:
    if not isinstance(description, str) or not description.strip():
        return ["frontmatter must declare a non-empty 'description'"]
    problems: list[str] = []
    collapsed = " ".join(description.split())
    if len(collapsed) > DESCRIPTION_MAX:
        problems.append(
            f"description is {len(collapsed)} characters; the limit is {DESCRIPTION_MAX}"
        )
    if XML_TAG.search(description):
        problems.append("description may not contain XML tags")
    return problems


def check_links(skill_md: Path, directory: Path) -> list[str]:
    """Relative links must resolve to a file that ships inside the skill."""
    problems: list[str] = []
    for target in LOCAL_LINK.findall(skill_md.read_text(encoding="utf-8")):
        path = (directory / target.split("#", 1)[0]).resolve()
        if not path.exists():
            problems.append(f"SKILL.md links to {target!r}, which does not exist")
        elif directory.resolve() not in path.parents:
            problems.append(f"SKILL.md links to {target!r}, which is outside the skill")
    return problems


def check_junk(directory: Path) -> list[str]:
    junk = sorted(
        str(path.relative_to(directory))
        for path in directory.rglob("*")
        if path.name in JUNK_NAMES
    )
    return [f"remove {name} before publishing" for name in junk]


def check_skill(directory: Path) -> list[str]:
    """Return every problem found in one skill directory. Empty means it is clean."""
    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        return ["no SKILL.md"]
    try:
        frontmatter = parse_frontmatter(skill_md)
    except SkillError as error:
        return [str(error)]
    return [
        *check_name(frontmatter.get("name"), directory),
        *check_description(frontmatter.get("description")),
        *check_links(skill_md, directory),
        *check_junk(directory),
    ]


def find_skills(root: Path) -> list[Path]:
    """Skill directories are the ones holding a SKILL.md, at any depth below root."""
    if (root / "SKILL.md").is_file():
        return [root]
    return sorted(path.parent for path in root.rglob("SKILL.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "skills",
        help="directory to search for skills (default: this repo's skills/)",
    )
    args = parser.parse_args()

    if not args.root.exists():
        print(f"lint_skills.py: {args.root} does not exist", file=sys.stderr)
        return 2

    skills = find_skills(args.root)
    if not skills:
        print(f"lint_skills.py: no SKILL.md found under {args.root}", file=sys.stderr)
        return 2

    failed = 0
    for skill in skills:
        problems = check_skill(skill)
        label = skill.name
        if problems:
            failed += 1
            print(f"FAIL {label}")
            for problem in problems:
                print(f"     {problem}")
        else:
            print(f"ok   {label}")

    print()
    print(f"{len(skills) - failed}/{len(skills)} skills passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
