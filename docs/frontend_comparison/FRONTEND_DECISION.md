# Frontend Selection Decision

## Decision

```yaml
decision: RETAIN_FASTAPI_JINJA2
primary_presentation_layer: FASTAPI_JINJA2
technical_mvp_rc: FASTAPI_JINJA2
streamlit_status: CHALLENGER_EVALUATED_NOT_SELECTED_AS_PRIMARY
decision_status: ACCEPTED_WITH_ONE_PRESENTATION_FIX_REQUIRED
```

FastAPI + Jinja2 tetap menjadi primary presentation layer dan Technical MVP RC.

Streamlit dipertahankan sebagai thin challenger/fallback presentation layer, bukan source of truth dan bukan primary competition UI.

---

## Why

Streamlit terbukti berhasil melakukan hal yang ingin diuji: reuse canonical pipeline, tidak menyalin business logic, menampilkan canonical report secara lengkap, lebih cepat dibangun, lebih sederhana dijalankan, dan lebih ringan dipelihara.

Tetapi FastAPI + Jinja2 menghasilkan presentation layer yang lebih kuat untuk menjelaskan decision flow ke juri, mempertahankan visual hierarchy, menunjukkan hard gates, alternatives, human authority, provenance, dan limitations sebagai satu narrative, serta mempertahankan explicit HTTP/API contract.

Karena canonical output sudah parity, mengganti primary UI ke Streamlit sekarang hanya menukar presentation quality dengan implementation convenience tanpa keuntungan domain atau model.

---

## Required Fix Before Demo Freeze

### MUST_FIX: invalid-schema error presentation on FastAPI + Jinja2

Observed manual failure:

```text
Unexpected token 'I', "Internal S"... is not valid JSON
```

Expected behavior:

- invalid workbook/schema menghasilkan controlled 4xx response;
- frontend menampilkan validation message dari API;
- tidak ada raw JSON parse error;
- tidak ada raw Internal Server Error yang bocor ke operator.

### Required regression coverage

Tambahkan/pertahankan test yang membuktikan:

1. `/api/analyze` dengan valid XLSX tetapi missing required column mengembalikan 422 JSON.
2. Jinja frontend error handler tetap menampilkan useful message ketika response bukan JSON.
3. Temp-file cleanup tidak boleh menutupi original validation exception.
4. Existing canonical parity tetap PASS.

---

## No Changes Allowed for This Fix

Fix tidak boleh mengubah triage rules, safety/feasibility gates, candidate generation, scoring, optimizer, model artifact, atau fixture hanya agar test menjadi hijau.

---

## Final Checklist

### Streamlit Adapter

- [x] Thin Streamlit presentation layer
- [x] Reuse canonical application pipeline
- [x] Reuse validation, triage, planner, scoring, optimizer, reporting
- [x] One XLSX input
- [x] Validation errors
- [x] Triage summary
- [x] Selected rescue allocations
- [x] Warnings and manual-review items
- [x] Scoring provenance
- [x] Downloadable Rescue Decision Report

### Fair Comparison

- [x] Same fixture
- [x] Same core pipeline
- [x] Same model artifact/configuration
- [x] Canonical output parity
- [x] Framework-only differences recorded

### Comparison Dimensions

- [x] Development effort
- [x] Demo clarity
- [x] Operator usability
- [x] UI flexibility
- [x] Runtime stability
- [x] Startup/setup complexity
- [x] Docker/reproducibility
- [x] Testability
- [x] Maintenance burden
- [x] Competition presentation quality

### Invariants

- [x] Safety/feasibility deterministic
- [x] Model remains after hard gates
- [x] Quantity conservation preserved
- [x] No new database
- [x] No new auth
- [x] No new server-side history
- [x] No Streamlit-specific retraining

---

## Exit State

```yaml
frontend_comparison: COMPLETE
winner: FASTAPI_JINJA2
streamlit_challenger: VALID_BUT_NOT_SELECTED
canonical_pipeline: UNCHANGED
remaining_blocker_before_demo_freeze:
  - FASTAPI_JINJA2_INVALID_SCHEMA_ERROR_PRESENTATION
```
