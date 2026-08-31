#!/usr/bin/env python3
"""Build one Claude Science upload archive per public skill.

Claude Science cannot install from git; skills get there as ZIP uploads, one skill
per ZIP. Public sources are fetched at build time rather than vendored, so there is
no committed copy to go stale.

    python3 scripts/build_zips.py              # -> dist/*.zip + dist/RELEASE_NOTES.md
    python3 scripts/build_zips.py --only biotope

Embargoed and gated sources are skipped: CI has no credentials for them, and their
content must not reach a public release. Build those from a local checkout instead.

    python3 scripts/build_zips.py --source-root /path/to/checkout --only hmgu-hpc
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_skills import check_skill  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
SKIP_NAMES = {".DS_Store", "__MACOSX", "__pycache__", ".git", ".pytest_cache"}

# Content that identifies the gated tier. A published release cannot be recalled, so
# a public archive is checked for these before it is written.
GATED_MARKERS = ("scidom.de", "hpc-submit", "ascgitlab", "digit-hpc@", "/lustre/groups")


class BuildError(RuntimeError):
    """Anything that should stop the build rather than produce a wrong archive."""


def load_registry() -> dict:
    return json.loads((REPO / "sources.json").read_text(encoding="utf-8"))


def clone(url: str, ref: str, destination: Path) -> str:
    """Shallow-clone one ref and return the commit it resolved to."""
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", ref, "--quiet", url, str(destination)],
            check=True,
            capture_output=True,
            text=True,
        )
        resolved = subprocess.run(
            ["git", "-C", str(destination), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        raise BuildError(f"could not clone {url} at {ref}: {detail}") from error
    return resolved.stdout.strip()


def discover_skills(root: Path) -> list[Path]:
    """A skill is a directory holding a SKILL.md, one level below root (or root itself)."""
    if (root / "SKILL.md").is_file():
        return [root]
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())


def shipped_files(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and not any(part in SKIP_NAMES for part in path.relative_to(directory).parts)
    )


def check_no_gated_content(skill: str, files: list[Path], directory: Path) -> None:
    hits: list[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary asset: nothing to match against
        for marker in GATED_MARKERS:
            if marker in text:
                hits.append(f"{path.relative_to(directory)} contains {marker!r}")
    if hits:
        raise BuildError(
            f"{skill}: refusing to publish, gated content found:\n    "
            + "\n    ".join(hits)
            + "\n  Remove it, or drop this skill to the gated tier in sources.json."
        )


def write_archive(skill_dir: Path, source: dict, commit: str | None, output: Path) -> None:
    name = skill_dir.name
    files = shipped_files(skill_dir)
    # Public tier only: building a gated skill's own archive is a supported operation,
    # and that archive contains gated content by definition.
    if source["tier"] == "public":
        check_no_gated_content(name, files, skill_dir)

    provenance = {
        "skill": name,
        "source": source["name"],
        "repository": source.get("homepage") or source.get("url"),
        "ref": source.get("ref"),
        "commit": commit,
        "builtAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "Re-download and re-upload if this commit is older than the source.",
    }

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(f"{name}/{path.relative_to(skill_dir).as_posix()}", ZIP_TIME)
            info.external_attr = (0o755 if path.stat().st_mode & 0o100 else 0o644) << 16
            archive.writestr(info, path.read_bytes())
        info = zipfile.ZipInfo(f"{name}/PROVENANCE.json", ZIP_TIME)
        info.external_attr = 0o644 << 16
        archive.writestr(info, json.dumps(provenance, indent=2) + "\n")


def head_commit(repo: Path) -> str | None:
    """The commit a local checkout is on, so an uploaded archive can be dated."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, OSError):
        return None  # not a checkout, or no commits yet
    return result.stdout.strip()


def resolve_root(source: dict, workspace: Path, source_root: Path | None) -> tuple[Path, str | None]:
    """Return the directory holding this source's skills, and the commit it came from."""
    if source_root is not None:
        return source_root / source.get("path", "."), head_commit(source_root)
    if source["type"] == "local":
        return REPO / source["path"], head_commit(REPO)
    checkout = workspace / source["name"]
    commit = clone(source["url"], source.get("ref", "main"), checkout)
    return checkout / source.get("path", "."), commit


def build_source(source: dict, workspace: Path, dist: Path, source_root: Path | None) -> list[dict]:
    root, commit = resolve_root(source, workspace, source_root)
    if not root.is_dir():
        raise BuildError(f"{source['name']}: {root} is not a directory")

    skills = discover_skills(root)
    if not skills:
        raise BuildError(f"{source['name']}: no SKILL.md found under {root}")

    found = sorted(skill.name for skill in skills)
    declared = sorted(source.get("skills", []))
    if declared and found != declared:
        raise BuildError(
            f"{source['name']}: sources.json declares {declared} but the source has {found}; "
            "update sources.json"
        )

    built: list[dict] = []
    for skill_dir in skills:
        problems = check_skill(skill_dir)
        if problems:
            raise BuildError(
                f"{skill_dir.name}: fails validation, refusing to package:\n    "
                + "\n    ".join(problems)
            )
        output = dist / f"{skill_dir.name}.zip"
        write_archive(skill_dir, source, commit, output)
        built.append({"skill": skill_dir.name, "source": source["name"], "commit": commit})
        print(f"  built {output.name}", flush=True)
    return built


def release_notes(built: list[dict], registry: dict) -> str:
    by_source = {source["name"]: source for source in registry["sources"]}
    lines = [
        "# Claude Science skill archives",
        "",
        "One ZIP per skill. In Claude Science or claude.ai, go to **Customize > Skills**,",
        "add a skill, and upload the ZIP **without extracting it first**.",
        "",
        "| Skill | From | Commit |",
        "|---|---|---|",
    ]
    for entry in built:
        source = by_source.get(entry["source"], {})
        home = source.get("homepage")
        origin = f"[{entry['source']}]({home})" if home else entry["source"]
        commit = f"`{entry['commit'][:8]}`" if entry["commit"] else "local"
        lines.append(f"| `{entry['skill']}` | {origin} | {commit} |")
    lines += [
        "",
        "Each archive carries a `PROVENANCE.json` naming the commit it was built from,",
        "so you can tell whether an uploaded copy is still current.",
        "",
        "Skills in the embargoed and gated tiers are not published here; build those from",
        "their own repository.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", action="append", metavar="SOURCE", help="build just this source (repeatable)")
    parser.add_argument("--dist", type=Path, default=REPO / "dist", help="output directory (default: dist/)")
    parser.add_argument(
        "--source-root",
        type=Path,
        help="use this local checkout instead of cloning; requires a single --only",
    )
    args = parser.parse_args()

    registry = load_registry()
    sources = registry["sources"]

    if args.source_root and (not args.only or len(args.only) != 1):
        print("build_zips.py: --source-root needs exactly one --only", file=sys.stderr)
        return 2

    if args.only:
        names = {source["name"] for source in sources}
        unknown = sorted(set(args.only) - names)
        if unknown:
            print(f"build_zips.py: unknown source(s) {unknown}; known: {sorted(names)}", file=sys.stderr)
            return 2
        selected = [source for source in sources if source["name"] in args.only]
    else:
        selected = [source for source in sources if source["tier"] == "public"]

    skipped = [source for source in selected if source.get("pending")]
    selected = [source for source in selected if not source.get("pending")]
    if not selected:
        print("build_zips.py: nothing to build", file=sys.stderr)
        return 2

    if args.dist.exists():
        shutil.rmtree(args.dist)
    args.dist.mkdir(parents=True)

    built: list[dict] = []
    try:
        with tempfile.TemporaryDirectory(prefix="ass-build-") as temporary:
            for source in selected:
                print(f"{source['name']} ({source['tier']})", flush=True)
                built += build_source(source, Path(temporary), args.dist, args.source_root)
    except BuildError as error:
        print(f"\nbuild_zips.py: {error}", file=sys.stderr)
        return 1

    (args.dist / "RELEASE_NOTES.md").write_text(release_notes(built, registry), encoding="utf-8")

    print()
    for source in skipped:
        print(f"skipped {source['name']}: {source['pending']}")
    print(f"{len(built)} archive(s) in {args.dist}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
