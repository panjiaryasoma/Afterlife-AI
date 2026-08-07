# Afterlife AI — Expected Rescue Decision Report

**Integration:** `INTEGRATION-001`  
**Version:** `1.0`  
**Status:** `LOCKED_EXPECTED_ACCEPTANCE_OUTPUT`  
**Source type:** `SYNTHETIC_ACCEPTANCE_FIXTURE`  
**Automatic execution:** `NOT ALLOWED`  
**Human approval:** `REQUIRED`

## Executive Summary

Satu file inventori berisi enam lot dan total 102 unit telah dievaluasi.

```yaml
input_lots: 6
input_quantity: 102
protected_quantity: 30
monitor_quantity: 10
planning_quantity: 18
expired_quantity: 12
review_quantity: 32
allocated_planning_quantity: 18
unallocated_planning_quantity: 0
```

Hanya 18 sachet yang masuk Rescue Planner. Sebanyak 84 unit lain tetap dilindungi, dipantau, diblokir, atau ditahan untuk review.

## Selected Rescue Plan

| Source lot | Action | Quantity | Fixture acceptance score | Expected value |
|---|---|---:|---:|---:|
| `LOT-003` | Internal repurpose | 6 | 0.86 | Rp12.384 |
| `LOT-003` | Bundle | 4 | 0.80 | Rp5.120 |
| `LOT-006` | Local discount | 8 | 0.76 | Rp9.120 |
| **Total** |  | **18** |  | **Rp26.624** |

Expected rescued quantity berdasarkan fixture acceptance score:

```text
6 × 0,86 + 4 × 0,80 + 8 × 0,76 = 14,44 unit
```

Angka 14,44 adalah expectation matematis, bukan quantity fisik yang dieksekusi.

## Why These Actions Were Selected

### LOT-003

Enam sachet mangga dialokasikan ke internal repurpose karena kandidat tersebut memiliki expected value per unit tertinggi dan kapasitas repurpose batch tersedia enam unit.

Empat sachet sisanya dialokasikan ke bundle karena hanya empat companion units yang dapat digunakan tanpa mengambil stok yang telah direservasi.

Local discount tetap feasible, tetapi tidak dipilih karena expected value-nya lebih rendah.

### LOT-006

Delapan sachet melon dialokasikan ke local discount.

Internal repurpose sebenarnya feasible, tetapi shared repurpose capacity sudah digunakan oleh kandidat mangga yang memiliki expected value per unit lebih tinggi.

Promotional bonus ditolak sebelum scoring karena tidak ada qualifying transaction.

## Material Alternatives

| Candidate | Result | Explanation |
|---|---|---|
| `CAND-003-DISCOUNT` | Feasible, not selected | Expected value lebih rendah dari repurpose dan bundle |
| `CAND-006-REPURPOSE` | Feasible, not selected | Shared repurpose capacity telah digunakan |
| `CAND-006-BONUS` | Rejected | `NO_QUALIFYING_TRANSACTION` |

## Lots Excluded From Rescue Planner

| Lot or portion | Quantity | Treatment |
|---|---:|---|
| `LOT-001` | 15 | Protected normal stock |
| `LOT-002` | 10 | Continue normal sales and monitor |
| `LOT-003` protected portion | 15 | Excluded from planner |
| `LOT-004` | 12 | Blocked from consumption route |
| `LOT-005` | 20 | Hold for cold-chain evidence review |
| `LOT-006` remainder | 12 | Hold for demand-evidence review |

## Human Review Items

```yaml
LOT-005:
  quantity: 20
  reason: CRITICAL_STORAGE_EVIDENCE_MISSING

LOT-006_REMAINDER:
  quantity: 12
  reason: SALES_EVIDENCE_MISSING_FOR_UNDECLARED_REMAINDER
```

## Audit and Configuration

```yaml
input_snapshot: RAW_INVENTORY_FIXTURE.xlsx
ruleset: integration-001-fixture-rules-v1.0
capability_snapshot: BCP-STORE-01-INTEGRATION-001
partner_registry_snapshot: PDR-INTEGRATION-001-EMPTY-MATCH
optimization_objective: BALANCED
deterministic_configuration: STATIC_FIXTURE_NO_RANDOMNESS
trained_model_used: false
optimizer_production_used: false
```

## Limitations and Claim Boundary

- Seluruh capability, capacity, demand, score, biaya, dan recovery merupakan parameter sintetis.
- Fixture acceptance score bukan probabilitas keberhasilan lapangan yang telah divalidasi.
- Tidak ada external partner yang diklaim tersedia.
- Final handling untuk expired stock masih mengikuti deterministic compliance policy.
- `LOT-005` tidak boleh dianggap safe atau unsafe sebelum evidence selesai.
- `SCHEMA-CR-001` masih harus diterapkan saat final schema packaging.
- Rekomendasi adalah rencana. Tidak ada transaksi, repurpose, bundle, discount, return, donation, atau disposal yang dieksekusi otomatis.

## Approval State

```yaml
final_plan_approval_required: true
automatic_execution_allowed: false
approval_status: PENDING_DECISION_OWNER_REVIEW
```
