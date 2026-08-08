# Rescue Planner Cost Semantics Correction v1

**Status:** ACTIVE_PRODUCTION_CORRECTION

## Context

During production modeling preparation, an audit identified a semantic
mismatch between candidate-level action costs and the expected-value layer.

`CandidateAction` stores:

- `direct_action_cost`
- `logistics_cost`
- `handling_cost`

as candidate-level costs.

The expected-value layer accepts corresponding per-unit cost inputs.

The previous integration path passed candidate-level costs directly into
per-unit fields, causing those costs to be multiplied again by candidate
quantity.

## Correction

Before expected-value calculation, candidate-level costs are now amortized
over `maximum_feasible_quantity`:

```text
cost_per_unit
=
candidate_total_cost
/
maximum_feasible_quantity
```

This preserves the candidate-level total cost when the expected-value layer
multiplies the per-unit cost by quantity.

## Solver Precision Boundary

The corrected division may create long Decimal representations.

Before CP-SAT integer scaling, per-unit economic objective values are bounded
to four decimal places.

Materialized monetary allocation values are rounded to two decimal places.

This prevents unsafe CP-SAT integer coefficients without materially changing
economic decision precision.

## INTEGRATION-001 Impact

The selected allocation remains unchanged:

```text
CAND-003-REPURPOSE : 6
CAND-003-BUNDLE    : 4
CAND-006-DISCOUNT  : 8
```

Total allocated planning quantity remains:

```text
18
```

The corrected expected total economic value changes from:

```text
26624
```

to:

```text
31354.00
```

The previous value is retained only as historical pre-production evidence and
must not be interpreted as the current production economic value.

## Regression Validation

Production correction passed:

```text
pytest          : 258 passed
ruff            : PASS
mypy            : PASS
git diff --check: PASS
```

## Claim Boundary

This correction changes economic-value semantics only.

It does not change:

- synthetic feature generation;
- synthetic outcomes;
- grouped train/validation/test split;
- trained-model benchmark results already produced;
- candidate feasibility rules;
- INTEGRATION-001 allocation choice.

Allocation-regret evaluation must use the corrected cost semantics.
