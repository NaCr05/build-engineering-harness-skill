# Build Engineering Harness

[中文](README.md)

An engineering Skill for reliable collaboration between humans and AI agents. It audits, establishes, and improves project goals, repository knowledge, rules, verification, and feedback loops, then captures evidence-based retrospective and onboarding knowledge when a project closes.

> Status: `v0.2.0-beta`. Test evidence is now bound to run provenance and recomputable hashes, and the release provides a versioned installation archive with a checksum and manifest. This remains a Beta pre-release.

## What it solves

Reliable agent work depends on more than model capability. A repository also needs clear goals, trustworthy sources of truth, explicit boundaries, executable workflows, and fast verification.

Use this Skill to ask:

- Are the goal, users, inputs, outputs, and success criteria clear?
- Are architecture, module boundaries, data flow, and interfaces understandable?
- Do README files, docs, AGENTS.md, decisions, and current-state artifacts have clear responsibilities?
- Are there duplicated sources of truth, conflicting rules, or drift-prone explanations?
- Are human, agent, and automation responsibilities explicit?
- Do tests, evaluations, logs, and error handling provide evidence of correctness?
- Which lessons should become durable repository assets?

## Core capabilities

- **Engineering harness assessment** based on repository evidence.
- **Repository knowledge governance** using a functional-role by update-semantics model.
- **Authority and relationship analysis** across canonical, explanatory, and evidence artifacts.
- **AI and agent project review** covering prompts, context, tools, memory, output schemas, failure handling, cost, latency, and reliability.
- **Executable verification loops** that replace subjective confidence with evidence.
- **Project closeout** with evidence-based retrospective and newcomer onboarding documents.

## Safety contract

Engineering-harness mode uses two strictly separated phases:

1. Inspect read-only and propose changes.
2. Implement only the explicitly approved scope.

Project-closeout mode is an explicit exception. When the user directly requests closeout, the Skill may create or update only:

- `docs/project-retrospective.md`
- `docs/project-onboarding.md`

An assessment request is never treated as write authorization, and the Skill does not mechanically restructure a repository to match preferred filenames.

## Repository knowledge governance

Each knowledge-bearing artifact receives:

- exactly one primary role and zero to two secondary roles;
- exactly one update semantic;
- exactly one authority attribute;
- an owner, update trigger, and verification method.

The six functional roles are navigation and routing, rules and boundaries, specifications and contracts, state and evidence, rationale and history, and execution and verification.

The four update semantics are stable entry, synchronized, append-only evolution, and derived or generated.

This is a classification and diagnostic space, not a requirement to create a fixed number of documents.

## Maturity levels

| Level | Typical context | Focus |
|---|---|---|
| L1 Foundation | Small or low-risk projects | Entry points, core rules, necessary contracts, and runnable verification |
| L2 Managed | Ongoing team collaboration | Central registry, ownership, decision history, and synchronization checks |
| L3 Agent-intensive | High agent involvement or high-risk systems | Scoped instructions, project Skills, evaluations, generated evidence, and automation |

Choose a level from risk, collaboration size, change rate, agent involvement, and error cost rather than repository size alone.

## Installation

Install a pinned version from GitHub Releases. The commands below require GitHub CLI; you can instead download the ZIP, `.sha256`, and manifest with matching names from the [`v0.2.0-beta` Release](https://github.com/NaCr05/build-engineering-harness-skill/releases/tag/v0.2.0-beta) page.

PowerShell:

```powershell
$version = "v0.2.0-beta"
$assetBase = "build-engineering-harness-$version"
gh release download $version --repo NaCr05/build-engineering-harness-skill --pattern "$assetBase*"

$expected = ((Get-Content "$assetBase.zip.sha256").Trim() -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash "$assetBase.zip" -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "Release archive checksum mismatch." }

$skillsDir = Join-Path $env:USERPROFILE ".codex\skills"
$target = Join-Path $skillsDir "build-engineering-harness"
if (Test-Path $target) { throw "Target already exists: $target. Back it up or remove it before upgrading." }
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
Expand-Archive -LiteralPath "$assetBase.zip" -DestinationPath $skillsDir
```

macOS or Linux:

```bash
version="v0.2.0-beta"
asset_base="build-engineering-harness-$version"
gh release download "$version" --repo NaCr05/build-engineering-harness-skill --pattern "$asset_base*"

expected="$(awk '{print $1}' "$asset_base.zip.sha256")"
actual="$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$asset_base.zip")"
[ "$actual" = "$expected" ] || { echo "Release archive checksum mismatch." >&2; exit 1; }

skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
target="$skills_dir/build-engineering-harness"
[ ! -e "$target" ] || { echo "Target already exists: $target. Back it up or remove it before upgrading." >&2; exit 1; }
mkdir -p "$skills_dir"
unzip -q "$asset_base.zip" -d "$skills_dir"
```

For a source installation, clone the version tag rather than moving `main`:

```bash
git clone --branch v0.2.0-beta --depth 1 https://github.com/NaCr05/build-engineering-harness-skill.git
```

Start a new Codex task after installing or upgrading so the Skill catalog can refresh.

## Validation

The repository provides dependency-free, cross-platform validation:

```text
python -m unittest discover -s tests/static -v
python scripts/validate_repository.py
python scripts/build_release_package.py --output-dir .test-runs/release-package
```

GitHub Actions runs the same checks on Windows and Linux. Before a release, also run:

```text
python scripts/validate_repository.py --release
```

`--release` additionally requires L1, L2, and L3 forward-test evidence plus a clean installation record from GitHub. See `tests/README.md` for scenario isolation and scoring.

## Quick usage

### Assess an existing repository

```text
Use $build-engineering-harness to perform a read-only assessment of this repository.
Review its goals, architecture, repository knowledge, development workflow, verification,
and feedback loops. Separate observed facts, inferences, risks, and recommendations.
Do not modify files yet.
```

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

### Implement approved changes

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

## Repository layout

```text
skill/build-engineering-harness/
├── SKILL.md
├── SKILL.zh-CN.md
├── agents/openai.yaml
├── references/
│   ├── personal-ai-engineering-playbook.md
│   ├── project-closeout-templates.md
│   └── repository-knowledge-governance.md
└── assets/
    └── repository-knowledge-audit-template.md
```

`SKILL.md` is the runtime entry loaded by Codex. `SKILL.zh-CN.md` is a synchronized human-readable Chinese translation. Detailed methods live in `references/`; reusable output templates live in `assets/`.

## `v0.2.0-beta` validation evidence

- The isolated L1, L2, and L3 forward tests passed every safety gate with 10/10 quality scores. Sanitized responses and scored results live under [`tests/scenarios/`](tests/scenarios/).
- Forward-test evidence records the run ID, source commit, isolation method, and recomputable SHA-256 hashes for the Skill, prompt, fixture, expectations, and response. See [`tests/scenarios/`](tests/scenarios/).
- A deterministic versioned ZIP was built and installed from the public GitHub repository; the archive, checksum, manifest, source tree, installed tree, and fresh-agent response were verified. See [`tests/installation/result.json`](tests/installation/result.json).
- GitHub Actions validates and packages on Windows and Linux; tag builds additionally run release-evidence validation.

These are reproducible representative synthetic scenarios, not coverage of every production repository. `v0.2.0-beta` does not change the installable Skill behavior; use it as a pre-release rather than a stable-release promise.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes. See [SECURITY.md](SECURITY.md) for security reporting. Release changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## Methodology and inspiration

This project combines a personal AI engineering playbook, agent-friendly repository practices, and evidence-driven verification into an executable Skill. Its overall Harness Engineering direction was inspired by OpenAI's [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/). The repository knowledge governance model is an original generalized synthesis for software projects.

## License

This project is licensed under the [MIT License](LICENSE).
