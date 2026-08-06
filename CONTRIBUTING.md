# Contributing

Thank you for helping improve Build Engineering Harness.

## Maintenance status

Active maintenance is paused as of 2026-08-06. Issues and pull requests may remain unreviewed until maintenance resumes, and submission does not imply a response or merge timeline. Report suspected vulnerabilities privately through the route in `SECURITY.md`; do not publish exploitable details in an issue or pull request.

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

Release-relevant changes under `skill/`, `scripts/`, `tests/`, public governance files, or GitHub workflows must update the `Unreleased` section of `CHANGELOG.md` in the same pull request. CI enforces this relationship with `scripts/check_changelog.py`.

## Supported development environments

- Repository tooling and the Python installer support CPython 3.10 through 3.13.
- Windows validation uses Python 3.12 and PowerShell 7 on the current GitHub-hosted Windows runner.
- Ubuntu validates Python 3.10, 3.11, 3.12, and 3.13 plus the POSIX installer wrapper.
- macOS validates Python 3.12 plus the POSIX installer wrapper.
- Windows PowerShell 5.1, WSL, and other Unix distributions are best-effort rather than CI-guaranteed.

## Validation

Run the repository-native checks:

```text
python -m unittest discover -s tests/static -v
python scripts/validate_repository.py
python scripts/build_release_package.py --output-dir .test-runs/release-package
```

Before tagging a release, run `python scripts/validate_repository.py --release`.

Formal package builds require a real source commit that is HEAD or an ancestor of HEAD. `VERSION` and `skill/build-engineering-harness/` must be committed and byte-equivalent to that source commit. Symbolic links, junctions, and special files are forbidden in hashed or packaged trees.

Installer sources under `scripts/install*` are also formal package inputs. Test installers only against a disposable `CODEX_HOME`; verify dry-run, fresh install, upgrade backup, tamper rejection, and rollback behavior before release.

GitHub Actions uploads the independently built Windows and Linux packages and runs `scripts/compare_release_artifacts.py` before any tag can advance to release validation. A passing version tag produces attestations and a draft prerelease for maintainer review; do not replace those assets with a separate local build.

If the Codex `skill-creator` validator is available, run it as an additional compatibility check against `skill/build-engineering-harness`.

Also confirm:

- every local Markdown link resolves;
- `SKILL.md` remains concise and routes to detailed references;
- the English and Chinese entry documents remain behaviorally aligned;
- no secret, personal path, private project name, or confidential content is present;
- the change does not weaken approval, safety, or product-code boundaries.
- every external GitHub Action remains pinned to a full commit SHA.

Forward tests must use fresh tasks and disposable synthetic or public repositories. Pass raw fixtures rather than intended answers, and do not disclose evaluator expectations to the agent. Follow `tests/README.md`.

Committed `tests/scenarios/*/runs/<run-id>/` evidence is append-only. Never edit, rename, or delete a historical response or result. Add a new unique run directory and update the synchronized `release_run` pointer when appropriate.

Do not hand-edit recorded hashes. When an evidence-bearing prompt, fixture, response, expected result, installation artifact, or Skill file changes, rerun the applicable test and record hashes produced by `scripts/evidence_hashes.py` or the release-package builder. A stale hash is a release-blocking failure.

## Pull requests

Describe:

- the problem and affected scenario;
- files changed and their authority role;
- validation evidence;
- behavior that remains untested;
- any compatibility or migration concern.

By contributing, you confirm that you have the right to submit the material under the repository's selected license.
