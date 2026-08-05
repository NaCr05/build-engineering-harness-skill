# Read-only engineering-harness assessment

Scope: only the named repository and the requested Skill. No files were modified or created.

## Recommended maturity

Target **L1 — Foundation**. The repository is a tiny, low-risk, single-maintainer CLI with no AI/agent components. L2 governance artifacts such as a registry, ownership matrix, ADR system, or synchronization automation would add maintenance cost without a demonstrated need.

Current state is **partial L1**: it has a usable entry point and executable verification, but the verification route and some input behavior are not documented.

## Observed facts

- [`README.md`](repository-fixture/README.md) describes a greeter CLI, gives `python cli.py Ada`, and shows `Hello, Ada!`.
- [`cli.py`](repository-fixture/cli.py) contains:
  - a pure `greet(name)` function;
  - whitespace trimming via `name.strip()`;
  - an `argparse` CLI with one required positional argument;
  - console output through `main()`.
- [`tests/test_cli.py`](repository-fixture/tests/test_cli.py) contains one `unittest` covering `greet("Ada")`.
- The complete recursive inventory contained only those three files. There is no dependency/package manifest, CI configuration, release configuration, contributor guidance, or scoped agent instruction file.
- The README example agrees with the implementation and actual smoke-test output.
- The README does not provide a test command, supported/tested Python version, whitespace behavior, or empty-name policy.
- The test does not exercise the public CLI path, argument parsing, output stream, exit status, whitespace trimming, or failure behavior.

Useful existing assets to retain:

| Artifact | Harness role | Value |
|---|---|---|
| `README.md` | Stable navigation entry | Concise purpose and runnable example |
| `cli.py` | De facto canonical implementation/contract | Small, readable boundary between greeting logic and CLI |
| `tests/test_cli.py` | Executable verification evidence | Dependency-free test foundation |

No conflicting authorities or stale parallel documents were found.

## Inferences

- The intended user runs the utility directly from a terminal, supplies a name, and expects one greeting line.
- The implementation uses only Python’s standard library; a dependency manifest is therefore unnecessary unless packaging or distribution is introduced.
- Verification is currently expected to be run manually.
- A whitespace-only name would produce `Hello, !` because the implementation strips the input, but that behavior was not executed and no repository artifact says whether it is intended.
- The success criterion currently recoverable from the repository is only the ordinary-name example; boundary behavior is undecided.

## Material risks

- **P2 — Public interface is weakly verified.** The sole test calls `greet()` directly, so CLI parsing, printed output, and exit behavior can regress while the suite remains green.
- **P2 — Input contract is incomplete.** Trimming is implemented but undocumented and untested; whitespace-only input has no stated policy. Future changes could silently alter behavior.
- **P2 — Verification is not discoverable.** A newcomer or agent cannot learn the test command from the stable entry point.
- **P3 — Runtime support is unclear.** Python 3.13.9 worked in this assessment, but the repository makes no broader support promise.

## Smallest proportional improvements

1. Update `README.md`; do not add a new documentation file.
   - Add the exact local test command.
   - State that the utility uses Python 3 and that verification was performed on Python 3.13, without claiming untested version support.
   - Add a two- or three-line behavior contract covering surrounding whitespace and the chosen blank-name policy.
   - Keep the existing example.

2. Extend `tests/test_cli.py`.
   - Retain the ordinary-name unit test.
   - Add a trimming test.
   - Add one subprocess-level success test for `python cli.py Ada`, asserting exit code and stdout.
   - Add one blank/missing-input test after its expected behavior is chosen.

3. Change `cli.py` only if blank names should be rejected.
   - Recommended behavior: reject empty or whitespace-only input with a clear message and nonzero exit.
   - This changes currently observable behavior and should therefore be treated as a separately approved product decision, not an automatic harness edit.

No new `AGENTS.md`, documentation hierarchy, central registry, ADR log, CI workflow, package manifest, lint setup, or release process is justified at this maturity. Reconsider CI only if contributions, release frequency, or supported Python versions grow.

## Verification evidence

Actually run, using Python 3.13.9:

- `python -B -m unittest discover -s tests -v`
  - Passed: 1 test.
- `python -B cli.py Ada`
  - Exit code 0.
  - Output: `Hello, Ada!`
- A post-check recursive inventory still contained only the original three files; `-B` prevented bytecode-cache creation.

Not run: whitespace, blank-name, missing-argument, or multi-version checks. They remain unverified.

## Decision needed

Choose the blank-name contract. Recommended: whitespace around a non-empty name is trimmed; empty or whitespace-only names are rejected. After that decision, the README and tests can make the behavior durable with minimal overhead.
