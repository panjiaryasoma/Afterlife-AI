# Afterlife AI — README INTEGRATION-001

**Package:** `afterlife_ai_integration_001_v1.0`  
**Status:** `LOCKED_FOR_PREPRODUCTION`  
**Production:** `BLOCKED`

## 1. What this package is

Paket ini adalah terjemahan teknis dari satu dokumen manusia:

```text
INTEGRATION-001.md
```

Urutannya:

```text
RAW_INVENTORY_FIXTURE.xlsx
→ EXPECTED_TRIAGE_OUTPUT.yaml
→ PLANNING_LOTS_FIXTURE.yaml
→ capability + partner snapshot
→ EXPECTED_CANDIDATES.yaml
→ EXPECTED_GATE_RESULTS.yaml
→ EXPECTED_SCORES.yaml
→ EXPECTED_ALLOCATION.yaml
→ EXPECTED_RESCUE_DECISION_REPORT.md
```

File teknis tidak membuat keputusan baru. Mereka hanya memecah keputusan di `INTEGRATION-001.md` menjadi bentuk yang nanti mudah dijadikan fixture test.

## 2. Story in plain language

Dari 102 unit inventori:

```text
30 protected
10 monitor
12 expired
32 review
18 masuk planner
```

Delapan belas sachet yang masuk planner terdiri dari:

```text
10 sachet mangga
8 sachet melon
```

Planner menggunakan capability toko sintetis:

```text
repurpose bersama maksimal 6
bundle mangga maksimal 4
local discount tersedia
bonus memerlukan qualifying transaction
```

Pada snapshot ini tidak ada external partner yang aktif dan terverifikasi. Sistem tidak mengarang partner.

Hasil fixture:

```text
Mangga:
6 repurpose
4 bundle

Melon:
8 local discount
```

Promotional bonus ditolak karena qualifying transaction = 0.

## 3. File roles

### `INTEGRATION-001.md`

Single source of truth dalam bahasa manusia.

### `RAW_INVENTORY_FIXTURE.xlsx`

Data mentah enam lot. Ini adalah soal.

### `POLICY_FIXTURE.yaml`

Aturan triage untuk membaca raw inventory.

### `EXPECTED_TRIAGE_OUTPUT.yaml`

Kunci hasil raw inventory sampai planner boundary.

### `PLANNING_LOTS_FIXTURE.yaml`

Hanya dua planning lot dan total 18 unit yang boleh diterima planner.

### `BUSINESS_CAPABILITY_PROFILE_FIXTURE.yaml`

Menjelaskan apa yang mampu dilakukan toko pada fixture ini dan kapasitasnya.

### `PARTNER_DEMAND_REGISTRY_FIXTURE.yaml`

Menjelaskan bahwa tidak ada matching external partner aktif pada snapshot. Ini mencegah sistem mengarang penerima.

### `EXPECTED_CANDIDATES.yaml`

Daftar pilihan tindakan yang dibangkitkan. Candidate belum berarti keputusan final.

### `EXPECTED_GATE_RESULTS.yaml`

Menjelaskan kandidat mana yang feasible dan mana yang ditolak sebelum scoring.

### `EXPECTED_SCORES.yaml`

Score sintetis hanya untuk candidate feasible. Bukan output model terlatih.

### `EXPECTED_ALLOCATION.yaml`

Pembagian 18 unit secara global dengan shared capacity.

### `EXPECTED_RESCUE_DECISION_REPORT.md`

Contoh output yang akan dilihat decision owner.

### `INTEGRATION_CONSISTENCY_AUDIT.yaml`

Memeriksa quantity, gate, score, capacity, dan allocation. Status saat ini `PASS_WITH_DEBT`.

## 4. Important distinction

```text
FEASIBLE
≠ SELECTED

REJECTED
→ NO SCORE

FIXTURE SCORE
≠ REAL-WORLD PROBABILITY

RECOMMENDED
≠ EXECUTED
```

## 5. Current status

```yaml
integration_contract: LOCKED_FOR_PREPRODUCTION
technical_artifacts_generated: true
consistency_audit: SUPERSEDED_BY_FINAL_PREPRODUCTION_AUDIT
schema_cr_001: PENDING
preproduction_readiness_gate: BLOCKED
production: BLOCKED
```

## 6. What remains

```text
1. Review paket ini sebagai satu kesatuan.
2. Terapkan SCHEMA-CR-001.
3. Buat schema v2.0 package.
4. Tutup malformed-input validation debt atau dokumentasikan limitation.
5. Putuskan PREPRODUCTION_READINESS_GATE.
```
