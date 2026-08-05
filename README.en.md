# Build Engineering Harness

[中文](README.md)

An engineering Skill for reliable collaboration between humans and AI agents. It audits, establishes, and improves project goals, repository knowledge, rules, verification, and feedback loops, then captures evidence-based retrospective and onboarding knowledge when a project closes.

> Status: `v0.1.1-beta`. Three independent forward tests, a clean installation from GitHub, and Windows/Linux GitHub Actions have passed. This release adds public security-reporting and feedback routes and remains a Beta pre-release.

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

Clone this repository and run the following from its root.

PowerShell:

```powershell
$codexSkillsDir = Join-Path $env:USERPROFILE ".codex\skills"
New-Item -ItemType Directory -Force -Path $codexSkillsDir | Out-Null
Copy-Item -Recurse -Force ".\skill\build-engineering-harness" $codexSkillsDir
```

macOS or Linux:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R ./skill/build-engineering-harness "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Start a new Codex task after copying so the Skill catalog can refresh.

## Validation

The repository provides dependency-free, cross-platform validation:

```text
python -m unittest discover -s tests/static -v
python scripts/validate_repository.py
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

## `v0.1.1-beta` validation evidence

- The isolated L1, L2, and L3 forward tests passed every safety gate with 10/10 quality scores. Sanitized responses and scored results live under [`tests/scenarios/`](tests/scenarios/).
- The Skill was cloned and installed from the public GitHub repository, then checked for file-hash equality, repository validity, official Skill validity, and use by a fresh agent. See [`tests/installation/result.json`](tests/installation/result.json).
- GitHub Actions validates both Windows and Linux; tag builds additionally run release-evidence validation.

These are reproducible representative synthetic scenarios, not coverage of every production repository. `v0.1.1-beta` does not change the installable Skill behavior; use it as a pre-release rather than a stable-release promise.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes. See [SECURITY.md](SECURITY.md) for security reporting. Release changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## Methodology and inspiration

This project combines a personal AI engineering playbook, agent-friendly repository practices, and evidence-driven verification into an executable Skill. Its overall Harness Engineering direction was inspired by OpenAI's [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/). The repository knowledge governance model is an original generalized synthesis for software projects.

## License

This project is licensed under the [MIT License](LICENSE).
