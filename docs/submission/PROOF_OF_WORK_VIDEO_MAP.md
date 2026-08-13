# Afterlife AI — Proof-of-Work Video Map

**Competition:** COMPFEST 18 AI Innovation Challenge  
**Deliverable:** Video Proof of Work  
**Project:** Afterlife AI  
**Target duration:** 6:20–6:40  
**Hard maximum:** 7:00  
**Recording mode:** one continuous take, no cuts

---

## 1. Rulebook Contract

The Proof-of-Work video must:

```yaml
content:
  - show only the MVP running
  - explain what the MVP does
  - reflect the latest submitted MVP state
  - show working and imperfect/buggy behavior honestly
  - include every feature that will appear in the promotion video

software_only_demo:
  terminal_visible: true
  application_visible: true
  timestamp_visible: true

editing:
  cuts: prohibited
  fast_forward_for_loading: allowed
  voice_over: allowed

maximum_duration: 7 minutes
youtube_visibility: unlisted
```

Required YouTube naming format:

```text
COMPFEST 18 AIC: PROOF OF WORK - [Nama Tim] - Afterlife AI
```

The recording used for submission must be made from the final submission commit after G10 release audit.

---

# 2. Core Recording Principle

This is **not** a pitch video.

Do not spend proof-of-work time on:

- problem statistics;
- cinematic intro;
- team introduction;
- animations;
- investor language;
- long model-training history;
- hypothetical future features.

The recording should answer one question:

> Does the submitted repository actually run the MVP being claimed?

The strongest proof is therefore:

```text
timestamp
+ exact final commit
+ live terminal
+ live application
+ one real analysis
+ visible report output
+ honest limitations
```

---

# 3. Screen Layout

Recommended desktop layout for the entire recording:

```text
┌───────────────────────┬──────────────────────────────────────┐
│                       │                                      │
│   TERMINAL            │           AFTERLIFE AI UI            │
│   ~35–40% width       │           ~60–65% width              │
│                       │                                      │
│   server logs         │   upload / controls / report         │
│   timestamp           │                                      │
│   final commit SHA    │                                      │
│                       │                                      │
└───────────────────────┴──────────────────────────────────────┘

Windows taskbar clock stays visible.
```

Use:

```text
Browser zoom: 80–90%
Terminal font: large enough for 720p playback
Resolution: preferably 1920×1080
```

Do not hide the terminal after launch.

Server request logs are useful proof that the visible UI is connected to the submitted backend rather than a detached mock screen.

---

# 4. Pre-Recording Setup

Do this **before pressing Record**:

```text
1. Complete G10 final release audit.
2. Commit and push final submission checkpoint.
3. Confirm working tree is clean.
4. Close unrelated tabs and notifications.
5. Disable notification popups.
6. Open final repository root in PowerShell.
7. Open browser at http://127.0.0.1:8000 but do not analyze yet.
8. Prepare the controlled XLSX demo fixture.
9. Verify fixture path.
10. Make sure taskbar clock is visible.
```

Recommended demo fixture:

```text
tests/fixtures/integration_001/RAW_INVENTORY_FIXTURE.xlsx
```

This is a controlled technical evaluation fixture, not real transaction data.

Do not describe it as merchant production data.

---

# 5. Recording Start Commands

At the start of the continuous recording, show:

```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
git rev-parse --short HEAD
git status --short
```

Expected final behavior:

```text
timestamp printed
final submission commit SHA printed
git status --short returns no modified/untracked files
```

Then start the application:

```powershell
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Keep the server terminal visible.

If startup takes unusually long, fast-forward is allowed by the rulebook, but do not cut the recording.

---

# 6. Canonical 6:30 Recording Timeline

## 0:00–0:35 — Runtime Identity

### Screen

Terminal + browser visible simultaneously.

### Action

Run:

```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
git rev-parse --short HEAD
git status --short
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Refresh application once server starts.

### Narration

> Ini adalah kondisi final MVP Afterlife AI dari commit yang terlihat di terminal. Aplikasi berjalan secara lokal melalui FastAPI dan Jinja2. Proof-of-work ini direkam dalam satu alur tanpa pemotongan.

### Evidence demonstrated

```text
latest submission state
timestamp
repository identity
real runtime
terminal + application
```

---

## 0:35–1:10 — What the MVP Accepts

### Screen

Hero / Decision Context area.

### Action

Briefly point to:

```text
inventory XLSX upload
optimization objective
maximum logistics budget
minimum expected rescue ratio
rescue deadline
```

Do not change every field merely to prove it exists.

Use one deliberate request configuration.

Recommended safe demo configuration:

```yaml
optimization_objective: MAXIMIZE_RECOVERY_VALUE
max_logistics_budget: 50000
minimum_expected_rescue_ratio: leave disabled / empty
rescue_deadline_at: choose a valid future timezone-aware UI value
```

### Narration

> MVP menerima satu workbook inventori dan konteks keputusan. Operator dapat memilih objective, memberi batas biaya logistik, dan bila relevan mengatur target rescue atau deadline. Input ini divalidasi sebelum pipeline dijalankan.

### Evidence demonstrated

```text
single XLSX core input
request-level decision context
UI is connected to current API contract
```

---

## 1:10–1:40 — Upload Controlled Fixture

### Action

Upload:

```text
tests/fixtures/integration_001/RAW_INVENTORY_FIXTURE.xlsx
```

Press:

```text
Analyze Inventory
```

### Narration

> Untuk demonstrasi ini saya menggunakan fixture evaluasi terkontrol dari repository. Fixture ini bukan data transaksi dunia nyata. Sistem menjalankan analisis secara synchronous dan file upload hanya diproses sementara.

### Evidence demonstrated

```text
honest synthetic/evaluation boundary
real XLSX upload
live request
```

Do not navigate away while loading.

Server terminal should visibly log the request.

---

## 1:40–2:20 — Rescue Summary / Deterministic Triage

### Screen

Section:

```text
02 Rescue Summary
```

Show the batch-level quantities.

### Narration

> Tahap pertama bukan langsung memberi skor AI. Sistem terlebih dahulu melakukan deterministic inventory triage untuk melindungi stok normal dan memisahkan quantity yang benar-benar masuk rescue planning. Report tetap merekonsiliasi protected, monitor, planning, expired, dan review quantity terhadap total input.

### Evidence demonstrated

```text
healthy-stock protection
planning quantity isolation
quantity reconciliation
model is not used to decide safety
```

Do not claim that every row is surplus.

That would contradict the purpose of triage.

---

## 2:20–3:15 — Selected Rescue Plan

### Screen

Section:

```text
03 Selected Rescue Plan
```

Show selected allocation cards/rows.

Point out:

```text
action
destination
allocated quantity
rescue-success estimate
expected recovery/value
binding constraints when present
```

### Narration

> Hanya candidate yang lolos deterministic hard safety dan feasibility gates yang boleh masuk scoring. HGB-E kemudian memberi rescue-success estimate untuk candidate yang eligible. Setelah expected value dihitung, CP-SAT memilih alokasi secara global dengan menjaga quantity dan shared constraints.

If an external-partner allocation is selected:

> External partner ini berasal dari Partner Demand Registry demo yang statis dan sintetis, bukan partner live yang sudah terverifikasi.

If external partner is not selected, do **not** force a false claim. It can be shown later in Alternatives / Provenance if present.

### Evidence demonstrated

```text
hard-gate-before-model boundary
HGB-E scoring
expected-value semantics
global constrained optimization
selected allocation
```

---

## 3:15–4:05 — Alternatives

### Screen

Section:

```text
04 Alternatives
```

Show at least one candidate that was:

```text
feasible but not selected
or
rejected / blocked with reason
```

### Narration

> Report tidak hanya menampilkan keputusan yang dipilih. Candidate lain tetap ditampilkan sebagai alternative atau rejection dengan reason code. Ini penting supaya output dapat diaudit dan operator bisa melihat bahwa model score tidak otomatis menjadi keputusan.

If partner option appears here, mention:

> Partner matching menggunakan registry fixture yang disertakan di repository dan provenance-nya ikut dilaporkan.

### Evidence demonstrated

```text
explainability
unselected alternatives
rejection reasoning
partner candidate visibility if available
```

---

## 4:05–4:40 — Human Review

### Screen

Section:

```text
05 Human Review
```

### Narration

> Afterlife AI adalah decision-support system, bukan autonomous execution system. Item yang membutuhkan review tetap ditahan untuk human review, dan final approval report tetap berstatus pending. Aplikasi tidak mengeksekusi diskon, transfer, disposal, atau tindakan fisik lain secara otomatis.

### Evidence demonstrated

```text
review-required boundary
human authority
execution_performed = false
```

This point must remain consistent with the promotion video.

---

## 4:40–5:20 — Evidence / Provenance

### Screen

Section:

```text
06 Evidence
```

Show several traceability fields, for example:

```text
request ID
feature schema version
ruleset version
capability snapshot
scoring provider
optimization status
Partner Demand Registry provenance
deterministic execution metadata
```

### Narration

> Setiap report membawa provenance untuk schema, ruleset, capability profile, scoring provider, dan optimizer. Untuk demo partner matching, report juga menandai source registry dan bahwa fixture tersebut tidak real-world verified.

### Evidence demonstrated

```text
traceability
model provenance
runtime provenance
partner-registry claim boundary
determinism metadata
```

---

## 5:20–5:50 — Known Limitations

### Screen

Section:

```text
07 Limitations
```

### Narration

> Model saat ini dilatih pada synthetic benchmark, sehingga rescue-success score tidak boleh ditafsirkan sebagai probabilitas dunia nyata yang sudah tervalidasi. Runtime parameter dan partner registry juga masih static MVP defaults. Batasan ini ditampilkan langsung di report.

### Evidence demonstrated

```text
synthetic-data disclosure
no field-calibration claim
static-runtime disclosure
responsible claim boundary
```

Do not skip this section just because limitations look less glamorous.

For judging, honest limitations are stronger than imaginary deployment statistics.

---

## 5:50–6:15 — JSON Report Download

### Action

Click:

```text
Download JSON Report
```

Show the download event / downloaded filename briefly.

Do not leave the application to browse through the entire JSON.

### Narration

> Hasil analysis dapat diunduh sebagai satu Rescue Decision Report JSON berbasis request ID. Server tidak menyimpan report history atau database dalam scope MVP ini.

### Evidence demonstrated

```text
core output
download flow
no server-side history boundary
```

---

## 6:15–6:35 — Closing Proof

### Screen

Return to top or keep report visible while terminal remains visible.

### Narration

> Jadi flow MVP yang ditunjukkan adalah satu XLSX masuk, inventory ditriage secara deterministic, candidate rescue difilter oleh hard gates, candidate eligible diberi rescue-success score, optimizer menentukan alokasi global, dan hasil akhirnya tetap berupa advisory report untuk human review. Seluruh flow yang akan disebut di video promosi dibatasi pada fitur yang sudah ditunjukkan di proof-of-work ini.

Stop recording.

Target final timestamp:

```text
~6:30
```

Hard safety margin before 7:00:

```text
~30 seconds
```

---

# 7. Promotion-Video Feature Whitelist

G7 promotion video may mention/show these implemented capabilities because they are covered in the proof-of-work plan:

```text
[x] one XLSX inventory analysis
[x] decision-context controls
[x] deterministic inventory triage
[x] healthy-stock protection
[x] rescue candidate generation
[x] internal rescue actions
[x] external-partner matching through static demo PDR
[x] deterministic hard safety / feasibility gates
[x] HGB-E rescue-success scoring
[x] expected-value calculation
[x] CP-SAT global constrained allocation
[x] selected allocations
[x] alternatives / rejection reasoning
[x] provenance
[x] known limitations
[x] human review
[x] JSON Rescue Decision Report download
```

The promotion video must **not** introduce features absent from this proof-of-work recording.

Examples prohibited unless implemented before final submission and added to both videos:

```text
live marketplace
real-time internet partner search
WhatsApp automation
automatic price negotiation
automatic physical execution
live logistics tracking
authentication
merchant dashboard history
online learning
automatic retraining
OCR
multi-agent workflow
```

---

# 8. Things We Deliberately Do Not Need to Demonstrate

The Proof-of-Work video does not need a live demonstration of:

```text
model training
all 319+ automated tests
Docker build
every triage acceptance case
all 30 planner evaluation cases
every fallback branch
every optimizer objective
every invalid input type
full notebook evaluation
Git history
```

Those are repository evidence.

Trying to demonstrate all of them in seven minutes would produce neither proof nor work, merely frantic mouse movement.

---

# 9. Recording Risk Checklist

Before final recording:

```yaml
final_commit_visible: required
working_tree_clean: required
terminal_visible_all_video: required
application_visible_all_video: required
timestamp_visible: required

fixture:
  controlled: true
  known_to_pass: true
  not_claimed_as_real_transaction_data: true

browser:
  notifications_disabled: true
  zoom_checked: true
  no_private_tabs_visible: true

runtime:
  server_logs_visible: true
  analysis_completes: true
  report_download_works: true

editing:
  cuts: false
  transitions: false
  montage: false
  fast_forward_only_if_waiting: true

duration:
  target_under_6m40s: true
  hard_limit_under_7m: true
```

---

# 10. Final Recording Dry Run

Before the real take, perform exactly one dry run with the same fixture and request context.

Record:

```text
start-to-report duration
selected allocation result
whether external partner appears selected or alternative
sections that require scrolling
download filename
```

Then **do not change the pipeline merely to make the demo prettier**.

If the valid final system selects an unexpected but explainable candidate, explain it.

The proof-of-work exists to prove the software, not train the software to act for the camera.

---

# 11. G6 Completion Gate

```yaml
rulebook_constraints_mapped: true
continuous_take_plan_defined: true
terminal_and_app_layout_defined: true
timestamp_plan_defined: true
runtime_identity_plan_defined: true

mvp_flow_mapped:
  input: true
  triage: true
  candidate_generation: true
  hard_gates: true
  scoring: true
  optimization: true
  report: true
  human_review: true

promotion_feature_whitelist_defined: true
claim_boundaries_defined: true
final_recording: pending
final_video_upload: pending
```

**G6 Decision: PROOF-OF-WORK VIDEO MAP READY.**

Final recording remains pending until G10 freezes and verifies the exact submission commit.
