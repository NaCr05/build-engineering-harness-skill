# Repository Knowledge Governance

Use this model to audit or design repository knowledge so humans and agents can find the right information, identify its authority, update it safely, and verify it. Apply it to all knowledge-bearing artifacts, not only Markdown: instructions, schemas, tests, scripts, manifests, generated reports, and code-level contracts can all participate.

## Contents

1. [Core model](#core-model)
2. [Functional roles](#functional-roles)
3. [Update semantics](#update-semantics)
4. [Authority](#authority)
5. [Controlled relationships](#controlled-relationships)
6. [Central registry](#central-registry)
7. [Enforcement ladder](#enforcement-ladder)
8. [Proportional maturity](#proportional-maturity)
9. [Audit workflow](#audit-workflow)
10. [Audit output contract](#audit-output-contract)

## Core model

Classify each artifact using two independent dimensions:

- **Functional role**: why the artifact exists.
- **Update semantics**: how the artifact is allowed to change.

Assign every artifact:

- exactly one primary role;
- zero to two secondary roles;
- exactly one update semantic;
- exactly one authority attribute.

Let the primary role determine location, ownership, maintenance responsibility, required structure, and verification. Use secondary roles only for navigation and understanding; never let them create a second maintenance contract.

Treat the role-by-update model as a classification space, not a checklist. Empty cells are valid. Do not create six documents or populate all 24 combinations merely to make the matrix look complete.

## Functional roles

Use these six roles without merging them.

### Navigation and routing (`navigation_routing`, 导览与路由)

Answer what the repository or area is, where a newcomer starts, and where each class of task goes. Keep detailed fields, implementation facts, and open discussion elsewhere. Verify links, route completeness, and bounded size.

### Rules and boundaries (`rules_boundaries`, 规则与边界)

State mandatory behavior, prohibitions, scope, consequences, safe paths, and the basis for the rule. Prefer mechanically checkable rules when possible. Exclude volatile parameters and long tutorials.

### Specifications and contracts (`specifications_contracts`, 规格与契约)

Define inputs, outputs, states, interfaces, failure semantics, and responsibility boundaries. Exclude current completion status, scheduling, and historical rationale.

### State and evidence (`state_evidence`, 状态与证据)

Record the current implementation level, gaps, and supporting evidence. Use a finite status vocabulary. Do not mix in historical rationale or unsupported future aspirations.

### Rationale and history (`rationale_history`, 原因与历史)

Record context, alternatives, decisions, consequences, and conditions for reopening a decision. Do not duplicate current normative values that belong to a canonical contract.

### Execution and verification (`execution_verification`, 执行与验证)

Define inputs, preconditions, steps, outputs, success criteria, failure classification, and recovery or stop conditions. Do not duplicate domain semantics that have a separate canonical source.

Only the primary role controls the artifact's required template. A secondary role never adds a second set of mandatory sections.

## Update semantics

Assign exactly one of these four modes.

### Stable entry (`stable_entry`, 稳定入口)

Change only when governance, navigation, scope, or locations change. Keep it compact. Verify links, scope, size, and freshness on an explicit review cadence.

### Synchronized (`synchronized`, 同步更新)

Update in the same change as the underlying truth. If no update is needed, record why when the relationship is not obvious. Verify against the canonical implementation, schema, configuration, or contract.

### Append-only evolution (`append_only`, 追加演进)

Add new entries or explicitly supersede old ones. Permit non-semantic corrections, but do not silently rewrite historical meaning. Verify ordering, identifiers, supersession links, and immutability expectations.

### Derived or generated (`derived_generated`, 派生生成)

Require explicit canonical inputs and a reproducible generator. The output must be deletable and regenerable, must not become an input to its own generation, and should record the generator or environment version or a result fingerprint. Fix the input or generator instead of hand-editing the output.

Every registered artifact must declare an `update_trigger` and `verification` appropriate to its update semantic.

## Authority

Treat authority as a mandatory orthogonal attribute, not a third classification axis.

### Canonical (`canonical`)

Defines truth for an explicit `authority_scope`. Two canonical artifacts must not overlap in scope unless an explicit upstream/downstream generation relationship explains the overlap.

### Explanatory (`explanatory`)

Explains canonical truth for a particular audience. It must declare `source_of_truth` and must not independently maintain normative facts. Resolve conflicts in favor of the canonical artifact.

### Evidence (`evidence`)

Supports, refutes, or triggers an update to a claim. It may demonstrate the current state but cannot define a standard by itself.

## Controlled relationships

Use only these relationship names in the registry:

- `routes_to`: directs a reader or agent to the next relevant artifact.
- `source_of_truth`: points explanatory material to its canonical source.
- `evidenced_by`: connects a claim or state to supporting evidence.
- `verified_by`: connects an artifact or rule to an executable or reviewable check.
- `generated_from`: connects derived output to canonical inputs and its generator.
- `supersedes`: records an explicit replacement in an append-only history.

Record direction centrally. Avoid vague `related_to` links.

Enforce these graph rules:

- explanatory artifacts must reach a canonical source through `source_of_truth`;
- material state claims must have `evidenced_by` links;
- verification targets must be locatable and executable or reviewable;
- derived artifacts require canonical inputs and a generator through `generated_from`;
- substantive historical changes use `supersedes` rather than silent edits;
- routing chains must terminate at canonical content, executable verification, or evidenced current state;
- flag dangling targets, unjustified cycles, orphaned canonical artifacts, and route chains without a useful terminal node.

## Central registry

Keep classification in one registry rather than repeating frontmatter in every document. Register a homogeneous directory once and add file-level exceptions when necessary. A derived output may include a visible do-not-edit header, but the registry remains authoritative for classification.

Use these fields, adapting their physical representation to repository conventions:

```yaml
artifact:
primary_role:
secondary_roles: []
update_semantics:
authority:
authority_scope:
owner:
update_trigger:
verification:
enforcement_level:
enforced_by: []
relations: []
```

Derive directory ownership and verification rules from the primary role. Do not let a secondary role create competing owners or checks.

## Enforcement ladder

Classify enforcement using five cumulative levels:

1. `documented`: the rule exists in maintained documentation.
2. `review_required`: a pull-request template or review checklist requires judgment.
3. `automated_warning`: automation reports a concern without blocking work.
4. `automated_blocking`: a local or CI check fails deterministically.
5. `structural_prevention`: types, interfaces, directory structure, or generators make the invalid state difficult or impossible to represent.

Escalate a rule when risk, repetition, and reliable detectability justify it:

- first make a real issue explicit in documentation;
- move repeated issues to review or warning;
- block when the judgment is deterministic, impact is clear, false positives are low, the fix is actionable, and the result is reproducible;
- prefer structural prevention when architecture can eliminate the failure class;
- allow high-risk security and contract rules to enter directly at blocking;
- keep product judgment, architectural sufficiency, writing quality, evidence adequacy, and visual or UX quality under human review when automation cannot judge them reliably.

Allow de-escalation. Move noisy checks back to warnings, remove obsolete rules when architecture eliminates the risk, and reassess automation after tooling or model changes.

## Proportional maturity

Choose a target maturity from risk, collaboration size, change rate, agent involvement, and error cost rather than repository size alone.

### L1 — Foundation

Provide a stable entry, core rules, necessary canonical contracts, executable setup or verification, and current state where it materially changes decisions.

### L2 — Managed

Add the central registry, explicit ownership, decision history, controlled relationships, and synchronization checks. L2 includes L1 capabilities.

### L3 — Agent-intensive

Add scoped instruction files, project Skills, evaluations and manifests, generated evidence, warning or blocking checks, and a maintenance feedback loop. L3 includes L1 and L2 capabilities.

Do not build a higher level without a concrete risk or coordination need. Artifacts may be documents, code, schemas, tests, scripts, or generated reports.

## Audit workflow

Keep audit and implementation separate. Unless the user has explicitly approved changes, perform these steps read-only:

1. **Set scope**: identify repository type, risk, collaboration model, agent involvement, and target maturity.
2. **Inventory artifacts**: locate Markdown, instruction files, Skills, configuration, schemas, tests, scripts, manifests, and generated reports.
3. **Classify artifacts**: assign primary role, secondary roles, update semantics, authority, and authority scope.
4. **Audit authority**: find overlapping canonical scopes, conflicting rules, explanatory content without sources, and state claims without evidence.
5. **Audit relationships**: build the controlled relationship graph and find orphans, broken links, cycles, and routes without useful terminals.
6. **Audit lifecycle**: check location, owner, update trigger, verification, and whether actual change behavior matches the declared update semantic.
7. **Audit enforcement**: identify the current level and justified upgrades or downgrades.
8. **Find proportional gaps**: compare the current state only with the selected L1, L2, or L3 target; do not fill the matrix mechanically.
9. **Report**: separate observed facts, inferences, risks, and recommendations; prioritize actionable findings.
10. **Await approval**: propose exact file and check changes, then implement only the approved scope.

Prefer repository evidence over claims in stale plans. Preserve existing conventions and useful documents. Recommend consolidation only when duplicated authority or maintenance contracts create a real risk.

## Audit output contract

For a formal audit, use `assets/repository-knowledge-audit-template.md` as a starting point. Include:

1. scope and target maturity;
2. executive summary;
3. artifact registry;
4. role-by-update coverage matrix;
5. authority and relationship analysis;
6. lifecycle and enforcement analysis;
7. prioritized findings;
8. proposed changes and verification plan;
9. deferred items and evidence limitations.

Use this finding schema:

```yaml
id:
priority:
artifact:
location:
observed_fact:
violated_contract:
impact:
recommendation:
target_enforcement:
confidence:
```

Assign priorities consistently:

- **P0**: immediate security, integrity, irrecoverability, or severe misleading-authority risk.
- **P1**: likely wrong action, contract violation, or unreliable agent execution.
- **P2**: drift, maintenance burden, broken navigation, or unclear responsibility.
- **P3**: quality improvement or higher-maturity opportunity.

Every `observed_fact` must cite a file location, command result, or other reproducible evidence. Label inference as inference. Never present an unverified recommendation as a current fact.
