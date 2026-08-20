# Afterlife AI — Final Release / Submission Audit Gate

**Project:** Afterlife AI
**Gate:** G10
**Current status:** PASS ? TECHNICAL REPOSITORY FREEZE
**Execution date:** 2026-08-20
**Audit subject commit:** `52cfb2d7563e2b359a2c0dae0137262fad6b6100`
**Release record ref:** `submission-final-2026-08-20`
**Reason:** all technical G10 gates passed; external competition deliverables are tracked separately.

This file defines the final release audit that must be executed only after all code and submission-relevant implementation work is frozen.

Running a “final” audit before the remaining issues are complete would create evidence for the wrong repository state.

---

# 1. Gate Rule

G10 may begin only when:

```yaml
remaining_code_issues: 0
remaining_required_runtime_changes: 0
remaining_required_contract_changes: 0
remaining_required_UI_changes: 0
submission_documents_can_reference_current_behavior: true
```

G7 promotion-video work and G8 screenshot capture may still be recorded after the technical freeze, but they may not introduce new product behavior.

---

# 2. Required Final Repository State

Before G10 execution:

```powershell
git status --short
git log -1 --oneline
```

Required:

```yaml
working_tree_before_audit: clean
branch: main
all_required_changes_committed: true
```

Record:

```text
full commit SHA
short commit SHA
audit timestamp
Python version
uv version
Docker version
```

---

# 3. Final Static Integrity Checks

Run:

```powershell
git diff --check
```

Expected:

```text
no errors
```

Check project metadata:

```powershell
Test-Path .\README.md
Test-Path .\BRAND_GUIDELINES.md
Test-Path .\DESIGN.md
Test-Path .\pyproject.toml
Test-Path .\uv.lock
Test-Path .\Dockerfile
Test-Path .\compose.yaml
```

All required files must return:

```text
True
```

---

# 4. Final Production Lint

Run the production lint scope:

```powershell
uv run ruff check src backend tests scripts
```

Required:

```text
All checks passed!
```

Do not fail the final release merely because locked historical notebooks contain pre-existing long-line evidence noise unless notebook lint was explicitly added to the project contract.

If notebook code changes later, reevaluate this exception instead of using it forever as a sacred loophole.

---

# 5. Final Type Check

Run:

```powershell
uv run mypy src backend
```

Required:

```text
Success: no issues found
```

Record exact source-file count reported by mypy.

---

# 6. Final Full Regression

Run:

```powershell
uv run pytest -q
```

Required:

```yaml
failed: 0
errors: 0
```

Record exact:

```text
passed count
warning count
duration
```

Do not copy the historical RC test count.

The final README, proposal evidence, and release evidence must use the exact G10 result.

---

# 7. Targeted API / UI Regression

Run:

```powershell
uv run pytest `
  tests/api/test_demo_ui.py `
  tests/api/test_report_download_ui.py `
  -q
```

Required:

```yaml
failed: 0
```

Also include any additional UI/API test module added by later issues.

---

# 8. Core Contract Regression

Run the relevant acceptance/integration suites if not already included in full pytest.

At minimum verify:

```yaml
triage_acceptance: PASS
planner_evaluation: PASS
integration_001: PASS
quantity_conservation: PASS
hard_constraint_violations: 0
```

The exact commands should follow the final repository test structure.

---

# 9. Final Demo Analysis

Start the application:

```powershell
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Use the controlled final demo fixture.

Verify:

```text
GET /
GET /health
POST /api/analyze
```

Required behavior:

```yaml
root_ui: PASS
health: PASS
analysis: PASS
report_render: PASS
json_download: PASS
```

Capture one final JSON report as:

```text
reports/evidence/submission_final/FINAL_DEMO_REPORT.json
```

The report must preserve:

```yaml
human_final_approval_status: PENDING
execution_performed: false
```

---

# 10. Decision-Context Smoke Tests

Manually verify:

```text
MAXIMIZE_RECOVERY_VALUE
MINIMIZE_WASTE
BALANCED
```

Check that:

```text
maximum logistics budget behaves as expected
minimum rescue ratio is only required/applicable where intended
rescue deadline affects feasibility where applicable
invalid combinations produce clear errors
```

Record:

```text
reports/evidence/submission_final/FINAL_UI_SMOKE.md
```

This replaces the residual browser-smoke debt from the earlier UI hardening stage.

---

# 11. Partner Registry Smoke

Verify the demo PDR behavior:

```yaml
registry_loaded: true
source_type: synthetic/static fixture
real_world_verified: false
runtime_internet: false
```

Verify at least one controlled case where external-partner candidate behavior is observable.

Do not require external partner to win the optimizer merely for presentation aesthetics.

---

# 12. Determinism Check

Run the same controlled analysis at least twice with identical:

```text
input
analysis timestamp if fixture-controlled
runtime config
partner registry
request objective
constraints
```

Compare deterministic outputs that are expected to remain stable.

Record:

```yaml
deterministic_execution: true
optimizer_random_seed: 42
optimizer_num_search_workers: 1
```

Request IDs or real-time timestamps may differ where generated dynamically; compare the deterministic decision content rather than pretending UUIDs should magically repeat.

---

# 13. Final Docker Build

Run:

```powershell
docker compose down --remove-orphans
docker compose build --no-cache
docker compose up -d
```

Verify:

```powershell
docker compose ps
```

Then check:

```text
GET /health
GET /
```

Required:

```yaml
docker_build: PASS
container_start: PASS
container_health: PASS
ui_from_container: PASS
```

Shut down:

```powershell
docker compose down
```

Required:

```yaml
clean_shutdown: PASS
```

---

# 14. Fresh-Clone Reproducibility

This is mandatory for the final submission claim.

Create a fresh directory outside the active repository.

Example PowerShell pattern:

```powershell
$AuditRoot = Join-Path $env:TEMP "afterlife-ai-final-audit"

Remove-Item $AuditRoot -Recurse -Force -ErrorAction SilentlyContinue

git clone https://github.com/panjiaryasoma/Afterlife-AI.git $AuditRoot

Set-Location $AuditRoot
```

Verify exact commit:

```powershell
git rev-parse HEAD
git status --short
```

Then:

```powershell
uv sync --locked
uv run ruff check src backend tests scripts
uv run mypy src backend
uv run pytest -q
```

Then Docker:

```powershell
docker compose build --no-cache
docker compose up -d
docker compose ps
docker compose down
```

Required:

```yaml
fresh_clone_working_tree: clean
uv_sync_locked: PASS
ruff: PASS
mypy: PASS
pytest: PASS
docker_build: PASS
docker_runtime: PASS
```

Do not reuse the main repository `.venv`.

That would rather defeat the philosophical point of a clean-clone test.

---

# 15. Final Evidence Directory

Create:

```text
reports/evidence/submission_final/
```

Required final files:

```text
FINAL_RELEASE_VERIFICATION.md
FINAL_REPOSITORY_STATE.txt
FINAL_RUFF.txt
FINAL_MYPY.txt
FINAL_PYTEST.txt
FINAL_CLEAN_CLONE.md
FINAL_DOCKER_SMOKE.md
FINAL_UI_SMOKE.md
FINAL_DEMO_REPORT.json
```

Optional useful files:

```text
FINAL_HEALTH_RESPONSE.json
FINAL_DETERMINISM_CHECK.json
FINAL_PARTNER_REGISTRY_SMOKE.json
```

---

# 16. Final Claim Audit

Review:

```text
README.md
docs/submission/FINAL_CLAIM_BOUNDARY.md
docs/submission/PROPOSAL_EVIDENCE_MAP.md
docs/submission/PROOF_OF_WORK_VIDEO_MAP.md
reports/evidence/SUBMISSION_EVIDENCE_INDEX.md
```

Search for risky claims:

```powershell
rg -n -i `
  "real.?world probability|live marketplace|verified partner|autonomous|automatic execution|outperform.*greedy|greedy.*outperform|waste reduction|revenue increase|production deployed" `
  README.md docs reports
```

Every hit must either:

```text
be a prohibition / limitation
or
have direct final evidence
```

---

# 17. Documentation Consistency Audit

Verify all final public-facing materials agree on:

```yaml
input: one XLSX
processing: synchronous
core_output: Rescue Decision Report
model: HGB-E
model_data: synthetic benchmark
hard_gate_before_model: true
optimizer: constrained global CP-SAT
partner_registry: static synthetic demo fixture
automatic_execution: false
human_approval: required
```

If two documents describe different products, G10 fails.

---

# 18. Architecture Consistency Audit

Verify final diagrams do not claim:

```text
live services that do not exist
automatic approval workflow
automatic physical execution
real-time marketplace
unused model/agent layers
```

Canonical simplified story:

```text
Inventory
→ Validation
→ Triage
→ Candidate Generation
→ Hard Gates
→ HGB-E Scoring
→ Expected Value
→ Global Optimization
→ Rescue Decision Report
→ Human Review
```

---

# 19. Submission-Readiness Flags

G10 controls the final technical repository freeze.

After successful G10:

```yaml
final_release_audit: PASS
technical_repository_frozen: true
```

Overall competition submission readiness is broader than the technical repository.

If external competition deliverables remain pending:

```yaml
submission_ready: false
```

---

# 20. Pass / Fail Criteria

## PASS requires all

```yaml
working_tree_clean: PASS
final_commit_recorded: PASS

ruff: PASS
mypy: PASS
pytest: PASS

api_smoke: PASS
ui_smoke: PASS
json_download: PASS

triage_contract: PASS
planner_contract: PASS
quantity_conservation: PASS
hard_constraint_violations: 0

partner_registry_claim_boundary: PASS
determinism_check: PASS

docker_build: PASS
docker_runtime: PASS

fresh_clone: PASS
fresh_clone_tests: PASS
fresh_clone_docker: PASS

claim_audit: PASS
documentation_consistency: PASS
architecture_consistency: PASS
```

Any blocking failure means:

```yaml
G10_status: FAIL
submission_ready: false
```

Fix, recommit, and restart the affected audit steps.

---

# 21. G10 Current Decision

```yaml
audit_specification: READY
final_audit_execution: PASS
audit_subject_commit: 52cfb2d7563e2b359a2c0dae0137262fad6b6100
release_record_ref: submission-final-2026-08-20
technical_repository_frozen: true
submission_ready: false
technical_gates:
  static_integrity: PASS
  ruff: PASS
  mypy: PASS
  pytest: PASS
  api_ui_smoke: PASS
  partner_registry_smoke: PASS
  determinism: PASS
  docker: PASS
  fresh_clone: PASS
  claim_audit: PASS
  documentation_consistency: PASS
  architecture_consistency: PASS
```

**G10 Decision: PASS ? TECHNICAL REPOSITORY FROZEN.**

External competition deliverables remain outside this technical gate.
