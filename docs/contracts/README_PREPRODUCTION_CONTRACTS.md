# Afterlife AI — Preproduction Contracts v2.0

## Ringkasan

Paket ini adalah kontrak aktif untuk menutup preproduction.

Perubahan utama dari v1.1 hanya satu:

```text
SCHEMA-CR-001
```

Schema sekarang dapat merepresentasikan satu lot `SURPLUS_CANDIDATE` yang memiliki:

```text
planning quantity
+ review remainder
```

tanpa membiarkan review quantity bocor ke planner.

## Isi paket

```text
FEATURE_SCHEMA_FINAL_v2.0.yaml
SCHEMA_CHANGE_REQUEST_001.md
SCHEMA_FINALIZATION_DECISION_v2.0.md
SCHEMA_SUPERSESSION_NOTICE.md
SIMPLE_PRD_SCHEMA_ALIGNMENT_ADDENDUM_v1.0.md
BASELINE_CONTRACT_v1.0.md
TOOLCHAIN_DECISION_v1.0.md
PREPRODUCTION_GATE_SUMMARY.md
VALIDATION_REPORT.json
MANIFEST.json
```

## Hubungan versi

```text
FEATURE_SCHEMA_FINAL_v1.1.yaml
→ SUPERSEDED, tetap disimpan

FEATURE_SCHEMA_FINAL_v2.0.yaml
→ ACTIVE
```

Baseline dan toolchain tetap v1.0 karena tidak ada perubahan isi pada kedua kontrak tersebut.

## Batas penting

```text
review_quantity
≠ planner quantity

fixture_rescue_success_score
≠ trained model output

readiness gate prepared
≠ production automatically opened
```
