# Afterlife AI — Submission Evidence Index

**Purpose:** curate the evidence that should actually be surfaced during submission, proposal writing, proof-of-work recording, and final audit.

**Status:** G4 evidence curation

This file is an index, not a new benchmark result. It points to existing evidence and separates current submission-grade evidence from historical development evidence so older numbers do not accidentally become final claims.

---

## 1. Evidence Policy

Use evidence in this order:

1. **Final locked evaluation evidence** for model-performance claims.
2. **Frozen model-selection evidence** for explaining why HGB-E was selected.
3. **Synthetic split evidence** for leakage and evaluation-protocol claims.
4. **Technical MVP verification evidence** for end-to-end runtime and reproducibility claims.
5. **Planner / acceptance evidence** for deterministic safety, feasibility, quantity conservation, and optimizer-contract claims.
6. **Historical sprint evidence** only when reconstructing development history or proof-of-work chronology.

Do not promote an older development metric when a later locked or release-candidate artifact exists.

---

## 2. Canonical Submission Evidence

### EVID-01 — Final Locked Model Evaluation

**Path**

```text
reports/evidence/modeling/final_test/FINAL_LOCKED_TEST_v1.json
```

**Use for**

- final synthetic-benchmark predictive performance;
- ranking performance;
- downstream allocation diagnostics;
- final-test safety checks;
- reproducibility hashes.

**Key verified values**

```yaml
status: COMPLETED
selected_model: HGB-E
selection_frozen_before_test: true
test_rows: 1780
test_scenario_groups: 360

HGB_E:
  pr_auc: 0.874229
  brier: 0.151383
  mrr: 0.930093
  ndcg_at_3: 0.890749
  top1_success_rate: 0.872222
  pairwise_accuracy: 0.663004
  mean_allocation_regret: 9454.805111
  oracle_value_retained: 0.998591

B1:
  pr_auc: 0.834923
  brier: 0.156801
  mrr: 0.915972
  ndcg_at_3: 0.869309
  top1_success_rate: 0.844444
  pairwise_accuracy: 0.596337
  mean_allocation_regret: 20545.045250
  oracle_value_retained: 0.996938

safety:
  quantity_conservation: PASS
  hard_constraint_violations: 0
```

**Permitted claim**

The selected HGB-E model performs better than the B1 action-prior baseline on the frozen synthetic final-test benchmark across the reported predictive metrics, ranking metrics, and observed allocation-regret diagnostic.

**Do not claim**

- field-validated real-world probability accuracy;
- real-world business impact;
- optimizer superiority over greedy or another optimizer;
- statistical significance beyond what the registered evidence actually establishes.

---

### EVID-02 — Frozen Model Selection and AI Value Gate

**Paths**

```text
reports/evidence/modeling/MODEL_SELECTION_AND_AI_VALUE_GATE_DECISION_v1.md
configs/selected_model_v1.yaml
```

**Use for**

- why HGB-E was selected;
- showing model selection was frozen before final-test access;
- AI-value justification against the B1 baseline;
- robustness protocol.

**Key verified values**

```yaml
selected_model: HGB-E
model_family: HistGradientBoostingClassifier
selection_status: FROZEN_BEFORE_FINAL_TEST
final_test_accessed_during_selection: false

validation:
  HGB_E_pr_auc: 0.853664
  HGB_E_brier: 0.155145

robustness:
  seeds: [42, 137, 2026]
  mean_HGB_E_pr_auc: 0.856632
  mean_B1_pr_auc: 0.834086
  mean_pr_auc_delta: 0.022546
  aggregate_bootstrap_95pct_ci_pr_auc_delta:
    lower: 0.012832
    upper: 0.032417
  consistency: 3/3

AI_VALUE_GATE: PASS
```

**Permitted claim**

HGB-E passed the registered AI Value Gate against the train-only B1 action-prior baseline on the frozen synthetic benchmark and was selected before accessing the locked final test.

**Important nuance**

The selection record explicitly states that one individual robustness seed had a bootstrap interval crossing zero. Do not describe improvement as statistically significant on every individual seed.

---

### EVID-03 — Synthetic Dataset Split Integrity

**Path**

```text
reports/evidence/synthetic_dataset/SPLIT_MANIFEST_v2.json
```

**Use for**

- grouped train / validation / test split;
- leakage prevention;
- locked final-test policy;
- dataset scale disclosure.

**Key verified values**

```yaml
total_rows: 12020
total_scenario_groups: 2400
split_unit: scenario_group_id
split_seed: 42
random_row_split_allowed: false
group_leakage: false
group_leakage_count: 0

authorized_splits:
  train:
    groups: 1680
    rows: 8435
  validation:
    groups: 360
    rows: 1805
  test:
    groups: 360
    rows: 1780

test_split_policy: LOCKED_FINAL_EVALUATION
test_outcomes_inspected_for_model_selection: false
```

**Permitted claim**

The synthetic benchmark uses deterministic group-based splitting by `scenario_group_id` with no group leakage between train, validation, and final-test partitions.

---

### EVID-04 — Technical MVP Release Candidate Verification

**Paths**

```text
reports/evidence/TECHNICAL_MVP_RC_VERIFICATION.md
reports/evidence/technical_mvp_rc_pytest.txt
reports/evidence/technical_mvp_rc_ruff.txt
reports/evidence/technical_mvp_rc_example_report.json
```

**Use for**

- one-XLSX-to-report proof;
- API / UI / report-download proof;
- deterministic triage acceptance;
- planner evaluation;
- quantity conservation;
- clean-clone reproducibility;
- Docker Compose verification;
- model fallback boundary;
- advisory / no-auto-execution boundary.

**Verified RC checkpoint**

```yaml
verified_commit: 3e91cf2
verification_date: 2026-08-10
technical_mvp_release_status: READY
submission_ready: false

triage_cases: 8/8
planner_cases: 30/30
integration_cases: 1/1
quantity_conservation: PASS
hard_constraint_violations: 0
clean_clone: PASS
docker_compose: PASS
```

**Historical-number warning**

This release-candidate document records the earlier RC regression state. Its test count and UI wording are historical checkpoint evidence, not the final post-Issue-7 submission state. Final regression, UI, and clean-clone evidence must be recaptured during the final release audit.

---

### EVID-05 — Canonical Rescue Decision Report Example

**Path**

```text
reports/evidence/technical_mvp_rc_example_report.json
```

**Use for**

- showing the concrete output contract;
- quantity reconciliation;
- scoring provenance;
- selected allocations;
- limitations;
- human-approval boundary.

**Verified RC example**

```yaml
feature_schema_version: 2.0.0
provider_name: M1_HIST_GRADIENT_BOOSTING
input_lots: 6
input_quantity: 102
planning_quantity: 18
allocated_planning_quantity: 18
unallocated_planning_quantity: 0
model_execution_performed: true
human_final_approval_status: PENDING
execution_performed: false
```

The exact economic allocation values in this historical RC example should not be presented as universal product performance.

---

## 3. Supporting Technical Evidence

### EVID-06 — Planner Contract and Quantity Conservation

Primary supporting path:

```text
reports/evidence/rescue_planner/
```

Useful evidence includes:

```text
planner_eval_001_030_summary.json
quantity_conservation_evidence.json
integration_001_solver_evidence.json
integration_001_rescue_decision_report.json
```

Supports:

- 30 planner evaluation cases;
- hard-constraint enforcement;
- quantity conservation;
- deterministic rerun behavior;
- allocation reconciliation.

`DAY2_RESCUE_PLANNER_EVIDENCE.md` is useful as development chronology but is not the preferred final source for numeric business-value claims because later release-candidate and final-test evidence supersedes it.

---

### EVID-07 — Triage Acceptance

Use the acceptance tests and release-candidate verification for:

```text
TRIAGE-001 ... TRIAGE-008
```

Supports:

- protection of healthy stock;
- monitor routing;
- surplus quantity isolation;
- expired routing;
- review-required routing;
- deterministic policy behavior.

For proposal language, prefer describing the behavior rather than dumping eight case IDs into the main narrative. Humanity has survived this long without reading every fixture name in a pitch deck.

---

### EVID-08 — Evaluation Visualizations

Directory:

```text
reports/figures/notebook_visualizations/
```

Use only a small curated subset for proposal / video. Recommended figure categories:

1. final-test PR-AUC comparison;
2. final-test Brier / calibration evidence;
3. ranking-quality comparison;
4. allocation-regret or oracle-value-retained comparison;
5. reliability / calibration plot when explaining probability limitations.

Do not place the entire visualization directory into the proposal. Evidence abundance is not the same thing as communication quality, a discovery mankind continues making the hard way.

---

## 4. Development-History Evidence — Do Not Use as Primary Final Claims

Examples:

```text
reports/evidence/rescue_planner/DAY2_RESCUE_PLANNER_EVIDENCE.md
reports/evidence/release/ISSUE_3_CLOSURE.md
reports/evidence/release/ISSUE_4_CLOSURE.md
reports/evidence/notebook_text_evidence/
```

These are valuable for:

- proof-of-work chronology;
- showing how requirements were tested and hardened;
- reconstructing implementation decisions;
- demonstrating that evaluation preceded final polishing.

They should not override later frozen / final evidence when the values differ.

---

## 5. Claim-to-Evidence Map

Evidence classes:

* `PROVEN_BY_REPO` — directly supported by implemented runtime behavior, committed contracts, tests, or reproducibility evidence.
* `SUPPORTED_BY_SYNTHETIC_EVAL` — supported by the frozen synthetic benchmark or evaluation protocol, not by real-world field validation.
* `DESIGN_INTENT_ONLY` — describes the intended mechanism or potential outcome but is not established as observed real-world impact.
* `DO_NOT_CLAIM` — unsupported or explicitly contradicted by the current implementation/evidence boundary.
* `PENDING_G10` — may only be promoted after the final release audit is executed on the exact frozen submission commit.

| Submission claim | Canonical evidence | Evidence class | Boundary |
| --- | --- | --- | --- |
| System processes one XLSX into one advisory Rescue Decision Report | `TECHNICAL_MVP_RC_VERIFICATION.md` + example report + current production pipeline | `PROVEN_BY_REPO` | Supported |
| Deterministic triage protects non-surplus inventory before rescue planning | RC verification + TRIAGE acceptance tests + production triage pipeline | `PROVEN_BY_REPO` | Supported |
| Only planning quantity enters rescue planning | triage contract + production pipeline + planner integration evidence | `PROVEN_BY_REPO` | Supported |
| Deterministic hard gates execute before model scoring | production pipeline + hard-gate implementation + regression tests | `PROVEN_BY_REPO` | Supported |
| HGB-E is the selected production rescue-success model | `configs/selected_model_v1.yaml` + selected-model manifest + runtime scoring configuration | `PROVEN_BY_REPO` | Supported |
| HGB-E was frozen before locked final-test access | model-selection decision + selected-model manifest | `SUPPORTED_BY_SYNTHETIC_EVAL` | Supported |
| HGB-E provides measurable value over B1 on the frozen benchmark | AI Value Gate + robustness evidence + final locked test | `SUPPORTED_BY_SYNTHETIC_EVAL` | Supported only for synthetic benchmark |
| Final locked synthetic-test HGB-E PR-AUC is approximately 0.874 | `FINAL_LOCKED_TEST_v1.json` | `SUPPORTED_BY_SYNTHETIC_EVAL` | Supported only for synthetic benchmark |
| Group leakage between train, validation, and test is zero in the registered split | `SPLIT_MANIFEST_v2.json` | `SUPPORTED_BY_SYNTHETIC_EVAL` | Supported |
| Global planner preserves planning-quantity and applicable hard constraints in recorded evaluation evidence | planner evidence + integration evidence + final locked test | `PROVEN_BY_REPO` | Supported for recorded repository evidence |
| Hard-constraint violations are zero in the locked synthetic evaluation evidence | `FINAL_LOCKED_TEST_v1.json` + planner evidence | `SUPPORTED_BY_SYNTHETIC_EVAL` | Supported for recorded evaluation |
| Partner Demand Registry is integrated into runtime external-partner matching | current runtime implementation + `partner_registry_demo_v1.yaml` | `PROVEN_BY_REPO` | Static synthetic demo fixture only |
| Partner Demand Registry represents verified live partner commitments | none | `DO_NOT_CLAIM` | Unsupported |
| Rescue-success score is a field-validated real-world probability | none | `DO_NOT_CLAIM` | Unsupported |
| Optimizer empirically outperforms greedy or another optimizer | no completed optimizer-comparison benchmark | `DO_NOT_CLAIM` | Unsupported |
| System automatically executes physical rescue actions | report contract explicitly prohibits automatic execution | `DO_NOT_CLAIM` | Contradicted by current governance boundary |
| Afterlife AI is designed to reduce avoidable waste by improving rescue decisions | problem brief + PRD + implemented decision mechanism | `DESIGN_INTENT_ONLY` | Intended outcome; real-world reduction not validated |
| Afterlife AI may create business or environmental value through rescued inventory | problem brief + PRD + decision mechanism | `DESIGN_INTENT_ONLY` | Potential impact only |
| Real-world merchant adoption, willingness-to-pay, or operational savings are established | none | `DO_NOT_CLAIM` | Not validated |
| Final submission reproducibility is verified on the frozen final commit | final release audit evidence | `PENDING_G10` | Not yet established |
| Hard-gate bypass prevention is enforced | production pipeline + hard-gate regression tests + fallback semantics | `PROVEN_BY_REPO` | Model and fallback paths cannot revive candidates blocked by deterministic hard gates |
| Deterministic scoring and optimizer fallback are implemented | fallback implementation + regression tests + architecture/runtime evidence | `PROVEN_BY_REPO` | Fallback preserves applicable deterministic constraints |
| Local and Docker reproducibility have historical repository evidence | Technical MVP RC clean-clone + Docker verification evidence | `PROVEN_BY_REPO` | Historical RC checkpoint; final frozen-commit verification remains `PENDING_G10` |
| Training and evaluation evidence uses synthetic data | synthetic dataset manifest + benchmark freeze + final locked test | `SUPPORTED_BY_SYNTHETIC_EVAL` | Must not be presented as real merchant transaction or field-validation evidence |
| Human review and approval remain outside automatic execution | report contract + runtime behavior + UI/report evidence | `PROVEN_BY_REPO` | Advisory decision-support only |


---

## 6. Evidence to Capture During Final Release Audit

These should be generated only after all submission-polish changes are frozen:

```text
reports/evidence/submission_final/
├── FINAL_PYTEST.txt
├── FINAL_RUFF.txt
├── FINAL_MYPY.txt
├── FINAL_CLEAN_CLONE.md
├── FINAL_DOCKER_SMOKE.md
├── FINAL_DEMO_REPORT.json
├── FINAL_UI_SMOKE.md
└── FINAL_REPOSITORY_STATE.txt
```

The final audit should record the exact final commit SHA. Until that capture exists, older RC verification remains historical technical evidence rather than proof of the final submission tree.

---

## 7. Recommended Submission Evidence Set

For judges, proposal, and video, surface **five things**, not the entire archaeological dig:

```text
1. ARCH-02 simplified system overview
2. one real Technical MVP Rescue Decision Report screenshot / JSON excerpt
3. HGB-E vs B1 final-test performance figure
4. grouped-split / no-leakage statement
5. final clean-clone + test + Docker verification summary
```

Everything else remains available in the repository as supporting proof.

---

## 8. Final G4 Decision

```yaml
evidence_inventory: CURATED
canonical_model_evidence: IDENTIFIED
canonical_dataset_evidence: IDENTIFIED
canonical_runtime_evidence: IDENTIFIED
historical_evidence_separated: true
unsupported_claims_flagged: true
final_submission_capture: PENDING_G10_RELEASE_AUDIT
```

G4 is complete when this index is placed under `reports/evidence/` and the final release audit remains explicitly pending rather than silently borrowing numbers from an older checkpoint.
