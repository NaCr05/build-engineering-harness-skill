from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_changelog import missing_changelog_update, unreleased_has_changes  # noqa: E402


class ChangelogSynchronizationTests(unittest.TestCase):
    def test_release_relevant_change_requires_changelog(self) -> None:
        self.assertEqual(
            ["skill/build-engineering-harness/SKILL.md"],
            missing_changelog_update(
                ["skill/build-engineering-harness/SKILL.md", "notes/scratch.md"]
            ),
        )

    def test_changelog_update_satisfies_release_relevant_change(self) -> None:
        self.assertEqual(
            [],
            missing_changelog_update(
                ["scripts/validate_repository.py", "CHANGELOG.md"]
            ),
        )

    def test_unrelated_change_does_not_require_changelog(self) -> None:
        self.assertEqual([], missing_changelog_update(["notes/scratch.md"]))

    def test_unreleased_requires_substantive_content(self) -> None:
        self.assertFalse(
            unreleased_has_changes(
                "# Changelog\n\n## [Unreleased]\n\nNo unreleased changes.\n"
            )
        )
        self.assertTrue(
            unreleased_has_changes(
                "# Changelog\n\n## [Unreleased]\n\n### Changed\n\n- Updated validation.\n\n## [0.1.0]\n"
            )
        )


if __name__ == "__main__":
    unittest.main()
