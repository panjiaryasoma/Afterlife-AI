# AFTERLIFE AI — SCHEMA CHANGE REQUEST 001

**ID:** `SCHEMA-CR-001`  
**Status:** `APPROVED_AND_APPLIED`  
**Requested version:** `2.0.0`  
**Date:** 5 Agustus 2026  
**Supersedes invariant from:** `FEATURE_SCHEMA_FINAL_v1.1.yaml`

## 1. Problem

Schema v1.1 memiliki invariant:

```text
review_quantity > 0 only when inventory_status == NEEDS_REVIEW
```

Invariant tersebut benar untuk lot yang seluruh quantity-nya ditahan, tetapi menolak mixed routing yang telah dikunci pada `TRIAGE-008` dan `LOT-006`.

Kasus valid:

```yaml
inventory_status: SURPLUS_CANDIDATE
current_quantity: 20
planning_quantity: 8
review_quantity: 12
```

Delapan unit memiliki user-declared surplus yang valid dan boleh masuk planner. Dua belas unit sisanya tidak memiliki sales evidence yang cukup dan harus tetap ditahan untuk review.

## 2. Approved change

Invariant baru:

```text
review_quantity > 0 only when inventory_status in
{NEEDS_REVIEW, SURPLUS_CANDIDATE}
```

Proteksi tambahan:

```text
review_quantity never emits SURPLUS_PLANNING_LOT
review_quantity never enters candidate generation
review_quantity never receives model or fixture scoring
review_quantity never enters allocation
```

Untuk mixed-routing `SURPLUS_CANDIDATE`, hanya `planning_quantity` yang boleh diteruskan.

## 3. Why this is a major version

Validator v1.1 akan menolak state yang sekarang dinyatakan valid. Perubahan ini mengubah accepted state space dan perilaku implementasi validator. Sesuai versioning policy schema, perubahan tersebut diklasifikasikan sebagai breaking change dan menaikkan major version menjadi `2.0.0`.

## 4. Impact

| Area | Impact |
|---|---|
| Raw inventory columns | Tidak berubah |
| Inventory statuses | Tidak berubah |
| Quantity buckets | Tidak berubah |
| Planner boundary | Diperketat |
| Model feature boundary | Tidak berubah |
| Optimizer input | Tidak berubah |
| Report | Harus menampilkan planning dan review remainder secara terpisah |
| Existing v1.1 package | Tetap disimpan sebagai immutable historical artifact |

## 5. Non-goals

Change request ini tidak:

- menambah action baru;
- mengubah formula calculated surplus;
- mengubah policy category;
- mengizinkan review quantity diproses secara optimistis;
- membuktikan partner, model probability, atau capability dunia nyata;
- membuka production secara otomatis.

## 6. Acceptance evidence

```text
TRIAGE-008
LOT-006 declared partial surplus
EXPECTED_TRIAGE_OUTPUT.yaml
INTEGRATION-001.md
quantity invariant: 0 + 0 + 8 + 0 + 12 = 20
planner receives exactly 8 units
review retains exactly 12 units
```

## 7. Decision

```yaml
change_request: SCHEMA-CR-001
decision: APPROVED
applied_to: FEATURE_SCHEMA_FINAL_v2.0.yaml
old_schema_status: SUPERSEDED
old_package_overwritten: false
```
