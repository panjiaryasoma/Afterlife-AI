# Synthetic Benchmark Freeze v1.0

**Status:** FROZEN_FOR_MODELING

## Benchmark Identity

- Feature schema version: `2.0.0`
- Generator config version: `1.0.0`
- Outcome recipe version: `1.0.0`
- Primary seed: `42`
- Scenario groups: `2400`
- Candidate rows: `12020`

## Artifact Identity

Candidate SHA-256:

~~~text
c1c47ace2097f6a566e9d825436fd2b6b4483905b6e2e4a447bf961d3f944ca0
~~~

Oracle SHA-256:

~~~text
0efeac6a17f84f74a1c8cdfbb9de9afa8aea044a55168dd15285c6aff6bd4171
~~~

## Dataset Quality

- Quality gate: `PASS`
- Missing cells: `0`
- Duplicate rows: `0`
- Duplicate candidate IDs: `0`
- Candidate/oracle alignment: `True`
- Positive rate: `0.801581`
- Minority rate: `0.198419`
- Candidate range per group: `2-8`

## Quality Warnings

- class minority berada di bawah 20%; interpretasikan ranking dan calibration dengan hati-hati

## Model Eligibility

Production generator was corrected before model training so that generated
model-scored candidates satisfy deterministic feasibility invariants.

Locked requirements:

~~~text
remaining_safe_window_hours <= remaining_shelf_life_days * 24
estimated_completion_hours <= remaining_safe_window_hours
estimated_completion_hours <= remaining_commercial_window_days * 24
minimum_order_quantity <= allocatable_quantity
~~~

Production model-eligibility audit:

~~~text
safe_window_vs_shelf_life       = 0 violations
completion_vs_safe_window       = 0 violations
completion_vs_commercial_window = 0 violations
minimum_order_vs_allocatable    = 0 violations
~~~

## Grouped Split

Split unit:

~~~text
scenario_group_id
~~~

Split seed:

~~~text
42
~~~

Assignments:

~~~text
train       1680 groups / 8435 rows
validation  360 groups / 1805 rows
test        360 groups / 1780 rows
~~~

Group leakage:

~~~text
0
~~~

Test policy:

~~~text
LOCKED_FINAL_EVALUATION
~~~

## Freeze Decision

This benchmark is frozen for baseline and candidate-model development.

From this point forward:

- training may use only the train split;
- action priors must be estimated from train only;
- preprocessing must be fit on train only;
- model and hyperparameter selection may inspect validation;
- test outcomes must not be used for model selection, calibration fitting,
  threshold tuning, feature selection, or rule editing;
- `generator_success_probability` remains oracle-only;
- hard safety and feasibility rules remain outside learned scoring.

A previous pre-freeze dataset draft was invalidated before model training after
a model-eligibility diagnostic found infeasible generated candidates. No model
selection or test evaluation was performed using that rejected draft.

## Claim Boundary

This benchmark validates behavior against a synthetic generator. It does not
establish real-world rescue-success probabilities.
