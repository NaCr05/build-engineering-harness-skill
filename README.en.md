# Build Engineering Harness

[中文](README.md)

[![Validate repository](https://github.com/NaCr05/build-engineering-harness-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/NaCr05/build-engineering-harness-skill/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/NaCr05/build-engineering-harness-skill?include_prereleases&label=release)](https://github.com/NaCr05/build-engineering-harness-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Codex engineering Skill that helps humans and AI agents collaborate around clear goals, trustworthy repository knowledge, explicit boundaries, and executable evidence instead of relying on one-off prompts.

`Read-only assessment → improvement plan → user approval → implementation → automated verification`

> Repository version: `v0.3.3-beta`. [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases) is authoritative for publication and download availability; `main` may be ahead of a public release.

## 30-second start

After installation, open your project in Codex and send:

```text
Use $build-engineering-harness to perform a read-only assessment of this repository.
Review its goals, architecture, repository knowledge, development workflow, verification,
and feedback loops. Separate observed facts, inferences, risks, and recommendations.
Do not modify files yet.
```

The Skill first uses repository evidence to report maturity, prioritized findings, and a staged improvement plan. It changes only the scope you explicitly approve. Not installed yet? Jump to [Installation](#installation).

## What you get

| Your situation | Primary output |
|---|---|
| A nearly finished project needs cleanup or open-source preparation | A readiness assessment across goals, architecture, repository knowledge, workflow, verification, and release practices |
| README files, docs, AGENTS.md, or current-state notes keep drifting | An audit of artifact roles, authority, sources of truth, ownership, and drift risks |
| AI or agent behavior needs engineering rigor | Checks for prompts, context, tools, memory, output schemas, failure handling, cost, latency, and reliability |
| You approve an improvement plan | Scope-controlled changes, automated verification evidence, and remaining risks |
| A project is ready for handoff or closure | An evidence-based retrospective and newcomer onboarding guide |

It works for new, legacy, team, and agent-intensive repositories without forcing every project into the same fixed document set.

## Workflow and safety boundary

Engineering-harness mode has two strictly separated phases:

1. **Read-only assessment:** inspect evidence, separate facts from inferences, and propose a reviewable plan without modifying the project.
2. **Approved implementation:** implement only explicitly approved items, preserve unrelated changes, and report verification results.

Ordinary requests to assess, audit, or explain do not authorize writes. Project closeout is an explicit exception: when the user directly requests `project-closeout`, the Skill may create or update only `docs/project-retrospective.md` and `docs/project-onboarding.md`.

See [`SKILL.md`](skill/build-engineering-harness/SKILL.md) for the runtime rules loaded by Codex and [`SKILL.zh-CN.md`](skill/build-engineering-harness/SKILL.zh-CN.md) for the synchronized Chinese explanation.

## Use cases and maturity

The Skill scales its recommendations to risk, team size, change rate, agent involvement, and error cost:

| Level | Typical context | Focus |
|---|---|---|
| L1 Foundation | Small or low-risk projects | Entry points, core rules, necessary contracts, and runnable verification |
| L2 Managed | Ongoing team collaboration | Central registry, ownership, decision history, and synchronization checks |
| L3 Agent-intensive | High agent involvement or high-risk systems | Scoped instructions, project Skills, evaluations, generated evidence, and automation |

Repository knowledge is governed with a **functional-role × update-semantics** model. Every artifact has exactly one primary role, one update semantic, one authority attribute, and explicit ownership, update triggers, and verification. See the [repository knowledge governance reference](skill/build-engineering-harness/references/repository-knowledge-governance.md) for the six roles and four update semantics.

## Installation

### Support scope

| Surface | Supported contract | CI evidence |
|---|---|---|
| Python tooling and installer | CPython 3.10–3.13 | Every version on Ubuntu; Python 3.12 on Windows and macOS |
| PowerShell installer wrapper | PowerShell 7 on Windows | `windows-latest` dry-run |
| POSIX installer wrapper | `sh` on Ubuntu and macOS | `ubuntu-latest` and `macos-latest` dry-run |
| Operating systems | Current GitHub-hosted Windows, Ubuntu, and macOS runner images | Verified on every pull request and `main` push |

Windows PowerShell 5.1, other Unix distributions, and WSL are best-effort rather than CI-guaranteed. Include exact versions and a minimal reproduction when reporting compatibility issues.

Prerequisites: Python within the supported range, a [GitHub CLI](https://cli.github.com/) version that supports `gh attestation`, and an authenticated `gh auth login`. Choose an explicitly published, pinned version from [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases). The examples use the current repository version.

The fixed sequence is: download assets → verify GitHub Artifact Attestations → run the installer's read-only validation → install. Provenance is constrained to this repository, the selected version tag, and the pinned signer workflow.

<details>
<summary>PowerShell (Windows)</summary>

```powershell
$version = "v0.3.3-beta"
$repository = "NaCr05/build-engineering-harness-skill"
$signerWorkflow = "$repository/.github/workflows/validate.yml"
$assetBase = "build-engineering-harness-$version"
$assets = Join-Path $env:TEMP "$assetBase-assets"
New-Item -ItemType Directory -Force -Path $assets | Out-Null
gh release download $version --repo $repository --dir $assets --pattern "$assetBase*" --pattern "install*"

Get-ChildItem -LiteralPath $assets -File | ForEach-Object {
    gh attestation verify $_.FullName --repo $repository --source-ref "refs/tags/$version" --signer-workflow $signerWorkflow
    if ($LASTEXITCODE -ne 0) { throw "Attestation verification failed for $($_.Name)" }
}

& "$assets\install.ps1" -Version $version -AssetDir $assets -DryRun
& "$assets\install.ps1" -Version $version -AssetDir $assets
```

</details>

<details>
<summary>macOS or Linux</summary>

```bash
set -eu
version="v0.3.3-beta"
repository="NaCr05/build-engineering-harness-skill"
signer_workflow="$repository/.github/workflows/validate.yml"
asset_base="build-engineering-harness-$version"
assets="$(mktemp -d)"
gh release download "$version" --repo "$repository" --dir "$assets" --pattern "$asset_base*" --pattern "install*"

for asset in "$assets"/*; do
  gh attestation verify "$asset" --repo "$repository" --source-ref "refs/tags/$version" --signer-workflow "$signer_workflow"
done

sh "$assets/install.sh" --version "$version" --asset-dir "$assets" --dry-run
sh "$assets/install.sh" --version "$version" --asset-dir "$assets"
```

</details>

The installer honors `CODEX_HOME` and otherwise uses `.codex` under the user home directory. Upgrades first retain a backup and automatically restore it on failure. Start a new Codex task after installing or upgrading so the Skill catalog can refresh.

## Common prompts

### Audit repository knowledge governance

```text
Use $build-engineering-harness to audit this repository's knowledge governance at L2 maturity.
Check artifact roles, update semantics, authority scopes, sources of truth, verification
relationships, and documentation drift. Wait for approval before implementing changes.
```

### Review an AI or agent project

```text
Use $build-engineering-harness to assess this agent project.
In addition to the general engineering review, inspect prompts, context, tools, memory,
output schemas, failure handling, and evaluation coverage for accuracy, latency, cost,
and reliability.
```

### Implement approved improvements

```text
I approve items 1, 3, and 4 from the previous proposal.
Implement only those items, preserve unrelated changes, and report verification evidence
and remaining risks when finished.
```

### Close a project

```text
Use $build-engineering-harness in project-closeout mode.
Create the evidence-based retrospective and onboarding documents without modifying product
code or any other project files.
```

## Trust and verification

| Guarantee | Mechanism | Evidence |
|---|---|---|
| Skill behavior is evaluable | Isolated L1, L2, and L3 forward tests with common safety gates | [`tests/scenarios/`](tests/scenarios/) and [`tests/README.md`](tests/README.md) |
| Evaluation runs are traceable | Schema v2 hashes, run and evaluator provenance, scoring rationale, and append-only history | [`tests/scenarios/`](tests/scenarios/) |
| Installation is verifiable | Manifest, archive and file hashes, backups, and automatic rollback | [`tests/installation/result.json`](tests/installation/result.json) |
| Cross-platform builds agree | Independent Windows and Linux builds compared byte for byte | [Validation workflow](.github/workflows/validate.yml) |
| Release provenance is verifiable | GitHub Artifact Attestations for all six release assets | [GitHub Releases](https://github.com/NaCr05/build-engineering-harness-skill/releases) |

Local validation requires no third-party Python package:

```text
python -m unittest discover -s tests/static -v
python scripts/validate_repository.py
python scripts/build_release_package.py --output-dir .test-runs/release-package
python scripts/validate_repository.py --release
```

This evidence comes from reproducible representative synthetic scenarios. It is not coverage of every production repository or a stable-release promise.

## Project navigation

| What you need | Authoritative entry |
|---|---|
| Runtime behavior and safety boundaries | [`skill/build-engineering-harness/SKILL.md`](skill/build-engineering-harness/SKILL.md) |
| Personal AI engineering method | [`personal-ai-engineering-playbook.md`](skill/build-engineering-harness/references/personal-ai-engineering-playbook.md) |
| Repository knowledge governance model | [`repository-knowledge-governance.md`](skill/build-engineering-harness/references/repository-knowledge-governance.md) |
| Forward tests, isolation, and scoring | [`tests/README.md`](tests/README.md) |
| Release history | [`CHANGELOG.md`](CHANGELOG.md) |
| Contribution workflow | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Security reporting | [`SECURITY.md`](SECURITY.md) |

## Methodology and license

This project combines a personal AI engineering method, agent-friendly repository practices, and evidence-driven verification into an executable Skill. Its overall direction was inspired by OpenAI's [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/). The repository knowledge governance model is an original generalized synthesis for software projects.

This project is licensed under the [MIT License](LICENSE).
