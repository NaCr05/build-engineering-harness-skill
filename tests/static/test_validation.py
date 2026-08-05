from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_repository import validate_repository  # noqa: E402


class RepositoryValidationTests(unittest.TestCase):
    def make_copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        target = Path(temporary.name) / "repository"
        shutil.copytree(
            REPO_ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".test-runs"),
        )
        return temporary, target

    @staticmethod
    def error_codes(root: Path, release: bool = False) -> set[str]:
        return {
            issue.code
            for issue in validate_repository(root, release=release)
            if issue.level == "error"
        }

    def test_current_repository_passes_base_validation(self) -> None:
        errors = self.error_codes(REPO_ROOT)
        self.assertEqual(set(), errors)

    def test_missing_skill_entry_is_blocking(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        (root / "skill/build-engineering-harness/SKILL.md").unlink()
        self.assertIn("REQUIRED_SKILL_FILE", self.error_codes(root))

    def test_missing_issue_form_is_blocking(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        (root / ".github/ISSUE_TEMPLATE/bug-report.yml").unlink()
        self.assertIn("REQUIRED_PATH", self.error_codes(root))

    def test_public_governance_drift_is_blocking(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        security = root / "SECURITY.md"
        security.write_text(
            security.read_text(encoding="utf-8").replace(
                "/security/advisories/new", "/issues/new"
            ),
            encoding="utf-8",
        )
        self.assertIn("PUBLIC_GOVERNANCE_DRIFT", self.error_codes(root))

    def test_broken_local_link_is_blocking(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        readme = root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n[broken](missing.md)\n", encoding="utf-8")
        self.assertIn("BROKEN_LINK", self.error_codes(root))

    def test_high_confidence_secret_is_blocking(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        fake_secret = "github" + "_pat_" + ("A" * 24)
        (root / "accidental-secret.txt").write_text(fake_secret, encoding="utf-8")
        self.assertIn("HIGH_CONFIDENCE_SECRET", self.error_codes(root))

    def test_default_prompt_must_name_the_skill(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        metadata = root / "skill/build-engineering-harness/agents/openai.yaml"
        content = metadata.read_text(encoding="utf-8").replace(
            "$build-engineering-harness", "the engineering skill"
        )
        metadata.write_text(content, encoding="utf-8")
        self.assertIn("OPENAI_DEFAULT_PROMPT", self.error_codes(root))

    def test_fixed_document_rule_is_blocking(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        playbook = root / "skill/build-engineering-harness/references/personal-ai-engineering-playbook.md"
        playbook.write_text(
            playbook.read_text(encoding="utf-8")
            + "\nEvery project must maintain these files: README, architecture, workflow, FAQ, and current-state.\n",
            encoding="utf-8",
        )
        self.assertIn("FIXED_DOC_CONFLICT", self.error_codes(root))

    def test_release_mode_requires_forward_test_evidence(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)

        scenario = root / "tests/scenarios/l1-small-project"
        for name in ("response.md", "result.json"):
            evidence = scenario / name
            if evidence.exists():
                evidence.unlink()

        installation = root / "tests/installation/result.json"
        if installation.exists():
            installation.unlink()

        errors = self.error_codes(root, release=True)
        self.assertIn("RELEASE_SCENARIO_RESPONSE", errors)
        self.assertIn("RELEASE_SCENARIO_RESULT", errors)
        self.assertIn("RELEASE_INSTALLATION", errors)


if __name__ == "__main__":
    unittest.main()
