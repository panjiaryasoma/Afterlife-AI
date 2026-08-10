# Afterlife AI

> AI-assisted rescue inventory planning for retail and F&B surplus.

Afterlife AI adalah decision-support system untuk memisahkan stok normal dari inventori yang perlu ditangani, mengevaluasi opsi rescue yang aman dan feasible, memberi rescue-success score pada kandidat yang lolos hard gate, lalu mengoptimalkan alokasi inventori menjadi satu Rescue Decision Report.

Sistem menerima satu file `.xlsx` dan menjalankan alur:

```text
Inventory XLSX
-> structural and semantic validation
-> deterministic inventory triage
-> surplus planning lots
-> candidate rescue actions
-> hard safety and feasibility gates
-> rescue-success scoring
-> expected-value calculation
-> global allocation optimization
-> Rescue Decision Report
```

Keputusan akhir tetap memerlukan human review. Sistem tidak mengeksekusi diskon, transfer, repurpose, disposal, atau tindakan fisik lainnya secara otomatis.

---

## Technical MVP Status

```yaml
phase: Production
development_mode: Local First
technical_mvp: Release Candidate Verification
submission_ready: false
```

Implemented:

- [x] Final repository structure
- [x] XLSX intake and validation
- [x] Deterministic inventory triage
- [x] Rescue planning-lot construction
- [x] Production candidate generation
- [x] Deterministic hard safety and feasibility gates
- [x] HGB-E production scoring provider
- [x] Deterministic scoring fallback
- [x] Expected-value calculation
- [x] Global CP-SAT allocation optimizer
- [x] Rescue Decision Report
- [x] FastAPI HTTP interface
- [x] Minimal Jinja2 web UI
- [x] JSON report download
- [x] Dockerfile and Docker Compose runtime
- [x] Full local regression suite
- [x] Container end-to-end verification
- [ ] Final clean-clone verification
- [ ] Technical MVP Release Candidate evidence package

---

## Problem

Retail dan F&B dapat memiliki inventori yang:

- bergerak lambat;
- berlebih;
- mendekati akhir masa jual;
- tidak sesuai dengan demand lokal;
- memiliki peluang recovery melalui tindakan alternatif.

File inventori juga dapat mencampurkan:

- stok sehat;
- stok yang perlu dimonitor;
- surplus parsial;
- barang near-expiry;
- barang expired;
- data tidak lengkap;
- kondisi yang tidak aman untuk diproses otomatis.

Keputusan rescue seperti discount, bundling, repurpose, transfer, donation, atau disposal perlu mempertimbangkan safety, feasibility, capacity, economics, dan timing secara konsisten.

---

## Solution Principles

1. Healthy stock harus dilindungi.
2. Safety dan feasibility ditentukan secara deterministik.
3. Model hanya boleh menilai kandidat yang telah lolos hard gate.
4. Model dan deterministic fallback tidak dapat menghidupkan kembali kandidat yang sudah `BLOCKED`.
5. Optimizer harus menjaga quantity dan shared-capacity constraints.
6. Sistem harus abstain atau meminta review ketika evidence tidak cukup.
7. Output bersifat advisory dan memerlukan human approval.

---

## Core Input

Technical MVP menerima satu workbook:

```text
.xlsx
```

Worksheet utama:

```text
inventory_lots
```

Workbook divalidasi sebelum masuk ke triage dan planning pipeline.

Reference fixture untuk development dan integration testing:

```text
tests/fixtures/integration_001/RAW_INVENTORY_FIXTURE.xlsx
```

Fixture tersebut adalah technical evaluation fixture, bukan data transaksi dunia nyata.

---

## Core Output

Satu `Rescue Decision Report` yang mencakup:

- request ID;
- analysis timestamp;
- input snapshot hash;
- feature schema version;
- ruleset version;
- capability snapshot version;
- optimization objective;
- scoring provenance;
- inventory batch metrics;
- selected allocations;
- rejected alternatives;
- manual-review items;
- allocated and unallocated planning quantity;
- expected economic value;
- fallback information;
- known limitations;
- final human approval status.

Report dapat diunduh dari UI sebagai JSON dengan nama berbasis `request_id`.

Report tidak disimpan secara permanen di server.

---

## Scoring

Selected production model:

```yaml
model_id: M1_HIST_GRADIENT_BOOSTING
algorithm: HistGradientBoostingClassifier
artifact: models/HGB_E_v1.joblib
feature_schema: docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml
```

Model hanya dipanggil setelah deterministic hard gates lulus.

Jika production model artifact tidak tersedia atau tidak dapat dimuat, scoring layer menggunakan deterministic neutral fallback:

```yaml
model_version: DETERMINISTIC_FALLBACK_V1
score: 0.50
```

Fallback tidak boleh:

- melewati hard safety gates;
- mengubah candidate `BLOCKED` menjadi `ALLOWED`;
- membuat klaim probabilitas dunia nyata.

---

## Rescue Actions

Domain contract mencakup action vocabulary:

1. `LOCAL_DISCOUNT`
2. `BUNDLE`
3. `PROMOTIONAL_BONUS`
4. `INTERNAL_REPURPOSE`
5. `INTERNAL_USE`
6. `RETURN_TO_SUPPLIER`
7. `BRANCH_TRANSFER`
8. `WHOLESALE`
9. `EXTERNAL_PARTNER`
10. `DONATION`
11. `SAFE_DISPOSAL`

Technical MVP runtime menggunakan static capability configuration dan hanya menghasilkan tindakan yang diaktifkan serta feasible pada runtime configuration aktif.

Tidak semua domain action wajib aktif pada satu demo configuration.

---

## Technical Architecture

```text
User / Browser
    |
    v
Web Interface
├── Jinja2
├── HTML / CSS / JavaScript
└── JSON Report Download
    |
    v
FastAPI Interface
├── GET /
├── GET /health
└── POST /api/analyze
    |
    v
Application Orchestration
└── run_production_pipeline()
    |
    v
Inventory Intake & Validation
├── workbook validation
├── worksheet validation
├── column validation
├── row / contract validation
└── canonical inventory records
    |
    v
Deterministic Triage
├── healthy-stock protection
├── monitor routing
├── surplus calculation
├── expired routing
└── needs-review routing
    |
    v
Rescue Planning
├── planning-lot construction
└── candidate generation
    |
    v
Deterministic Hard Gates
├── safety
├── verification
├── storage compatibility
├── timing
├── action eligibility
├── shelf-life
├── logistics
└── capability / coverage
    |
    v
Rescue-Success Scoring
├── HGB-E model provider
└── deterministic fallback 0.50
    |
    v
Expected-Value Calculation
    |
    v
Global Allocation Optimization
├── CP-SAT
├── quantity constraints
└── shared-capacity constraints
    |
    v
Rescue Decision Report
├── allocation
├── unallocated quantity
├── scoring provenance
├── review flags
├── limitations
└── human approval status
```

### Runtime Contracts and Configuration

The production pipeline is constrained by versioned runtime artifacts rather than ad-hoc values embedded in the HTTP or UI layer:

```text
Runtime Contracts & Configuration
├── configs/runtime_v1.yaml
├── docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml
├── docs/evaluation_source_v1.0/domain_rules_v1.0.yaml
├── docs/evaluation_source_v1.0/evaluation_spec_v1.0.yaml
├── models/HGB_E_v1.joblib
└── uv.lock
```

Application core berada di:

```text
src/afterlife_ai/
```

Production orchestration entry point berada di:

```text
src/afterlife_ai/pipeline/application.py
```

HTTP entry point berada di:

```text
backend/main.py
```

HTTP analysis route berada di:

```text
backend/api/routes.py
```

Frontend berada di:

```text
frontend/templates/
frontend/static/
```

---

## Technology Stack

```yaml
language: Python 3.12
package_manager: uv
api: FastAPI
server: Uvicorn
validation: Pydantic v2
spreadsheet:
  - openpyxl
  - pandas
machine_learning:
  - scikit-learn
optimization: OR-Tools CP-SAT
frontend:
  - Jinja2
  - HTML
  - CSS
  - vanilla JavaScript
testing: pytest
linting: Ruff
containerization:
  - Docker
  - Docker Compose
database: none
runtime_internet_dependency: none
```

---

## Repository Structure

```text
Afterlife-AI/
|-- backend/
|   |-- api/
|   `-- main.py
|
|-- frontend/
|   |-- static/
|   `-- templates/
|
|-- configs/
|-- data/
|-- docs/
|-- models/
|-- notebooks/
|-- reports/
|-- scripts/
|
|-- src/
|   `-- afterlife_ai/
|       |-- contracts/
|       |-- intake/
|       |-- pipeline/
|       |-- planner/
|       |-- scoring/
|       `-- triage/
|
|-- tests/
|   |-- acceptance/
|   |-- api/
|   |-- fixtures/
|   |-- integration/
|   `-- unit/
|
|-- Dockerfile
|-- compose.yaml
|-- pyproject.toml
|-- uv.lock
`-- README.md
```

---

## Local Installation

Requirements:

```text
Python 3.12
uv
```

Install locked dependencies:

```powershell
uv sync
```

Run the application locally:

```powershell
uv run uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## API

### `GET /`

Renders the minimal Jinja2 inventory-analysis interface.

### `GET /health`

Expected response:

```json
{
  "status": "ok",
  "service": "afterlife-ai"
}
```

### `POST /api/analyze`

Accepts multipart upload:

```text
inventory_file=<one .xlsx workbook>
```

Processing is synchronous.

A valid request returns one Rescue Decision Report.

Invalid behavior:

```text
wrong file extension -> HTTP 400
empty upload         -> HTTP 400
corrupt XLSX         -> HTTP 422
invalid workbook     -> HTTP 422 with validation detail
internal system bug  -> HTTP 500
```

Uploads are processed through a temporary file and deleted after the request completes.

---

## Docker Compose

Requirements:

```text
Docker Desktop or compatible Docker Engine
Docker Compose
```

Build and run:

```powershell
docker compose up --build
```

Or detached:

```powershell
docker compose up --build -d
```

Check service status:

```powershell
docker compose ps
```

Check health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Stop:

```powershell
docker compose down
```

Verified Technical MVP flow:

```text
Docker Compose
-> FastAPI health PASS
-> web UI PASS
-> XLSX upload PASS
-> HGB-E scoring PASS
-> optimization PASS
-> Rescue Decision Report PASS
-> JSON download PASS
```

---

## Testing

Run the complete suite:

```powershell
uv run pytest -q
```

Latest local Technical MVP regression:

```text
287 passed
0 failed
```

Run production lint scope:

```powershell
uv run ruff check src/afterlife_ai backend tests/unit tests/integration tests/acceptance tests/api
```

Latest result:

```text
All checks passed!
```

Important test coverage includes:

- workbook validation and malformed input;
- `TRIAGE-001` through `TRIAGE-008`;
- planner evaluation suite;
- `INTEGRATION-001`;
- production triage pipeline;
- production candidate generation;
- deterministic hard gates;
- model scoring;
- deterministic scoring fallback;
- fallback hard-gate preservation;
- expected-value calculation;
- shared-capacity optimization;
- quantity conservation;
- application end-to-end pipeline;
- API happy path;
- API invalid upload;
- web UI smoke test;
- JSON report download behavior.

Known third-party warnings currently include deprecation warnings emitted by the installed NumPy/joblib combination when loading the trained model artifact, plus a Starlette TestClient deprecation warning. These warnings do not currently cause regression-test failures.

---

## Runtime Boundary

```yaml
request_processing: synchronous
runtime_database: none
server_side_history: none
uploaded_file_persistence: temporary_only
report_persistence: user_download_only
runtime_internet: none
automatic_execution: none
```

The MVP does not provide:

- accounts;
- authentication;
- server-side report history;
- database persistence;
- background workers;
- cloud dependency;
- automatic outreach;
- automatic logistics execution.

---

## Model and Data Claim Boundary

Training and evaluation use synthetic data and technical evaluation fixtures.

Therefore:

- synthetic data is not real transaction data;
- model output is not a field-validated real-world probability;
- model score is used only for ranking/economic planning of gate-eligible candidates;
- the model does not determine safety;
- the model cannot bypass deterministic hard gates;
- static runtime capability and pricing parameters are not validated real-world operating thresholds;
- synthetic evaluation does not prove real-world business effectiveness;
- final decisions require human review.

---

## Known Limitations

Technical MVP limitations:

- training data remains synthetic;
- real-world probability calibration has not been validated;
- runtime capability, cost, capacity, and price parameters are static MVP defaults;
- business adoption and willingness-to-pay remain unvalidated;
- current Partner Demand Registry behavior is not a live marketplace;
- no authentication or multi-user isolation;
- no server-side history or database;
- no automatic action execution;
- no automatic retraining or online learning;
- runtime is designed for one synchronous analysis request;
- third-party NumPy/joblib deprecation warnings remain during model loading;
- UI is functional MVP styling, not final competition polish.

These limitations are disclosed intentionally and should not be interpreted as validated real-world capabilities.

---

## Non-Goals

Technical MVP intentionally excludes:

- authentication;
- user accounts;
- distributed database;
- background jobs;
- marketplace implementation;
- WhatsApp or email automation;
- transaction execution;
- logistics tracking;
- online learning;
- automatic retraining;
- multi-agent orchestration;
- full ERP integration;
- advanced analytics dashboard;
- cloud deployment.

---

## Reproducibility

Local path:

```text
clone repository
-> uv sync
-> uv run pytest -q
-> uv run uvicorn backend.main:app --reload
-> upload one XLSX
-> download Rescue Decision Report
```

Docker path:

```text
clone repository
-> docker compose up --build
-> verify /health
-> upload one XLSX
-> download Rescue Decision Report
```

Dependency versions are locked in:

```text
uv.lock
```

---

## Development Workflow

Project uses a local-first workflow:

```text
implement locally
-> automated tests
-> inspect results
-> commit locally
-> push stable checkpoint
```

Commits follow Conventional Commits.

Examples:

```text
feat: add production planning pipeline
test: preserve hard gate blocks under fallback
build: add reproducible Docker Compose runtime
docs: update Technical MVP documentation
```

---

## Competition Context

Afterlife AI is developed for COMPFEST 18 AI Innovation Challenge.

Technical MVP scope follows the competition-oriented constraint of keeping one core interaction:

```text
one XLSX
-> one analysis
-> one Rescue Decision Report
```

This repository represents the final project repository, not a temporary technical prototype repository.

Technical MVP readiness does not mean final competition submission readiness.

---

## Source of Truth

Primary implementation references include:

- `SIMPLE_PRD_v1.1_UPDATED.md`
- `docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml`
- `docs/evaluation_source_v1.0/domain_rules_v1.0.yaml`
- `docs/evaluation_source_v1.0/evaluation_spec_v1.0.yaml`
- `configs/runtime_v1.yaml`
- executable acceptance, integration, and regression tests.

Where documentation and executable contracts disagree, active contracts and passing tests should be treated as the implementation source of truth.
