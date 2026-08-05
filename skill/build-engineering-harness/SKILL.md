---
name: build-engineering-harness
description: Establish, audit, improve, and close out an engineering harness for new or existing software repositories. Use when Codex is asked to assess project readiness, clarify goals and success criteria, document architecture or development workflows, audit or organize repository knowledge such as README files, docs, AGENTS.md, decision records, and current-state artifacts, define human-agent responsibilities, prevent knowledge drift, strengthen tests or evaluations, add feedback and learning loops, apply the user's Personal AI Engineering Playbook, or close a completed project by writing an evidence-based retrospective and a newcomer onboarding guide. Apply to any software project and add prompt, context, tool, memory, output-schema, failure-handling, cost, latency, and reliability checks when AI or agent components are present.
---

# Build Engineering Harness

Turn a software repository into an environment where humans and agents can work reliably. Treat documentation, rules, tools, verification, and feedback as parts of the product rather than afterthoughts.

Read [references/personal-ai-engineering-playbook.md](references/personal-ai-engineering-playbook.md) before assessing a project. Use it as the governing methodology while following the operational workflow below.

When the task concerns repository knowledge architecture, documentation governance, scoped instructions, source-of-truth conflicts, documentation drift, or agent navigability, also read [references/repository-knowledge-governance.md](references/repository-knowledge-governance.md). For a formal audit, copy and adapt [assets/repository-knowledge-audit-template.md](assets/repository-knowledge-audit-template.md); do not force the template onto a smaller request that only needs a focused finding or recommendation.

## Choose the operating mode

Use **engineering-harness mode** for project assessment, setup, or improvement. Follow the two-phase approval contract below.

Use **project-closeout mode** when the user explicitly asks to close, wrap up, retrospect, summarize lessons from, or create onboarding documentation for a completed project. In this mode, create or update exactly:

- `docs/project-retrospective.md`
- `docs/project-onboarding.md`

An explicit request for project-closeout mode authorizes writing only these two documentation files. Do not require a separate proposal approval unless a required fact cannot be discovered or updating an existing file would discard conflicting hand-written content.

## Operating contract

In engineering-harness mode, use two strictly separated phases:

1. Inspect and propose without modifying the project.
2. Implement only after the user explicitly approves the proposal.

Do not interpret the initial request to assess, prepare, establish, or improve a harness as approval to write files. End phase 1 with a concrete proposal and wait for confirmation.

Respect repository instructions and existing conventions. Preserve unrelated user changes and do not replace sound existing documentation merely to enforce preferred filenames.

## Phase 1: Inspect and propose

Inspect the repository read-only. Locate governing instructions, documentation, source layout, build configuration, tests, automation, version-control state, and current validation commands. Infer discoverable facts from the repository instead of asking the user.

Classify the project as a general software project or a project containing AI or agent components. Identify:

- the project goal, intended users, inputs, outputs, and measurable success criteria;
- architectural boundaries, data flow, APIs, and core components;
- existing repository knowledge and where it lives;
- development and release workflows;
- the current division of responsibility between humans, agents, and automation;
- available tests, evaluations, logging, error handling, and feedback loops;
- knowledge that should be captured as reusable documentation, templates, or automation.

For AI or agent components, additionally inspect:

- prompt clarity and versioning;
- context sources, selection, freshness, and limits;
- tool inputs, outputs, permissions, and error behavior;
- output schemas and downstream validation;
- memory scope, retention, privacy, and stale-state risks;
- failure handling, retries, fallbacks, and observability;
- evaluation coverage for accuracy, latency, cost, and reliability.

If essential intent cannot be discovered, ask one focused decision question at a time and provide a recommended answer.

Deliver a phase-1 proposal containing:

1. **Project understanding** — current purpose, users, inputs, outputs, architecture, and important assumptions.
2. **Harness inventory** — what already exists and should be retained.
3. **Gaps and risks** — prioritized by impact, with evidence from repository files.
4. **Proposed changes** — exact files to create or update and a concise description of each change.
5. **Verification plan** — commands, tests, evaluations, and expected evidence of success.
6. **Supporting code changes** — any proposed small product-code edits, separately identified with their scope and behavior-preservation rationale.
7. **Decisions needed** — unresolved choices that belong to the user.

Wait for explicit approval. If the user approves only part of the proposal, implement only that part.

## Phase 2: Implement the approved plan

Prefer updating useful existing files over adding parallel documentation. Create new files only when the required knowledge has no suitable home. Adapt names and locations to repository conventions; do not mechanically create a fixed document set.

Ensure the resulting project knowledge covers, where relevant:

- project purpose, users, inputs, outputs, and measurable success criteria;
- architecture, module boundaries, data flow, interfaces, and major decisions;
- setup, development, testing, debugging, and release workflows;
- human-agent responsibilities and safe handoff points;
- common failures, troubleshooting, and learned constraints;
- verification procedures and interpretation of results;
- reusable templates, automation, and lessons learned.

Keep documentation close to the code or configuration it governs. Prefer explicit module names and responsibilities over vague catch-all structures.

## Project-closeout mode

Read [references/project-closeout-templates.md](references/project-closeout-templates.md) before writing either closeout document.

### Gather evidence

Inspect repository instructions, existing documentation, manifests, source layout, entry points, tests, build and deployment configuration, version-control history, and current working-tree state. Use source files and actual verification results as evidence; do not treat plans or stale documentation as delivered behavior.

Infer discoverable facts instead of asking the user. If a critical fact such as the intended project goal cannot be recovered, ask one focused question. Record non-critical unknowns explicitly rather than inventing them.

Do not expose secrets, personal data, credentials, or sensitive environment values. Mention configuration variable names only when needed.

### Verify the final state

Run existing safe and relevant build, test, lint, or evaluation commands when their cost and side effects are reasonable. Do not run destructive, production, deployment, migration, or paid evaluation commands without separate authorization.

Distinguish:

- implemented and verified behavior;
- implemented but unverified behavior;
- planned or incomplete behavior.

Never present a passing status without actual command evidence.

### Write the fixed outputs

Create the `docs/` directory if needed. Create or update both required files in the same run:

1. `docs/project-retrospective.md`
2. `docs/project-onboarding.md`

Match the user's requested language; otherwise follow the dominant language of maintained project documentation. When a target file already exists, preserve accurate hand-written knowledge and refresh stale sections instead of replacing it wholesale.

Use relative repository links for referenced files. Keep both documents useful after the current conversation ends and avoid duplicating long content already maintained elsewhere; link to the source of truth.

In project-closeout mode, do not modify product code, tests, configuration, dependencies, or any other project documentation unless the user separately requests it.

### Check document quality

Before finishing:

- confirm both required files exist;
- confirm every required section from the template is present;
- verify commands and file links where practical;
- cross-check that goals, architecture, entry points, and verification status agree across both documents;
- remove vague lessons, unsupported claims, placeholders, and accidental secrets.

Report the two file paths, checks actually run, remaining unknowns, and any evidence limitation.

## Product-code boundary

Apply this section only in engineering-harness mode. Project-closeout mode is documentation-only.

Do not implement new business features or perform broad architectural rewrites.

Make a supporting product-code change only when all of these conditions hold:

- it was listed in the approved phase-1 proposal;
- it preserves intended business behavior;
- it does not change a public API, database schema, or external protocol;
- it does not add a production dependency;
- its impact is localized, explainable, and testable.

Allowed supporting changes include:

- improving ambiguous names;
- splitting a clearly oversized function, class, or file along existing responsibilities;
- adding logging, error handling, type information, or input validation;
- making a localized adjustment that improves testability.

If the scope or behavioral impact cannot be stated confidently, provide a recommendation instead of changing the code.

## Build executable verification

Run existing relevant checks first. Add only the tests, evaluation scripts, fixtures, or minimal validation configuration approved by the user.

Cover normal behavior, important boundaries, and failure paths in proportion to project risk. For AI or agent systems, use measurable evaluations for accuracy, latency, cost, and reliability when applicable.

Never report that something works based only on inspection. Record the exact checks run, distinguish passed checks from unrun ones, and explain any environmental limitation or remaining gap.

## Close the feedback loop

Finish phase 2 with:

- files created or changed;
- verification evidence and results;
- unresolved risks or decisions;
- reusable assets produced;
- lessons worth adding to existing project knowledge;
- the smallest useful next iteration.

Keep the harness proportional to the project. Favor a small, maintained source of truth over a large set of stale documents.
