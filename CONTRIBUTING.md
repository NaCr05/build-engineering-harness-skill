# Contributing

Thank you for helping improve Build Engineering Harness.

## Contribution principles

- Preserve the two-phase contract: inspect and propose first, implement only after explicit approval.
- Prefer a small maintained source of truth over duplicated documentation.
- Keep the harness proportional to project risk and collaboration needs.
- Support claims with repository evidence and label inference explicitly.
- Do not add private repository content, credentials, personal paths, or confidential examples.

## Sources of truth

- `skill/build-engineering-harness/SKILL.md` is the runtime and behavioral source of truth.
- `skill/build-engineering-harness/SKILL.zh-CN.md` is its synchronized Chinese explanation.
- Detailed repository governance rules live in `references/repository-knowledge-governance.md`.
- The audit output structure lives in `assets/repository-knowledge-audit-template.md`.
- `README.md` is the canonical public project overview; `README.en.md` is its synchronized English version.

When behavior changes, update the canonical artifact first and synchronize every affected explanation in the same pull request.

## Making a change

1. Explain the problem and provide a concrete usage example.
2. Identify the canonical file that owns the behavior.
3. Make the smallest change that resolves the problem.
4. Update synchronized documentation and metadata when applicable.
5. Run structural validation and check local links.
6. Record what was tested and what remains unverified.

Do not create new reference files when an existing source of truth can be extended without becoming unclear.

## Validation

Run the repository-native checks:

```text
python -m unittest discover -s tests/static -v
python scripts/validate_repository.py
```

Before tagging a release, run `python scripts/validate_repository.py --release`.

If the Codex `skill-creator` validator is available, run it as an additional compatibility check against `skill/build-engineering-harness`.

Also confirm:

- every local Markdown link resolves;
- `SKILL.md` remains concise and routes to detailed references;
- the English and Chinese entry documents remain behaviorally aligned;
- no secret, personal path, private project name, or confidential content is present;
- the change does not weaken approval, safety, or product-code boundaries.

Forward tests must use fresh tasks and disposable synthetic or public repositories. Pass raw fixtures rather than intended answers, and do not disclose evaluator expectations to the agent. Follow `tests/README.md`.

## Pull requests

Describe:

- the problem and affected scenario;
- files changed and their authority role;
- validation evidence;
- behavior that remains untested;
- any compatibility or migration concern.

By contributing, you confirm that you have the right to submit the material under the repository's selected license.
