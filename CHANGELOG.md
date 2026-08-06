# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

No unreleased changes.

## [0.3.2-beta] - 2026-08-06

### Changed

- Replaced mutable Draft-versus-Published claims in the public README and security policy with durable links to GitHub Releases as the publication source of truth.
- Installation guidance now verifies Artifact Attestations for all six downloaded assets before running an installer and constrains provenance to the repository, version tag, and signer workflow.
- Repository validation now blocks volatile publication-status wording and missing installation-provenance guidance.

### Security

- Release automation may refresh assets only while a release remains a draft and fails rather than overwriting an already published release.
- Static regression tests enforce the published-release immutability guard and provenance-verification documentation.

## [0.3.1-beta] - 2026-08-05

### Added

- Evaluation Schema v2 with runner, model, timing, usage, evaluator, rubric, per-dimension rationale, and explicit unknown-value provenance.
- Domain-separated agent-input and evaluator-input bundle hashes with deterministic recomputation.
- Append-only scenario run directories and pull-request enforcement that rejects edits or deletion of committed run history.
- Dependency-free PowerShell, POSIX shell, and Python safe installers with dry-run support.
- Isolated tests for fresh installation, verified upgrade backups, path traversal rejection, installer tampering, and automatic rollback.

### Changed

- Release manifests now bind all three installer assets and all six release assets are compared byte for byte across Windows and Linux.
- Existing L1, L2, and L3 evidence was migrated without rewriting raw responses; unavailable historical telemetry is recorded as unknown rather than inferred.
- Release attestation now covers the ZIP, checksum, manifest, and every installer asset.

### Security

- Installation verifies the archive checksum, manifest schema, installer hashes, exact archive layout, every packaged file, and the canonical package tree before replacing a Skill target.
- Upgrades preserve the previous Skill directory under a unique backup path and restore it automatically if replacement fails.

## [0.3.0-beta] - 2026-08-05

### Added

- Cross-platform release-artifact uploads and byte-for-byte comparison in GitHub Actions.
- GitHub build-provenance attestations for tagged release assets.
- Automatic draft prerelease creation after tag validation and attestation.
- Negative tests for source-commit mismatch, unpinned Actions, missing attestation, artifact divergence, and symbolic links.

### Changed

- Every third-party GitHub Action is pinned to a full commit SHA.
- Release packaging now requires an existing source commit that is HEAD or an ancestor of HEAD and exactly matches committed package inputs.
- Skill packaging and canonical tree hashing now reject symbolic links, junctions, and unsupported special files.
- Tagged releases consume the same Linux artifact that passed cross-platform comparison rather than rebuilding an untracked local copy.

### Security

- The release workflow now produces verifiable build provenance and keeps generated prereleases in draft state for maintainer review.
- Repository branch and version-tag rulesets protect required checks and immutable release references.

## [0.2.0-beta] - 2026-08-05

### Added

- Deterministic versioned Skill ZIP, SHA-256 checksum, and provenance manifest builder.
- Cross-platform canonical hashing for prompts, fixtures, responses, expected findings, installed packages, and release archives.
- Repository-native tests for deterministic packaging, artifact completeness, version synchronization, and evidence tampering.

### Changed

- Forward-test results now record a schema version, run ID, source commit, runner context, isolation statement, and canonical artifact hashes.
- Clean-install evidence now binds the tested archive, checksum, manifest, installed tree, and fresh-agent response to reproducible hashes.
- Installation guidance now defaults to version-pinned GitHub Release assets rather than a clone of the moving `main` branch.
- GitHub Actions now builds the deterministic release package on Windows, Linux, and release tags.

## [0.1.1-beta] - 2026-08-05

### Added

- Structured bug-report and forward-test scenario proposal forms.
- A private security-report route in the issue chooser.

### Changed

- Updated the security policy with current Beta support and response expectations.
- Added public repository description and discovery topics.

### Security

- Enabled GitHub private vulnerability reporting.

## [0.1.0-beta] - 2026-08-05

### Added

- Public repository wrapper with Chinese and English project documentation.
- Contribution, security, and pull-request governance.
- Installable Skill package under `skill/build-engineering-harness/`.
- Repository knowledge governance model and formal audit template.
- MIT License.
- Dependency-free repository validator and validator unit tests.
- Windows and Linux GitHub Actions validation.
- Synthetic L1, L2, and L3 forward-test scenarios with hard gates and scoring rules.
- Sanitized responses and passing evaluation evidence for the L1, L2, and L3 forward tests.
- Clean GitHub installation evidence, including package hash comparison and a fresh-agent usability probe.

### Changed

- Replaced the fixed five-document recommendation in the Personal AI Engineering Playbook with proportional knowledge coverage.
- Updated Skill interface metadata to include repository auditing.
- Made release-evidence unit tests independent of the repository's current release phase.
