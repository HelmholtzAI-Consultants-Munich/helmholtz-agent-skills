#!/usr/bin/env python3
"""Create, validate, and build dataset-scouting datasheets."""

from __future__ import annotations

import argparse
import sys

from datasheet_lib.markdown import DatasheetError, scaffold_candidates
from datasheet_lib.validate import format_issues, validate_datasheet
from datasheet_lib.workbook import build_workbook


def cmd_new(args: argparse.Namespace) -> int:
    for message in scaffold_candidates(args.datasheet_dir, args.identifiers):
        print(message)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    candidates, _, issues = validate_datasheet(
        args.datasheet_dir, review_baseline=args.review_baseline
    )
    if issues:
        print(format_issues(issues))
    errors = sum(issue.severity == "ERROR" for issue in issues)
    warnings = len(issues) - errors
    print(f"{len(candidates)} candidates · {errors} error · {warnings} warning")
    return 1 if errors else 0


def cmd_build(args: argparse.Namespace) -> int:
    candidates, criteria, issues = validate_datasheet(args.datasheet_dir)
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    if issues:
        print(format_issues(issues))
    if errors:
        print(f"build stopped: {len(errors)} validation error(s)", file=sys.stderr)
        return 1
    out = build_workbook(args.datasheet_dir, candidates, criteria)
    print(f"built and verified {out} · {len(candidates)} candidates")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="scaffold one or more candidate records")
    new.add_argument("datasheet_dir")
    new.add_argument("identifiers", nargs="+")
    new.set_defaults(func=cmd_new)

    check = commands.add_parser("check", help="validate the datasheet")
    check.add_argument("datasheet_dir")
    check.add_argument(
        "--review-baseline",
        help="datasheet whose human Review blocks must remain byte-identical",
    )
    check.set_defaults(func=cmd_check)

    build = commands.add_parser("build", help="validate, generate, and verify datasheet.xlsx")
    build.add_argument("datasheet_dir")
    build.set_defaults(func=cmd_build)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.func(args)
    except DatasheetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
