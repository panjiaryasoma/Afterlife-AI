# Afterlife AI — INTEGRATION-001

## Raw Inventory to Rescue Decision Report

**Version:** 1.0  
**Status:** `LOCKED_FOR_PREPRODUCTION`  
**Phase:** Preproduction Acceptance  
**Production implementation:** `BLOCKED`  
**Canonical input:** `RAW_INVENTORY_FIXTURE.xlsx`  
**Canonical output:** one `Rescue Decision Report`

---

## 0. Cara Membaca Dokumen Ini

Dokumen ini adalah satu cerita end-to-end yang menjelaskan bagaimana satu file inventori diproses sampai menjadi rencana rescue.

Dokumen ini sengaja ditulis dalam bahasa manusia terlebih dahulu. File teknis seperti `EXPECTED_CANDIDATES.yaml`, `EXPECTED_GATE_RESULTS.yaml`, `EXPECTED_SCORES.yaml`, dan `EXPECTED_ALLOCATION.yaml` baru boleh dibuat ulang setelah isi dokumen ini disetujui satu kali.

Status informasi dibedakan menjadi:

| Label | Arti |
|---|---|
| **LOCKED** | Sudah berasal dari kontrak atau fixture yang sebelumnya disetujui |
| **PROPOSED FIXTURE** | Parameter sintetis yang diusulkan khusus untuk acceptance test ini |
| **OPEN DEBT** | Belum diselesaikan dan harus ditutup sebelum readiness gate |

Membuat file tidak otomatis berarti keputusan di dalamnya sudah final. Kita rupanya perlu menuliskan hukum alam ini karena folder proyek sempat berkembang biak tanpa pengawasan.

---

## 1. Tujuan Integration Case

`INTEGRATION-001` harus membuktikan satu alur lengkap:

```text
raw inventory
→ validation
→ inventory triage
→ quantity partition
→ planner entry
→ candidate generation
→ hard gates
→ fixture scoring
→ fixture allocation
→ Rescue Decision Report
```

Integration case ini hanya acceptance contract. Pada tahap ini belum ada klaim bahwa:

- API production sudah berjalan;
- model sudah dilatih;
- optimizer production sudah dijalankan;
- partner nyata sudah tersedia;
- score merupakan probabilitas dunia nyata;
- tindakan rescue sudah dieksekusi.

---

## 2. Cerita Singkat Integration Case

Seorang operator toko mengunggah satu file Excel berisi enam lot inventori campuran.

File tersebut tidak berisi surplus saja. Isinya sengaja mencampurkan:

- stok sehat;
- stok yang perlu dipantau;
- surplus parsial;
- barang expired;
- barang dengan bukti keselamatan tidak cukup;
- declared surplus dengan sisa quantity yang masih perlu ditinjau.

Sistem memeriksa seluruh lot, melindungi stok normal, menahan barang yang tidak aman atau belum cukup bukti, lalu hanya mengirim 18 sachet ke Rescue Planner.

Rescue Planner tidak mencari partner secara bebas di internet. Ia memakai snapshot capability dan demand yang sudah disediakan. Pada fixture ini tidak ada external partner yang memiliki kebutuhan aktif dan terverifikasi untuk dua SKU yang sedang direncanakan. Karena itu, sistem tidak mengarang partner. Planner membandingkan tindakan internal yang memang didukung toko:

- mengolah sachet menjadi minuman siap jual;
- membuat bundle terbatas;
- melakukan local discount;
- menguji promotional bonus, lalu menolaknya karena tidak ada qualifying transaction.

Model fixture hanya memberi score kepada kandidat yang lolos hard gates. Global allocation kemudian membagi 18 sachet dengan memperhatikan kapasitas pengolahan bersama, stok companion untuk bundle, dan expected value.

Output akhirnya adalah satu Rescue Decision Report yang dapat ditinjau pemilik toko sebelum keputusan benar-benar dijalankan.

---

## 3. Input Utama — LOCKED

### 3.1 File

```text
RAW_INVENTORY_FIXTURE.xlsx
```

### 3.2 Sheet

```text
inventory_lots
```

### 3.3 Bentuk input

```yaml
lot_count: 6
column_count: 33
total_current_quantity: 102
input_scope: FULL_MIXED_INVENTORY
source_type: SYNTHETIC_INTEGRATION_FIXTURE
```

Workbook hanya berisi raw evidence. Policy dan expected result berada di file terpisah agar input tidak membawa kunci jawaban di dalam dirinya sendiri, sebuah konsep yang tampaknya perlu dijaga secara aktif.

---

## 4. Validation Result — LOCKED

Secara struktur, keenam row dapat dibaca dan diproses.

```yaml
file_validation_status: PASSED_WITH_WARNINGS
structurally_valid_rows: 6
blocking_file_errors: 0
```

Warnings yang diharapkan:

| Lot | Warning |
|---|---|
| `LOT-004` | Barang expired membutuhkan non-consumption routing |
| `LOT-005` | Critical cold-chain evidence tidak cukup |
| `LOT-006` | Sales history tidak tersedia untuk remainder |

Warning tidak berarti sistem boleh mengabaikannya. Warning menentukan jalur keputusan berikutnya.

Malformed-input cases seperti negative quantity, invalid date, duplicate lot ID, dan declared quantity melebihi current quantity belum diuji oleh workbook ini. Kasus-kasus tersebut tetap menjadi validation debt dan harus ditutup pada final consistency audit.

---

## 5. Inventory Triage — LOCKED

### 5.1 Hasil per lot

| Lot | Current quantity | Hasil | Quantity disposition |
|---|---:|---|---|
| `LOT-001` | 15 | `HEALTHY_STOCK` | 15 protected |
| `LOT-002` | 10 | `MONITOR` | 10 monitor |
| `LOT-003` | 25 | `SURPLUS_CANDIDATE` | 15 protected + 10 planning |
| `LOT-004` | 12 | `EXPIRED` | 12 expired |
| `LOT-005` | 20 | `NEEDS_REVIEW` | 20 review |
| `LOT-006` | 20 | `SURPLUS_CANDIDATE` | 8 planning + 12 review |

### 5.2 Workbook reconciliation

```yaml
total_current_quantity: 102

protected_normal_stock_quantity: 30
monitor_quantity: 10
planning_quantity: 18
expired_quantity: 12
review_quantity: 32
```

Invariant:

```text
30 + 10 + 18 + 12 + 32 = 102
```

Tidak ada quantity yang hilang dan tidak ada quantity yang dihitung dua kali.

### 5.3 Planner boundary

Hanya dua planning lot yang boleh keluar dari triage:

```yaml
PLAN-LOT-003:
  source_lot_id: LOT-003
  product: Minuman Serbuk Rasa Mangga
  planning_quantity: 10
  surplus_source: CALCULATED

PLAN-LOT-006:
  source_lot_id: LOT-006
  product: Minuman Serbuk Rasa Melon
  planning_quantity: 8
  surplus_source: USER_DECLARED
```

Total:

```text
18 unit masuk planner
84 unit dilarang masuk planner
```

Dua belas sachet remainder dari `LOT-006` tetap berada di review. Status lot `SURPLUS_CANDIDATE` tidak memberi izin kepada planner untuk mengambil seluruh 20 sachet.

---

## 6. Decision Context — PROPOSED FIXTURE

Integration case menggunakan objective:

```text
BALANCED
```

Maknanya:

- mengutamakan expected economic recovery;
- tetap menjaga seluruh hard constraints;
- tidak menganggap cash value sebagai satu-satunya nilai;
- tidak mengizinkan model atau objective mengalahkan safety, verification, quantity, atau capability limits.

Konteks eksekusi:

```yaml
runtime_internet: false
external_partner_search: false
human_approval_required: true
automatic_execution: false
```

---

## 7. Business Capability Snapshot — PROPOSED FIXTURE

Fixture menggunakan capability toko yang diturunkan dari pola insiden keluarga dan ruleset yang sudah tersedia.

### 7.1 Capability yang tersedia

```yaml
can_internal_repurpose: true
can_bundle: true
can_local_discount: true
can_offer_promotional_bonus: true
```

### 7.2 Shared internal-repurpose capacity

Sachet dapat diolah menjadi minuman siap jual, tetapi kapasitasnya terbatas.

```yaml
equipment_capacity: 8
labor_capacity: 6
ingredient_and_cup_capacity: 8
verified_repurpose_demand: 8

maximum_batch_repurpose_quantity: 6
binding_resource: LABOR_CAPACITY
```

Aturannya:

```text
maximum repurpose quantity
= minimum dari equipment, labor, ingredient, dan verified demand
= 6
```

Kapasitas enam unit berlaku untuk seluruh batch, bukan enam unit per lot.

### 7.3 Bundle capacity

Bundle hanya tersedia untuk campaign SKU mangga pada snapshot ini.

```yaml
companion_product: SNACK-FIXTURE-01
companion_current_quantity: 6
companion_reserved_quantity: 2
bundle_ratio: 1:1
allocatable_companion_quantity: 4
maximum_bundle_quantity: 4
supported_source_sku:
  - PBEV-003
```

Dua companion units tetap dilindungi untuk operasi normal.

### 7.4 Promotional bonus context

```yaml
qualifying_transactions: 0
max_bonus_per_transaction: 1
campaign_margin_status: NOT_EVALUABLE_WITHOUT_TRANSACTION
```

Capability toko memang ada, tetapi kondisi transaksi saat request ini tidak memenuhi syarat.

### 7.5 Partner Demand Registry snapshot

```yaml
matching_external_partner_found: false
matching_active_demand_found: false
external_candidate_generation_allowed: false
```

Maknanya bukan bahwa tidak ada calon partner di dunia nyata. Maknanya hanya:

> Pada snapshot acceptance fixture ini, tidak ada kebutuhan eksternal aktif dan terverifikasi untuk kedua SKU.

Sistem dilarang mengarang partner agar report terlihat lebih meriah.

---

## 8. Candidate Generation — PROPOSED FIXTURE

Candidate generation belum memilih keputusan akhir. Ia hanya membuat pilihan yang didukung action catalog dan capability snapshot.

### 8.1 Kandidat untuk `PLAN-LOT-003`

Produk: Minuman Serbuk Rasa Mangga  
Planning quantity: 10 sachet

| Candidate | Maksimum quantity | Alasan dibuat |
|---|---:|---|
| `CAND-003-REPURPOSE` | 6 | Toko mampu mengolah sachet menjadi minuman siap jual |
| `CAND-003-BUNDLE` | 4 | Ada empat companion units yang benar-benar allocatable |
| `CAND-003-DISCOUNT` | 10 | Local discount tersedia sebagai fallback |

### 8.2 Kandidat untuk `PLAN-LOT-006`

Produk: Minuman Serbuk Rasa Melon  
Planning quantity: 8 sachet

| Candidate | Maksimum quantity | Alasan dibuat |
|---|---:|---|
| `CAND-006-REPURPOSE` | 6 | Toko memiliki capability repurpose, tetapi berbagi kapasitas batch |
| `CAND-006-DISCOUNT` | 8 | Local discount tersedia |
| `CAND-006-BONUS` | 8 secara teoritis | Capability bonus tersedia, tetapi masih harus melewati transaction gate |

### 8.3 Tindakan yang tidak dibuat

Tindakan berikut tidak dibuat untuk kedua lot:

```text
RETURN_TO_SUPPLIER
BRANCH_TRANSFER
WHOLESALE
EXTERNAL_PARTNER
DONATION
SAFE_DISPOSAL
```

Alasannya:

- tidak ada supplier-return policy yang dikonfirmasi;
- toko fixture tidak memiliki destination branch;
- quantity terlalu kecil dan tidak ada wholesale snapshot yang valid;
- tidak ada active verified partner demand;
- tidak ada verified donation recipient pada snapshot;
- safe disposal tidak layak menjadi candidate selama opsi komersial aman masih tersedia.

---

## 9. Hard Gates — PROPOSED FIXTURE

Setiap kandidat diperiksa sebelum scoring.

### 9.1 Gates yang berlaku

```text
validation
coverage
safety
verification
capability
storage compatibility
timing
demand
capacity
quantity feasibility
```

### 9.2 Hasil gate

| Candidate | Gate result | Konsekuensi |
|---|---|---|
| `CAND-003-REPURPOSE` | `FEASIBLE` | Boleh diberi score |
| `CAND-003-BUNDLE` | `FEASIBLE` | Boleh diberi score |
| `CAND-003-DISCOUNT` | `FEASIBLE` | Boleh diberi score |
| `CAND-006-REPURPOSE` | `FEASIBLE` | Boleh diberi score |
| `CAND-006-DISCOUNT` | `FEASIBLE` | Boleh diberi score |
| `CAND-006-BONUS` | `REJECTED` | Tidak boleh diberi score |

Reason code kandidat bonus:

```text
NO_QUALIFYING_TRANSACTION
```

Penjelasan manusia:

> Toko mampu menjalankan program bonus, tetapi pada snapshot request ini tidak ada transaksi yang memenuhi syarat. Sistem tidak boleh mengklaim bonus akan meningkatkan penjualan dan tidak boleh memberi bonus tanpa transaksi utama.

---

## 10. Fixture Scoring — PROPOSED FIXTURE

### 10.1 Claim boundary

Semua nilai di bagian ini adalah:

```text
FIXTURE_EXPECTED_SCORE
```

Nilai tersebut:

- bukan hasil model terlatih;
- bukan probabilitas lapangan yang telah divalidasi;
- hanya dipakai untuk membuktikan urutan scoring dan optimizer;
- nanti harus digantikan oleh output model aktual pada implementation test.

### 10.2 Score yang diusulkan

| Candidate | Fixture score | Net value jika berhasil per unit | Expected value per unit |
|---|---:|---:|---:|
| `CAND-003-REPURPOSE` | 0.86 | Rp2.400 | Rp2.064 |
| `CAND-003-BUNDLE` | 0.80 | Rp1.600 | Rp1.280 |
| `CAND-003-DISCOUNT` | 0.74 | Rp1.500 | Rp1.110 |
| `CAND-006-REPURPOSE` | 0.79 | Rp2.400 | Rp1.896 |
| `CAND-006-DISCOUNT` | 0.76 | Rp1.500 | Rp1.140 |
| `CAND-006-BONUS` | `null` | Tidak dihitung | Ditolak oleh hard gate |

Perhitungan:

```text
expected value per unit
= fixture score × net value jika berhasil
```

Contoh:

```text
CAND-003-REPURPOSE
= 0,86 × Rp2.400
= Rp2.064 per sachet
```

Nilai Rp2.400 untuk repurpose berasal dari fixture:

```text
harga minuman siap jual
- direct execution cost
= net value jika berhasil
```

Angka score, biaya, dan recovery tetap synthetic acceptance parameters. Mereka menguji logika, bukan membuktikan outcome UMKM.

---

## 11. Global Fixture Allocation — PROPOSED FIXTURE

Optimizer fixture harus melihat kedua planning lot sekaligus.

### 11.1 Shared constraint

```yaml
total_internal_repurpose_capacity: 6
```

Kedua lot bersaing memakai kapasitas yang sama.

Perbandingan expected value:

```text
Mangga repurpose: Rp2.064 per unit
Melon repurpose:  Rp1.896 per unit
```

Karena mangga memiliki expected value lebih tinggi, enam slot repurpose diberikan kepada `PLAN-LOT-003`.

### 11.2 Expected allocation

```yaml
PLAN-LOT-003:
  INTERNAL_REPURPOSE: 6
  BUNDLE: 4
  LOCAL_DISCOUNT: 0
  total_allocated: 10
  unallocated: 0

PLAN-LOT-006:
  INTERNAL_REPURPOSE: 0
  LOCAL_DISCOUNT: 8
  PROMOTIONAL_BONUS: 0
  total_allocated: 8
  unallocated: 0
```

### 11.3 Kenapa hasilnya begitu?

#### `PLAN-LOT-003`

- enam unit masuk repurpose karena action ini memiliki expected value tertinggi;
- kapasitas repurpose habis pada enam unit;
- empat unit sisanya masuk bundle;
- bundle dibatasi empat companion units yang allocatable;
- local discount tetap feasible tetapi tidak dipilih.

#### `PLAN-LOT-006`

- repurpose feasible tetapi tidak dipilih karena shared capacity sudah digunakan pada kandidat dengan expected value lebih tinggi;
- promotional bonus ditolak sebelum scoring;
- seluruh delapan unit masuk local discount;
- dua belas unit remainder dari raw `LOT-006` tetap review dan tidak ikut allocation.

### 11.4 Allocation reconciliation

```yaml
total_planning_quantity: 18
total_allocated_quantity: 18
total_unallocated_quantity: 0
```

Invariant:

```text
10 + 8 = 18
18 = 18 allocated + 0 unallocated
```

### 11.5 Expected fixture metrics

```yaml
expected_total_economic_value: 26624
expected_rescued_units: 14.44
fixture_weighted_rescue_score: 0.8022
```

Perhitungan expected economic value:

```text
6 × Rp2.064
+ 4 × Rp1.280
+ 8 × Rp1.140
= Rp26.624
```

Perhitungan expected rescued units:

```text
6 × 0,86
+ 4 × 0,80
+ 8 × 0,76
= 14,44 unit
```

Nilai fractional hanya expectation dari fixture score, bukan klaim bahwa 0,44 sachet akan berjalan meninggalkan toko.

---

## 12. Expected Rescue Decision Report

Report final harus dapat dibaca pemilik toko tanpa membuka YAML atau kode.

### 12.1 Ringkasan batch

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

### 12.2 Rekomendasi yang ditampilkan

| Source lot | Action | Quantity | Status |
|---|---|---:|---|
| `LOT-003` | Internal repurpose | 6 | Direkomendasikan |
| `LOT-003` | Bundle | 4 | Direkomendasikan |
| `LOT-006` | Local discount | 8 | Direkomendasikan |

### 12.3 Alternatif penting yang tidak dipilih

| Candidate | Status | Alasan |
|---|---|---|
| `CAND-003-DISCOUNT` | Feasible, tidak dipilih | Expected value lebih rendah dari repurpose dan bundle |
| `CAND-006-REPURPOSE` | Feasible, tidak dipilih | Shared repurpose capacity digunakan oleh kandidat bernilai lebih tinggi |
| `CAND-006-BONUS` | Rejected | Tidak ada qualifying transaction |

### 12.4 Lot yang tidak masuk Rescue Planner

| Lot | Quantity | Treatment |
|---|---:|---|
| `LOT-001` | 15 | Dipertahankan sebagai stok normal |
| `LOT-002` | 10 | Tetap dijual normal dan dipantau |
| `LOT-003` protected portion | 15 | Tidak boleh dialokasikan |
| `LOT-004` | 12 | Diblokir dari consumption route |
| `LOT-005` | 20 | Ditahan untuk cold-chain evidence review |
| `LOT-006` remainder | 12 | Ditahan untuk demand-evidence review |

### 12.5 Human review dan approval

```yaml
human_review_items:
  LOT-005: 20
  LOT-006_REMAINDER: 12

final_plan_approval_required: true
automatic_execution_allowed: false
```

### 12.6 Warnings dan limitation

Report wajib menyatakan:

- seluruh capability, capacity, demand, score, dan recovery pada integration case bersifat sintetik;
- score bukan real-world probability;
- tidak ada external partner yang diklaim tersedia;
- expired handling final masih mengikuti deterministic compliance policy;
- `LOT-005` tidak boleh dianggap safe atau unsafe sebelum evidence selesai;
- `SCHEMA-CR-001` masih harus diterapkan pada final schema packaging;
- rekomendasi hanya rencana dan memerlukan persetujuan manusia.

---

## 13. End-to-End Invariants

Integration case hanya lulus bila seluruh kondisi berikut benar.

### 13.1 Quantity conservation

```text
30 protected
+ 10 monitor
+ 18 planning
+ 12 expired
+ 32 review
= 102 input
```

### 13.2 Planner isolation

```text
planner input = 18
non-planning quantity entering planner = 0
```

### 13.3 Safety isolation

```text
expired quantity entering consumption route = 0
review quantity entering planner = 0
```

### 13.4 Scoring isolation

```text
hard-rejected candidate receiving score = 0
non-planning lot receiving score = 0
```

### 13.5 Capacity constraints

```text
repurpose allocation <= 6
bundle allocation <= 4
bonus allocation <= qualifying transactions
```

### 13.6 Allocation conservation

```text
selected allocation
+ fallback quantity
+ unallocated quantity
= planning quantity
```

Pada fixture ini:

```text
18 + 0 + 0 = 18
```

### 13.7 Human authority

```text
automatic execution = false
final human approval = required
```

---

## 14. Integration Failure Conditions

`INTEGRATION-001` gagal bila salah satu kondisi berikut terjadi:

- workbook invalid tetap diteruskan tanpa error;
- hasil triage berbeda dari locked fixture;
- protected, monitor, expired, atau review quantity masuk planner;
- planner menerima 20 unit penuh dari `LOT-006`;
- candidate eksternal dibuat tanpa active verified demand;
- repurpose dialokasikan lebih dari enam unit;
- bundle memakai reserved companion stock;
- bundle melebihi empat unit;
- promotional bonus menerima score;
- score mengalahkan hard reject;
- `CAND-006-REPURPOSE` dipilih tanpa memperhitungkan shared capacity;
- allocation melebihi 18 unit;
- report kehilangan expired atau review quantity;
- inventory loss dilaporkan sebagai cash recovery;
- fixture score dipresentasikan sebagai hasil model production;
- rekomendasi dianggap sudah dieksekusi;
- final human approval dilewati.

---

## 15. Traceability

| Integration decision | Primary source |
|---|---|
| Raw mixed inventory dan triage | `RAW_INVENTORY_FIXTURE.xlsx`, `EXPECTED_TRIAGE_OUTPUT.yaml` |
| Hanya planning quantity masuk planner | TRIAGE suite dan Simple PRD |
| Repurpose dibatasi minimum resource | `CAPABILITY-RULE-001`, `CAPABILITY-RULE-002`, `EVAL-002`, `EVAL-017` |
| Bundle dibatasi companion allocatable | `BUNDLE-RULE-001`, `EVAL-018` |
| Bonus membutuhkan qualifying transaction | `BONUS-RULE-001`, `EVAL-019` |
| Kandidat gagal tidak menerima score | AI Model Contract dan Domain Rulebook |
| Capacity dihitung global | Optimization Contract dan planner evaluations |
| Score fixture bukan probabilitas dunia nyata | Simple PRD claim boundary |
| Tidak mengarang partner | Partner validation, fallback, dan abstention requirements |

---

## 16. Yang LOCKED dan Yang Masih Diusulkan

### Sudah locked

```text
6 raw inventory lots
102 total quantity
30 protected
10 monitor
18 planning
12 expired
32 review
PLAN-LOT-003 = 10
PLAN-LOT-006 = 8
review remainder LOT-006 = 12
model hanya setelah hard gates
human approval wajib
```

### Proposed fixture yang perlu satu approval

```text
shared repurpose capacity = 6
bundle capacity = 4
no active matching external partner
qualifying bonus transactions = 0
candidate set per planning lot
fixture score values
fixture net values
final allocation:
  LOT-003 → 6 repurpose + 4 bundle
  LOT-006 → 8 local discount
```

### Open debt yang tidak disamarkan

```text
malformed-input acceptance cases
real capability validation
real partner validation
trained model output
optimizer implementation
report usability test
SCHEMA-CR-001 file update
schema v2.0 packaging
final consistency audit
```

---

## 17. Single Approval Decision

Dokumen ini hanya membutuhkan satu keputusan.

```yaml
decision_scope:
  - integration story
  - synthetic capability snapshot
  - candidate set
  - hard-gate outcomes
  - fixture score ranking
  - global allocation
  - report contents
  - claim boundary

current_status: LOCKED_FOR_PREPRODUCTION
technical_yaml_generation: COMPLETE
preproduction_readiness_gate: PENDING_FINAL_AUDIT_AND_APPROVAL
production: BLOCKED
```

Setelah dokumen ini disetujui:

```text
1. Turunkan isi yang sama ke YAML teknis.
2. Buat EXPECTED_RESCUE_DECISION_REPORT.md.
3. Jalankan final consistency audit.
4. Terapkan SCHEMA-CR-001.
5. Paketkan schema v2.0.
6. Putuskan PREPRODUCTION_READINESS_GATE.
```

Tidak ada lagi desain ulang per lot atau per candidate kecuali ditemukan kontradiksi nyata.
