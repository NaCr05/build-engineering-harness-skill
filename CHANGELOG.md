# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

No unreleased changes.

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
