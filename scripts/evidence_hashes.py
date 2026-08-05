#!/usr/bin/env python3
"""Cross-platform canonical hashing for repository evidence and release packages."""

from __future__ import annotations

import hashlib
from pathlib import Path


TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {".gitattributes", ".gitignore", "LICENSE", "VERSION"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".test-runs"}


def canonical_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_file_sha256(path: Path) -> str:
    return sha256_bytes(canonical_bytes(path))


def raw_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_tree_files(root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def tree_records(root: Path) -> list[dict[str, str | int]]:
    records: list[dict[str, str | int]] = []
    for path in iter_tree_files(root):
        data = canonical_bytes(path)
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_bytes(data),
                "size": len(data),
            }
        )
    return records


def canonical_tree_sha256(root: Path) -> str:
    if not root.is_dir():
        raise ValueError(f"Tree root is not a directory: {root}")
    digest = hashlib.sha256(b"build-engineering-harness-tree-v1\0")
    for record in tree_records(root):
        digest.update(str(record["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(record["size"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(record["sha256"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()
