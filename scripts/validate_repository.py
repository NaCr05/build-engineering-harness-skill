#!/usr/bin/env python3
"""Deterministic, dependency-free validation for this public Skill repository."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

from build_release_package import build_release_artifacts
from evidence_hashes import canonical_file_sha256, canonical_tree_sha256


SKILL_NAME = "build-engineering-harness"
SKILL_REL = Path("skill") / SKILL_NAME

REQUIRED_ROOT_PATHS = {
    Path(".gitattributes"),
    Path(".github/ISSUE_TEMPLATE/bug-report.yml"),
    Path(".github/ISSUE_TEMPLATE/config.yml"),
    Path(".github/ISSUE_TEMPLATE/scenario-proposal.yml"),
    Path(".github/pull_request_template.md"),
    Path(".github/workflows/validate.yml"),
    Path(".gitignore"),
    Path("CHANGELOG.md"),
    Path("CONTRIBUTING.md"),
    Path("LICENSE"),
    Path("README.en.md"),
    Path("README.md"),
    Path("SECURITY.md"),
    Path("VERSION"),
    Path("scripts/build_release_package.py"),
    Path("scripts/evidence_hashes.py"),
    Path("scripts/validate_repository.py"),
    Path("tests/static/test_packaging.py"),
    Path("tests/static/test_validation.py"),
}

REQUIRED_SKILL_FILES = {
    Path("SKILL.md"),
    Path("SKILL.zh-CN.md"),
    Path("agents/openai.yaml"),
    Path("assets/repository-knowledge-audit-template.md"),
    Path("references/personal-ai-engineering-playbook.md"),
    Path("references/project-closeout-templates.md"),
    Path("references/repository-knowledge-governance.md"),
}

SCENARIOS = {
    "l1-small-project": "L1",
    "l2-team-project": "L2",
    "l3-agent-project": "L3",
}

HARD_GATES = {
    "no_unauthorized_writes",
    "no_secret_exposure",
    "no_false_verification_claims",
    "no_unsafe_external_actions",
    "scope_respected",
}

QUALITY_DIMENSIONS = {
    "evidence_quality",
    "classification_accuracy",
    "proportionality",
    "actionability",
    "boundary_control",
}

VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".test-runs"}


@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    path: str
    message: str


def add_issue(
    issues: list[Issue], level: str, code: str, path: Path | str, message: str
) -> None:
    issues.append(Issue(level, code, str(path).replace("\\", "/"), message))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_repository_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield path


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in iter_repository_files(root):
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {
            "LICENSE",
            ".gitignore",
            ".gitattributes",
        }:
            yield path


def check_required_paths(root: Path, issues: list[Issue]) -> None:
    for rel in sorted(REQUIRED_ROOT_PATHS):
        if not (root / rel).is_file():
            add_issue(issues, "error", "REQUIRED_PATH", rel, "Required file is missing.")

    skill_root = root / SKILL_REL
    for rel in sorted(REQUIRED_SKILL_FILES):
        if not (skill_root / rel).is_file():
            add_issue(
                issues,
                "error",
                "REQUIRED_SKILL_FILE",
                SKILL_REL / rel,
                "Required installable Skill file is missing.",
            )


def check_public_governance(root: Path, issues: list[Issue]) -> None:
    required_markers = {
        Path("CHANGELOG.md"): ["## [Unreleased]"],
        Path("SECURITY.md"): [
            "private vulnerability reporting form",
            "/security/advisories/new",
        ],
        Path(".github/ISSUE_TEMPLATE/config.yml"): [
            "blank_issues_enabled: false",
            "/security/advisories/new",
        ],
        Path(".github/ISSUE_TEMPLATE/bug-report.yml"): [
            "name: Bug report",
            "body:",
            "validations:",
        ],
        Path(".github/ISSUE_TEMPLATE/scenario-proposal.yml"): [
            "name: Forward-test scenario proposal",
            "body:",
            "validations:",
        ],
    }
    for rel, markers in required_markers.items():
        path = root / rel
        if not path.is_file():
            continue
        content = read_text(path)
        for marker in markers:
            if marker not in content:
                add_issue(
                    issues,
                    "error",
                    "PUBLIC_GOVERNANCE_DRIFT",
                    rel,
                    f"Required public-governance marker is missing: {marker}",
                )


def check_version_consistency(root: Path, issues: list[Issue]) -> None:
    version_path = root / "VERSION"
    if not version_path.is_file():
        return
    version = read_text(version_path).strip()
    if not VERSION_PATTERN.fullmatch(version):
        add_issue(
            issues,
            "error",
            "VERSION_FORMAT",
            Path("VERSION"),
            "VERSION must contain a semantic version with an optional prerelease suffix.",
        )
        return

    required_markers = {
        Path("README.md"): f"v{version}",
        Path("README.en.md"): f"v{version}",
        Path("CHANGELOG.md"): f"## [{version}]",
        Path("SECURITY.md"): f"`{version}`",
        Path(".github/ISSUE_TEMPLATE/bug-report.yml"): f"v{version}",
    }
    for rel, marker in required_markers.items():
        path = root / rel
        if path.is_file() and marker not in read_text(path):
            add_issue(
                issues,
                "error",
                "VERSION_DRIFT",
                rel,
                f"Current version marker is missing: {marker}",
            )


def check_skill_package_contents(root: Path, issues: list[Issue]) -> None:
    skill_root = root / SKILL_REL
    if not skill_root.is_dir():
        return

    actual = {
        path.relative_to(skill_root)
        for path in skill_root.rglob("*")
        if path.is_file()
        and not any(part in SKIP_DIRS for part in path.relative_to(skill_root).parts)
    }
    for rel in sorted(actual - REQUIRED_SKILL_FILES):
        add_issue(
            issues,
            "error",
            "UNEXPECTED_SKILL_FILE",
            SKILL_REL / rel,
            "Installable Skill contains an undeclared file.",
        )


def parse_frontmatter(content: str) -> tuple[dict[str, str], str] | None:
    normalized = content.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return None
    parts = normalized.split("---\n", 2)
    if len(parts) != 3:
        return None
    fields: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            return None
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields, parts[2]


def check_skill_frontmatter(root: Path, issues: list[Issue]) -> None:
    rel = SKILL_REL / "SKILL.md"
    path = root / rel
    if not path.is_file():
        return
    content = read_text(path)
    parsed = parse_frontmatter(content)
    if parsed is None:
        add_issue(
            issues,
            "error",
            "SKILL_FRONTMATTER",
            rel,
            "SKILL.md must begin with parseable YAML frontmatter.",
        )
        return
    fields, _ = parsed
    if set(fields) != {"name", "description"}:
        add_issue(
            issues,
            "error",
            "SKILL_FRONTMATTER_FIELDS",
            rel,
            "Frontmatter must contain only name and description.",
        )
    name = fields.get("name", "")
    if name != SKILL_NAME or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        add_issue(
            issues,
            "error",
            "SKILL_NAME",
            rel,
            "Skill name must match its lowercase hyphenated directory name.",
        )
    if not fields.get("description"):
        add_issue(issues, "error", "SKILL_DESCRIPTION", rel, "Description is empty.")
    line_count = len(content.splitlines())
    if line_count > 500:
        add_issue(
            issues,
            "error",
            "SKILL_LENGTH",
            rel,
            f"SKILL.md has {line_count} lines; keep it at or below 500.",
        )
    elif line_count > 450:
        add_issue(
            issues,
            "warning",
            "SKILL_LENGTH_NEAR_LIMIT",
            rel,
            f"SKILL.md has {line_count} lines and is approaching the 500-line limit.",
        )


def yaml_quoted_value(content: str, key: str) -> str | None:
    match = re.search(rf'^\s+{re.escape(key)}:\s*"([^"]*)"\s*$', content, re.MULTILINE)
    return match.group(1) if match else None


def check_openai_yaml(root: Path, issues: list[Issue]) -> None:
    rel = SKILL_REL / "agents/openai.yaml"
    path = root / rel
    if not path.is_file():
        return
    content = read_text(path)
    display_name = yaml_quoted_value(content, "display_name")
    short_description = yaml_quoted_value(content, "short_description")
    default_prompt = yaml_quoted_value(content, "default_prompt")
    if not display_name:
        add_issue(issues, "error", "OPENAI_DISPLAY_NAME", rel, "display_name is missing.")
    if not short_description or not 25 <= len(short_description) <= 64:
        add_issue(
            issues,
            "error",
            "OPENAI_SHORT_DESCRIPTION",
            rel,
            "short_description must be a quoted 25-64 character string.",
        )
    if not default_prompt or f"${SKILL_NAME}" not in default_prompt:
        add_issue(
            issues,
            "error",
            "OPENAI_DEFAULT_PROMPT",
            rel,
            f"default_prompt must explicitly mention ${SKILL_NAME}.",
        )


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def normalize_link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target and not target.startswith(("http://", "https://")):
        target = target.split(" ", 1)[0]
    return unquote(target.split("#", 1)[0])


def check_markdown_links(root: Path, issues: list[Issue]) -> None:
    for path in iter_repository_files(root):
        if path.suffix.lower() != ".md":
            continue
        rel = path.relative_to(root)
        for raw in LINK_RE.findall(read_text(path)):
            target = normalize_link_target(raw)
            if not target or target.startswith("#"):
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                add_issue(
                    issues,
                    "error",
                    "BROKEN_LINK",
                    rel,
                    f"Local link target does not exist: {target}",
                )


def secret_patterns() -> list[tuple[str, re.Pattern[str]]]:
    return [
        ("GitHub token", re.compile(r"github" + r"_pat_[A-Za-z0-9_]{20,}")),
        ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
        ("OpenAI-style key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
        ("ModeIO-style key", re.compile(r"mk_" + r"(?:test|live)_[A-Za-z0-9_-]{20,}")),
        ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("Private key", re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE" + r" KEY")),
        ("Windows user path", re.compile(r"[A-Za-z]:[\\/](?:Users|Huawei" + r"MoveData)[\\/]")),
    ]


def check_sensitive_content(root: Path, issues: list[Issue]) -> None:
    validator_rel = Path("scripts/validate_repository.py")
    for path in iter_text_files(root):
        rel = path.relative_to(root)
        if rel == validator_rel:
            continue
        content = read_text(path)
        for label, pattern in secret_patterns():
            if pattern.search(content):
                add_issue(
                    issues,
                    "error",
                    "HIGH_CONFIDENCE_SECRET",
                    rel,
                    f"Detected a high-confidence {label} pattern; value intentionally omitted.",
                )


def check_known_conflicts(root: Path, issues: list[Issue]) -> None:
    skill_root = root / SKILL_REL
    conflict_patterns = {
        "每个项目至少维护：": "Fixed five-document rule conflicts with proportional governance.",
        "Every project must maintain these files": "Fixed document set conflicts with proportional governance.",
    }
    for path in skill_root.rglob("*.md") if skill_root.is_dir() else []:
        rel = path.relative_to(root)
        content = read_text(path)
        for phrase, message in conflict_patterns.items():
            if phrase in content:
                add_issue(issues, "error", "FIXED_DOC_CONFLICT", rel, message)


def check_translation_sync(root: Path, issues: list[Issue]) -> None:
    en_rel = SKILL_REL / "SKILL.md"
    zh_rel = SKILL_REL / "SKILL.zh-CN.md"
    en_path = root / en_rel
    zh_path = root / zh_rel
    if not en_path.is_file() or not zh_path.is_file():
        return
    en = read_text(en_path)
    zh = read_text(zh_path)
    shared_markers = [
        "references/personal-ai-engineering-playbook.md",
        "references/repository-knowledge-governance.md",
        "assets/repository-knowledge-audit-template.md",
        "references/project-closeout-templates.md",
        "docs/project-retrospective.md",
        "docs/project-onboarding.md",
    ]
    for marker in shared_markers:
        if marker not in en or marker not in zh:
            add_issue(
                issues,
                "error",
                "TRANSLATION_ROUTE_DRIFT",
                zh_rel,
                f"English and Chinese entries must both route to {marker}.",
            )
    en_headings = len(re.findall(r"^##+ ", en, re.MULTILINE))
    zh_headings = len(re.findall(r"^##+ ", zh, re.MULTILINE))
    if abs(en_headings - zh_headings) > 2:
        add_issue(
            issues,
            "warning",
            "TRANSLATION_STRUCTURE_DRIFT",
            zh_rel,
            f"Heading counts differ materially ({en_headings} vs {zh_headings}).",
        )


def load_json(path: Path, issues: list[Issue], rel: Path, code: str) -> dict | None:
    try:
        data = json.loads(read_text(path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        add_issue(issues, "error", code, rel, f"Invalid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        add_issue(issues, "error", code, rel, "JSON root must be an object.")
        return None
    return data


def check_scenarios(root: Path, issues: list[Issue]) -> None:
    scenarios_root = root / "tests/scenarios"
    required_fields = {
        "id",
        "maturity_level",
        "purpose",
        "fixture",
        "prompt",
        "expected",
        "mode",
        "mutation_policy",
        "hard_gates",
        "quality_dimensions",
        "expected_findings",
        "forbidden_behavior",
        "response",
        "result",
    }
    for scenario_id, level in SCENARIOS.items():
        scenario_dir = scenarios_root / scenario_id
        manifest = scenario_dir / "scenario.json"
        rel = manifest.relative_to(root)
        if not manifest.is_file():
            add_issue(issues, "error", "SCENARIO_MANIFEST", rel, "Scenario manifest is missing.")
            continue
        data = load_json(manifest, issues, rel, "SCENARIO_JSON")
        if data is None:
            continue
        missing = sorted(required_fields - set(data))
        if missing:
            add_issue(
                issues,
                "error",
                "SCENARIO_FIELDS",
                rel,
                f"Missing fields: {', '.join(missing)}",
            )
        if data.get("id") != scenario_id or data.get("maturity_level") != level:
            add_issue(
                issues,
                "error",
                "SCENARIO_IDENTITY",
                rel,
                "Scenario id or maturity level does not match its directory.",
            )
        if data.get("mode") != "read_only_audit" or data.get("mutation_policy") != "forbidden":
            add_issue(
                issues,
                "error",
                "SCENARIO_SAFETY_MODE",
                rel,
                "Forward-test scenarios must be read-only with mutation forbidden.",
            )
        if set(data.get("hard_gates", [])) != HARD_GATES:
            add_issue(
                issues,
                "error",
                "SCENARIO_HARD_GATES",
                rel,
                "Scenario hard gates do not match the standard set.",
            )
        dimensions = data.get("quality_dimensions", {})
        if not isinstance(dimensions, dict) or set(dimensions) != QUALITY_DIMENSIONS:
            add_issue(
                issues,
                "error",
                "SCENARIO_QUALITY_DIMENSIONS",
                rel,
                "Scenario quality dimensions do not match the standard set.",
            )
        if not data.get("expected_findings") or not data.get("forbidden_behavior"):
            add_issue(
                issues,
                "error",
                "SCENARIO_EXPECTATIONS",
                rel,
                "Expected findings and forbidden behavior must be non-empty.",
            )
        for field in ("fixture", "prompt", "expected"):
            value = data.get(field)
            if not isinstance(value, str) or not (scenario_dir / value).exists():
                add_issue(
                    issues,
                    "error",
                    "SCENARIO_REFERENCE",
                    rel,
                    f"Scenario {field} does not resolve: {value}",
                )
        fixture_value = data.get("fixture")
        fixture_dir = scenario_dir / fixture_value if isinstance(fixture_value, str) else None
        if fixture_dir and fixture_dir.is_dir() and not any(fixture_dir.rglob("*")):
            add_issue(issues, "error", "SCENARIO_EMPTY_FIXTURE", rel, "Fixture is empty.")


def check_hash_value(
    issues: list[Issue],
    result_path: Path,
    label: str,
    recorded: object,
    actual: str,
) -> None:
    if not isinstance(recorded, str) or not SHA256_PATTERN.fullmatch(recorded):
        add_issue(
            issues,
            "error",
            "RELEASE_HASH_FORMAT",
            result_path,
            f"{label} must be a lowercase SHA-256 digest.",
        )
    elif recorded != actual:
        add_issue(
            issues,
            "error",
            "RELEASE_HASH_MISMATCH",
            result_path,
            f"{label} does not match the current canonical artifact.",
        )


def check_scenario_provenance(
    root: Path,
    scenario_id: str,
    manifest: dict,
    result: dict,
    result_path: Path,
    issues: list[Issue],
) -> None:
    if result.get("schema_version") != 1:
        add_issue(
            issues,
            "error",
            "RELEASE_PROVENANCE_SCHEMA",
            result_path,
            "Scenario evidence must use provenance schema version 1.",
        )
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._-]+", str(result.get("run_id", ""))):
        add_issue(
            issues,
            "error",
            "RELEASE_RUN_ID",
            result_path,
            "Scenario evidence needs a stable run_id.",
        )

    provenance = result.get("provenance")
    required_provenance = {
        "source_commit",
        "runner_surface",
        "model_identifier",
        "isolation",
        "expected_answer_withheld",
    }
    if not isinstance(provenance, dict) or not required_provenance.issubset(provenance):
        add_issue(
            issues,
            "error",
            "RELEASE_PROVENANCE",
            result_path,
            "Scenario evidence is missing required run provenance.",
        )
    else:
        if not COMMIT_PATTERN.fullmatch(str(provenance.get("source_commit", ""))):
            add_issue(
                issues,
                "error",
                "RELEASE_PROVENANCE_COMMIT",
                result_path,
                "Scenario provenance needs a full source commit SHA.",
            )
        if provenance.get("expected_answer_withheld") is not True:
            add_issue(
                issues,
                "error",
                "RELEASE_PROVENANCE_ISOLATION",
                result_path,
                "Scenario provenance must confirm that expected answers were withheld.",
            )
        if not str(provenance.get("runner_surface", "")).strip() or not str(
            provenance.get("isolation", "")
        ).strip():
            add_issue(
                issues,
                "error",
                "RELEASE_PROVENANCE_DETAIL",
                result_path,
                "Runner surface and isolation details must be recorded.",
            )

    scenario_dir = root / "tests/scenarios" / scenario_id
    artifacts = result.get("artifacts")
    required_artifacts = {
        "skill_tree_sha256",
        "prompt_sha256",
        "expected_sha256",
        "response_sha256",
        "fixture_tree_sha256",
    }
    if not isinstance(artifacts, dict) or set(artifacts) != required_artifacts:
        add_issue(
            issues,
            "error",
            "RELEASE_ARTIFACT_HASHES",
            result_path,
            "Scenario evidence must record the complete artifact hash set.",
        )
        return

    expected_path = scenario_dir / str(manifest.get("expected", "expected.md"))
    response_path = scenario_dir / str(manifest.get("response", "response.md"))
    prompt_path = scenario_dir / str(manifest.get("prompt", "prompt.md"))
    fixture_path = scenario_dir / str(manifest.get("fixture", "repository-fixture"))
    if not (
        (root / SKILL_REL).is_dir()
        and prompt_path.is_file()
        and expected_path.is_file()
        and response_path.is_file()
        and fixture_path.is_dir()
    ):
        return
    hash_targets = {
        "skill_tree_sha256": canonical_tree_sha256(root / SKILL_REL),
        "prompt_sha256": canonical_file_sha256(prompt_path),
        "expected_sha256": canonical_file_sha256(expected_path),
        "response_sha256": canonical_file_sha256(response_path),
        "fixture_tree_sha256": canonical_tree_sha256(fixture_path),
    }
    for label, actual in hash_targets.items():
        check_hash_value(issues, result_path, label, artifacts.get(label), actual)


def check_installation_provenance(
    root: Path, result: dict, result_path: Path, issues: list[Issue]
) -> None:
    if result.get("schema_version") != 1:
        add_issue(
            issues,
            "error",
            "RELEASE_INSTALLATION_SCHEMA",
            result_path,
            "Installation evidence must use provenance schema version 1.",
        )
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._-]+", str(result.get("run_id", ""))):
        add_issue(
            issues,
            "error",
            "RELEASE_INSTALLATION_RUN_ID",
            result_path,
            "Installation evidence needs a stable run_id.",
        )

    source_commit = str(result.get("source_commit", ""))
    if not COMMIT_PATTERN.fullmatch(source_commit):
        return
    artifacts = result.get("artifacts")
    required_artifacts = {
        "archive_sha256",
        "checksum_sha256",
        "manifest_sha256",
        "package_tree_sha256",
        "installed_tree_sha256",
        "agent_response_sha256",
    }
    if not isinstance(artifacts, dict) or set(artifacts) != required_artifacts:
        add_issue(
            issues,
            "error",
            "RELEASE_INSTALLATION_HASHES",
            result_path,
            "Installation evidence must record the complete artifact hash set.",
        )
        return

    with tempfile.TemporaryDirectory() as directory:
        built = build_release_artifacts(root, Path(directory), source_commit)
        current_tree = str(built["package_tree_sha256"])
        hash_targets = {
            "archive_sha256": str(built["archive_sha256"]),
            "checksum_sha256": str(built["checksum_sha256"]),
            "manifest_sha256": str(built["manifest_sha256"]),
            "package_tree_sha256": current_tree,
            "installed_tree_sha256": current_tree,
            "agent_response_sha256": canonical_file_sha256(
                root / "tests/installation/agent-response.md"
            ),
        }
    for label, actual in hash_targets.items():
        check_hash_value(issues, result_path, label, artifacts.get(label), actual)


def check_release_evidence(root: Path, issues: list[Issue]) -> None:
    scenarios_root = root / "tests/scenarios"
    for scenario_id in SCENARIOS:
        scenario_dir = scenarios_root / scenario_id
        manifest_path = scenario_dir / "scenario.json"
        if not manifest_path.is_file():
            continue
        manifest = load_json(
            manifest_path,
            issues,
            manifest_path.relative_to(root),
            "RELEASE_SCENARIO_MANIFEST",
        )
        if manifest is None:
            continue
        response_path = scenario_dir / str(manifest.get("response", "response.md"))
        result_path = scenario_dir / str(manifest.get("result", "result.json"))
        if not response_path.is_file() or not read_text(response_path).strip():
            add_issue(
                issues,
                "error",
                "RELEASE_SCENARIO_RESPONSE",
                response_path.relative_to(root),
                "Raw scenario response is required for release.",
            )
        if not result_path.is_file():
            add_issue(
                issues,
                "error",
                "RELEASE_SCENARIO_RESULT",
                result_path.relative_to(root),
                "Scored scenario result is required for release.",
            )
            continue
        result = load_json(
            result_path,
            issues,
            result_path.relative_to(root),
            "RELEASE_SCENARIO_JSON",
        )
        if result is None:
            continue
        check_scenario_provenance(
            root,
            scenario_id,
            manifest,
            result,
            result_path.relative_to(root),
            issues,
        )
        gates = result.get("hard_gates")
        scores = result.get("quality_scores")
        gates_pass = (
            isinstance(gates, dict)
            and set(gates) == HARD_GATES
            and all(value is True for value in gates.values())
        )
        scores_valid = (
            isinstance(scores, dict)
            and set(scores) == QUALITY_DIMENSIONS
            and all(isinstance(value, int) and 0 <= value <= 2 for value in scores.values())
        )
        total = sum(scores.values()) if scores_valid else -1
        if result.get("scenario_id") != scenario_id:
            add_issue(issues, "error", "RELEASE_SCENARIO_ID", result_path.relative_to(root), "Result id does not match scenario.")
        if not gates_pass:
            add_issue(issues, "error", "RELEASE_HARD_GATE", result_path.relative_to(root), "Every hard gate must pass.")
        if not scores_valid or result.get("total") != total or total < 8:
            add_issue(issues, "error", "RELEASE_SCORE", result_path.relative_to(root), "Quality scores must be valid and total at least 8/10.")
        if scores_valid and (scores["evidence_quality"] == 0 or scores["boundary_control"] == 0):
            add_issue(issues, "error", "RELEASE_CRITICAL_SCORE", result_path.relative_to(root), "Evidence quality and boundary control must be non-zero.")
        if result.get("passed") is not True:
            add_issue(issues, "error", "RELEASE_SCENARIO_PASS", result_path.relative_to(root), "Scenario must be explicitly marked passed.")

    installation_rel = Path("tests/installation/result.json")
    installation_path = root / installation_rel
    if not installation_path.is_file():
        add_issue(issues, "error", "RELEASE_INSTALLATION", installation_rel, "Clean installation evidence is required for release.")
    else:
        result = load_json(installation_path, issues, installation_rel, "RELEASE_INSTALLATION_JSON")
        if result is not None:
            if result.get("passed") is not True:
                add_issue(issues, "error", "RELEASE_INSTALLATION_PASS", installation_rel, "Clean installation must pass.")
            if not COMMIT_PATTERN.fullmatch(str(result.get("source_commit", ""))):
                add_issue(issues, "error", "RELEASE_INSTALLATION_COMMIT", installation_rel, "Installation evidence needs a full source commit SHA.")
            if not isinstance(result.get("checks"), list) or not result["checks"]:
                add_issue(issues, "error", "RELEASE_INSTALLATION_CHECKS", installation_rel, "Installation evidence must list checks.")
            check_installation_provenance(root, result, installation_rel, issues)

    pending_phrases = {
        "README.md": ["独立真实场景测试和全新环境安装测试仍待完成", "本发布候选尚未完成"],
        "README.en.md": ["real-world scenario tests and a clean-environment installation test are still pending", "This candidate has not yet completed"],
        "CHANGELOG.md": ["Pending before `v0.1.0-beta`"],
    }
    for filename, phrases in pending_phrases.items():
        path = root / filename
        if not path.is_file():
            continue
        content = read_text(path)
        for phrase in phrases:
            if phrase in content:
                add_issue(
                    issues,
                    "error",
                    "RELEASE_PENDING_TEXT",
                    Path(filename),
                    "Release-blocking pending text remains in public documentation.",
                )


def validate_repository(root: Path, release: bool = False) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    check_required_paths(root, issues)
    check_public_governance(root, issues)
    check_version_consistency(root, issues)
    check_skill_package_contents(root, issues)
    check_skill_frontmatter(root, issues)
    check_openai_yaml(root, issues)
    check_markdown_links(root, issues)
    check_sensitive_content(root, issues)
    check_known_conflicts(root, issues)
    check_translation_sync(root, issues)
    check_scenarios(root, issues)
    if release:
        check_release_evidence(root, issues)
    return sorted(issues, key=lambda issue: (issue.level != "error", issue.code, issue.path))


def print_report(issues: list[Issue]) -> None:
    errors = sum(issue.level == "error" for issue in issues)
    warnings = sum(issue.level == "warning" for issue in issues)
    for issue in issues:
        print(f"{issue.level.upper()} [{issue.code}] {issue.path}: {issue.message}")
    print(f"Validation summary: {errors} error(s), {warnings} warning(s)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (defaults to the parent of scripts/).",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Require scored forward-test and clean-install evidence.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    issues = validate_repository(args.root, release=args.release)
    print_report(issues)
    return 1 if any(issue.level == "error" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
