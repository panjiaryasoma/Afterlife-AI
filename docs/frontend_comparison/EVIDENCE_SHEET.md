# Frontend Comparison Evidence

## Comparison Run

```yaml
fixture: tests/fixtures/integration_001/RAW_INVENTORY_FIXTURE.xlsx
optimization_objective: MAXIMIZE_RECOVERY_VALUE
max_logistics_budget: 50000
minimum_expected_rescue_ratio: null
deadline_timezone: Asia/Jakarta
```

---

## Canonical Parity Evidence

FastAPI + Jinja2 dan Streamlit sama-sama bergantung pada canonical production pipeline dan tidak memiliki salinan business logic untuk validation, triage, planning, scoring, optimization, atau report construction.

API endpoint memiliki parity test terhadap `run_production_pipeline()`. Streamlit adapter juga memiliki parity coverage terhadap canonical production pipeline.

Observed regression state pada comparison run:

```text
targeted frontend/API parity tests: PASS
ruff: PASS
mypy: PASS
full pytest suite: 359 passed
```

---

## Functional Evidence

### Streamlit

Observed:

- menerima satu XLSX;
- menolak missing upload;
- menolak empty XLSX;
- menolak corrupt XLSX;
- menampilkan missing-schema validation error;
- mengaktifkan minimum expected rescue ratio hanya untuk BALANCED;
- menampilkan triage summary;
- menampilkan selected rescue allocations;
- menampilkan manual-review items;
- menampilkan warnings/limitations;
- menampilkan execution boundary;
- menampilkan scoring and technical provenance;
- menyediakan downloadable canonical Rescue Decision Report.

### FastAPI + Jinja2

Observed:

- menerima satu XLSX;
- menyediakan decision context;
- menampilkan rescue summary;
- menampilkan selected rescue allocations;
- menampilkan alternatives;
- menampilkan human review;
- menampilkan evidence/provenance;
- menampilkan limitations/advisory boundary;
- menyediakan downloadable JSON report;
- custom presentation lebih terstruktur dan competition-facing.

---

## Observed Defect

### FastAPI + Jinja2 invalid-schema path

Pada manual invalid-schema smoke test, browser menampilkan client-side JSON parsing error:

```text
Unexpected token 'I', "Internal S"... is not valid JSON
```

Sementara Streamlit menampilkan domain validation message yang lebih berguna:

```text
Inventory tidak valid: Kolom wajib tidak ditemukan: lot_id
```

Ini dicatat sebagai presentation/runtime robustness defect pada baseline. Defect ini tidak mengubah canonical core decision logic, tetapi harus dibereskan sebelum submission/demo freeze karena validation error merupakan bagian eksplisit dari presentation-layer contract.

Root cause belum dianggap terbukti hanya dari browser evidence. Current frontend JavaScript memanggil `response.json()` sebelum memeriksa `response.ok`, sehingga non-JSON 500 response akan berubah menjadi parsing error. Backend cleanup/error path juga perlu diuji agar canonical 4xx validation response tidak tertutup exception lain.

---

## Score Matrix

| Dimension | FastAPI + Jinja2 | Streamlit | Winner | Evidence-based note |
|---|---:|---:|---|---|
| Development effort | 3 | 5 | Streamlit | Widget bawaan dan presentation code yang lebih sedikit mempercepat challenger. |
| Demo clarity | 5 | 3 | FastAPI + Jinja2 | Flow 01-07 dan hierarchy lebih kuat untuk menjelaskan cerita produk. |
| Operator usability | 5 | 3 | FastAPI + Jinja2 | Workflow, labels, alternatives, review, provenance, dan limitations lebih eksplisit. |
| UI flexibility | 5 | 2 | FastAPI + Jinja2 | HTML/CSS/JS memberi kontrol penuh atas layout, states, responsive behavior, dan visual identity. |
| Runtime stability | 3 | 4 | Streamlit | Happy path keduanya berjalan; baseline masih memiliki observed invalid-schema failure path. |
| Startup/setup complexity | 3 | 5 | Streamlit | Satu Streamlit process lebih sederhana untuk demo lokal. |
| Docker/reproducibility | 5 | 4 | FastAPI + Jinja2 | HTTP/server contract lebih eksplisit dan conventional untuk packaging. |
| Testability | 5 | 4 | FastAPI + Jinja2 | TestClient + API contract memberi coverage yang lebih langsung; Streamlit AppTest tetap memadai. |
| Maintenance burden | 3 | 5 | Streamlit | Thin Streamlit surface lebih kecil; custom Jinja/CSS/JS butuh maintenance lebih besar. |
| Competition presentation quality | 5 | 3 | FastAPI + Jinja2 | Custom visual hierarchy dan narrative framing jauh lebih kuat untuk judging/demo. |

### Total

```text
FASTAPI_JINJA2 = 42 / 50
STREAMLIT      = 38 / 50
```

### Dimension wins

```text
FASTAPI_JINJA2 : 6
STREAMLIT      : 4
TIES           : 0
```

---

## Invariant Check

- [x] FastAPI + Jinja2 tetap baseline selama decision belum dibuat.
- [x] Streamlit bukan source of truth domain logic.
- [x] Safety dan feasibility tetap deterministic.
- [x] Model scoring tetap setelah hard gates.
- [x] Quantity conservation tetap berlaku.
- [x] Tidak ada database baru.
- [x] Tidak ada auth baru.
- [x] Tidak ada server-side history baru.
- [x] Tidak ada model retraining untuk Streamlit.
- [x] Canonical report parity diberi automated coverage.

---

## Comparison Result

Secara engineering speed dan maintenance surface, Streamlit adalah challenger yang valid dan lebih ringan.

Namun untuk Technical MVP RC dan competition demo, FastAPI + Jinja2 unggul pada demo clarity, operator usability, UI flexibility, testability, Docker/reproducibility, dan competition presentation quality.

Streamlit tidak memberikan keuntungan yang cukup besar untuk membenarkan pergantian primary presentation layer.
