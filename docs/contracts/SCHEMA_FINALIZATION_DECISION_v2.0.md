# AFTERLIFE AI — SCHEMA FINALIZATION DECISION

**Version:** 2.0  
**Status:** `LOCKED_FOR_PREPRODUCTION_FINAL`  
**Date:** 5 Agustus 2026  
**Supersedes:** `FEATURE_SCHEMA_FINAL_v1.1.yaml`  
**Applied change request:** `SCHEMA-CR-001`

## 1. Decision

`FEATURE_SCHEMA_FINAL_v2.0.yaml` menjadi schema aktif untuk penutupan preproduction dan implementasi berikutnya.

Schema v1.1 tetap disimpan sebagai historical artifact dan tidak ditimpa.

## 2. Reason for v2.0

Schema v1.1 tidak dapat merepresentasikan mixed routing pada declared partial surplus:

```text
sebagian quantity → planner
sebagian quantity → review
```

Schema v2.0 memperbolehkan `review_quantity` pada `SURPLUS_CANDIDATE` tanpa memperlemah planner boundary.

## 3. Locked quantity semantics

```text
protected_normal_stock_quantity
+ monitor_quantity
+ planning_quantity
+ expired_quantity
+ review_quantity
= current_quantity
```

`planning_quantity` adalah satu-satunya quantity yang boleh menghasilkan `SURPLUS_PLANNING_LOT`.

`review_quantity` selalu berada di luar planner, candidate generation, scoring, dan allocation.

## 4. Entity flow

```text
ANALYSIS_REQUEST
+ INVENTORY_LOT
        ↓
INVENTORY_TRIAGE_RESULT
        ↓ only planning_quantity from SURPLUS_CANDIDATE
SURPLUS_PLANNING_LOT
        ↓
CANDIDATE_ACTION
        ↓ deterministic gates
fixture_rescue_success_score or estimated_rescue_success_score
        ↓
ALLOCATION_DECISION
        ↓
DECISION_REPORT
```

## 5. Acceptance status

```yaml
schema_parse: PASS
triage_suite: COMPLETE
integration_001: COMPLETE
quantity_invariants: PASS
mixed_routing_support: PASS
model_feature_boundary: LOCKED
optimizer_io_boundary: LOCKED
human_approval_boundary: LOCKED
```

## 6. Remaining debt

Remaining debt does not change schema structure:

- malformed-input acceptance execution;
- category policy field validation;
- real business capability validation;
- real partner-demand validation;
- trained model and optimizer benchmark;
- report usability test.

These items must remain explicit limitations and may not be converted into optimistic defaults.
