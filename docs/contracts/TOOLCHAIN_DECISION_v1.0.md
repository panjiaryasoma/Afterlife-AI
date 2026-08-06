# AFTERLIFE AI — TOOLCHAIN DECISION

**Version:** 1.0  
**Status:** Locked for MVP Implementation  
**Date:** 3 Agustus 2026  
**Architecture:** One synchronous local web application, one model, no database

## 1. Decision summary

```yaml
language: Python 3.12.x
project_manager: uv + pyproject.toml + uv.lock
backend_api: FastAPI
validation: Pydantic v2
server: Uvicorn
frontend: Jinja2 + HTML + CSS + vanilla JavaScript
spreadsheet: pandas + openpyxl
configuration: PyYAML + Pydantic validation
modeling: scikit-learn
model_candidates:
  - LogisticRegression
  - HistGradientBoostingClassifier
calibration: CalibratedClassifierCV when validation gate passes
optimizer: Google OR-Tools CP-SAT
testing: pytest
quality: Ruff
containerization: Docker + Docker Compose v2
persistence: bundled trusted model artifact + manifest; no database
runtime_internet: none
```

## 2. Why this stack

### 2.1 Python 3.12

Python 3.12 dipilih sebagai runtime freeze untuk menjaga kompatibilitas library dan mengurangi risiko perubahan mayor selama kompetisi. `requires-python` dikunci:

```toml
requires-python = ">=3.12,<3.13"
```

Tim tidak mengejar runtime Python terbaru hanya karena angka versinya lebih besar. MVP membutuhkan stabilitas, bukan koleksi release notes.

### 2.2 FastAPI + Pydantic

FastAPI dipilih karena request utama adalah multipart upload yang berisi satu file dan beberapa form fields, sementara seluruh domain contract sudah dirancang sebagai typed schema. FastAPI memberi kontrak API, validation integration, dan OpenAPI documentation tanpa membuat layer manual tambahan.

Endpoint P0:

```text
GET  /health
GET  /
POST /api/analyze
```

`POST /api/analyze` menerima:

```text
inventory_file
optimization_objective
max_logistics_budget
rescue_deadline_at
minimum_expected_rescue_ratio
```

Pydantic v2 menjadi single source untuk:

- request context;
- row validation;
- static artifact validation;
- candidate and report objects;
- generated JSON Schema.

### 2.3 Jinja2 + vanilla JavaScript

Frontend tidak memakai React, Next.js, atau separate Node build. Jinja2 dipilih untuk satu UI flow:

1. upload Excel;
2. pilih objective dan context;
3. submit;
4. tampilkan report.

Vanilla JavaScript hanya dipakai untuk form behavior, loading state, file feedback, dan report interaction ringan. Tidak ada CDN dependency karena runtime internet harus nol.

### 2.4 pandas + openpyxl

`pandas.read_excel` menangani parsing sheet `inventory_lots`, sedangkan `openpyxl` menjadi engine `.xlsx`. DataFrame dipakai hanya pada boundary tabular dan feature preparation. Domain logic tidak diletakkan sebagai serangkaian operasi DataFrame tanpa tipe; setelah parsing, rows diubah menjadi Pydantic domain objects.

### 2.5 scikit-learn

scikit-learn cukup untuk:

- preprocessing pipeline;
- Logistic Regression baseline;
- HistGradientBoosting candidate;
- probability calibration;
- model evaluation;
- model persistence.

Tidak memakai pretrained model, LLM API, LightGBM, atau XGBoost pada MVP. Menambah dependency model baru hanya diperbolehkan bila baseline contract menunjukkan kebutuhan nyata.

Canonical training pipeline:

```text
raw candidate feature table
→ group split by scenario_group_id
→ ColumnTransformer
→ estimator
→ optional calibration on validation-only data
→ locked test evaluation
→ artifact + manifest
```

### 2.6 OR-Tools CP-SAT

Allocation memiliki discrete quantities, shared capacity, budget, minimum order, bundle ratios, storage limits, and objective variants. CP-SAT cocok untuk integer decision variables dan hard constraints.

Integer scaling policy:

```text
quantity units      → integer base units
money               → integer rupiah
probability         → basis points 0..10000
ratio coefficients  → scaled integers
```

Jika unit input bersifat pecahan seperti kilogram, category policy menentukan scaling factor sebelum optimization. Report mengembalikan nilai ke unit pengguna.

Solver configuration P0:

```text
max_time_in_seconds: 5
num_search_workers: 1
random_seed: request random_seed
```

Satu worker dipilih untuk determinism. Bila solver tidak memberi `OPTIMAL` dalam batas waktu tetapi memberi `FEASIBLE`, hasil dapat digunakan dengan warning. Bila `INFEASIBLE`, `MODEL_INVALID`, atau `UNKNOWN`, sistem memakai deterministic fallback planner dan melaporkan solver status.

### 2.7 uv and lockfile

Project memakai:

```text
pyproject.toml
uv.lock
```

Development:

```bash
uv sync
uv run pytest
uv run uvicorn app.main:app --reload
```

Container and judging:

```bash
uv sync --frozen --no-dev
```

Exact package versions berada di `uv.lock` dan wajib di-commit. Dependency upgrade tidak dilakukan otomatis menjelang deadline.

### 2.8 Docker Compose

MVP berjalan sebagai satu service:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
```

Command resmi:

```bash
docker compose up --build
```

Tidak ada database, queue, Redis, worker, atau second frontend container. `compose.yaml` tetap disediakan karena diwajibkan untuk reproducible local startup, walaupun satu service sebenarnya cukup hidup sendirian tanpa drama keluarga antarkontainer.

## 3. Model artifact policy

Runtime hanya boleh memuat model yang dibundel bersama repository release atau image.

Artifact set:

```text
artifacts/rescue_success_model.joblib
artifacts/model_manifest.json
artifacts/feature_contract.json
```

Manifest wajib menyimpan:

```text
model_version
schema_version
training_data_version
feature_list
feature_list_sha256
package_lock_sha256
model_sha256
training_timestamp
random_seed
selected_metrics
claim_boundary
```

Security rule:

- jangan memuat model file dari upload pengguna;
- hanya load artifact dengan hash yang cocok;
- artifact persistence dianggap trusted-local only;
- container memakai dependency versions yang sama dengan training environment.

Jika waktu memungkinkan, `skops.io` dapat dievaluasi setelah MVP karena lebih aman daripada pickle-based persistence. Ia bukan P0 karena menambah format dan compatibility work.

## 4. Repository layout

```text
afterlife-ai/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routes.py
│   │   └── dependencies.py
│   ├── schemas/
│   │   ├── request.py
│   │   ├── inventory.py
│   │   ├── triage.py
│   │   ├── partner.py
│   │   ├── candidate.py
│   │   ├── allocation.py
│   │   └── report.py
│   ├── services/
│   │   ├── workbook_reader.py
│   │   ├── validation_service.py
│   │   ├── triage_service.py
│   │   ├── enrichment_service.py
│   │   ├── candidate_generator.py
│   │   ├── gate_service.py
│   │   ├── scoring_service.py
│   │   ├── value_service.py
│   │   ├── optimizer_service.py
│   │   ├── fallback_service.py
│   │   └── report_service.py
│   ├── templates/
│   └── static/
├── config/
│   ├── business_capability.yaml
│   ├── partner_registry.yaml
│   ├── domain_rules.yaml
│   ├── category_policies.yaml
│   └── objective_policy.yaml
├── artifacts/
│   ├── rescue_success_model.joblib
│   ├── model_manifest.json
│   └── feature_contract.json
├── data/
│   ├── sample_input/
│   ├── synthetic/
│   └── processed/
├── evaluation/
│   ├── evaluation_spec.yaml
│   ├── triage_spec.yaml
│   └── integration_spec.yaml
├── scripts/
│   ├── generate_synthetic.py
│   ├── train.py
│   ├── evaluate.py
│   └── validate_artifacts.py
├── tests/
│   ├── fixtures/
│   ├── test_schema.py
│   ├── test_triage.py
│   ├── test_domain_rules.py
│   ├── test_optimizer.py
│   ├── test_acceptance_cases.py
│   ├── test_integration.py
│   └── test_invariants.py
├── reports/
├── compose.yaml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## 5. Runtime lifecycle

Pada startup:

```text
1. Validate schema version.
2. Load and validate capability profile.
3. Load and validate partner registry snapshot.
4. Load and validate domain rules and category policies.
5. Verify model and feature-contract hashes.
6. Load model exactly once.
7. Expose health status.
```

Pada request:

```text
1. Read file into memory/temp file with size limit.
2. Validate workbook and rows.
3. Build triage results.
4. Generate planning lots and candidates.
5. Apply deterministic gates.
6. Score feasible candidates only.
7. Calculate expected value components.
8. Optimize globally.
9. Build report.
10. Delete temporary upload.
```

## 6. Data and storage decision

No database.

- static artifacts disimpan sebagai versioned files;
- upload diproses sementara dan dihapus;
- report tidak dipersist secara otomatis;
- sample report dapat disimpan hanya sebagai repository fixture;
- tidak ada history page atau user account.

Ini mengikuti MVP boundary dan mengurangi risiko data pribadi atau inventori tertinggal pada mesin juri.

## 7. Testing stack

```text
pytest
pytest-cov
```

Required test layers:

- schema validation;
- TRIAGE-001–008;
- EVAL-001–030;
- INTEGRATION-001;
- quantity and capacity invariants;
- model scoring isolation;
- optimizer determinism;
- artifact hash validation;
- API happy path and invalid upload.

Ruff digunakan untuk lint dan formatting. Mypy tidak menjadi P0 karena Pydantic schema dan Ruff sudah memberi manfaat terbesar dengan setup lebih kecil. Ia dapat ditambahkan setelah seluruh acceptance tests hijau.

## 8. Rejected alternatives

| Alternative | Decision | Reason |
|---|---|---|
| Flask | Rejected for MVP | Bisa dipakai, tetapi typed request/schema/OpenAPI memerlukan wiring lebih manual dibanding FastAPI. |
| Streamlit | Rejected | Cepat untuk demo, tetapi mencampur UI dan decision engine serta membuat API contract kurang eksplisit. |
| React / Next.js | Rejected | Build chain dan separate frontend tidak memberi nilai untuk satu upload-report flow. |
| SQLite / PostgreSQL | Rejected | Tidak ada auth, history, atau dynamic registry update pada MVP. |
| Celery / Redis | Rejected | Request harus sinkron dan tidak ada background job. |
| PuLP / external CBC setup | Rejected | OR-Tools memberi solver dan integer constraint workflow yang lebih langsung untuk container lokal. |
| LightGBM / XGBoost | Deferred | Tidak diperlukan sebelum scikit-learn baselines diuji. |
| SHAP runtime explanations | Deferred | Structured reason codes dan rejected alternatives lebih selaras dengan keputusan sistem. |
| Cloud deployment | Deferred | Local Docker runtime adalah acceptance target. |

## 9. Dependency groups

Runtime dependencies:

```text
fastapi
uvicorn
pydantic
python-multipart
jinja2
pandas
openpyxl
numpy
scikit-learn
joblib
ortools
pyyaml
```

Development dependencies:

```text
pytest
pytest-cov
ruff
httpx
```

Exact versions diselesaikan dan dikunci oleh `uv.lock` pada repo initialization. Tidak ada dependency dengan unbounded direct URL atau floating Git branch.

## 10. Toolchain gate

```yaml
language_and_runtime: LOCKED
api_framework: LOCKED
schema_validation: LOCKED
frontend_strategy: LOCKED
spreadsheet_engine: LOCKED
modeling_library: LOCKED
optimizer: LOCKED
dependency_locking: LOCKED
containerization: LOCKED
database: EXPLICITLY_NONE
cloud_runtime: OUT_OF_SCOPE
final_model_algorithm: PENDING_BASELINE_BENCHMARK
exact_package_versions: PENDING_UV_LOCK_GENERATION
```
