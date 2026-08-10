# Technical MVP Release Candidate Verification

## Verification Summary

```yaml
project: Afterlife AI
verification_scope: Technical MVP Release Candidate
verified_commit: 3e91cf2
verification_date: 2026-08-10
release_status: READY
submission_ready: false
```

This document records the final technical verification performed for the Afterlife AI Technical MVP Release Candidate.

The verified release candidate implements the complete local-first flow:

```text
one XLSX
-> validation
-> deterministic triage
-> rescue planning
-> hard safety and feasibility gates
-> rescue-success scoring
-> expected-value calculation
-> global allocation optimization
-> Rescue Decision Report
```

The release candidate is a technical milestone, not the final competition submission.

---

## Verified Commit

```text
3e91cf2 docs: update Technical MVP architecture and runtime guide
```

The clean-clone verification was performed from this committed state.

---

## Acceptance Summary

```yaml
one_xlsx_to_report: PASS
report_download: PASS

api:
  root: PASS
  health: PASS
  analyze: PASS

evaluation:
  triage_cases: 8/8
  planner_cases: 30/30
  integration_cases: 1/1
  quantity_conservation: PASS
  hard_constraint_violations: 0

scoring:
  selected_model: M1_HIST_GRADIENT_BOOSTING
  deterministic_fallback: PASS
  blocked_candidate_preservation: PASS

runtime:
  clean_clone: PASS
  uv_sync_locked: PASS
  docker_no_cache_build: PASS
  docker_compose: PASS
  container_health: PASS

quality:
  pytest: PASS
  ruff: PASS

release:
  technical_mvp_release_candidate: READY
  submission_ready: false
```

---

## Clean Clone Verification

A fresh clone was created from the committed repository state.

Verification steps:

```text
git clone --no-local
-> clean working tree
-> uv sync --locked
-> full pytest regression
-> Ruff production lint scope
-> Docker Compose no-cache build
-> Docker Compose runtime
-> GET /health
-> clean shutdown
```

Result:

```yaml
clean_working_tree: PASS
dependency_installation: PASS
locked_dependency_resolution: PASS
```

No existing project virtual environment was reused.

---

## Automated Regression

Clean-clone regression result:

```text
287 passed
0 failed
4139 warnings
```

Primary-repository evidence run:

```text
287 passed
0 failed
4137 warnings
```

The warning-count difference is caused by additional environment-level deprecation warnings observed in the fresh clone. No test failure was introduced.

Evidence:

```text
reports/evidence/technical_mvp_rc_pytest.txt
```

---

## Lint Verification

Ruff verification result:

```text
All checks passed!
```

Validated scope:

```text
src/afterlife_ai
backend
tests/unit
tests/integration
tests/acceptance
tests/api
```

Evidence:

```text
reports/evidence/technical_mvp_rc_ruff.txt
```

---

## Triage Acceptance

The deterministic triage acceptance suite passes:

```text
TRIAGE-001: PASS
TRIAGE-002: PASS
TRIAGE-003: PASS
TRIAGE-004: PASS
TRIAGE-005: PASS
TRIAGE-006: PASS
TRIAGE-007: PASS
TRIAGE-008: PASS
```

Result:

```yaml
triage_cases: 8/8
```

---

## Planner Evaluation

The planner evaluation contract remains green:

```yaml
evaluation_cases: 30/30
quantity_conservation: PASS
hard_constraint_violations: 0
```

The optimizer preserves global quantity constraints and shared-capacity constraints.

---

## Integration Verification

`INTEGRATION-001` passes end-to-end against the controlled technical fixture.

Verified production chain:

```text
XLSX
-> validation
-> triage
-> planning lots
-> production candidate generation
-> deterministic hard gates
-> scoring
-> expected value
-> global optimizer
-> Rescue Decision Report
```

Result:

```yaml
integration_cases: 1/1
```

---

## Scoring Verification

Selected production provider:

```yaml
provider_name: M1_HIST_GRADIENT_BOOSTING
algorithm: HistGradientBoostingClassifier
artifact: models/HGB_E_v1.joblib
feature_schema: docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml
```

The production scoring stage only evaluates candidates that remain eligible after deterministic hard gates.

---

## Deterministic Fallback Verification

If the trained model artifact is missing or cannot be loaded, the scoring layer falls back to:

```yaml
model_version: DETERMINISTIC_FALLBACK_V1
score: 0.50
```

The fallback is intentionally neutral and does not represent a validated real-world probability.

A dedicated regression verifies that a candidate already marked `BLOCKED` by hard gates:

```text
remains BLOCKED
does not receive fallback score
does not receive fallback model version
preserves rejection reason codes
```

Result:

```yaml
hard_gate_bypass: false
blocked_candidate_preservation: PASS
```

---

## API Verification

Verified endpoints:

```text
GET  /
GET  /health
POST /api/analyze
```

Behavior:

```yaml
root_ui: PASS
health: PASS
valid_xlsx_analysis: PASS
wrong_extension_error: PASS
corrupt_xlsx_error: PASS
synchronous_processing: PASS
temporary_upload_cleanup: PASS
server_side_history: NONE
database: NONE
```

Malformed input is returned as a clear client error instead of being silently treated as a successful analysis.

---

## UI Verification

The minimal Jinja2 interface was manually verified.

Verified behavior:

```text
upload XLSX
-> Analyze Inventory
-> analysis status
-> batch metrics
-> scoring provider
-> selected allocations
-> manual review items
-> limitations
-> Download JSON Report
```

Result:

```yaml
web_interface: PASS
report_rendering: PASS
json_download: PASS
```

---

## Example Rescue Decision Report

A downloaded Rescue Decision Report is stored as release-candidate evidence:

```text
reports/evidence/technical_mvp_rc_example_report.json
```

The verified example includes:

```yaml
feature_schema_version: 2.0.0
provider_name: M1_HIST_GRADIENT_BOOSTING
input_lots: 6
input_quantity: 102
planning_quantity: 18
allocated_planning_quantity: 18
unallocated_planning_quantity: 0
expected_total_economic_value: 33397.22
model_execution_performed: true
human_final_approval_status: PENDING
execution_performed: false
```

Quantity reconciliation:

```text
protected 30
+ monitor 10
+ planning 18
+ expired 12
+ review 32
= input quantity 102
```

Planning reconciliation:

```text
allocated 18
+ unallocated 0
= planning quantity 18
```

---

## Docker Verification

Docker verification was performed from the clean clone using a no-cache build.

Build command:

```powershell
docker compose build --no-cache
```

Result:

```yaml
docker_build: PASS
cache_dependency: NONE
```

Runtime command:

```powershell
docker compose up -d
```

Container status:

```text
healthy
```

Health verification:

```text
status  service
------  ------------
ok      afterlife-ai
```

The container was then shut down cleanly with:

```powershell
docker compose down
```

Result:

```yaml
docker_compose_runtime: PASS
container_health: PASS
clean_shutdown: PASS
```

---

## Runtime Boundary

The verified Technical MVP preserves the intended runtime boundary:

```yaml
request_processing: synchronous
runtime_database: none
server_side_history: none
uploaded_file_persistence: temporary_only
report_persistence: user_download_only
runtime_internet: none
automatic_execution: none
```

The system remains advisory.

No rescue action is physically executed by the application.

---

## Synthetic Data and Claim Boundary

The selected model was trained on a frozen synthetic benchmark.

Therefore:

- the training data is not real transaction data;
- model output is not a field-validated real-world rescue probability;
- static runtime capacity, pricing, and operational parameters are MVP defaults;
- the model does not determine safety;
- deterministic hard gates cannot be overridden by the model or fallback;
- synthetic evaluation does not prove real-world business effectiveness;
- human approval remains required.

---

## Known Non-Blocking Warnings

### NumPy / joblib deprecation warning

Model artifact loading currently emits repeated third-party deprecation warnings related to NumPy array shape handling inside `joblib.numpy_pickle`.

These warnings:

```yaml
source: third_party_dependency
regression_failure: false
runtime_failure: false
```

### Starlette TestClient deprecation warning

The installed Starlette TestClient emits a deprecation warning related to its current `httpx` integration.

This warning:

```yaml
source: third_party_dependency
regression_failure: false
runtime_failure: false
```

These warnings are documented rather than globally suppressed.

---

## Known Limitations

The Technical MVP Release Candidate still has the following intentional or unresolved limitations:

- model training data remains synthetic;
- real-world probability calibration is not validated;
- runtime capability, cost, capacity, and pricing parameters are static MVP defaults;
- real-world business adoption and willingness-to-pay are not validated;
- the Partner Demand Registry is not a live marketplace;
- no authentication or multi-user isolation;
- no server-side report history;
- no database persistence;
- no background workers;
- no automatic action execution;
- no automatic logistics execution;
- no online learning or automatic retraining;
- UI remains functional Technical MVP styling rather than final competition polish;
- third-party dependency deprecation warnings remain during model-related tests.

No known limitation currently blocks the Technical MVP Release Candidate.

---

## Post-Sprint Work

The following work is intentionally moved outside the four-day technical production sprint:

- UI and visual polish;
- final proposal writing;
- proof-of-work curation;
- architecture and evaluation figures;
- demo recording;
- promotional video;
- competition submission packaging;
- final documentation polish;
- additional real-world validation where feasible;
- dependency-warning cleanup if it can be done without destabilizing the release candidate.

No major architecture migration is required after this Technical MVP milestone.

The same repository continues toward final submission.

---

## Evidence Files

```text
reports/evidence/TECHNICAL_MVP_RC_VERIFICATION.md
reports/evidence/technical_mvp_rc_pytest.txt
reports/evidence/technical_mvp_rc_ruff.txt
reports/evidence/technical_mvp_rc_example_report.json
```

---

## Final Technical Decision

```yaml
one_xlsx_to_report: WORKING
report_download: WORKING

api:
  root: PASS
  health: PASS
  analyze: PASS

evaluation:
  triage_cases: 8/8
  planner_cases: 30/30
  integration_cases: 1/1
  quantity_conservation: PASS
  hard_constraint_violations: 0

runtime:
  clean_clone: PASS
  docker_compose: PASS

release:
  technical_mvp_release_candidate: READY
  submission_ready: false
```

**Decision: Technical MVP Release Candidate is READY.**

This decision does not represent final competition submission approval.
