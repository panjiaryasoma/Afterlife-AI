# Afterlife AI

> AI-assisted rescue inventory planning for retail and F&B surplus.

Afterlife AI membantu usaha retail dan F&B memisahkan stok normal dari unit yang perlu ditangani, mengevaluasi tindakan rescue yang aman dan feasible, lalu menyusun alokasi inventori berdasarkan peluang rescue, nilai ekonomi, keterbatasan kapasitas, biaya, dan waktu.

Sistem menerima satu file inventori `.xlsx` dan menghasilkan satu **Rescue Decision Report** yang menjelaskan:

- stok yang tetap dilindungi sebagai stok normal;
- stok yang perlu dimonitor;
- surplus yang dapat direncanakan;
- barang expired atau membutuhkan review;
- tindakan rescue yang dipilih;
- kuantitas yang dialokasikan;
- alternatif yang ditolak beserta alasannya;
- warning, fallback, limitation, dan kebutuhan human review.

---

## Current Development Status

```yaml
phase: Production
development_mode: Local First
repository_structure: Initialized
technical_mvp: In Progress
submission_ready: false
```

Progress awal:

- [x] Final repository structure initialized
- [x] Python project configuration added
- [x] Git ignore policy defined
- [x] Python package initialized
- [x] XLSX intake implemented
- [x] Input validation implemented
- [x] Deterministic inventory triage implemented
- [x] Rescue planner implemented
- [x] Synthetic dataset generator implemented
- [x] Candidate models evaluated
- [ ] FastAPI and minimal UI integrated
- [ ] Docker Compose verified
- [ ] Technical MVP release candidate completed

---

## Problem

Usaha retail dan F&B dapat memiliki inventori yang:

- bergerak lambat;
- berlebih;
- mendekati akhir masa jual;
- tidak sesuai dengan demand lokal;
- memiliki peluang recovery melalui tindakan alternatif.

Keputusan seperti diskon, bundling, penggunaan internal, retur, transfer, wholesale, donasi, atau disposal sering dilakukan secara manual dan tidak selalu mempertimbangkan seluruh constraint secara konsisten.

Masalah tambahan muncul karena file inventori dapat mencampurkan:

- stok sehat;
- surplus parsial;
- barang near-expiry;
- barang expired;
- data tidak lengkap;
- kondisi yang tidak aman untuk diproses otomatis.

Afterlife AI dirancang sebagai decision-support system, bukan sistem eksekusi otomatis.

---

## Solution Overview

Alur utama sistem:

```text
Inventory XLSX
→ structural and semantic validation
→ deterministic inventory triage
→ surplus planning lots
→ candidate rescue actions
→ safety and feasibility gates
→ rescue-success scoring
→ expected-value calculation
→ global allocation optimization
→ Rescue Decision Report
```

Prinsip utama:

1. Stok normal harus dilindungi.
2. Safety dan feasibility ditentukan secara deterministik.
3. Model hanya menilai kandidat yang telah lolos seluruh hard gate.
4. Optimizer tidak boleh melanggar quantity, capacity, budget, storage, atau deadline constraints.
5. Sistem harus abstain ketika evidence tidak cukup.
6. Keputusan akhir tetap memerlukan human review.

---

## Core Input and Output

### Input

Satu file `.xlsx` dengan main worksheet:

```text
inventory_lots
```

Input mencakup data lot inventori, konteks keputusan, objective optimasi, budget logistik, dan rescue deadline.

### Output

Satu **Rescue Decision Report** yang berisi:

- validation summary;
- inventory triage;
- protected normal stock;
- surplus planning quantity;
- selected rescue allocations;
- unallocated quantity;
- rejected alternatives;
- reason codes;
- warning dan review flags;
- scoring provenance;
- ruleset dan model version;
- fallback dan known limitations.

---

## Supported Rescue Actions

Technical MVP dirancang untuk mendukung:

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

Ketersediaan tindakan ditentukan oleh capability profile, domain rules, partner demand, storage requirement, capacity, dan safety evidence.

---

## Technical Architecture

```text
XLSX Intake
├── workbook validation
├── worksheet validation
├── column validation
└── canonical inventory records

Deterministic Triage
├── healthy stock protection
├── monitor routing
├── surplus calculation
├── expired routing
└── needs-review routing

Rescue Planner
├── planning-lot construction
├── candidate generation
├── hard safety gates
├── feasibility gates
├── scoring provider
├── expected-value calculation
├── global optimizer
└── deterministic fallback

Application Layer
├── FastAPI
├── Jinja2
├── HTML/CSS/JavaScript
├── synchronous analysis
└── downloadable report
```

---

## Technology Stack

```yaml
language: Python 3.12
package_manager: uv
backend: FastAPI
validation: Pydantic v2
data_processing:
  - pandas
  - openpyxl
machine_learning:
  - scikit-learn
optimization: OR-Tools CP-SAT
frontend:
  - Jinja2
  - HTML
  - CSS
  - JavaScript
testing: pytest
linting: Ruff
type_checking: mypy
runtime: Docker Compose
database: none
runtime_internet_dependency: none
```

---

## Repository Structure

```text
Afterlife-AI/
├── backend/
│   ├── api/
│   ├── main.py
│   └── __init__.py
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── js/
│   └── templates/
│
├── configs/
├── data/
│   ├── fixtures/
│   ├── generated/
│   ├── processed/
│   └── templates/
├── docs/
│   ├── architecture/
│   ├── contracts/
│   ├── decisions/
│   └── methodology/
├── models/
├── notebooks/
├── reports/
│   ├── evidence/
│   ├── figures/
│   └── tables/
├── scripts/
├── src/
│   └── afterlife_ai/
│       ├── candidates/
│       ├── contracts/
│       ├── fallback/
│       ├── gates/
│       ├── intake/
│       ├── optimization/
│       ├── pipeline/
│       ├── planner/
│       ├── reporting/
│       ├── scoring/
│       ├── triage/
│       └── validation/
├── tests/
│   ├── acceptance/
│   ├── fixtures/
│   ├── integration/
│   └── unit/
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Documentation Policy

Repository ini memisahkan dokumentasi menjadi tiga lapisan.

### `README.md`

Entry point untuk memahami masalah, solusi, arsitektur, setup, penggunaan, status proyek, dan claim boundary.

### `docs/`

Berisi referensi teknis dan metodologis:

- architecture;
- contracts;
- design decisions;
- methodology;
- reproducibility instructions.

### `reports/`

Berisi hasil aktual dan interpretasi:

- validation findings;
- triage findings;
- planner findings;
- dataset findings;
- model training and evaluation;
- API and integration findings;
- testing results;
- limitations.

### `reports/evidence/`

Berisi bukti mentah:

- test output;
- generated examples;
- evaluation artifacts;
- command logs;
- screenshots;
- release verification.

---

## Development Workflow

Project menggunakan alur local-first:

```text
implement locally
→ run automated tests
→ inspect results
→ document findings
→ commit locally
→ push stable checkpoint
```

Perubahan tidak langsung dikirim ke remote repository sebelum checkpoint lokal diperiksa.

Commit mengikuti Conventional Commits:

```text
feat: add xlsx inventory intake
fix: correct surplus quantity calculation
test: add deterministic triage acceptance cases
docs: document validation findings
refactor: separate candidate gates from scoring
```

---

## Installation

Instruksi instalasi akan difinalisasi setelah package initialization dan dependency lock selesai.

Target local setup:

```powershell
uv sync
```

Target application command:

```powershell
uv run uvicorn app.main:app --reload
```

Target test command:

```powershell
uv run pytest
```

Perintah tersebut masih merupakan target kontrak dan belum dinyatakan bekerja sampai diverifikasi pada clean environment.

---

## Runtime Boundary

```yaml
request_processing: synchronous
runtime_database: none
server_side_history: none
uploaded_file_persistence: none
report_persistence: user_download_only
runtime_internet: none
```

Pengguna harus mengunduh report jika ingin menyimpannya. Aplikasi tidak menyediakan account, login, atau halaman history pada MVP.

---

## Model and Data Claim Boundary

Dataset training dapat menggunakan data sintetis yang dibuat berdasarkan scenario contracts dan domain rules.

Batas klaim:

- data sintetis bukan transaksi dunia nyata;
- model score bukan probabilitas lapangan yang telah tervalidasi;
- model hanya membantu scoring atau ranking kandidat feasible;
- model tidak menentukan safety;
- model tidak dapat melewati hard gates;
- optimizer tidak dapat mengubah aturan keselamatan;
- keputusan akhir tetap memerlukan peninjauan manusia.

---

## Non-Goals

Technical MVP tidak mencakup:

- authentication;
- user accounts;
- report history;
- distributed database;
- background job;
- cloud deployment;
- automated outreach;
- WhatsApp atau email automation;
- transaction execution;
- logistics tracking;
- marketplace publik;
- automatic retraining;
- online learning;
- multi-agent system;
- full ERP;
- advanced analytics dashboard.

---

## Reproducibility

Target reproducibility:

```text
clone repository
→ install dependencies using uv
→ generate or load deterministic fixtures
→ run automated tests
→ run local application
→ upload reference XLSX
→ generate Rescue Decision Report
```

Versi dependency akan dikunci melalui `uv.lock`.

Dataset generator, preprocessing, model training, evaluation, dan optimizer configuration harus menggunakan seed serta manifest yang terdokumentasi.

---

## Known Limitations

Status awal:

- implementation belum tersedia;
- pipeline end-to-end belum dapat dijalankan;
- model belum dipilih;
- model value gate belum dievaluasi;
- Docker Compose belum dibuat;
- real-world validation masih terbatas;
- business adoption dan willingness-to-pay belum tervalidasi;
- synthetic evaluation tidak membuktikan efektivitas dunia nyata.

Bagian ini akan diperbarui berdasarkan hasil implementasi dan evaluasi aktual.

---

## Project Scope Boundary

Repository ini dibangun langsung sebagai repository final proyek.

Sprint empat hari hanya mengatur jadwal implementasi. Setelah technical sprint selesai, repository yang sama akan digunakan untuk:

- bug fixing;
- UI refinement;
- report completion;
- proposal preparation;
- proof-of-work recording;
- promotional video;
- submission packaging.

Tidak ada repository technical sementara yang nantinya dipindahkan ke repository final.

---

## Competition Context

Project ini dikembangkan untuk **COMPFEST 18 — AI Innovation Challenge**, pada area utama **Smart Commerce** dengan dukungan aspek **Smart Logistics**.

Batas MVP mengikuti ketentuan kompetisi:

- satu alur input dan output inti;
- synchronous local processing;
- core AI inference dengan parameter statis saat demonstrasi;
- local reproducibility melalui Docker Compose;
- tidak overbuilt dengan authentication kompleks, history page, atau distributed database.

---

## Source of Truth

Dokumen utama yang menjadi basis implementasi:

- `SIMPLE_PRD_v1.1_UPDATED.md`
- final feature schema aktif;
- baseline contract;
- toolchain decision;
- deterministic triage acceptance suite;
- raw inventory integration contract;
- domain ruleset;
- evaluation specification.
