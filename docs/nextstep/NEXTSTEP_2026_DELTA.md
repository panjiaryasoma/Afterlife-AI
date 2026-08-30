# Afterlife AI — NextStep Hacks 2026 Delta

## 1. Baseline Before NextStep

Tag:
`nextstep-prehackathon-baseline-2026-08-30`

Existing capabilities:
- XLSX inventory intake
- deterministic triage
- rescue candidate generation
- deterministic hard gates
- HGB-E rescue-success scoring
- expected-value calculation
- CP-SAT global allocation
- Rescue Decision Report
- human review
- FastAPI + Jinja2 UI

## 2. NextStep Objective

Extend Afterlife AI from:

rescue planning

into:

rescue planning + measurable environmental outcome reconciliation

## 3. New Scope

### NEXTSTEP-01 — Sustainability Summary

Add:
- expected physical rescue quantity
- expected waste quantity
- expected rescue/diversion ratio
- optional mass-based metrics derived per source lot from `package_weight_g`
- explicit batch mass-evidence coverage: `COMPLETE`, `PARTIAL`, or `NONE`

Batch mass claims are emitted only when every relevant positive-quantity slice has weight evidence. Mixed package weights are aggregated per source lot rather than by applying one global package weight to the whole batch.

### NEXTSTEP-02 — Outcome Reconciliation

Allow operator-confirmed outcomes:
- actual rescued quantity
- actual waste quantity
- unresolved quantity

Calculate:
- realized diversion ratio from confirmed outcomes
- expected vs realized rescue delta
- expected vs realized waste delta

The first production surface is a stateless `POST /api/outcomes/reconcile` endpoint. It validates an operator observation against the expected planning scope and returns a reconciliation result. It does not claim to persist the observation or mutate the original rescue plan.

### NEXTSTEP-03 — Sustainability UI

Expose:
- expected impact
- realized impact
- reconciliation status
- mass-evidence coverage
- missing-data limitations

The first UI increment adds operator-confirmed outcome reconciliation directly below the existing rescue summary. It clearly separates model/plan estimates from realized operator-confirmed outcomes and uses the stateless reconciliation endpoint. Batch mass-evidence coverage remains available in the NextStep pipeline output and will be surfaced when the NextStep analysis envelope is connected to the web analysis path.

### NEXTSTEP-04 — Impact-Aware Report Envelope

Preserve the pre-NextStep `RescueDecisionReport` contract and wrap it in a NextStep-specific output:

- `rescue_decision_report`: unchanged canonical advisory report
- `sustainability_summary`: first-class NextStep sustainability output

The wrapper validates that sustainability quantities agree with canonical batch metrics. This avoids silently changing the historical report contract while still exposing impact as an official pipeline result.

## 4. Non-Goals

- no second ML model
- no HGB-E retraining
- no optimizer replacement
- no automatic outcome prediction
- no invented CO2 estimates
- no automatic retraining
- no database expansion or outcome persistence in the NextStep MVP
- no major UI redesign

## 5. Core Invariants

- existing rescue plan semantics must remain unchanged
- actual outcomes must never alter historical recommendations
- confirmed outcome quantity cannot exceed reconciled quantity
- expected rescue quantity + expected waste quantity must equal reconciled quantity
- quantity conservation must hold
- mass metrics only exist when complete weight evidence exists for the relevant batch scope
- partial weight coverage must not be presented as full batch mass
- mixed package weights must be applied per source lot
- missing weight must not be imputed
- synthetic model scores remain synthetic evidence
- expected impact must never be presented as realized impact
- the canonical `RescueDecisionReport` contract remains backward compatible
- NextStep sustainability output must reconcile with canonical report quantity metrics
- reconciliation API responses must not imply that observations were stored or persisted
- the UI must label expected/model-derived quantities separately from operator-confirmed realized outcomes

## 6. Acceptance Suite

NEXTSTEP-001 — expected rescue and expected waste quantities reconcile against the relevant quantity scope
NEXTSTEP-002 — mass metrics are produced only when `package_weight_g` evidence is available
NEXTSTEP-003 — missing weight produces no fabricated mass metric
NEXTSTEP-004 — confirmed outcome cannot exceed reconciled quantity
NEXTSTEP-005 — realized diversion ratio is computed only from confirmed outcomes
NEXTSTEP-006 — partial outcome records produce explicit unresolved quantity
NEXTSTEP-007 — reconciliation cannot mutate the original observation or rescue plan
NEXTSTEP-008 — existing AIC-era fixtures and report contracts remain backward compatible
NEXTSTEP-009 — a single-lot batch produces correct rescue and waste mass
NEXTSTEP-010 — mixed-weight lots aggregate mass per source lot correctly
NEXTSTEP-011 — missing weight in a relevant lot yields `PARTIAL` mass-evidence coverage
NEXTSTEP-012 — partial coverage never claims full batch rescue or waste mass
NEXTSTEP-013 — sustainability reporting preserves existing report quantity metrics
NEXTSTEP-014 — sustainability reporting cannot mutate optimizer-selected rescue allocations
NEXTSTEP-015 — the NextStep pipeline returns canonical rescue output and sustainability output together
NEXTSTEP-016 — the NextStep report envelope rejects sustainability quantities that disagree with canonical report metrics
NEXTSTEP-017 — the reconciliation API returns realized impact for a valid operator observation
NEXTSTEP-018 — the reconciliation API rejects confirmed quantities above the reconciled scope
NEXTSTEP-019 — the reconciliation API rejects expected quantities that do not reconcile to the observation scope
NEXTSTEP-020 — repeated reconciliation calls are deterministic and do not claim persistence
NEXTSTEP-021 — the web UI loads the dedicated outcome reconciliation interface
NEXTSTEP-022 — the UI exposes operator-confirmed rescued and waste quantity controls
NEXTSTEP-023 — the UI renders expected and realized outcomes as distinct claim classes
NEXTSTEP-024 — the UI submits reconciliation to the stateless outcome endpoint without claiming persistence
