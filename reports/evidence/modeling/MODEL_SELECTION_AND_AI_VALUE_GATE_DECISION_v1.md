# Afterlife AI ? Model Selection and AI Value Gate Decision

**Version:** 1.0  
**Status:** FROZEN BEFORE TEST ACCESS  
**Test accessed:** No

## 1. Selected production model

The final validation-selected model is:

- Model family: HistGradientBoostingClassifier
- Configuration label: HGB-E
- learning_rate: 0.05
- max_iter: 150
- max_leaf_nodes: 7
- min_samples_leaf: 40
- l2_regularization: 2.0
- max_bins: 255
- early_stopping: false
- random_state: 42

Selection followed the locked lexicographic model-selection contract.

All compared models were within the 1% relative PR-AUC competitive window.
HGB-E achieved the lowest validation Brier score within that competitive set.

Allocation regret was therefore retained as downstream diagnostic evidence
and did not override the earlier lexicographic selection stage.

## 2. Validation model-selection evidence

Validation results:

| Model | PR-AUC | Brier | Mean allocation regret |
|---|---:|---:|---:|
| LR | 0.849653 | 0.156055 | 5978.697861 |
| HGB-B | 0.858194 | 0.155372 | 11401.584056 |
| HGB-E | 0.853664 | 0.155145 | 14793.478944 |

Selected model: **HGB-E**

Although LR produced the lowest nominal allocation regret, grouped-bootstrap
allocation-regret comparisons did not establish conclusive pairwise
superiority at the 95% confidence level.

## 3. Robustness protocol

Robustness seeds:

- 42
- 137
- 2026

The canonical 360-group test set remained fixed for every robustness run.

Only the development pool was reshuffled into train and validation groups.
The locked test groups were excluded before model fitting and validation
scoring.

Locked test-group SHA-256:

`bdefd0f2807c26c8f7468ef3f1037e8741ae6c7a1d9613978db1f20301aa3503`

## 4. AI Value Gate results

| Seed | HGB-E PR-AUC | B1 PR-AUC | Delta PR-AUC | HGB-E Brier | B1 Brier | Delta Brier |
|---:|---:|---:|---:|---:|---:|---:|
| 42 | 0.853664 | 0.834524 | +0.019140 | 0.155145 | 0.156771 | -0.001625 |
| 137 | 0.861126 | 0.826670 | +0.034456 | 0.152999 | 0.155880 | -0.002882 |
| 2026 | 0.855107 | 0.841065 | +0.014042 | 0.154221 | 0.156090 | -0.001868 |

Aggregate:

- HGB-E mean PR-AUC: 0.856632
- B1 mean PR-AUC: 0.834086
- Mean PR-AUC delta: +0.022546
- HGB-E mean Brier: 0.154122
- B1 mean Brier: 0.156247
- Mean Brier delta: -0.002125
- Aggregate grouped-bootstrap 95% CI for PR-AUC delta:
  [+0.012832, +0.032417]
- Robustness consistency: 3/3 seeds

## 5. AI Value Gate decision

Contract criteria:

1. Mean PR-AUC higher than B1: PASS
2. Mean Brier not worse by more than 0.01 absolute: PASS
3. Bootstrap 95% lower bound for PR-AUC improvement > 0: PASS
4. Improvement consistent on at least two of three robustness seeds: PASS

**AI VALUE GATE: PASS**

## 6. Claim boundary

The evidence supports the claim that the selected feature-aware HGB-E model
outperforms the train-only B1 action-prior baseline on the frozen synthetic
benchmark under the registered robustness protocol.

This result does not establish real-world performance.

The seed-2026 individual bootstrap confidence interval crossed zero, so the
evidence must not be described as statistically significant improvement on
every individual robustness seed.

## 7. Test-access boundary

At the time this decision was frozen:

**The locked test split had not been accessed for model fitting, model
selection, hyperparameter tuning, robustness selection, or development
scoring.**

The selected HGB-E configuration and AI Value Gate decision are frozen before
final test evaluation.
