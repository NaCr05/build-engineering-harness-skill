from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_release_package import build_release_artifacts  # noqa: E402
from evidence_hashes import canonical_tree_sha256  # noqa: E402
from install_skill import (  # noqa: E402
    InstallError,
    install_from_assets,
    validate_file_record,
    validated_archive_members,
)


class SafeInstallerTests(unittest.TestCase):
    source_commit = "b" * 40

    def build_assets(self, directory: Path) -> dict[str, Path | str]:
        return build_release_artifacts(
            REPO_ROOT, directory, self.source_commit, verify_source=False
        )

    def test_dry_run_verifies_without_creating_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            codex_home = root / "codex-home"
            self.build_assets(assets)

            result = install_from_assets(assets, codex_home, dry_run=True)

            self.assertEqual("dry-run", result["mode"])
            self.assertFalse(codex_home.exists())

    def test_fresh_install_and_upgrade_keep_verified_backup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            codex_home = root / "codex-home"
            built = self.build_assets(assets)

            first = install_from_assets(assets, codex_home)
            target = Path(str(first["target"]))
            self.assertEqual(
                built["package_tree_sha256"], canonical_tree_sha256(target)
            )

            (target / "old-install-marker.txt").write_text("old\n", encoding="utf-8")
            second = install_from_assets(assets, codex_home)
            backup = Path(str(second["backup"]))
            self.assertFalse((target / "old-install-marker.txt").exists())
            self.assertEqual("old\n", (backup / "old-install-marker.txt").read_text(encoding="utf-8"))

    def test_post_backup_failure_restores_previous_installation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            codex_home = root / "codex-home"
            self.build_assets(assets)
            target = codex_home / "skills/build-engineering-harness"
            target.mkdir(parents=True)
            (target / "marker.txt").write_text("preserve me\n", encoding="utf-8")

            with self.assertRaisesRegex(InstallError, "Injected post-backup failure"):
                install_from_assets(
                    assets, codex_home, fail_after_backup=True
                )

            self.assertEqual("preserve me\n", (target / "marker.txt").read_text(encoding="utf-8"))

    def test_archive_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            built = self.build_assets(assets)
            manifest = json.loads(Path(built["manifest"]).read_text(encoding="utf-8"))
            malicious = root / "malicious.zip"
            with zipfile.ZipFile(malicious, "w") as archive:
                archive.writestr("../outside.txt", "unsafe")
            with zipfile.ZipFile(malicious) as archive:
                with self.assertRaisesRegex(InstallError, "layout"):
                    validated_archive_members(archive, manifest)

    def test_tampered_installer_asset_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            codex_home = root / "codex-home"
            self.build_assets(assets)
            (assets / "install.sh").write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(InstallError, "Installer size mismatch"):
                install_from_assets(assets, codex_home, dry_run=True)

    def test_windows_unsafe_manifest_paths_are_rejected_cross_platform(self) -> None:
        for path in ("folder/file.txt:stream", "CON.txt", "folder/trailing. "):
            with self.subTest(path=path):
                with self.assertRaisesRegex(InstallError, "cross-platform safe"):
                    validate_file_record(
                        {"path": path, "sha256": "0" * 64, "size": 0}
                    )


if __name__ == "__main__":
    unittest.main()
