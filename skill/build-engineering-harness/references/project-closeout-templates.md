# Project Closeout Templates

Use these templates for project-closeout mode. Keep the two filenames fixed. Translate headings and prose into the user's requested language; otherwise match the dominant language of maintained project documentation.

Replace every bracketed prompt with repository evidence or an explicit `Unknown` statement. Remove instructional comments from the final files.

## `docs/project-retrospective.md`

```markdown
# Project Retrospective: [Project name]

## Project Goal and Final Outcome

- Original goal and intended users
- Planned output and what was actually delivered
- Success criteria and evidence
- Scope that was deferred or removed

## Key Technical Decisions

For each important decision, record:

- Context and constraint
- Decision
- Alternatives considered
- Why this option was chosen
- Consequences and relevant ADR or source links

## What Went Well

- Technical choices that worked, with evidence
- Process or collaboration practices that worked
- Tools, automation, or tests that saved time or prevented failures

## Problems, Causes, and Solutions

For each meaningful problem, record:

- Symptom and impact
- Contributing technical or process causes
- Implemented solution
- How the solution was verified
- Current status

Avoid vague lessons and personal blame. Explain the system conditions that allowed the problem.

## Technical Debt and Remaining Risks

| Item | Why it remains | Impact | Mitigation or next action | Status |
|---|---|---|---|---|

## Reusable Assets

| Asset | Location | Reuse value | Usage notes |
|---|---|---|---|

Include reusable modules, scripts, templates, tests, prompts, documentation patterns, and automation.

## What to Do Differently Next Time

- Start doing
- Stop doing
- Continue doing
- Pre-flight checks for a similar project
- Questions to answer earlier
```

## `docs/project-onboarding.md`

```markdown
# Project Onboarding: [Project name]

## Two-Minute Overview

- What the project does
- Who it serves
- Current lifecycle or release status
- The shortest accurate mental model

## Target Users and Core Workflow

Describe the main user types and trace the primary workflow from input to observable outcome.

## Tech Stack and Architecture

| Layer | Technology | Role |
|---|---|---|

Add a concise Mermaid architecture diagram when repository evidence supports it. Keep diagrams small and link to maintained architecture documentation for details.

## Directory Map and Key Entry Points

| Path | Purpose | Start here when... |
|---|---|---|

Include runtime entry points, configuration sources, core domain modules, tests, scripts, and deployment files.

## Data Flow

Trace at least one representative request, job, event, or data pipeline from entry through validation and business logic to persistence or output.

## Install, Run, and Test

### Prerequisites

### Installation

### Configuration

List configuration variable names without secret values.

### Run

### Test and Verify

Use copyable commands and state the expected success signal. Mark commands not executed during closeout as unverified.

## Common Development Tasks

| Task | Where to change | Command or verification |
|---|---|---|

## Gotchas and Troubleshooting

For each important issue, record the symptom, likely cause, diagnostic step, and fix or workaround.
```
