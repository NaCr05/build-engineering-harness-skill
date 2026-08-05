# Read-only L3 engineering-harness audit

## Audit profile

| Field | Assessment |
|---|---|
| Repository | `l3` disposable research-assistant fixture |
| Audit date | 2026-08-05 |
| Scope | Only the repository root and its nine files under `agent/`, `docs/`, and `tests/` |
| Target maturity | L3 — agent-intensive |
| Risk | Medium-high: unrestricted URL retrieval and persistent raw memory are present, although no runnable agent orchestration was found |
| Audit mode | Read-only; no files or caches created |
| Verification performed | `python -B -m unittest discover -s tests -v` — 1 test passed |
| Evidence limitations | No parent/sibling directories, version history, networks, models, paid services, production systems, or external scenario/expected-answer files were inspected |

## Executive summary

**Overall conclusion: not ready for L3.**

The repository has a compact stable entry point, root agent rules, isolated components for context, memory, URL access, prompting, and result formatting, plus one executable offline test. These are useful foundations.

It does not yet form a runnable or governable agent system. There is no orchestration connecting the prompt, context, URL tool, memory, and output formatter. Prompt and output contracts are underspecified; context, network, and memory operations lack bounds and permission controls; failures are reduced to unstructured prose; and the evaluation document contains unsupported manual claims. No executable evaluation covers accuracy, latency, cost, reliability, privacy, permissions, or stale-state behavior.

The smallest high-value remediation is to define the end-to-end contract, place hard boundaries around URL/context/memory operations, and replace prose evaluation claims with an offline, reproducible evaluation manifest and generated evidence.

## Project understanding

### Verified facts

- `README.md:1-3` describes an experimental research assistant that consumes local notes and requested URLs, remembers conversations, and returns prose.
- `README.md:5-11` supplies one unit-test command and says local tests do not connect to a production model.
- `agent/prompt.md:1` contains one unversioned sentence instructing the assistant to use context, URLs, and memory.
- `agent/context.py:6-7`, `agent/tools.py:6-8`, and `agent/memory.py:7-10` implement independent context, URL-fetch, and JSON-memory functions.
- `agent/runner.py:4-7` only formats an answer or exception. It does not call the other agent modules or a model.
- The only test, `tests/test_runner.py:8-10`, asserts merely that a successful result is a string.
- The documented test ran successfully: one test passed in 0.000 seconds.
- `docs/evaluation.md:3-5` records subjective manual claims but provides no cases, expected outputs, thresholds, timestamps, measurements, or generated results.

### Inferences and unknowns

- The likely intended user is a developer or demo operator; no user population or deployment boundary is defined.
- The separate modules appear intended to be composed into an agent pipeline, but no such composition is implemented.
- “Remember useful details” likely means persistent conversational memory, but usefulness, consent, identity scope, and retention are undefined.
- Whether arbitrary public internet access, intranet access, or only an allowlist is intended is unknown.
- No measurable success criteria exist for response accuracy, latency, cost, or reliability.

## Artifact registry

Classifications below are audit inferences; the repository has no declared registry, owners, update triggers, or authority relationships.

| Artifact | Primary role | Update semantics | Authority | Current verification/enforcement |
|---|---|---|---|---|
| `README.md` | `navigation_routing` | `stable_entry` | Explanatory | Test command was executable; product claims unverified |
| `AGENTS.md` | `rules_boundaries` | `stable_entry` | Canonical for repository work | Documented only |
| `agent/prompt.md` | `specifications_contracts` | `synchronized` | Intended canonical prompt | Not loaded or tested |
| `agent/context.py` | `specifications_contracts` | `synchronized` | Canonical implementation | None |
| `agent/tools.py` | `specifications_contracts` | `synchronized` | Canonical implementation | None |
| `agent/memory.py` | `specifications_contracts` | `synchronized` | Canonical implementation | None |
| `agent/runner.py` | `specifications_contracts` | `synchronized` | Canonical implementation | One shallow type assertion |
| `docs/evaluation.md` | `state_evidence` | `synchronized` | Purported evidence | No supporting evidence |
| `tests/test_runner.py` | `execution_verification` | `synchronized` | Evidence | Executable locally |

## Coverage matrix

| Primary role \ Update semantics | Stable entry | Synchronized | Append-only | Derived/generated |
|---|---:|---:|---:|---:|
| Navigation and routing | 1 | 0 | 0 | 0 |
| Rules and boundaries | 1 | 0 | 0 | 0 |
| Specifications and contracts | 0 | 5 | 0 | 0 |
| State and evidence | 0 | 1 | 0 | 0 |
| Rationale and history | 0 | 0 | 0 | 0 |
| Execution and verification | 0 | 1 | 0 | 0 |

The important L3 gaps are not empty cells by themselves. They are the absence of generated evaluation evidence, controlled authority relationships, scoped instructions, ownership, synchronization checks, decision history for sensitive policies, and warning or blocking enforcement.

## Authority and relationship analysis

- `README.md` routes to the test command, which is valid and passed.
- Its claims about notes, URL retrieval, memory, and assistant responses do not route to a runnable entry point or end-to-end verification.
- `agent/prompt.md` and all four Python modules are orphaned from an executable orchestration path.
- `docs/evaluation.md` makes material state claims without an `evidenced_by` relationship to cases, logs, measurements, or reports.
- The evaluation document’s reliability and speed claims exceed what `tests/test_runner.py` verifies.
- No explicit canonical-source overlaps or relationship cycles exist because no relationships are declared.
- No central registry identifies owners, authority scopes, update triggers, verification, or enforcement.

## Dimension coverage

| Dimension | Evidence-backed gap |
|---|---|
| Accuracy | Vague prompt; untrusted context and URL content are not separated from instructions; context loses source provenance; no answer-quality cases or thresholds |
| Latency | Recursive context ingestion, response reads, and memory growth are unbounded; URL fetch has no explicit timeout; no percentile measurements |
| Cost | No model/usage accounting, context budget, call budget, token budget, or cost evaluation |
| Reliability | No end-to-end runner, error taxonomy, retry policy, atomic memory update, concurrency control, fallback, health signal, or reliability suite |
| Privacy | Raw user and assistant text are persisted indefinitely; arbitrary Markdown may be loaded; raw exception text is returned |
| Permissions | URL scheme/destination and filesystem paths are not constrained; no capability enablement or least-privilege policy |
| Stale state | Memories have no timestamp, expiry, version, provenance, or session/user scope; context has no freshness metadata; evaluation claims are undated |

## Prioritized findings

### L3-001 — P1: No executable end-to-end agent contract

- **Location:** `README.md:3`; `agent/runner.py:4-7`; all files under `agent/`
- **Observed fact:** The advertised capabilities exist only as disconnected functions. `runner.py` neither loads the prompt nor invokes context, tools, memory, or a model.
- **Violated contract:** L1/L3 require discoverable architecture, stable inputs/outputs, responsibility boundaries, and executable verification.
- **Impact:** Product behavior, ordering, permissions, failure semantics, and claimed capabilities cannot be verified. Accuracy, latency, cost, and reliability measurements have no stable subject.
- **Risk:** Future integration may silently choose unsafe or inconsistent sequencing.
- **Recommendation:** Define and implement one explicit orchestration interface with dependency injection, budgets, tool authorization, memory policy, and structured result semantics.
- **Target enforcement:** `structural_prevention`
- **Confidence:** High

### L3-002 — P1: Prompt and context trust boundaries are undefined

- **Location:** `agent/prompt.md:1`; `agent/context.py:6-7`
- **Observed fact:** The prompt is a single unversioned sentence. Context recursively concatenates all Markdown without source labels, deterministic ordering, quotas, freshness, or error handling.
- **Violated contract:** AI prompt clarity/versioning and context-source selection, freshness, limits, and privacy requirements.
- **Impact:** Source attribution is lost; conflicting or injected instructions may be treated as trusted; large note sets increase latency and future model cost; outdated notes are indistinguishable from current facts.
- **Risk:** Wrong answers, prompt injection, accidental sensitive-data exposure, unstable runs, and unbounded context cost.
- **Recommendation:** Version the prompt; define instruction hierarchy and untrusted-data delimiters. Return structured context chunks containing source, timestamp/fingerprint, and bounded content in deterministic order.
- **Target enforcement:** `structural_prevention`
- **Confidence:** High

### L3-003 — P1: URL tool lacks permission, safety, and resource controls

- **Location:** `agent/tools.py:6-8`
- **Observed fact:** The caller-provided URL is passed directly to `urlopen`; the response is read fully. There is no explicit scheme/destination policy, redirect validation, timeout, byte limit, content-type check, or stable error mapping.
- **Violated contract:** Tool inputs, outputs, permissions, limits, and error behavior must be explicit.
- **Impact:** Calls may hang, allocate excessive memory, retrieve unsuitable content, or reach destinations outside the intended trust boundary.
- **Risk:** Conditional SSRF/local-resource access, privacy leakage, denial of service, unpredictable latency, and downstream prompt injection.
- **Recommendation:** Require explicit capability authorization; allow only approved HTTP(S) destinations; reject local/private/link-local targets and unsafe redirects; enforce timeout and byte/MIME limits; return typed results and errors.
- **Target enforcement:** `structural_prevention`
- **Confidence:** High for missing controls; medium for exploitability because no orchestrator is present

### L3-004 — P1: Memory is unscoped, indefinite, non-atomic, and privacy-blind

- **Location:** `agent/memory.py:7-10`; `agent/prompt.md:1`
- **Observed fact:** Full raw user and assistant text is appended to a caller-selected JSON path. Records contain no identity scope, consent, timestamp, expiry, provenance, schema version, or sensitivity classification. Read-modify-write has no locking or atomic replacement.
- **Violated contract:** Memory scope, retention, privacy, stale-state handling, and failure behavior are unspecified.
- **Impact:** Sensitive content may persist indefinitely; separate users or sessions may mix; concurrent updates may be lost; malformed or interrupted writes can make all memory unreadable; cost and latency grow with the file.
- **Recommendation:** Make memory opt-in and project/user/session scoped; store only approved fields; add timestamps, expiry, schema version, provenance, bounded retention, atomic writes, locking, and corruption recovery.
- **Target enforcement:** `structural_prevention`
- **Confidence:** High

### L3-005 — P1: Output and failure contracts are ambiguous and may leak internals

- **Location:** `agent/runner.py:4-7`; `AGENTS.md:5`
- **Observed fact:** Success and failure both return unstructured strings. Failure includes the raw exception text. No status, error category, retryability, citations, provenance, or machine-validatable schema is present.
- **Violated contract:** Stable output schema, downstream validation, safe failure semantics, and observability.
- **Impact:** Callers cannot reliably distinguish success from failure; exception strings may disclose paths, URLs, or other internals; failure recovery cannot be automated.
- **Recommendation:** Preserve the demo’s prose answer inside a typed envelope containing status, answer, sources, warnings, error code, and retryability. Map internal exceptions to sanitized public errors.
- **Target enforcement:** `structural_prevention`
- **Confidence:** High

### L3-006 — P1: Evaluation claims are unsupported

- **Location:** `docs/evaluation.md:3-5`
- **Observed fact:** “Three sample questions” and perceived speed/reliability are reported without cases, expected behavior, timestamps, model/prompt versions, measurements, thresholds, or artifacts.
- **Violated contract:** Prose documentation is not executed evaluation; material state claims require reproducible evidence.
- **Impact:** Accuracy, latency, cost, and reliability status cannot be reproduced or compared after changes.
- **Recommendation:** Replace the claims with methodology and links to a versioned manifest and generated results. Mark all agent-level metrics “not measured” until an executable evaluation is run.
- **Target enforcement:** `automated_blocking` for unsupported pass claims; `review_required` for qualitative interpretation
- **Confidence:** High

### L3-007 — P1: Tests do not exercise important behavior or repository rules

- **Location:** `tests/test_runner.py:8-10`; `AGENTS.md:3-5`
- **Observed fact:** One test checks only that `format_result("answer")` returns a string. The error branch, exact prose preservation, context, URL tool, memory, permissions, privacy, limits, and stale-state behavior are untested.
- **Violated contract:** Verification should cover normal, boundary, and failure paths proportionate to risk.
- **Impact:** The passing test provides almost no evidence for advertised behavior or safety.
- **Recommendation:** Add offline unit and integration suites with mocked networking, temporary isolated storage, adversarial context, corrupted memory, resource limits, and structured-output validation.
- **Target enforcement:** `automated_blocking`
- **Confidence:** High

### L3-008 — P2: L3 knowledge governance and feedback mechanisms are absent

- **Location:** Repository inventory; `README.md`; `AGENTS.md`
- **Observed fact:** There is no artifact registry, ownership declaration, controlled relationship map, scoped instruction file below the root, decision record, evaluation manifest, generated evidence, automation configuration, or maintenance feedback loop.
- **Violated contract:** L3 requires L1/L2 governance plus scoped instructions, evaluations/manifests, generated evidence, enforcement, and a maintenance loop.
- **Impact:** Authority, update responsibility, and evidence freshness will drift as agent behavior expands.
- **Recommendation:** Add a compact registry and architecture route, scoped agent/test instructions, append-only decisions for network and memory policy, evaluation manifests/results, and offline blocking checks.
- **Target enforcement:** Begin at `documented`/`review_required`; promote deterministic checks to `automated_blocking`
- **Confidence:** High

## Ordered remediation plan

1. **Define the canonical product and orchestration contract.**
   - Update `README.md` with users, inputs, outputs, trust boundary, architecture, measurable success criteria, and the real runnable entry point.
   - Update `agent/runner.py` to compose explicitly authorized dependencies and expose a typed request/result interface.
   - Verify with offline end-to-end tests using deterministic stubs.

2. **Close network and filesystem permission gaps before connecting a model.**
   - Update `agent/tools.py` with URL allowlisting, destination/redirect checks, timeout, size/MIME limits, and typed failures.
   - Constrain context and memory paths to explicit configured roots.
   - Add tests that block `file:` URLs, loopback/private destinations, unsafe redirects, oversized responses, and out-of-scope paths.

3. **Establish prompt and context contracts.**
   - Update `agent/prompt.md` with a version, instruction priority, untrusted-content handling, citation/provenance rules, tool conditions, memory conditions, refusal behavior, and output contract.
   - Update `agent/context.py` for deterministic bounded chunks, source identity, freshness/fingerprints, decoding failures, and privacy exclusions.
   - Test conflicts, injection-shaped notes, stale notes, empty context, and context-budget enforcement.

4. **Replace raw memory with bounded lifecycle-managed memory.**
   - Update `agent/memory.py` with opt-in consent, scope keys, schema version, timestamps, retention/expiry, sensitivity exclusions, size limits, atomic updates, locking, and corruption recovery.
   - Test concurrent writes, invalid JSON, expiry, isolation, pruning, and interruption recovery.

5. **Separate user-facing prose from machine-readable status.**
   - Update `agent/runner.py` with a validated result schema while preserving the prose answer required by `AGENTS.md`.
   - Sanitize error messages and classify timeout, permission, validation, transient, and permanent failures.
   - Add tests for every status and error class.

6. **Create reproducible evaluation infrastructure.**
   - Create `evals/manifest.yaml`, `evals/cases.jsonl`, and an offline `evals/run.py`.
   - Measure accuracy against explicit rubrics, latency percentiles, token/call/cost budgets when a model adapter exists, reliability rate, privacy leakage, permission enforcement, and stale-memory behavior.
   - Emit fingerprinted derived results such as `evals/results/<run-id>.json`; never hand-edit them.
   - Update `docs/evaluation.md` to describe methodology and link to evidence, removing unsupported pass claims.

7. **Expand blocking verification.**
   - Add focused test modules for prompt/context, tools, memory, runner, and end-to-end behavior.
   - Add a local verification entry point and CI-equivalent offline check that fails on network use, schema drift, unsafe destinations, unsupported evaluation claims, or test failure.
   - Keep real model/network evaluations opt-in and outside default tests.

8. **Add proportional L3 knowledge governance.**
   - Create a compact central registry declaring artifact role, authority, owner, update trigger, verification, enforcement, and typed relationships.
   - Add scoped instructions for `agent/` and `tests/`.
   - Record network and memory policy decisions append-only.
   - Add a project evaluation Skill only if this workflow will be repeatedly delegated to agents; otherwise defer it to avoid unnecessary maintenance.

## Verification plan

After approval and implementation:

- Run all tests with bytecode disabled: `python -B -m unittest discover -s tests -v`.
- Confirm default tests make no network or model calls.
- Validate output and memory records against explicit schemas.
- Exercise URL denial, timeout, redirect, MIME, and size boundaries using local mocks only.
- Exercise deterministic context ordering, quotas, provenance, and stale-content behavior.
- Exercise memory consent, isolation, expiry, concurrency, corruption, and atomic recovery.
- Run the offline evaluation twice and require identical case selection, fingerprints, and deterministic-component results.
- Require explicit thresholds for accuracy, p50/p95 latency, maximum context/token/call cost, reliability rate, privacy leakage, and permission violations.
- Treat model-level accuracy, real latency, and monetary cost as **unverified** until a separately authorized controlled evaluation runs.

## Decisions required

- **Network policy:** recommended default is deny-by-default, HTTP(S)-only, public destinations or explicit allowlist.
- **Memory policy:** recommended default is opt-in, per-user/per-project isolation, sensitive-data exclusion, and short retention.
- **Output contract:** recommended default is structured status plus preserved prose answer and source metadata.
- **Quality thresholds:** the owner must define acceptable answer accuracy, latency percentiles, budget, and reliability before any “ready” claim.
- **Deployment boundary:** clarify whether this remains a local demo or will process multi-user or sensitive data; that decision determines required isolation and enforcement.

## Deferred or intentionally absent

| Item | Reason | Revisit trigger |
|---|---|---|
| Real model accuracy/cost measurements | No model integration exists; models and paid services were prohibited during this audit | Before selecting or connecting a model |
| Live URL reliability testing | Network access was prohibited | After URL policy and isolated test environment are approved |
| Production readiness | No production system or deployment configuration was inspected | When deployment is proposed |
| Project-specific Skill | Potentially disproportionate for this tiny fixture | When the evaluation workflow becomes recurring |
| Version-history drift analysis | Parent repository and history were outside the permitted scope | A future audit explicitly authorizes history inspection |
