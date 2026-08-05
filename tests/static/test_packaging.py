from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_release_package import build_release_artifacts, read_version  # noqa: E402
from evidence_hashes import canonical_bytes, iter_tree_files, raw_file_sha256  # noqa: E402


class ReleasePackagingTests(unittest.TestCase):
    source_commit = "a" * 40

    def test_release_archive_is_deterministic_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = build_release_artifacts(
                REPO_ROOT, Path(first_dir), self.source_commit
            )
            second = build_release_artifacts(
                REPO_ROOT, Path(second_dir), self.source_commit
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
                REPO_ROOT, Path(output_dir), self.source_commit
            )
            manifest = json.loads(Path(artifacts["manifest"]).read_text(encoding="utf-8"))
            archive = Path(artifacts["archive"])
            checksum = Path(artifacts["checksum"]).read_text(encoding="utf-8")

            self.assertEqual(1, manifest["schema_version"])
            self.assertEqual(read_version(REPO_ROOT), manifest["version"])
            self.assertEqual(self.source_commit, manifest["source_commit"])
            self.assertEqual(raw_file_sha256(archive), manifest["archive"]["sha256"])
            self.assertEqual(
                f"{manifest['archive']['sha256']}  {archive.name}\n", checksum
            )
            self.assertEqual(7, manifest["package"]["file_count"])


if __name__ == "__main__":
    unittest.main()
