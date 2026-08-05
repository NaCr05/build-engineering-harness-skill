#!/usr/bin/env python3
"""Reject changes to committed forward-test run evidence."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


RUN_PATH = re.compile(
    r"^tests/scenarios/[^/]+/runs/[^/]+/(?:response\.md|result\.json)$"
)


@dataclass(frozen=True)
class Change:
    status: str
    path: str


def parse_name_status(output: str) -> list[Change]:
    changes: list[Change] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) != 2:
            raise ValueError(f"Unexpected git diff record: {line!r}")
        changes.append(Change(fields[0], fields[1].replace("\\", "/")))
    return changes


def forbidden_run_changes(changes: list[Change]) -> list[Change]:
    return [
        change
        for change in changes
        if RUN_PATH.fullmatch(change.path) and change.status != "A"
    ]


def git_changes(root: Path, base_ref: str) -> list[Change]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "diff",
            "--name-status",
            "--no-renames",
            f"{base_ref}...HEAD",
            "--",
            "tests/scenarios/*/runs/*/response.md",
            "tests/scenarios/*/runs/*/result.json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return parse_name_status(result.stdout)


def check_append_only(root: Path, base_ref: str) -> list[Change]:
    return forbidden_run_changes(git_changes(root.resolve(), base_ref))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True, help="Git base ref, for example origin/main.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    forbidden = check_append_only(args.root, args.base_ref)
    if forbidden:
        for change in forbidden:
            print(
                f"ERROR: historical run evidence is append-only: "
                f"{change.status}\t{change.path}",
                file=sys.stderr,
            )
        return 1
    print("Forward-test run history is append-only relative to the base ref.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
