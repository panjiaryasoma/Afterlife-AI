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
- optional mass-based metrics when `package_weight_g` evidence is available

### NEXTSTEP-02 — Outcome Reconciliation

Allow operator-confirmed outcomes:
- actual rescued quantity
- actual waste quantity
- unresolved quantity

Calculate:
- realized diversion ratio from confirmed outcomes
- expected vs realized rescue delta
- expected vs realized waste delta

### NEXTSTEP-03 — Sustainability UI

Expose:
- expected impact
- realized impact
- reconciliation status
- missing-data limitations

## 4. Non-Goals

- no second ML model
- no HGB-E retraining
- no optimizer replacement
- no automatic outcome prediction
- no invented CO2 estimates
- no automatic retraining
- no database expansion
- no major UI redesign

## 5. Core Invariants

- existing rescue plan semantics must remain unchanged
- actual outcomes must never alter historical recommendations
- confirmed outcome quantity cannot exceed reconciled quantity
- expected rescue quantity + expected waste quantity must equal reconciled quantity
- quantity conservation must hold
- mass metrics only exist when weight evidence exists
- missing weight must not be imputed
- synthetic model scores remain synthetic evidence
- expected impact must never be presented as realized impact

## 6. Acceptance Suite

NEXTSTEP-001 — expected rescue and expected waste quantities reconcile against the relevant quantity scope
NEXTSTEP-002 — mass metrics are produced only when `package_weight_g` evidence is available
NEXTSTEP-003 — missing weight produces no fabricated mass metric
NEXTSTEP-004 — confirmed outcome cannot exceed reconciled quantity
NEXTSTEP-005 — realized diversion ratio is computed only from confirmed outcomes
NEXTSTEP-006 — partial outcome records produce explicit unresolved quantity
NEXTSTEP-007 — reconciliation cannot mutate the original observation or rescue plan
NEXTSTEP-008 — existing AIC-era fixtures and report contracts remain backward compatible
