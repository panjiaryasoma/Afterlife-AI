# AFTERLIFE AI ? OPTIMIZER STRESS BENCHMARK

**Version:** 1.0
**Status:** LOCKED BEFORE BENCHMARK GENERATION
**Purpose:** Optimizer Value Gate only
**Model selection impact:** None
**Test access:** Forbidden

## 1. Purpose

The frozen synthetic model benchmark v2 contains one request and one lot
per scenario group and does not expose explicit shared budget, shared resource,
or destination-identity constraints.

It is therefore not structurally capable of testing the incremental value
of global optimization over greedy per-lot allocation.

This supplemental benchmark exists only to evaluate:

A1 = selected HGB-E model + greedy allocation

versus

P = selected HGB-E model + global CP-SAT optimization.

It must not be used for model selection, hyperparameter tuning, calibration,
or test-set decisions.

## 2. Frozen upstream decisions

Selected model:

- HGB-E
- learning_rate: 0.05
- max_iter: 150
- max_leaf_nodes: 7
- min_samples_leaf: 40
- l2_regularization: 2.0
- max_bins: 255
- early_stopping: false
- random_state: 42

The model configuration must not change because of optimizer benchmark results.

## 3. Source population

Only canonical development data may be used.

Canonical locked test groups are forbidden.

The canonical validation population contains 360 planning lots.

A deterministic fixed permutation is applied to those 360 validation lots
using stress benchmark seed 314159.

The permuted lots are partitioned without replacement into:

120 stress scenario groups
x
3 planning lots per group.

Every canonical validation lot appears exactly once.

## 4. Stress strata

The 120 stress groups are divided into three pre-registered strata:

- 40 shared-capacity conflict groups
- 40 logistics-budget conflict groups
- 40 shared-resource conflict groups

Stress constraints are supplemental synthetic evaluation parameters.

They do not claim to represent prevalence or magnitude of real-world
constraints.

Constraint generation must not use simulated_rescue_outcome or
generator_success_probability.

## 5. Compared systems

### A1 ? Selected Model + Greedy Allocation

- HGB-E probabilities
- deterministic per-lot greedy allocation
- no global optimization
- same candidate eligibility rules as P
- same hard constraints as P
- same expected-value calculation as P

### P ? Selected Model + Global Optimizer

- HGB-E probabilities
- production CP-SAT optimizer
- same candidate eligibility rules as A1
- same hard constraints as A1
- same expected-value calculation as A1

A1 may not ignore a hard constraint merely because the operational fallback
implementation does not currently expose that constraint.

An evaluation-only greedy comparator may be implemented if required.

### 5.1 A1 deterministic ordering

A1 is a true per-lot greedy comparator.

Planning lots are processed in lexicographic planning_lot_id order.

Within each planning lot, eligible candidates are ranked by:

1. expected value per unit descending;
2. candidate_id ascending as deterministic tie-breaker.

A1 does not perform cross-lot optimization, backtracking, or reallocation
after a later planning lot is processed.

For benchmark v1, both A1 and P use:

- MAXIMIZE_RECOVERY_VALUE;
- no minimum expected rescue-ratio constraint;
- no aggregate action MOQ constraint.

These optional constraints are excluded because they are not registered
optimizer-stress strata in benchmark v1.

Logistics budget uses fixed candidate-level logistics cost once whenever a
candidate receives positive allocation.

Shared resource requirements represent resource units consumed per allocated
product unit.

## 6. Oracle evaluation

generator_success_probability is used only after A1 and P have produced
their allocations.

For each scenario group:

oracle_objective_value =
    objective produced by CP-SAT using oracle probabilities

a1_oracle_value =
    A1 allocation re-valued using oracle probabilities

p_oracle_value =
    P allocation re-valued using oracle probabilities

a1_regret =
    oracle_objective_value - a1_oracle_value

p_regret =
    oracle_objective_value - p_oracle_value

regret_improvement =
    a1_regret - p_regret

Positive regret_improvement means P is better than A1.

## 7. Optimizer Value Gate

The global optimizer claim passes only if all conditions hold:

1. mean P allocation regret < mean A1 allocation regret;
2. P hard-constraint violations = 0;
3. improvement occurs in at least one registered conflict stratum;
4. lower bound of the grouped-bootstrap 95% confidence interval for mean
   regret_improvement is > 0.

For fairness, A1 hard-constraint violations must also remain zero.
Any scenario where the two systems receive different hard-rule semantics
invalidates the comparison.

## 8. Statistical protocol

Bootstrap unit:

scenario_group_id

Bootstrap iterations:

10000

Bootstrap seed:

314160

Report:

- mean regret
- median regret
- total regret
- normalized regret
- regret improvement
- 95% grouped-bootstrap CI
- exact allocation agreement
- results by conflict stratum
- hard-constraint violations
- oracle value retained

No failed scenario may be removed from the denominator.

## 9. Claim boundary

A passing result supports only the statement that global optimization
outperforms deterministic greedy allocation on the pre-registered synthetic
optimizer stress benchmark.

It does not establish real-world economic impact or real-world frequency
of shared-resource conflicts.

## 10. Test boundary

The canonical test split must remain unopened during benchmark construction,
implementation, debugging, execution, and interpretation.

The Optimizer Value Gate must be frozen before final test evaluation.
