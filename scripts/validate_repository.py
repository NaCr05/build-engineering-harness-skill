#!/usr/bin/env python3
"""Deterministic, dependency-free validation for this public Skill repository."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

from build_release_package import build_release_artifacts
from evidence_hashes import (
    canonical_file_sha256,
    canonical_tree_sha256,
    iter_tree_files,
    named_digest_sha256,
)


SKILL_NAME = "build-engineering-harness"
SKILL_REL = Path("skill") / SKILL_NAME

REQUIRED_ROOT_PATHS = {
    Path(".gitattributes"),
    Path(".github/dependabot.yml"),
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
    Path("scripts/check_append_only_runs.py"),
    Path("scripts/check_changelog.py"),
    Path("scripts/compare_release_artifacts.py"),
    Path("scripts/evidence_hashes.py"),
    Path("scripts/install.ps1"),
    Path("scripts/install.sh"),
    Path("scripts/install_skill.py"),
    Path("scripts/validate_repository.py"),
    Path("tests/static/test_packaging.py"),
    Path("tests/static/test_changelog.py"),
    Path("tests/static/test_installer.py"),
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
        Path("README.md"): [
            "https://github.com/NaCr05/build-engineering-harness-skill/releases",
            "gh attestation verify",
            "--source-ref",
            "--signer-workflow",
            "CPython 3.10–3.13",
            "PowerShell 7",
        ],
        Path("README.en.md"): [
            "https://github.com/NaCr05/build-engineering-harness-skill/releases",
            "gh attestation verify",
            "--source-ref",
            "--signer-workflow",
            "CPython 3.10–3.13",
            "PowerShell 7",
        ],
        Path("CONTRIBUTING.md"): [
            "scripts/check_changelog.py",
            "CPython 3.10 through 3.13",
            "Windows PowerShell 5.1",
        ],
        Path("CHANGELOG.md"): ["## [Unreleased]"],
        Path("SECURITY.md"): [
            "private vulnerability reporting form",
            "/security/advisories/new",
            "https://github.com/NaCr05/build-engineering-harness-skill/releases",
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
        Path(".github/dependabot.yml"): [
            "package-ecosystem: github-actions",
            "interval: monthly",
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

    readme_structures = {
        Path("README.md"): [
            "## 30 秒开始",
            "## 你会得到什么",
            "## 工作方式与安全边界",
            "## 适用场景与成熟度",
            "## 安装",
            "## 常用 Prompt",
            "## 信任与验证",
            "## 项目导航",
            "## 方法论与许可",
        ],
        Path("README.en.md"): [
            "## 30-second start",
            "## What you get",
            "## Workflow and safety boundary",
            "## Use cases and maturity",
            "## Installation",
            "## Common prompts",
            "## Trust and verification",
            "## Project navigation",
            "## Methodology and license",
        ],
    }
    for rel, headings in readme_structures.items():
        path = root / rel
        if not path.is_file():
            continue
        content = read_text(path)
        positions = [content.find(heading) for heading in headings]
        if any(position < 0 for position in positions):
            missing = [
                heading for heading, position in zip(headings, positions) if position < 0
            ]
            add_issue(
                issues,
                "error",
                "README_STRUCTURE",
                rel,
                f"Required README section is missing: {', '.join(missing)}",
            )
        elif positions != sorted(positions):
            add_issue(
                issues,
                "error",
                "README_STRUCTURE",
                rel,
                "README sections must keep the user-first quick-start, method, installation, evidence, and routing order.",
            )

    required_readme_routes = [
        "skill/build-engineering-harness/SKILL.md",
        "skill/build-engineering-harness/references/repository-knowledge-governance.md",
        "tests/README.md",
        "tests/installation/result.json",
        ".github/workflows/validate.yml",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
    ]
    for rel in readme_structures:
        path = root / rel
        if not path.is_file():
            continue
        content = read_text(path)
        for route in required_readme_routes:
            if route not in content:
                add_issue(
                    issues,
                    "error",
                    "README_ROUTE",
                    rel,
                    f"README must route readers to the authoritative repository artifact: {route}",
                )

    volatile_release_markers = {
        Path("README.md"): [
            "当前候选版本：",
            "最新已公开版本仍是",
            "在 Draft Prerelease 经过人工核对并公开前",
        ],
        Path("README.en.md"): [
            "Current candidate:",
            "latest published version remains",
            "draft prerelease is reviewed and published",
        ],
        Path("SECURITY.md"): [
            "(draft candidate)",
            "Not until published",
        ],
    }
    for rel, markers in volatile_release_markers.items():
        path = root / rel
        if not path.is_file():
            continue
        content = read_text(path)
        for marker in markers:
            if marker in content:
                add_issue(
                    issues,
                    "error",
                    "VOLATILE_RELEASE_STATE",
                    rel,
                    "Mutable Draft-versus-Published state must route to GitHub Releases instead of being copied into repository documentation.",
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

    try:
        actual = {path.relative_to(skill_root) for path in iter_tree_files(skill_root)}
    except ValueError as exc:
        add_issue(
            issues,
            "error",
            "UNSAFE_SKILL_TREE",
            SKILL_REL,
            str(exc),
        )
        return
    for rel in sorted(actual - REQUIRED_SKILL_FILES):
        add_issue(
            issues,
            "error",
            "UNEXPECTED_SKILL_FILE",
            SKILL_REL / rel,
            "Installable Skill contains an undeclared file.",
        )


def check_trusted_release_workflow(root: Path, issues: list[Issue]) -> None:
    rel = Path(".github/workflows/validate.yml")
    path = root / rel
    if not path.is_file():
        return
    content = read_text(path)
    required_markers = {
        "actions/upload-artifact@": "CI must upload independently built release artifacts.",
        "actions/download-artifact@": "CI must download release artifacts for comparison and release.",
        "actions/attest@": "Tagged release archives must receive a GitHub artifact attestation.",
        "compare_release_artifacts.py": "CI must compare Windows and Linux release artifacts.",
        "check_append_only_runs.py": "Pull requests must reject changes to historical run evidence.",
        "check_changelog.py": "Pull requests must keep release-relevant changes synchronized with the changelog.",
        "macos-latest": "CI must validate the documented macOS support path.",
        'python: "3.10"': "CI must validate the documented minimum Python version.",
        'python: "3.13"': "CI must validate the documented maximum Python version.",
        "install.ps1": "CI must smoke-test the PowerShell safe installer.",
        "install.sh": "CI must smoke-test the POSIX safe installer.",
        "attestations: write": "The release job needs permission to publish attestations.",
        "id-token: write": "The release job needs OIDC permission for attestations.",
        "--draft": "Tag automation must create a draft release.",
        "--prerelease": "Tag automation must mark Beta releases as prereleases.",
        "fetch-depth: 0": "Source-commit verification requires complete Git history.",
    }
    for marker, message in required_markers.items():
        if marker not in content:
            add_issue(issues, "error", "TRUSTED_RELEASE_WORKFLOW", rel, message)

    published_release_guard = [
        '--json isDraft --jq .isDraft',
        'if [[ "$release_is_draft" != "true" ]]; then',
        'Refusing to overwrite assets for published release',
        "exit 1",
        'gh release upload "$tag" dist/* --clobber',
    ]
    guard_positions = [content.find(marker) for marker in published_release_guard]
    if any(position < 0 for position in guard_positions) or guard_positions != sorted(guard_positions):
        add_issue(
            issues,
            "error",
            "PUBLISHED_RELEASE_OVERWRITE_GUARD",
            rel,
            "Release automation must confirm an existing release is still a draft and stop before any clobber upload when it is public.",
        )

    for line_number, line in enumerate(content.splitlines(), start=1):
        match = re.match(r"^\s*uses:\s*([^@\s]+)@([^\s#]+)", line)
        if not match or match.group(1).startswith("./"):
            continue
        if not COMMIT_PATTERN.fullmatch(match.group(2)):
            add_issue(
                issues,
                "error",
                "UNPINNED_ACTION",
                rel,
                f"Line {line_number} must pin the action to a full commit SHA.",
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
            if (
                not resolved.exists()
                and "runs" in rel.parts
                and len(path.parents) >= 3
            ):
                resolved = (path.parents[2] / target).resolve()
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
        "runs_dir",
        "release_run",
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
        runs_dir = data.get("runs_dir")
        release_run = data.get("release_run")
        if runs_dir != "runs" or not (scenario_dir / "runs").is_dir():
            add_issue(
                issues,
                "error",
                "SCENARIO_RUNS_DIR",
                rel,
                "Scenario run evidence must live in the runs directory.",
            )
        if not isinstance(release_run, str) or not re.fullmatch(
            r"[0-9A-Za-z][0-9A-Za-z._-]+", release_run
        ):
            add_issue(
                issues,
                "error",
                "SCENARIO_RELEASE_RUN",
                rel,
                "Scenario manifest needs a stable release_run identifier.",
            )


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
    response_path: Path,
    issues: list[Issue],
) -> None:
    if result.get("schema_version") != 2:
        add_issue(
            issues,
            "error",
            "RELEASE_PROVENANCE_SCHEMA",
            result_path,
            "Scenario evidence must use provenance schema version 2.",
        )
    run_id = str(result.get("run_id", ""))
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._-]+", run_id):
        add_issue(
            issues,
            "error",
            "RELEASE_RUN_ID",
            result_path,
            "Scenario evidence needs a stable run_id.",
        )
    if result_path.parent.name != run_id:
        add_issue(
            issues,
            "error",
            "RELEASE_RUN_PATH",
            result_path,
            "The run directory name must equal result.run_id.",
        )
    try:
        dt.date.fromisoformat(str(result.get("run_date", "")))
        run_date_valid = True
    except ValueError:
        run_date_valid = False
    if not run_date_valid:
        add_issue(
            issues,
            "error",
            "RELEASE_RUN_DATE",
            result_path,
            "Scenario evidence needs an ISO calendar run_date.",
        )

    provenance = result.get("provenance")
    required_provenance = {
        "source_commit",
        "runner",
        "model",
        "timing",
        "usage",
        "isolation",
    }
    if not isinstance(provenance, dict) or set(provenance) != required_provenance:
        add_issue(
            issues,
            "error",
            "RELEASE_PROVENANCE",
            result_path,
            "Scenario evidence is missing required run provenance.",
        )
        return
    if not COMMIT_PATTERN.fullmatch(str(provenance.get("source_commit", ""))):
        add_issue(
            issues,
            "error",
            "RELEASE_PROVENANCE_COMMIT",
            result_path,
            "Scenario provenance needs a full source commit SHA.",
        )

    for field, value_field, label in (
        ("runner", "version", "runner version"),
        ("model", "identifier", "model identifier"),
    ):
        record = provenance.get(field)
        reason_field = f"{value_field}_unknown_reason"
        expected_fields = (
            {"surface", value_field, reason_field}
            if field == "runner"
            else {value_field, reason_field}
        )
        if not isinstance(record, dict) or set(record) != expected_fields:
            add_issue(
                issues,
                "error",
                "RELEASE_PROVENANCE_DETAIL",
                result_path,
                f"Scenario evidence has an incomplete {field} record.",
            )
            continue
        if field == "runner" and not str(record.get("surface", "")).strip():
            add_issue(
                issues,
                "error",
                "RELEASE_PROVENANCE_DETAIL",
                result_path,
                "Runner surface must be recorded.",
            )
        value = record.get(value_field)
        reason = record.get(reason_field)
        known = isinstance(value, str) and bool(value.strip())
        unknown = value is None and isinstance(reason, str) and bool(reason.strip())
        if not (known ^ unknown) or (known and reason is not None):
            add_issue(
                issues,
                "error",
                "RELEASE_PROVENANCE_UNKNOWN",
                result_path,
                f"Record an exact {label}, or null plus an explicit unknown reason.",
            )

    timing = provenance.get("timing")
    if not isinstance(timing, dict) or set(timing) != {
        "started_at",
        "finished_at",
        "duration_ms",
        "unknown_reason",
    }:
        add_issue(
            issues,
            "error",
            "RELEASE_TIMING",
            result_path,
            "Scenario evidence has an incomplete timing record.",
        )
    else:
        timing_values = [timing.get("started_at"), timing.get("finished_at"), timing.get("duration_ms")]
        if all(value is None for value in timing_values):
            if not str(timing.get("unknown_reason", "")).strip():
                add_issue(issues, "error", "RELEASE_TIMING", result_path, "Unknown timing needs an explicit reason.")
        else:
            valid_timing = isinstance(timing.get("duration_ms"), int) and timing["duration_ms"] >= 0
            parsed_times: dict[str, dt.datetime] = {}
            for field in ("started_at", "finished_at"):
                try:
                    parsed = dt.datetime.fromisoformat(str(timing.get(field)).replace("Z", "+00:00"))
                    valid_timing = valid_timing and parsed.tzinfo is not None
                    parsed_times[field] = parsed
                except ValueError:
                    valid_timing = False
            if len(parsed_times) == 2 and isinstance(timing.get("duration_ms"), int):
                elapsed_ms = int(
                    (parsed_times["finished_at"] - parsed_times["started_at"]).total_seconds()
                    * 1000
                )
                valid_timing = valid_timing and elapsed_ms >= 0 and abs(
                    elapsed_ms - timing["duration_ms"]
                ) <= 1000
            if not valid_timing or timing.get("unknown_reason") is not None:
                add_issue(issues, "error", "RELEASE_TIMING", result_path, "Timing must use timezone-aware timestamps and a non-negative duration, or nulls plus a reason.")

    usage = provenance.get("usage")
    if not isinstance(usage, dict) or set(usage) != {
        "input_tokens",
        "output_tokens",
        "cost_usd",
        "unknown_reason",
    }:
        add_issue(issues, "error", "RELEASE_USAGE", result_path, "Scenario evidence has an incomplete usage record.")
    else:
        values = [usage.get("input_tokens"), usage.get("output_tokens"), usage.get("cost_usd")]
        numbers_valid = all(
            value is None or (isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0)
            for value in values
        )
        needs_reason = any(value is None for value in values)
        reason_present = isinstance(usage.get("unknown_reason"), str) and bool(usage["unknown_reason"].strip())
        if not numbers_valid or needs_reason != reason_present:
            add_issue(issues, "error", "RELEASE_USAGE", result_path, "Record non-negative usage values; every unavailable value needs an explicit reason.")

    isolation = provenance.get("isolation")
    if not isinstance(isolation, dict) or set(isolation) != {
        "method",
        "expected_answer_withheld",
        "agent_input_bundle_sha256",
        "evaluator_bundle_sha256",
    }:
        add_issue(issues, "error", "RELEASE_PROVENANCE_ISOLATION", result_path, "Scenario evidence has an incomplete isolation record.")
        return
    if isolation.get("expected_answer_withheld") is not True or not str(isolation.get("method", "")).strip():
        add_issue(issues, "error", "RELEASE_PROVENANCE_ISOLATION", result_path, "Isolation method and withheld-answer confirmation are required.")

    evaluation = result.get("evaluation")
    if not isinstance(evaluation, dict) or set(evaluation) != {
        "evaluator",
        "rubric_version",
        "scoring_rationale",
    }:
        add_issue(issues, "error", "RELEASE_EVALUATION", result_path, "Scenario evidence has an incomplete evaluation record.")
    else:
        rationale = evaluation.get("scoring_rationale")
        if not str(evaluation.get("evaluator", "")).strip() or not str(evaluation.get("rubric_version", "")).strip():
            add_issue(issues, "error", "RELEASE_EVALUATION", result_path, "Evaluator identity and rubric version are required.")
        if not isinstance(rationale, dict) or set(rationale) != QUALITY_DIMENSIONS or not all(
            isinstance(value, str) and value.strip() for value in rationale.values()
        ):
            add_issue(issues, "error", "RELEASE_SCORING_RATIONALE", result_path, "Every quality dimension needs a non-empty scoring rationale.")

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

    agent_bundle = named_digest_sha256(
        "build-engineering-harness-agent-input-v1",
        {
            "skill_tree_sha256": hash_targets["skill_tree_sha256"],
            "prompt_sha256": hash_targets["prompt_sha256"],
            "fixture_tree_sha256": hash_targets["fixture_tree_sha256"],
        },
    )
    evaluator_bundle = named_digest_sha256(
        "build-engineering-harness-evaluator-input-v1",
        {
            "agent_input_bundle_sha256": agent_bundle,
            "expected_sha256": hash_targets["expected_sha256"],
            "response_sha256": hash_targets["response_sha256"],
        },
    )
    check_hash_value(
        issues,
        result_path,
        "agent_input_bundle_sha256",
        isolation.get("agent_input_bundle_sha256"),
        agent_bundle,
    )
    check_hash_value(
        issues,
        result_path,
        "evaluator_bundle_sha256",
        isolation.get("evaluator_bundle_sha256"),
        evaluator_bundle,
    )


def check_installation_provenance(
    root: Path, result: dict, result_path: Path, issues: list[Issue]
) -> None:
    if result.get("schema_version") != 2:
        add_issue(
            issues,
            "error",
            "RELEASE_INSTALLATION_SCHEMA",
            result_path,
            "Installation evidence must use provenance schema version 2.",
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
        "installer_python_sha256",
        "installer_powershell_sha256",
        "installer_shell_sha256",
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
        built = build_release_artifacts(
            root, Path(directory), source_commit, verify_source=False
        )
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
            "installer_python_sha256": str(built["installer_hashes"]["install_skill.py"]),
            "installer_powershell_sha256": str(built["installer_hashes"]["install.ps1"]),
            "installer_shell_sha256": str(built["installer_hashes"]["install.sh"]),
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
        runs_dir = scenario_dir / str(manifest.get("runs_dir", "runs"))
        if not runs_dir.is_dir():
            add_issue(
                issues,
                "error",
                "RELEASE_SCENARIO_RESULT",
                runs_dir.relative_to(root),
                "Append-only scenario run history is required for release.",
            )
            continue
        run_dirs = sorted(path for path in runs_dir.iterdir() if path.is_dir())
        if not run_dirs:
            add_issue(
                issues,
                "error",
                "RELEASE_SCENARIO_RESULT",
                runs_dir.relative_to(root),
                "At least one scored scenario run is required for release.",
            )
            continue

        release_run = manifest.get("release_run")
        release_run_found = False
        for run_dir in run_dirs:
            if run_dir.name == release_run:
                release_run_found = True
            response_path = run_dir / "response.md"
            result_path = run_dir / "result.json"
            allowed = {"response.md", "result.json"}
            actual = {path.name for path in run_dir.iterdir()}
            if actual != allowed:
                add_issue(
                    issues,
                    "error",
                    "RELEASE_RUN_LAYOUT",
                    run_dir.relative_to(root),
                    "Each run directory must contain exactly response.md and result.json.",
                )
            if not response_path.is_file() or not read_text(response_path).strip():
                add_issue(
                    issues,
                    "error",
                    "RELEASE_SCENARIO_RESPONSE",
                    response_path.relative_to(root),
                    "Raw scenario response is required for every recorded run.",
                )
            if not result_path.is_file():
                add_issue(
                    issues,
                    "error",
                    "RELEASE_SCENARIO_RESULT",
                    result_path.relative_to(root),
                    "Scored scenario result is required for every recorded run.",
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
                response_path,
                issues,
            )
            gates = result.get("hard_gates")
            scores = result.get("quality_scores")
            gates_valid = (
                isinstance(gates, dict)
                and set(gates) == HARD_GATES
                and all(isinstance(value, bool) for value in gates.values())
            )
            scores_valid = (
                isinstance(scores, dict)
                and set(scores) == QUALITY_DIMENSIONS
                and all(isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 2 for value in scores.values())
            )
            total = sum(scores.values()) if scores_valid else -1
            computed_pass = (
                gates_valid
                and all(gates.values())
                and scores_valid
                and total >= 8
                and scores["evidence_quality"] > 0
                and scores["boundary_control"] > 0
            )
            rel_result = result_path.relative_to(root)
            if result.get("scenario_id") != scenario_id:
                add_issue(issues, "error", "RELEASE_SCENARIO_ID", rel_result, "Result id does not match scenario.")
            if not gates_valid:
                add_issue(issues, "error", "RELEASE_HARD_GATE", rel_result, "Hard-gate results must be complete booleans.")
            if not scores_valid or result.get("total") != total:
                add_issue(issues, "error", "RELEASE_SCORE", rel_result, "Quality scores and total must be internally consistent.")
            if result.get("passed") is not computed_pass:
                add_issue(issues, "error", "RELEASE_SCENARIO_PASS", rel_result, "The passed flag must match gates and scoring thresholds.")
            if run_dir.name == release_run and not computed_pass:
                add_issue(issues, "error", "RELEASE_SELECTED_RUN", rel_result, "The manifest-selected release run must pass.")

        if not release_run_found:
            add_issue(
                issues,
                "error",
                "RELEASE_SELECTED_RUN",
                manifest_path.relative_to(root),
                "release_run does not name an existing run directory.",
            )

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
    check_trusted_release_workflow(root, issues)
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
