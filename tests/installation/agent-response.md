# Versioned-package clean-install agent probe

## Scope and maturity

**Observed facts**

- Three-file, standard-library Python CLI: `README.md`, `cli.py`, and `tests/test_cli.py`.
- Data flow: positional `name` argument → `argparse` → `greet()` trims whitespace → greeting printed to stdout.
- No AI/agent components, dependency manifest, CI configuration, release workflow, or scoped repository instructions were present.
- The documented example and existing test both passed:
  - `python -B cli.py Ada` → `Hello, Ada!`
  - `python -B -m unittest discover -s tests -v` → 1 test passed.

**Inference**

- Intended users are people wanting a tiny greeting CLI.
- The likely success criterion is: a supplied name produces `Hello, <trimmed name>!`.
- Given the small scope, low apparent risk, and limited coordination needs, **L1 Foundation** is the appropriate target. The repository is close to L1 already; L2/L3 governance would be disproportionate.

## Useful existing assets

- `README.md` is a compact stable entry point with a runnable example.
- `cli.py` has a clear module boundary, descriptive function name, type annotation, and conventional entry point.
- `tests/test_cli.py` provides executable evidence for the core greeting behavior.
- The repository has no unnecessary dependencies or architectural complexity.

## Smallest meaningful gaps

1. **P2 — Verification is not discoverable.**

   The test exists, but `README.md` does not document how to run it. A newcomer or agent can run the program but cannot discover the expected verification workflow from the entry point.

2. **P3 — Input boundaries are implicit.**

   `greet()` trims whitespace, but trimming is not tested or documented. Blank or whitespace-only input formats as `Hello, !`; the repository does not say whether that is accepted behavior or an invalid input.

3. **P3 — Success criteria are implied rather than explicit.**

   The example establishes the happy path, but no concise contract identifies normalization or failure behavior.

## Risks

- The main practical risk is inconsistent verification during future changes because the test command is undocumented.
- Input handling could change accidentally because normalization and blank-input behavior lack explicit evidence.
- Absence of CI, an artifact registry, ADRs, `AGENTS.md`, packaging, or a larger documentation tree is **not currently a meaningful risk** at this scale.

## Proportional recommendations

1. Update `README.md` with a short **Test** section containing:
   `python -B -m unittest discover -s tests -v`
2. Add one test to `tests/test_cli.py` covering surrounding-whitespace normalization.
3. Decide whether blank names are valid:
   - If valid, document the behavior.
   - If invalid, separately approve a localized validation change and corresponding failure-path test.
4. Keep the current three-file structure. Do not add CI, a knowledge registry, ADRs, packaging metadata, or agent-specific instructions until collaboration, release, or change-rate needs justify them.

**Verification plan after any approved changes:** rerun the documented CLI example and unit-test command above. No lint, packaging, CI, or release checks were run because none were discovered.
