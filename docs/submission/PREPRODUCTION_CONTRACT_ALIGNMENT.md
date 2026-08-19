# Afterlife AI — Preproduction Contract Alignment

**Baseline:** Afterlife AI preproduction final package
**Runtime checkpoint:** `48938f3`
**Status:** `PARTIALLY_ALIGNED_WITH_EXPLICIT_DEBT`

## Purpose

This document records implementation alignment against the locked
preproduction contracts without rewriting or silently weakening those
contracts.

The preproduction artifacts remain historical source-of-truth records.
Where the production implementation differs, the difference is recorded
explicitly here.

---

## 1. Alignment Summary

```yaml
core_architecture: PASS
one_xlsx_request_boundary: PASS
deterministic_triage: PASS
planning_quantity_boundary: PASS
hard_gate_before_model: PASS
single_model_boundary: PASS
quantity_conservation: PASS
partner_capacity_boundary: PASS
decision_context_wiring: PASS
human_review_boundary: PASS
automatic_execution_boundary: PASS
synthetic_claim_boundary: PASS

global_resource_capacity_wiring: PARTIAL
report_value_separation: PARTIAL
infeasible_fallback_semantics: INTENTIONAL_DEVIATION

submission_ready: false
```

---

## 2. Fully Aligned Contracts

The current implementation preserves the following locked preproduction
semantics:

- one XLSX is processed per analysis request;
- processing remains synchronous;
- deterministic inventory triage runs before rescue planning;
- only `planning_quantity` enters rescue planning;
- `review_quantity` remains outside candidate generation, scoring, and allocation;
- deterministic safety and feasibility gates execute before model scoring;
- blocked or ineligible candidates cannot be revived by model scoring;
- HGB-E is used as the single production rescue-success model;
- rescue-success scores are not presented as field-validated probabilities;
- partner demand and partner capacity can restrict external-partner candidates;
- request-level objective, logistics budget, rescue ratio, and rescue deadline
  are represented in the production request path;
- quantity reconciliation is enforced by the report contract;
- human approval remains pending outside automatic execution;
- `execution_performed` remains `false`.

---

## 3. GAP-01 — Global Resource Capacity Wiring

### Locked preproduction requirement

`FEATURE_SCHEMA_FINAL_v2.0.yaml` defines business capability
`resource_capacities`, including examples such as:

```text
labor_hours
equipment_units
ingredient_units
bundle_companion_units
cold_storage_units
```

The locked cross-entity invariant also states:

```text
Global cold-storage use does not exceed available capacity after reservations.
```

### Current implementation

The core CP-SAT optimizer supports:

```text
shared_resource_capacities
candidate_resource_requirements
```

However, the active production runtime adapter currently derives and forwards:

```text
shared_action_capacities
shared_destination_capacities
max_logistics_budget
optimization_objective
minimum_expected_rescue_ratio
```

The current `RuntimeCapabilityConfig` does not expose the generic
`resource_capacities` map from the locked preproduction capability contract.

### Status

```yaml
contract_status: PARTIAL
core_optimizer_support: PRESENT
production_runtime_wiring: INCOMPLETE
```

### Claim boundary

Do not claim that arbitrary global capability resources, including generic
cold-storage capacity, are enforced by the current production runtime.

Existing action-level and partner-level capacity constraints remain supported.

### Required follow-up

Production hardening should wire locked capability resource capacities into
the optimizer without changing the preproduction contract.

---

## 4. GAP-02 — Rescue Decision Report Value Separation

### Locked preproduction requirement

The locked cross-entity invariant requires the report to separate:

```text
cash recovery
future branch recovery
avoided purchase cost
physical rescue
waste
inventory loss
social allocation
```

Implementation handoff also explicitly requested visibility for:

```text
cash recovery
future recovery
avoided purchase cost
physical rescue
waste
expired inventory loss
```

### Current implementation

Selected allocations currently expose:

```text
expected_cash_recovery
expected_future_branch_recovery
expected_avoided_purchase_cost
expected_physical_rescue_quantity
expected_waste_quantity
expected_net_recovery
```

Batch metrics currently expose:

```text
expected_total_economic_value
expected_physical_rescue_quantity
expected_waste_quantity
expected_rescue_ratio
```

The current report therefore preserves several expected-value components,
but does not yet provide explicit batch-level separation for every value
category named by the locked invariant.

Notably absent as explicit report-level categories are:

```text
inventory loss
social allocation
expired inventory loss
```

### Status

```yaml
contract_status: PARTIAL
allocation_level_value_components: PRESENT
complete_locked_report_separation: NOT_YET_IMPLEMENTED
```

### Claim boundary

Do not claim full implementation of every locked Rescue Decision Report
value category until those categories are represented explicitly.

### Required follow-up

Production hardening should extend report aggregation and presentation while
preserving the existing advisory report contract and quantity invariants.

---

## 5. DEV-01 — INFEASIBLE Optimizer Fallback Semantics

### Preproduction wording

`TOOLCHAIN_DECISION_v1.0.md` states that:

```text
INFEASIBLE
MODEL_INVALID
UNKNOWN
```

lead to deterministic fallback planning with solver status reported.

### Current implementation

The production optimizer currently treats:

```text
OPTIMAL
FEASIBLE
INFEASIBLE
```

as definitive CP-SAT outcomes.

`INFEASIBLE` is returned directly and is not converted into a successful
fallback allocation.

Fallback is reserved for non-definitive outcomes when request constraints
can still be preserved.

For an `INFEASIBLE` result:

```text
no rescue allocation is selected
planning quantity remains unallocated
solver status remains INFEASIBLE
human exception review is required
```

### Rationale

A proven `INFEASIBLE` constrained problem should not be transformed into a
successful allocation by a secondary planner unless the constraint model
itself changes.

The current production behavior is therefore intentionally more conservative
than the earlier toolchain wording.

### Status

```yaml
contract_status: INTENTIONAL_DEVIATION
safety_direction: MORE_CONSERVATIVE
silent_contract_rewrite: FORBIDDEN
```

### Required governance follow-up

Do not rewrite the locked historical toolchain document.

Before final contract closure, record this semantic refinement through an
explicit approved implementation/change decision so the production runtime
and historical contract do not silently disagree.

---

## 6. Accepted Non-Blocking Debt

The following remain explicitly non-blocking for this alignment checkpoint:

```text
optimizer-vs-greedy superiority benchmark
real-world merchant validation
real-world partner validation
field probability calibration
report usability study
final frozen-commit reproducibility
```

These must remain limitations or deferred evidence and must not be promoted
into stronger competition claims.

Final frozen-commit reproducibility remains:

```yaml
status: PENDING_G10
submission_ready: false
```

---

## 7. Decision

```yaml
preproduction_contract_alignment: PARTIAL_WITH_EXPLICIT_DEBT

blocking_safety_contradiction: false

production_follow_up_required:
  - wire generic global resource capacities
  - complete locked report-value separation
  - formally record INFEASIBLE fallback semantic refinement

preproduction_contracts_modified: false
submission_ready: false
```

Issue #11 may document these findings, but the two implementation gaps must
not be silently relabeled as fully implemented evidence.

The locked preproduction artifacts remain unchanged.
