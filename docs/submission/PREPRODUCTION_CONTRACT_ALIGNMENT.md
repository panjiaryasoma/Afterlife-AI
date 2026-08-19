# Afterlife AI — Preproduction Contract Alignment

**Baseline:** Afterlife AI preproduction final package
**Runtime checkpoint:** `DEV-01 governance checkpoint (post-321de449)`
**Status:** `ALIGNED_WITH_RECORDED_SEMANTIC_REFINEMENT`

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

global_resource_capacity_wiring: PASS
report_value_separation: PASS
infeasible_fallback_semantics: ACCEPTED_REFINEMENT

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

The production runtime now exposes typed generic resource capacities and
per-action resource requirements through `RuntimeCapabilityConfig`.

The active production optimizer derives and forwards:

```text
shared_resource_capacities
candidate_resource_requirements
```

to the existing CP-SAT resource-constraint interface.

The deterministic fallback receives the same resource-capacity contract and
limits partial allocations when remaining shared resources become binding.

Existing action-level and partner/destination capacity semantics remain
unchanged.

Regression coverage verifies:

- runtime parsing and validation of generic resources;
- production forwarding into CP-SAT;
- global resource enforcement with `cold_storage_units`;
- deterministic fallback resource enforcement;
- preservation of the existing shared-capacity and quantity-conservation tests.

### Status

```yaml
contract_status: PASS
core_optimizer_support: PRESENT
production_runtime_wiring: PRESENT
fallback_resource_enforcement: PRESENT
regression_status: PASS
```

### Claim boundary

The current production runtime may claim enforcement of configured generic
shared resource capacities for actions that declare corresponding per-unit
resource requirements.

This does not imply real-world measurement or validation of the configured
resource capacities.

### Verification

```text
targeted GAP-01 suite: PASS
full regression: 363 passed
ruff: PASS
mypy: PASS
frontend JavaScript syntax: PASS
```

GAP-01 is closed without modifying the locked preproduction contract.

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

It additionally requires visibility for applicable request and optimizer
observability such as logistics-budget use, capacity utilization, and the
BALANCED rescue-floor status.

### Current implementation

Selected allocations continue to expose the existing allocation-level
components:

```text
expected_cash_recovery
expected_future_branch_recovery
expected_avoided_purchase_cost
expected_physical_rescue_quantity
expected_waste_quantity
expected_net_recovery
```

Batch metrics now explicitly expose:

```text
expected_total_economic_value
expected_cash_recovery
expected_future_branch_recovery
expected_avoided_purchase_cost
expected_inventory_loss
expired_inventory_loss
social_allocation_quantity
expected_physical_rescue_quantity
expected_waste_quantity
expected_rescue_ratio
logistics_budget_used
capacity_utilization
minimum_expected_rescue_ratio
balanced_rescue_floor_status
```

The production report aggregates cash recovery, future branch recovery,
avoided purchase cost, physical rescue, and waste from the selected
allocation-level values.

`expected_inventory_loss` represents expected planning-stage waste valued
using the source lot unit cost.

`expired_inventory_loss` is reported separately from planning-stage expected
inventory loss and is derived from deterministic expired routing and source
lot unit cost.

`social_allocation_quantity` represents selected donation quantity. It is a
physical allocation quantity and is not converted into an invented monetary
social-value claim.

`logistics_budget_used` is sourced from the optimizer result rather than
recomputed independently by the report layer.

`capacity_utilization` reports optimizer-recorded shared-resource usage
relative to configured runtime resource capacities.

For the `BALANCED` objective, the report exposes the requested minimum rescue
ratio together with a `MET` or `NOT_MET` status derived from the resulting
expected rescue ratio. Other objectives report `NOT_APPLICABLE`.

Quantity reconciliation remains unchanged.

The report remains advisory:

```text
execution_performed: false
human_final_approval_status: PENDING
```

### Status

```yaml
contract_status: PASS
allocation_level_value_components: PRESERVED
batch_value_separation: PRESENT
inventory_loss_separation: PRESENT
expired_inventory_loss_separation: PRESENT
social_allocation_visibility: PRESENT
logistics_budget_visibility: PRESENT
capacity_utilization_visibility: PRESENT
balanced_rescue_floor_visibility: PRESENT
quantity_reconciliation: PRESERVED
advisory_boundary: PRESERVED
regression_status: PASS
```

### Claim boundary

The production runtime may claim explicit report separation for the
implemented expected-value, physical-quantity, loss, resource-utilization,
and request-floor fields.

These values are decision-support outputs derived from current runtime inputs,
configured capacities, deterministic routing, candidate economics, and
optimizer results.

They are not evidence of realized merchant cash recovery, realized social
impact, field-validated loss reduction, or real-world capacity utilization.

### Verification

```text
targeted GAP-02 report suite: 27 passed
full regression: 363 passed
ruff: PASS
mypy: PASS
frontend JavaScript syntax: PASS
```

GAP-02 is closed without modifying the locked preproduction contract.

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
contract_status: ACCEPTED_REFINEMENT

safety_direction: MORE_CONSERVATIVE
decision_record: docs/submission/IMPLEMENTATION_DECISION_INFEASIBLE_FALLBACK.md
silent_contract_rewrite: FORBIDDEN
regression_status: PASS
```

### Governance decision

The locked historical toolchain document remains unchanged.

The semantic refinement is formally recorded in:

`docs/submission/IMPLEMENTATION_DECISION_INFEASIBLE_FALLBACK.md`

The production runtime, regression behavior, architecture documentation, and
claim boundary use the narrower current-runtime semantic.

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
preproduction_contract_alignment: ALIGNED_WITH_RECORDED_SEMANTIC_REFINEMENT

blocking_safety_contradiction: false

resolved_findings:
  - GAP-01 global resource capacity wiring
  - GAP-02 Rescue Decision Report value separation
  - DEV-01 INFEASIBLE fallback semantic refinement

production_follow_up_required: []

preproduction_contracts_modified: false
submission_ready: false
```

GAP-01 and GAP-02 are supported by production implementation and regression
evidence.

DEV-01 is closed through an explicit implementation decision record while the
locked historical toolchain wording remains unchanged.

The production behavior is intentionally more conservative: a proven
INFEASIBLE result remains infeasible and is not converted into artificial
fallback success.

The locked preproduction artifacts remain unchanged.
