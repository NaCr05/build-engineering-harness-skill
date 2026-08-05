#!/usr/bin/env python3
"""Build a deterministic, versioned Skill archive and provenance manifest."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import zipfile
from pathlib import Path

from evidence_hashes import (
    canonical_bytes,
    canonical_tree_sha256,
    raw_file_sha256,
    tree_records,
)


SKILL_NAME = "build-engineering-harness"
VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def read_version(root: Path) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"Invalid VERSION value: {version!r}")
    return version


def git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Git did not return a full commit SHA.")
    return commit


def build_release_artifacts(
    root: Path, output_dir: Path, source_commit: str
) -> dict[str, Path | str]:
    root = root.resolve()
    output_dir = output_dir.resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source_commit must be a full lowercase commit SHA.")

    version = read_version(root)
    skill_root = root / "skill" / SKILL_NAME
    records = tree_records(skill_root)
    if not records:
        raise ValueError("Installable Skill package is empty.")

    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"{SKILL_NAME}-v{version}"
    archive_path = output_dir / f"{base_name}.zip"
    checksum_path = output_dir / f"{base_name}.zip.sha256"
    manifest_path = output_dir / f"{base_name}.manifest.json"

    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for record in records:
            source = skill_root / str(record["path"])
            info = zipfile.ZipInfo(
                f"{SKILL_NAME}/{record['path']}",
                date_time=ZIP_TIMESTAMP,
            )
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, canonical_bytes(source), compresslevel=9)

    archive_sha256 = raw_file_sha256(archive_path)
    checksum_path.write_text(
        f"{archive_sha256}  {archive_path.name}\n", encoding="utf-8", newline="\n"
    )

    manifest = {
        "schema_version": 1,
        "name": SKILL_NAME,
        "version": version,
        "source_commit": source_commit,
        "archive": {
            "file": archive_path.name,
            "sha256": archive_sha256,
            "size": archive_path.stat().st_size,
        },
        "package": {
            "root": SKILL_NAME,
            "tree_sha256": canonical_tree_sha256(skill_root),
            "file_count": len(records),
            "files": records,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return {
        "version": version,
        "archive": archive_path,
        "archive_sha256": archive_sha256,
        "checksum": checksum_path,
        "checksum_sha256": raw_file_sha256(checksum_path),
        "manifest": manifest_path,
        "manifest_sha256": raw_file_sha256(manifest_path),
        "package_tree_sha256": canonical_tree_sha256(skill_root),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist"),
        help="Directory for generated release artifacts.",
    )
    parser.add_argument(
        "--source-commit",
        help="Full source commit SHA; defaults to the repository HEAD.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_commit = (args.source_commit or git_commit(args.root.resolve())).lower()
    artifacts = build_release_artifacts(args.root, args.output_dir, source_commit)
    print(f"Version: {artifacts['version']}")
    print(f"Archive: {artifacts['archive']}")
    print(f"Archive SHA-256: {artifacts['archive_sha256']}")
    print(f"Checksum: {artifacts['checksum']}")
    print(f"Manifest: {artifacts['manifest']}")
    print(f"Package tree SHA-256: {artifacts['package_tree_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
