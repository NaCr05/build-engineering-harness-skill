from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_release_package import (  # noqa: E402
    build_release_artifacts,
    read_version,
    validate_source_commit,
)
from compare_release_artifacts import compare_release_directories  # noqa: E402
from evidence_hashes import canonical_bytes, iter_tree_files, raw_file_sha256  # noqa: E402


class ReleasePackagingTests(unittest.TestCase):
    source_commit = "a" * 40

    def test_release_archive_is_deterministic_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = build_release_artifacts(
                REPO_ROOT, Path(first_dir), self.source_commit, verify_source=False
            )
            second = build_release_artifacts(
                REPO_ROOT, Path(second_dir), self.source_commit, verify_source=False
            )

            self.assertEqual(first["archive_sha256"], second["archive_sha256"])
            self.assertEqual(
                raw_file_sha256(Path(first["manifest"])),
                raw_file_sha256(Path(second["manifest"])),
            )

            skill_root = REPO_ROOT / "skill/build-engineering-harness"
            expected = {
                f"build-engineering-harness/{path.relative_to(skill_root).as_posix()}": canonical_bytes(path)
                for path in iter_tree_files(skill_root)
            }
            with zipfile.ZipFile(Path(first["archive"])) as archive:
                actual_names = archive.namelist()
                self.assertEqual(sorted(expected), actual_names)
                for name, content in expected.items():
                    self.assertEqual(content, archive.read(name))
                    self.assertEqual((1980, 1, 1, 0, 0, 0), archive.getinfo(name).date_time)

    def test_manifest_and_checksum_describe_the_archive(self) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            artifacts = build_release_artifacts(
                REPO_ROOT, Path(output_dir), self.source_commit, verify_source=False
            )
            manifest = json.loads(Path(artifacts["manifest"]).read_text(encoding="utf-8"))
            archive = Path(artifacts["archive"])
            checksum = Path(artifacts["checksum"]).read_text(encoding="utf-8")

            self.assertEqual(2, manifest["schema_version"])
            self.assertEqual(read_version(REPO_ROOT), manifest["version"])
            self.assertEqual(self.source_commit, manifest["source_commit"])
            self.assertEqual(raw_file_sha256(archive), manifest["archive"]["sha256"])
            self.assertEqual(
                f"{manifest['archive']['sha256']}  {archive.name}\n", checksum
            )
            self.assertEqual(7, manifest["package"]["file_count"])
            self.assertEqual(
                {"install.ps1", "install.sh", "install_skill.py"},
                {record["path"] for record in manifest["installers"]},
            )

    def test_cross_platform_comparison_rejects_any_byte_difference(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left = build_release_artifacts(
                REPO_ROOT, Path(left_dir), self.source_commit, verify_source=False
            )
            build_release_artifacts(
                REPO_ROOT, Path(right_dir), self.source_commit, verify_source=False
            )

            hashes = compare_release_directories(
                REPO_ROOT, Path(left_dir), Path(right_dir)
            )
            self.assertEqual(6, len(hashes))

            checksum = Path(right_dir) / Path(left["checksum"]).name
            checksum.write_text(
                checksum.read_text(encoding="utf-8") + "tampered\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Cross-platform artifact mismatch"):
                compare_release_directories(REPO_ROOT, Path(left_dir), Path(right_dir))

    def test_tree_hashing_rejects_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.txt"
            link = root / "linked.txt"
            target.write_text("safe\n", encoding="utf-8")
            try:
                os.symlink(target, link)
            except OSError as exc:
                self.skipTest(f"Symbolic links are unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "symbolic link or junction"):
                iter_tree_files(root)

    def test_source_commit_must_exist_and_match_package_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_root = root / "skill/build-engineering-harness"
            skill_root.mkdir(parents=True)
            (root / "VERSION").write_text("0.0.0-test\n", encoding="utf-8")
            (skill_root / "SKILL.md").write_text("test\n", encoding="utf-8")

            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "test@example.invalid"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.name", "Test"], check=True
            )
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-q", "-m", "fixture"], check=True
            )
            commit = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            validate_source_commit(root, commit)
            with self.assertRaisesRegex(ValueError, "does not identify a local commit"):
                validate_source_commit(root, "f" * 40)

            (root / "VERSION").write_text("0.0.1-test\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "do not match source_commit"):
                validate_source_commit(root, commit)


if __name__ == "__main__":
    unittest.main()
