# README diagrams

These diagrams explain the instruction contract in `skill/build-engineering-harness/SKILL.md`. They are documentation assets; they do not implement or enforce an autonomous workflow.

| Source | README asset prefix |
|---|---|
| `overview.en.architecture.json` | `../assets/overview.en` |
| `overview.zh-CN.architecture.json` | `../assets/overview.zh-CN` |
| `approval.en.workflow.json` | `../assets/approval.en` |
| `approval.zh-CN.workflow.json` | `../assets/approval.zh-CN` |

The architecture sources pin repository evidence to commit `c186f5e26435f543056ded4e8db3797c29d009e1`. Workflow semantics were checked against the same revision. Update the evidence and both languages together when behavior changes. L1/L2/L3 are proportionality levels, not sequential lifecycle stages. Project closeout is a separate mode authorized by an explicit request for two named documents.

## Regeneration

Generated with [Archify](https://github.com/tt-a1i/archify), package version `2.17.0-dev.1`. Archify is an authoring dependency only; it is not required to install or use this Skill.

From the repository root, with `ARCHIFY_DIR` pointing to a local Archify checkout or installed Skill directory, use its supported CLI. For example, in PowerShell:

```powershell
node "$env:ARCHIFY_DIR/bin/archify.mjs" validate architecture docs/diagrams/overview.en.architecture.json --repo-root . --quality showcase --json
node "$env:ARCHIFY_DIR/bin/archify.mjs" deliver architecture docs/diagrams/overview.en.architecture.json .test-runs/overview.en.html --repo-root . --quality showcase --json
node "$env:ARCHIFY_DIR/bin/archify.mjs" visual-check .test-runs/overview.en.html --json
```

Repeat for the Chinese overview. For approval diagrams, use type `workflow` and omit `--repo-root`. Create the `.test-runs` directory first if absent. Require all nine showcase checks with zero errors and warnings, then collect browser evidence and review the actual light/dark images separately.

Open each delivered HTML locally and use the viewer's native PNG export in Light and Dark modes. Save them under `docs/assets/` using the prefixes above: `.png` for light and `.dark.png` for dark. The README selects the matching image through `<picture>` and links to the full-size light image. Do not upload screenshots of viewer controls as README assets.

The initial assets passed deterministic validation, browser checks at four desktop sizes, and separate visual review. Workflow inter-lane routes remain long, and secondary text is small when embedded; full-size links and textual steps support reading. The initial review is not evidence that later edits were checked.

Keep generated HTML, browser screenshots, and local receipts outside the tracked tree. GitHub renders the PNGs; it does not run the interactive viewer inline. Follow Archify's license for redistributed material and preserve project source attribution.
