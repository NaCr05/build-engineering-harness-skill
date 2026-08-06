#!/usr/bin/env python3
"""Safely install or upgrade Build Engineering Harness from verified release assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath


SKILL_NAME = "build-engineering-harness"
DEFAULT_REPOSITORY = "NaCr05/build-engineering-harness-skill"
VERSION_PATTERN = re.compile(r"v?[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
INSTALLER_FILES = {"install_skill.py", "install.ps1", "install.sh"}
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
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


class InstallError(RuntimeError):
    """An installation input or filesystem operation failed safely."""


def raw_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def canonical_file_sha256(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def canonical_tree_sha256(root: Path) -> str:
    digest = hashlib.sha256(b"build-engineering-harness-tree-v1\0")
    files = sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    for path in files:
        relative = path.relative_to(root).as_posix()
        data = canonical_bytes(path)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def load_manifest(asset_dir: Path, version: str | None) -> tuple[Path, dict]:
    if version:
        normalized = version.removeprefix("v")
        manifest_path = asset_dir / f"{SKILL_NAME}-v{normalized}.manifest.json"
        candidates = [manifest_path] if manifest_path.is_file() else []
    else:
        candidates = sorted(asset_dir.glob(f"{SKILL_NAME}-v*.manifest.json"))
    if len(candidates) != 1:
        raise InstallError(
            "Expected exactly one matching release manifest in the asset directory."
        )
    manifest_path = candidates[0]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"Release manifest is unreadable: {exc}") from exc
    if not isinstance(manifest, dict):
        raise InstallError("Release manifest root must be an object.")
    return manifest_path, manifest


def validate_manifest(manifest: dict, requested_version: str | None) -> None:
    if manifest.get("schema_version") != 2:
        raise InstallError("Release manifest must use schema version 2.")
    if manifest.get("name") != SKILL_NAME:
        raise InstallError("Release manifest names an unexpected Skill.")
    version = manifest.get("version")
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise InstallError("Release manifest contains an invalid version.")
    if requested_version and version != requested_version.removeprefix("v"):
        raise InstallError("Release manifest version does not match the requested version.")

    archive = manifest.get("archive")
    package = manifest.get("package")
    installers = manifest.get("installers")
    if not isinstance(archive, dict) or set(archive) != {"file", "sha256", "size"}:
        raise InstallError("Release manifest archive record is incomplete.")
    if not isinstance(package, dict) or set(package) != {
        "root",
        "tree_sha256",
        "file_count",
        "files",
    }:
        raise InstallError("Release manifest package record is incomplete.")
    if package.get("root") != SKILL_NAME:
        raise InstallError("Release manifest package root is unexpected.")
    if not isinstance(package.get("tree_sha256"), str) or not SHA256_PATTERN.fullmatch(
        package["tree_sha256"]
    ):
        raise InstallError("Release manifest package tree hash is invalid.")
    if not isinstance(installers, list) or len(installers) != len(INSTALLER_FILES):
        raise InstallError("Release manifest must describe all installer assets.")


def validate_file_record(record: object, *, expected_path: str | None = None) -> dict:
    if not isinstance(record, dict) or set(record) != {"path", "sha256", "size"}:
        raise InstallError("Manifest file record is malformed.")
    path = record.get("path")
    digest = record.get("sha256")
    size = record.get("size")
    if not isinstance(path, str) or not path or "\\" in path:
        raise InstallError("Manifest file path is invalid.")
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise InstallError("Manifest file path is unsafe.")
    for part in pure.parts:
        base_name = part.split(".", 1)[0].upper()
        if (
            "\x00" in part
            or ":" in part
            or part.endswith((" ", "."))
            or base_name in WINDOWS_RESERVED_NAMES
        ):
            raise InstallError("Manifest file path is not cross-platform safe.")
    if expected_path is not None and path != expected_path:
        raise InstallError("Manifest file path does not match its expected location.")
    if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
        raise InstallError("Manifest file hash is invalid.")
    if not isinstance(size, int) or size < 0:
        raise InstallError("Manifest file size is invalid.")
    return record


def verify_installer_assets(asset_dir: Path, manifest: dict) -> None:
    records: dict[str, dict] = {}
    for raw_record in manifest["installers"]:
        record = validate_file_record(raw_record)
        name = str(record["path"])
        if name in records:
            raise InstallError("Release manifest repeats an installer asset.")
        records[name] = record
    if set(records) != INSTALLER_FILES:
        raise InstallError("Release manifest installer set is unexpected.")
    for name, record in records.items():
        path = asset_dir / name
        if not path.is_file():
            raise InstallError(f"Required installer asset is missing: {name}")
        if path.stat().st_size != record["size"]:
            raise InstallError(f"Installer size mismatch: {name}")
        if canonical_file_sha256(path) != record["sha256"]:
            raise InstallError(f"Installer hash mismatch: {name}")


def verify_archive_assets(asset_dir: Path, manifest: dict) -> Path:
    archive_record = manifest["archive"]
    archive_name = archive_record.get("file")
    if not isinstance(archive_name, str) or Path(archive_name).name != archive_name:
        raise InstallError("Release manifest archive filename is unsafe.")
    archive_path = asset_dir / archive_name
    if not archive_path.is_file():
        raise InstallError(f"Release archive is missing: {archive_name}")
    if archive_path.stat().st_size != archive_record.get("size"):
        raise InstallError("Release archive size does not match its manifest.")
    archive_hash = raw_file_sha256(archive_path)
    if archive_hash != archive_record.get("sha256"):
        raise InstallError("Release archive hash does not match its manifest.")

    checksum_path = asset_dir / f"{archive_name}.sha256"
    if not checksum_path.is_file():
        raise InstallError("Release checksum file is missing.")
    checksum_fields = checksum_path.read_text(encoding="utf-8").strip().split()
    if checksum_fields != [archive_hash, archive_name]:
        raise InstallError("Release checksum file does not match the verified archive.")
    return archive_path


def validated_archive_members(
    archive: zipfile.ZipFile, manifest: dict
) -> list[tuple[zipfile.ZipInfo, dict]]:
    records: dict[str, dict] = {}
    for raw_record in manifest["package"]["files"]:
        record = validate_file_record(raw_record)
        package_path = f"{SKILL_NAME}/{record['path']}"
        if package_path in records:
            raise InstallError("Release manifest repeats a package path.")
        records[package_path] = record
    if manifest["package"].get("file_count") != len(records) or not records:
        raise InstallError("Release manifest package file count is invalid.")

    members = archive.infolist()
    names = [member.filename for member in members]
    if len(names) != len(set(names)):
        raise InstallError("Release archive contains duplicate paths.")
    if set(names) != set(records):
        raise InstallError("Release archive layout does not match its manifest.")

    validated: list[tuple[zipfile.ZipInfo, dict]] = []
    for member in members:
        if member.is_dir() or "\\" in member.filename:
            raise InstallError("Release archive contains an unsafe path.")
        pure = PurePosixPath(member.filename)
        if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
            raise InstallError("Release archive contains an unsafe path.")
        mode = member.external_attr >> 16
        if stat.S_ISLNK(mode) or (mode and not stat.S_ISREG(mode)):
            raise InstallError("Release archive contains a link or special file.")
        record = records[member.filename]
        if member.file_size != record["size"]:
            raise InstallError("Release archive member size does not match its manifest.")
        validated.append((member, record))
    return validated


def extract_verified_archive(archive_path: Path, manifest: dict, staging: Path) -> Path:
    staging.mkdir(parents=False, exist_ok=False)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = validated_archive_members(archive, manifest)
            for member, record in members:
                destination = staging.joinpath(*PurePosixPath(member.filename).parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                data = archive.read(member)
                if hashlib.sha256(data).hexdigest() != record["sha256"]:
                    raise InstallError(
                        f"Release archive member hash mismatch: {member.filename}"
                    )
                destination.write_bytes(data)
        package_root = staging / SKILL_NAME
        if not package_root.is_dir():
            raise InstallError("Verified archive did not produce the expected package root.")
        if canonical_tree_sha256(package_root) != manifest["package"]["tree_sha256"]:
            raise InstallError("Extracted package tree hash does not match its manifest.")
        return package_root
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def resolve_codex_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser().resolve() if configured else Path.home() / ".codex"


def download_release_assets(repository: str, version: str, destination: Path) -> None:
    if not VERSION_PATTERN.fullmatch(version):
        raise InstallError("Requested version is invalid.")
    tag = version if version.startswith("v") else f"v{version}"
    normalized = tag.removeprefix("v")
    patterns = [
        f"{SKILL_NAME}-v{normalized}.zip",
        f"{SKILL_NAME}-v{normalized}.zip.sha256",
        f"{SKILL_NAME}-v{normalized}.manifest.json",
        *sorted(INSTALLER_FILES),
    ]
    command = ["gh", "release", "download", tag, "--repo", repository, "--dir", str(destination)]
    for pattern in patterns:
        command.extend(["--pattern", pattern])
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise InstallError("GitHub CLI is required for release downloads.") from exc
    except subprocess.CalledProcessError as exc:
        raise InstallError(f"GitHub Release download failed with exit code {exc.returncode}.") from exc


def install_from_assets(
    asset_dir: Path,
    codex_home: Path,
    *,
    version: str | None = None,
    dry_run: bool = False,
    fail_after_backup: bool = False,
) -> dict[str, str | None]:
    asset_dir = asset_dir.resolve()
    manifest_path, manifest = load_manifest(asset_dir, version)
    validate_manifest(manifest, version)
    verify_installer_assets(asset_dir, manifest)
    archive_path = verify_archive_assets(asset_dir, manifest)

    skills_dir = codex_home.resolve() / "skills"
    target = skills_dir / SKILL_NAME
    staging = skills_dir / f".beh-stage-{uuid.uuid4().hex[:12]}"
    backup = skills_dir / f".beh-backup-{uuid.uuid4().hex[:12]}"

    if dry_run:
        with tempfile.TemporaryDirectory() as directory:
            probe = Path(directory) / "stage"
            extract_verified_archive(archive_path, manifest, probe)
        return {
            "version": str(manifest["version"]),
            "manifest": str(manifest_path),
            "target": str(target),
            "backup": None,
            "mode": "dry-run",
        }

    is_junction = getattr(skills_dir, "is_junction", lambda: False)
    if skills_dir.is_symlink() or is_junction():
        raise InstallError("The Codex skills directory must not be a link or junction.")
    skills_dir.mkdir(parents=True, exist_ok=True)
    target_is_junction = getattr(target, "is_junction", lambda: False)
    if target.is_symlink() or target_is_junction() or (
        target.exists() and not target.is_dir()
    ):
        raise InstallError("Existing Skill target must be a real directory.")

    package_root = extract_verified_archive(archive_path, manifest, staging)
    backup_created = False
    try:
        if target.exists():
            os.replace(target, backup)
            backup_created = True
        if fail_after_backup:
            raise InstallError("Injected post-backup failure.")
        os.replace(package_root, target)
        shutil.rmtree(staging, ignore_errors=True)
    except Exception as exc:
        shutil.rmtree(staging, ignore_errors=True)
        if backup_created:
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            os.replace(backup, target)
        if isinstance(exc, InstallError):
            raise
        raise InstallError(f"Installation failed and rollback was attempted: {exc}") from exc

    return {
        "version": str(manifest["version"]),
        "manifest": str(manifest_path),
        "target": str(target),
        "backup": str(backup) if backup_created else None,
        "mode": "installed",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Pinned release version, for example v0.3.2-beta.")
    parser.add_argument("--repo", default=DEFAULT_REPOSITORY, help="GitHub owner/repository.")
    parser.add_argument("--asset-dir", type=Path, help="Use already-downloaded release assets.")
    parser.add_argument("--codex-home", help="Override CODEX_HOME for the installation target.")
    parser.add_argument("--dry-run", action="store_true", help="Verify and show the plan without installing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.asset_dir:
            result = install_from_assets(
                args.asset_dir,
                resolve_codex_home(args.codex_home),
                version=args.version,
                dry_run=args.dry_run,
            )
        else:
            if not args.version:
                raise InstallError("--version is required when downloading a release.")
            with tempfile.TemporaryDirectory() as directory:
                asset_dir = Path(directory)
                download_release_assets(args.repo, args.version, asset_dir)
                result = install_from_assets(
                    asset_dir,
                    resolve_codex_home(args.codex_home),
                    version=args.version,
                    dry_run=args.dry_run,
                )
        print(f"Mode: {result['mode']}")
        print(f"Version: {result['version']}")
        print(f"Target: {result['target']}")
        if result["backup"]:
            print(f"Previous installation backup: {result['backup']}")
        if result["mode"] == "installed":
            print("Start a new Codex task to reload the Skill catalog.")
        return 0
    except (InstallError, OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
