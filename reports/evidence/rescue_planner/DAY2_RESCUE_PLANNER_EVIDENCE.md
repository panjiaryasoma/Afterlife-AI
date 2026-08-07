# Day 2 Rescue Planner Evidence

## Status

- Planner evaluation: 30/30 PASS
- INTEGRATION-001: PASS
- Full pytest regression: 177 PASS
- Hard constraint violations: 0
- Quantity conservation: PASS
- Deterministic rerun: PASS
- Rescue Decision Report: GENERATED

## INTEGRATION-001 Quantity Flow

- Input inventory: 102
- Protected normal stock: 30
- Monitor: 10
- Rescue planning: 18
- Expired: 12
- Review: 32

Reconciliation:

30 + 10 + 18 + 12 + 32 = 102

## Planner Allocation

- Allocated planning quantity: 18
- Unallocated planning quantity: 0
- Solver status: OPTIMAL
- Objective value: 26624.00

Selected allocations:

- CAND-003-BUNDLE: 4 BUNDLE\n- CAND-003-REPURPOSE: 6 INTERNAL_REPURPOSE\n- CAND-006-DISCOUNT: 8 LOCAL_DISCOUNT\n
## Determinism

The same INTEGRATION-001 input was executed twice.

Identical structured result:

`True`

## Evaluation

- EVAL-001 through EVAL-030: 30/30 PASS
- Hard constraint violations: 0

## Claim Boundary

Fixture rescue scores are synthetic acceptance parameters.

They are not:

- trained-model outputs;
- field-validated probabilities;
- evidence of real-world rescue success.

No model training was executed during Day 2.

No API or UI implementation was added during Day 2.

## Acceptance-Discovered Fixes

The Day 2 acceptance suite exposed and closed:

- stale partner-demand hard gating;
- global logistics budget constraint;
- aggregate cross-lot MOQ;
- zero-cash donation fallback semantics;
- generic shared-resource capacity;
- multi-objective optimization behavior;
- blank `safety_stock` normalization falling back to the contract default.

## Evidence Files

- planner_acceptance_output.txt
- integration_001_output.txt
- fallback_output.txt
- full_regression_output.txt
- integration_001_planning_lots.json
- integration_001_candidates.json
- integration_001_rescue_decision_report.json
- integration_001_solver_evidence.json
- planner_eval_001_030_summary.json
- quantity_conservation_evidence.json
- repository_snapshot.json

## Repository State

- Branch: main
- HEAD at evidence capture: a186098c0ea76c425cf14fd1ee1c4e2c3e50cb45
- Day 2 implementation commit: PENDING_LOCAL_COMMIT
