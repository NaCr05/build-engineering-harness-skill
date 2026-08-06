#!/usr/bin/env python3
"""Require release-relevant pull requests to update CHANGELOG.md."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


CHANGELOG_PATH = "CHANGELOG.md"
RELEASE_RELEVANT_EXACT = {
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.en.md",
    "README.md",
    "SECURITY.md",
    "VERSION",
}
RELEASE_RELEVANT_PREFIXES = (
    ".github/ISSUE_TEMPLATE/",
    ".github/workflows/",
    "scripts/",
    "skill/",
    "tests/",
)


def normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/")


def is_release_relevant(path: str) -> bool:
    normalized = normalize_path(path)
    return normalized in RELEASE_RELEVANT_EXACT or normalized.startswith(
        RELEASE_RELEVANT_PREFIXES
    )


def missing_changelog_update(changed_paths: list[str]) -> list[str]:
    normalized = [normalize_path(path) for path in changed_paths if path.strip()]
    relevant = sorted(
        path
        for path in normalized
        if path != CHANGELOG_PATH and is_release_relevant(path)
    )
    if not relevant or CHANGELOG_PATH in normalized:
        return []
    return relevant


def unreleased_has_changes(content: str) -> bool:
    match = re.search(
        r"^## \[Unreleased\]\s*(.*?)(?=^## \[|\Z)",
        content.replace("\r\n", "\n"),
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return False
    body = match.group(1).strip()
    return bool(body) and body != "No unreleased changes."


def git_changed_paths(root: Path, base_ref: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "diff",
            "--name-only",
            "--no-renames",
            f"{base_ref}...HEAD",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_file_at_ref(root: Path, ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{ref}:{path}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


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
    root = args.root.resolve()
    changed_paths = git_changed_paths(root, args.base_ref)
    missing_for = missing_changelog_update(changed_paths)
    if missing_for:
        print(
            "ERROR: release-relevant changes require a CHANGELOG.md update under "
            "the Unreleased section:",
            file=sys.stderr,
        )
        for path in missing_for:
            print(f"  - {path}", file=sys.stderr)
        return 1

    relevant = [path for path in changed_paths if is_release_relevant(path)]
    version_changed = "VERSION" in {normalize_path(path) for path in changed_paths}
    if relevant and not version_changed and not unreleased_has_changes(
        (root / CHANGELOG_PATH).read_text(encoding="utf-8")
    ):
        print(
            "ERROR: release-relevant changes without a version bump require a "
            "substantive entry under CHANGELOG.md [Unreleased].",
            file=sys.stderr,
        )
        return 1

    if version_changed:
        current_version = (root / "VERSION").read_text(encoding="utf-8").strip()
        base_version = git_file_at_ref(root, args.base_ref, "VERSION").strip()
        if current_version == base_version:
            print(
                "ERROR: VERSION is listed as changed but its semantic value did not change.",
                file=sys.stderr,
            )
            return 1
    print("CHANGELOG.md is synchronized with release-relevant pull-request changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
