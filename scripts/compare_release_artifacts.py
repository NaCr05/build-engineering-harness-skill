#!/usr/bin/env python3
"""Compare two independently built release-package directories byte for byte."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_release_package import SKILL_NAME, read_version
from evidence_hashes import raw_file_sha256


def expected_artifact_names(root: Path) -> set[str]:
    version = read_version(root)
    base_name = f"{SKILL_NAME}-v{version}"
    return {
        f"{base_name}.zip",
        f"{base_name}.zip.sha256",
        f"{base_name}.manifest.json",
        "install.ps1",
        "install.sh",
        "install_skill.py",
    }


def compare_release_directories(root: Path, left: Path, right: Path) -> dict[str, str]:
    expected = expected_artifact_names(root)
    left_names = {path.name for path in left.iterdir() if path.is_file()}
    right_names = {path.name for path in right.iterdir() if path.is_file()}
    if left_names != expected:
        raise ValueError(f"Left artifact set mismatch: {sorted(left_names)}")
    if right_names != expected:
        raise ValueError(f"Right artifact set mismatch: {sorted(right_names)}")

    hashes: dict[str, str] = {}
    for name in sorted(expected):
        left_hash = raw_file_sha256(left / name)
        right_hash = raw_file_sha256(right / name)
        if left_hash != right_hash:
            raise ValueError(
                f"Cross-platform artifact mismatch for {name}: {left_hash} != {right_hash}"
            )
        hashes[name] = left_hash
    return hashes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path, help="First artifact directory.")
    parser.add_argument("right", type=Path, help="Second artifact directory.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root containing VERSION.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hashes = compare_release_directories(
        args.root.resolve(), args.left.resolve(), args.right.resolve()
    )
    print("Cross-platform release artifacts are byte-identical:")
    for name, digest in hashes.items():
        print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
