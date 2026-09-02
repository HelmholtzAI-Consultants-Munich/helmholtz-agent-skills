#!/usr/bin/env python3
"""Validate the root marketplace manifest without fetching remote plugins.

Checks that marketplace.json is well-formed, local plugin sources exist, and
declared local skills plus plugin.json name/version agree with the catalog.

    python3 scripts/verify_marketplace.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / ".claude-plugin" / "marketplace.json"


class VerifyError(RuntimeError):
    """Marketplace layout that would not install."""


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VerifyError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise VerifyError(f"{path} must contain a JSON object")
    return value


def relative_dir(raw: str, origin: Path) -> Path:
    if not isinstance(raw, str) or not raw.startswith("./"):
        raise VerifyError(f"relative path must start with './': {raw!r}")
    path = (origin / raw[2:]).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as error:
        raise VerifyError(f"path escapes the repository: {raw!r}") from error
    return path


def check_skills(plugin_root: Path, listed: object, plugin_name: str) -> None:
    if listed is None:
        skills_root = plugin_root / "skills"
        if not skills_root.is_dir():
            raise VerifyError(f"plugin {plugin_name!r} has no skills/ directory")
        found = [p for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]
        if not found:
            raise VerifyError(f"plugin {plugin_name!r} has no SKILL.md under skills/")
        return
    if isinstance(listed, str):
        listed = [listed]
    if not isinstance(listed, list) or not listed or not all(isinstance(item, str) for item in listed):
        raise VerifyError(f"plugin {plugin_name!r} has invalid skills")
    for item in listed:
        skill_dir = relative_dir(item, plugin_root)
        if not (skill_dir / "SKILL.md").is_file():
            raise VerifyError(f"plugin {plugin_name!r} missing {item}/SKILL.md")


def check_local_plugin(entry: dict) -> None:
    name = entry["name"]
    source = entry["source"]
    plugin_root = relative_dir(source, REPO)
    if not plugin_root.is_dir():
        raise VerifyError(f"plugin {name!r} source {source!r} is not a directory")

    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        raise VerifyError(f"plugin {name!r} is missing {manifest_path.relative_to(REPO)}")
    manifest = load_json(manifest_path)
    if manifest.get("name") != name:
        raise VerifyError(
            f"plugin {name!r} disagrees with plugin.json name {manifest.get('name')!r}"
        )
    version = entry.get("version")
    if version is not None and manifest.get("version") != version:
        raise VerifyError(
            f"plugin {name!r} marketplace version {version!r} "
            f"does not match plugin.json {manifest.get('version')!r}"
        )
    check_skills(plugin_root, entry.get("skills"), name)


def check_remote_plugin(entry: dict) -> None:
    name = entry["name"]
    source = entry["source"]
    kind = source.get("source")
    if kind == "github":
        if not isinstance(source.get("repo"), str) or "/" not in source["repo"]:
            raise VerifyError(f"plugin {name!r} github source needs owner/repo")
    elif kind == "url":
        url = source.get("url")
        if not isinstance(url, str) or not url:
            raise VerifyError(f"plugin {name!r} url source is missing url")
    elif kind == "git-subdir":
        url = source.get("url")
        path = source.get("path")
        if not isinstance(url, str) or not url:
            raise VerifyError(f"plugin {name!r} git-subdir source is missing url")
        if not isinstance(path, str) or not path or path.startswith("/"):
            raise VerifyError(f"plugin {name!r} git-subdir source has an invalid path")
        if entry.get("strict") is not False:
            raise VerifyError(
                f"plugin {name!r} is a skill-only git-subdir and must set strict: false"
            )
    else:
        raise VerifyError(f"plugin {name!r} has unsupported source type {kind!r}")


def verify() -> None:
    marketplace = load_json(MANIFEST)
    name = marketplace.get("name")
    if not isinstance(name, str) or not name:
        raise VerifyError(f"{MANIFEST} is missing name")
    owner = marketplace.get("owner")
    if not isinstance(owner, dict) or not isinstance(owner.get("name"), str):
        raise VerifyError(f"{MANIFEST} is missing owner.name")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise VerifyError(f"{MANIFEST} must declare at least one plugin")

    names: list[str] = []
    for entry in plugins:
        if not isinstance(entry, dict):
            raise VerifyError("each plugin entry must be an object")
        plugin_name = entry.get("name")
        if not isinstance(plugin_name, str) or not plugin_name:
            raise VerifyError("plugin is missing a name")
        names.append(plugin_name)
        source = entry.get("source")
        if isinstance(source, str):
            check_local_plugin(entry)
        elif isinstance(source, dict):
            check_remote_plugin(entry)
        else:
            raise VerifyError(f"plugin {plugin_name!r} is missing source")

    if len(names) != len(set(names)):
        raise VerifyError(f"{MANIFEST} has duplicate plugin names")


def main() -> int:
    try:
        verify()
    except VerifyError as error:
        print(f"verify_marketplace.py: {error}", file=sys.stderr)
        return 1
    print("Marketplace validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
