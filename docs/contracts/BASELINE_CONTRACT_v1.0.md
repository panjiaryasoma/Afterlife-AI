# AFTERLIFE AI — BASELINE AND EVALUATION CONTRACT

**Version:** 1.0  
**Status:** Locked for Pre-production  
**Date:** 3 Agustus 2026  
**Applies to:** synthetic benchmark, model selection, optimizer comparison, proposal claims

## 1. Purpose

Kontrak ini menentukan apa yang harus dibandingkan sebelum tim boleh mengklaim bahwa komponen AI dan global optimizer memberi nilai tambahan. Ia mencegah evaluasi berubah setelah hasil terlihat, sebuah kebiasaan penelitian yang sangat manusiawi dan sangat tidak membantu.

Kontrak ini tidak menggantikan 30 planner acceptance cases. Ia menambahkan pembuktian model dan system-level improvement.

## 2. Evaluation populations

### 2.1 Core planner acceptance suite

```text
EVAL-001 sampai EVAL-030
```

Fungsi:

- menguji routing, hard rules, capacity, budget, fallback, abstention, dan explanation;
- menggunakan `fixture_rescue_success_score` ketika scoring dibutuhkan;
- tidak dipakai untuk training atau hyperparameter selection.

Pass requirement:

```text
30 / 30 cases pass
0 hard-constraint violations
```

### 2.2 Triage acceptance suite

```text
TRIAGE-001 sampai TRIAGE-008
```

Fungsi:

- menguji healthy stock, monitor, partial surplus, near-expiry, slow-moving, mixed batch, missing sales evidence, dan expired routing.

Pass requirement sebelum production:

```text
8 / 8 cases pass
0 quantity-conservation violations
```

### 2.3 Raw inventory integration suite

```text
INTEGRATION-001: RAW_INVENTORY_TO_RESCUE_PLAN
```

Pass requirement:

- healthy stock tidak masuk model;
- partial surplus menghasilkan planning quantity yang benar;
- expired dan review-required lots tidak masuk scoring;
- feasible surplus menghasilkan allocation plan;
- report merekonsiliasi seluruh quantity.

### 2.4 Synthetic benchmark dataset

Satu baris training adalah satu candidate action untuk satu surplus planning lot dalam satu synthetic scenario.

Canonical fields:

```text
scenario_id
scenario_group_id
business_profile_id
candidate features
simulated_rescue_outcome        # binary target
```

Generator juga menyimpan:

```text
generator_success_probability   # latent oracle-only field
```

Latent field tidak boleh dipakai untuk training. Ia hanya digunakan untuk menghitung system regret secara offline.

## 3. Split contract

### 3.1 No random row split

Split dilakukan berdasarkan `scenario_group_id`. Seluruh varian dari skenario dasar yang sama harus berada pada split yang sama.

Default split:

```text
train      70% scenario groups
validation 15% scenario groups
test       15% scenario groups
```

Seed utama:

```text
42
```

Robustness seeds:

```text
42, 137, 2026
```

`business_profile_id` digunakan untuk secondary generalization report. Jika satu business profile berada di lebih dari satu split, hal itu harus dilaporkan dan tidak boleh disembunyikan.

### 3.2 Locked test set

Test split dibuat sekali setelah generator v1.0 freeze. Test set tidak boleh dipakai untuk:

- feature selection;
- threshold tuning;
- calibration fitting;
- hyperparameter selection;
- rule editing.

Perubahan generator yang memengaruhi label atau feature semantics membuat benchmark version naik dan test set lama tetap disimpan.

## 4. Compared systems

Semua system variants memakai validation, coverage, safety, verification, feasibility, and quantity rules yang sama. Baseline tidak diberi izin melanggar safety hanya supaya proposed system terlihat lebih sopan.

### B0 — Rule Priority Greedy

```text
No learned score
Fixed objective-specific action priority
Greedy allocation per lot
```

Purpose: baseline operasional paling sederhana.

### B1 — Action Prior + Global Optimizer

```text
Success estimate = action-level success rate from training split only
No feature-aware ML
Global optimizer enabled
```

Purpose: menguji apakah feature-aware model lebih baik daripada sekadar mengetahui base rate tiap tindakan.

### B2 — Logistic Regression + Global Optimizer

```text
LogisticRegression
Same preprocessing contract
Probability output
Global optimizer enabled
```

Purpose: baseline ML sederhana, interpretable, dan proporsional.

### A1 — Selected Model + Greedy Allocation

```text
Selected feature-aware model
Greedy per-lot allocation
No global optimizer
```

Purpose: ablation untuk mengukur kontribusi optimizer.

### P — Selected Model + Global Optimizer

```text
Selected feature-aware model
Calibration if validation contract permits
Global optimizer
```

Purpose: proposed system.

### O — Synthetic Oracle, report only

```text
Uses generator_success_probability
Global optimizer
Never deployable
```

Purpose: menghitung lower-bound regret dari system variants. Oracle tidak boleh muncul sebagai production component.

## 5. Candidate model families

Hanya dua family yang dibandingkan pada pre-production:

```text
LogisticRegression
HistGradientBoostingClassifier
```

Keduanya menggunakan pipeline preprocessing yang sama sejauh estimator memungkinkan. Menambah family ketiga memerlukan alasan tertulis dan tidak boleh dilakukan hanya karena leaderboard internal sedang mengecewakan.

Calibration candidate:

```text
CalibratedClassifierCV(method="sigmoid")
```

Calibration dipilih hanya bila validation Brier score membaik dan ranking tidak turun secara material. Calibration fitting tidak boleh memakai test set.

## 6. Model metrics

### Primary predictive metrics

```text
PR-AUC
Brier score
```

PR-AUC dipakai sebagai primary discrimination metric karena positive/negative candidate outcomes dapat tidak seimbang. Brier score dipakai untuk probabilistic quality.

### Secondary metrics

```text
ROC-AUC
Log loss
Balanced accuracy at locked threshold
Calibration curve / reliability table
Expected calibration error
```

Threshold classification hanya untuk diagnostic report. Optimizer menggunakan probability score, bukan hard class label.

## 7. Ranking metrics

Per planning lot, kandidat feasible diranking menggunakan model score.

```text
NDCG@3
Mean Reciprocal Rank
Top-1 positive-outcome rate
Pairwise ranking accuracy
```

Ranking metrics dihitung hanya pada lot dengan minimal dua feasible candidates.

## 8. System metrics

### Safety and feasibility

```text
hard_constraint_violation_count
unsafe_consumption_allocation_count
unsupported_scored_candidate_count
quantity_conservation_violation_count
partner_capacity_violation_count
logistics_budget_violation_count
cold_storage_capacity_violation_count
```

Semua harus nol.

### Decision quality

Menggunakan `generator_success_probability` sebagai offline truth:

```text
oracle_objective_value
system_objective_value
allocation_regret = oracle_objective_value - system_objective_value
```

Dilaporkan juga:

```text
true expected net recovery
true expected physical rescue quantity
true expected waste quantity
cash / future recovery / avoided purchase cost separately
abstention correctness
no-feasible-option correctness
```

`true` pada bagian ini berarti true terhadap synthetic generator, bukan dunia nyata.

## 9. Claim gates

### 9.1 Architecture gate

```text
30/30 planner acceptance cases pass
8/8 triage cases pass
1/1 integration case pass
0 hard-constraint violations
```

### 9.2 AI value gate

Tim boleh mengatakan model lebih baik daripada action prior hanya jika:

1. mean PR-AUC lebih tinggi daripada B1;
2. mean Brier score tidak lebih buruk lebih dari 0,01 absolute dibanding B1;
3. lower bound bootstrap 95% confidence interval untuk delta PR-AUC harus lebih besar dari 0;
4. hasil konsisten pada minimal dua dari tiga robustness seeds.

Jika gate tidak lulus, wording yang dipakai:

> Feature-aware model belum menunjukkan improvement yang meyakinkan terhadap action-prior baseline pada benchmark sintetis ini.

### 9.3 Optimizer value gate

Tim boleh mengatakan global optimizer lebih baik daripada greedy hanya jika:

1. P memiliki mean allocation regret lebih rendah daripada A1;
2. hard-constraint violations tetap nol;
3. improvement muncul pada shared-capacity, budget, atau resource-conflict scenario groups;
4. lower bound bootstrap 95% confidence interval untuk regret improvement harus lebih besar dari 0.

### 9.4 Final model selection

Final production model dipilih lexicographically:

1. zero scoring-eligibility violations;
2. zero pipeline leakage violations;
3. best validation Brier score among models within 1% relative PR-AUC of the best model;
4. lowest validation allocation regret;
5. lower complexity and faster inference as tie-breaker.

Jika Logistic Regression menang, ia tetap menjadi final model. Kompleksitas bukan hadiah moral.

## 10. Statistical reporting

- Report mean dan standard deviation untuk tiga seeds.
- Gunakan bootstrap by `scenario_group_id`, bukan bootstrap per row.
- Report absolute delta dan relative delta.
- Jangan hanya menampilkan metric terbaik.
- Jangan menghapus failed scenarios dari denominator.
- Jelaskan synthetic claim boundary di setiap tabel utama.

## 11. Required benchmark outputs

```text
reports/model_metrics.csv
reports/ranking_metrics.csv
reports/system_metrics.csv
reports/baseline_comparison.csv
reports/calibration_table.csv
reports/acceptance_case_results.csv
reports/benchmark_summary.md
```

Minimal visual:

```text
PR curve
calibration curve
allocation regret comparison
objective value comparison
constraint violation summary
```

## 12. Reproducibility contract

Setiap benchmark run menyimpan:

```text
benchmark_run_id
generator_version
schema_version
ruleset_version
feature_list_hash
train/validation/test group IDs
random seed
package lock hash
model artifact hash
```

## 13. Prohibited evaluation practices

- random row split;
- tuning memakai test set;
- menghitung action prior dari full dataset;
- menghapus hard cases setelah melihat hasil;
- memakai latent generator probability sebagai feature;
- membandingkan system variants dengan hard rules berbeda;
- mengklaim real-world success probability;
- memilih satu seed terbaik;
- menyebut optimizer menang bila hanya objective surrogate-nya yang berubah tanpa offline truth comparison.

## 14. Gate decision

```yaml
baseline_variants: LOCKED
split_policy: LOCKED
primary_metrics: LOCKED
system_regret_definition: LOCKED
claim_language: LOCKED
final_model_algorithm: NOT_YET_SELECTED
benchmark_execution: PENDING_DATASET_GENERATOR
```
