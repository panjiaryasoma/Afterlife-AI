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
- planned rescue quantity
- planned waste quantity
- planned diversion ratio
- optional mass-based metrics when unit weight is provided

### NEXTSTEP-02 — Outcome Reconciliation

Allow operator-confirmed outcomes:
- actual rescued quantity
- actual waste quantity
- unresolved quantity

Calculate:
- realized diversion ratio
- planned vs realized rescue delta
- planned vs realized waste delta

### NEXTSTEP-03 — Sustainability UI

Expose:
- planned impact
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
- actual quantities cannot exceed planning quantity
- quantity conservation must hold
- mass metrics only exist when weight evidence exists
- missing weight must not be imputed
- synthetic model scores remain synthetic evidence
- planned impact must never be presented as realized impact

## 6. Acceptance Suite

NEXTSTEP-001 — planned diversion quantity conservation
NEXTSTEP-002 — weight metrics when weight exists
NEXTSTEP-003 — no mass claim when weight is absent
NEXTSTEP-004 — actual outcome cannot exceed planning quantity
NEXTSTEP-005 — realized diversion ratio calculation
NEXTSTEP-006 — partial outcome produces unresolved quantity
NEXTSTEP-007 — reconciliation cannot mutate original plan
NEXTSTEP-008 — existing AIC fixtures remain backward compatible