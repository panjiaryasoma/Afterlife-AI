# Frontend Selection Decision

## Decision

```yaml
decision: RETAIN_FASTAPI_JINJA2
primary_presentation_layer: FASTAPI_JINJA2
technical_mvp_rc: FASTAPI_JINJA2
streamlit_status: CHALLENGER_EVALUATED_NOT_SELECTED_AS_PRIMARY
decision_status: ACCEPTED
```

FastAPI + Jinja2 tetap menjadi primary presentation layer dan Technical MVP RC.

Streamlit dipertahankan sebagai thin challenger/fallback presentation layer, bukan source of truth dan bukan primary competition UI.

---

## Why

Streamlit terbukti berhasil melakukan hal yang ingin diuji: reuse canonical pipeline, tidak menyalin business logic, menampilkan canonical report secara lengkap, lebih cepat dibangun, lebih sederhana dijalankan, dan lebih ringan dipelihara.

Tetapi FastAPI + Jinja2 menghasilkan presentation layer yang lebih kuat untuk menjelaskan decision flow ke juri, mempertahankan visual hierarchy, menunjukkan hard gates, alternatives, human authority, provenance, dan limitations sebagai satu narrative, serta mempertahankan explicit HTTP/API contract.

Karena canonical output sudah parity, mengganti primary UI ke Streamlit sekarang hanya menukar presentation quality dengan implementation convenience tanpa keuntungan domain atau model.

---

## Resolved Presentation Fix

### RESOLVED: invalid-schema error presentation on FastAPI + Jinja2

Frontend selection review sebelumnya menemukan satu presentation blocker:

```text
Unexpected token 'I', "Internal S"... is not valid JSON
```

Blocker tersebut telah diselesaikan.

Verified behavior:

- invalid workbook/schema menghasilkan controlled 4xx response;
- valid XLSX dengan missing required schema column menghasilkan HTTP 422;
- frontend menampilkan validation message dari API;
- raw JSON parse error tidak lagi ditampilkan kepada operator;
- non-JSON error response ditangani secara aman;
- raw Internal Server Error tidak dibocorkan sebagai presentation message;
- temporary-file cleanup tidak menutupi original validation exception;
- canonical pipeline behavior tetap tidak berubah.

Implementation checkpoint:

```text
5dd0853 fix: harden FastAPI invalid input handling
```

Required regression behavior telah diverifikasi tanpa mengubah domain logic.

---

## Preserved Invariants

Presentation fix tidak mengubah:

- triage rules;
- safety dan feasibility gates;
- candidate generation;
- scoring behavior;
- optimizer behavior;
- model artifact;
- evaluation fixture;
- canonical report semantics.

Model tetap berada setelah deterministic hard gates dan frontend tetap hanya menjadi presentation layer.

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
invalid_schema_presentation_fix: RESOLVED
remaining_blockers_before_demo_freeze: NONE
```