# Afterlife AI — Implementation Decision: INFEASIBLE Fallback Semantics

**Decision ID:** `DEV-01`
**Scope:** Post-speedrun preproduction contract hardening
**Runtime baseline:** `321de449`
**Decision status:** `ACCEPTED_FOR_CURRENT_PRODUCTION_RUNTIME`
**Locked preproduction artifacts modified:** `false`

## Context

The locked historical `docs/contracts/TOOLCHAIN_DECISION_v1.0.md` states that
`INFEASIBLE`, `MODEL_INVALID`, and `UNKNOWN` solver outcomes use the
deterministic fallback planner while preserving the solver status.

The current production optimizer uses a more conservative semantic:

- `OPTIMAL` is a definitive usable solver outcome;
- `FEASIBLE` is a definitive usable solver outcome;
- `INFEASIBLE` is a definitive non-usable solver outcome;
- non-definitive outcomes such as `UNKNOWN` may use deterministic fallback
  only when the fallback can preserve all applicable request constraints.

The historical locked toolchain document is not rewritten.

## Decision

`INFEASIBLE` is treated as a definitive CP-SAT outcome.

A proven `INFEASIBLE` result MUST NOT be converted into a successful
deterministic fallback allocation.

For `INFEASIBLE`:

```yaml
solver_status: INFEASIBLE
selected_rescue_allocation: none
planning_quantity: remains_unallocated
fallback_success: forbidden
human_exception_review: required
```

## Rationale

`INFEASIBLE` means the active constrained optimization model has established
that no feasible allocation satisfies the modeled constraints.

Running a second planner and presenting a successful allocation after that
result would either:

1. violate one or more applicable constraints; or
2. silently change the optimization problem.

Neither behavior is acceptable for the current decision-support contract.

The production semantic is therefore intentionally more conservative than
the historical toolchain wording.

## Fallback Boundary

Deterministic allocation fallback remains allowed only for documented
non-definitive optimizer outcomes when all applicable request constraints can
still be preserved.

Fallback MUST NOT:

- bypass deterministic hard gates;
- revive an ineligible candidate;
- exceed action, destination, or generic shared-resource capacities;
- bypass an applicable logistics budget;
- bypass an applicable minimum rescue-ratio constraint;
- convert `INFEASIBLE` into artificial success.

## Human Governance

Afterlife AI remains advisory.

An `INFEASIBLE` optimization outcome leaves the relevant planning quantity
unallocated and requires human exception review.

Automatic physical rescue execution remains forbidden:

```yaml
execution_performed: false
human_final_approval_status: PENDING
```

## Implementation Evidence

Current production behavior is implemented in:

```text
src/afterlife_ai/pipeline/optimizer.py
```

The production optimizer returns `INFEASIBLE` directly before the fallback
path is considered.

Regression coverage includes an integration test that explicitly fails if
deterministic fallback is invoked for an `INFEASIBLE` CP-SAT result.

The architecture overview already documents the same semantic:

```text
An INFEASIBLE CP-SAT result is not converted into a successful fallback allocation.
```

## Contract Relationship

This record does not modify the locked historical
`TOOLCHAIN_DECISION_v1.0.md`.

Instead, it records the production semantic refinement explicitly so that:

- historical preproduction intent remains auditable;
- current production behavior remains truthful;
- documentation does not silently rewrite history;
- claim boundaries can use the narrower and safer current-runtime semantic.

## Decision Summary

```yaml
historical_wording_preserved: true
production_semantic: INFEASIBLE_IS_DEFINITIVE
successful_fallback_after_infeasible: forbidden
safety_direction: MORE_CONSERVATIVE
architecture_alignment: consistent
runtime_alignment: consistent
regression_required: true
submission_ready: false
```
