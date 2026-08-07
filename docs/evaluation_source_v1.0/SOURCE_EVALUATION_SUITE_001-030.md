# Afterlife AI — Evaluation Suite EVAL-001 sampai EVAL-030

**Version:** 0.3  
**Status:** consolidated working specification  
**Evaluation layer:** Core Rescue Planner Acceptance Tests

## Cara membaca

- Satu file kasus menguji satu perilaku atau constraint dominan.
- Input kasus dinormalisasi sebagai `SURPLUS_PLANNING_LOT`.
- Kasus dapat berhenti di validation, coverage, safety, verification, feasibility, model, atau optimizer layer.
- Model hanya menerima kandidat tindakan yang sudah feasible.
- Semua angka skenario yang tidak berasal dari bukti transaksi adalah sintetis.
- `estimated_rescue_success_score` tidak boleh diklaim sebagai probabilitas keberhasilan dunia nyata.

## Indeks

- [EVAL-001 — Incomplete Surplus Data Harus Abstain](#eval-001-incomplete-surplus-data-harus-abstain)
- [EVAL-002 — Internal Repurpose Menang pada Bisnis yang Mampu Memproses](#eval-002-internal-repurpose-menang-pada-bisnis-yang-mampu-memproses)
- [EVAL-003 — Harga Partner Tinggi Ditolak karena Pickup Terlambat](#eval-003-harga-partner-tinggi-ditolak-karena-pickup-terlambat)
- [EVAL-004 — Kapasitas Partner Dibagi Secara Global](#eval-004-kapasitas-partner-dibagi-secara-global)
- [EVAL-005 — Safety Override untuk Kaleng Rusak](#eval-005-safety-override-untuk-kaleng-rusak)
- [EVAL-006 — Seasonality Window Berakhir Sebelum Expiry](#eval-006-seasonality-window-berakhir-sebelum-expiry)
- [EVAL-007 — Supplier Return Menang](#eval-007-supplier-return-menang)
- [EVAL-008 — Markdown Mengalahkan Retur Parsial yang Mahal](#eval-008-markdown-mengalahkan-retur-parsial-yang-mahal)
- [EVAL-009 — Internal Use Mengalahkan Retur dalam Batas Kebutuhan](#eval-009-internal-use-mengalahkan-retur-dalam-batas-kebutuhan)
- [EVAL-010 — Mixed Allocation untuk Medium Wholesaler](#eval-010-mixed-allocation-untuk-medium-wholesaler)
- [EVAL-011 — Stale Partner Demand Harus Dikeluarkan](#eval-011-stale-partner-demand-harus-dikeluarkan)
- [EVAL-012 — Category Mismatch Ditolak Sebelum Scoring](#eval-012-category-mismatch-ditolak-sebelum-scoring)
- [EVAL-013 — Cold Chain Harus Valid End-to-End](#eval-013-cold-chain-harus-valid-end-to-end)
- [EVAL-014 — Logistics Budget Bersifat Global](#eval-014-logistics-budget-bersifat-global)
- [EVAL-015 — Tindakan Bernilai Tinggi Ditolak karena Terlalu Lambat](#eval-015-tindakan-bernilai-tinggi-ditolak-karena-terlalu-lambat)
- [EVAL-016 — Wholesale Minimum Order dan Aggregation](#eval-016-wholesale-minimum-order-dan-aggregation)
- [EVAL-017 — Internal Repurpose Dibatasi Resource Minimum](#eval-017-internal-repurpose-dibatasi-resource-minimum)
- [EVAL-018 — Bundle Companion Stock Dibatasi](#eval-018-bundle-companion-stock-dibatasi)
- [EVAL-019 — Bonus Promosi Tidak Boleh Mengarang Sales Uplift](#eval-019-bonus-promosi-tidak-boleh-mengarang-sales-uplift)
- [EVAL-020 — Donasi Sukses dengan Penerima dan Pickup Terverifikasi](#eval-020-donasi-sukses-dengan-penerima-dan-pickup-terverifikasi)
- [EVAL-021 — Donasi Diblokir karena Tidak Ada Jalur Feasible](#eval-021-donasi-diblokir-karena-tidak-ada-jalur-feasible)
- [EVAL-022 — Cacat Kosmetik Tetap Sellable](#eval-022-cacat-kosmetik-tetap-sellable)
- [EVAL-023 — Riwayat Suhu atau Penyimpanan Tidak Diketahui](#eval-023-riwayat-suhu-atau-penyimpanan-tidak-diketahui)
- [EVAL-024 — Expired Tetap Hard Reject meskipun Nilainya Tinggi](#eval-024-expired-tetap-hard-reject-meskipun-nilainya-tinggi)
- [EVAL-025 — Kapasitas Cold Storage Dibagi Global](#eval-025-kapasitas-cold-storage-dibagi-global)
- [EVAL-026 — Branch Transfer vs Local Markdown](#eval-026-branch-transfer-vs-local-markdown)
- [EVAL-027 — Kemasan Besar Cocok ke Mitra B2B](#eval-027-kemasan-besar-cocok-ke-mitra-b2b)
- [EVAL-028 — Out-of-Distribution Harus Abstain](#eval-028-out-of-distribution-harus-abstain)
- [EVAL-029 — Objective Mengubah Keputusan](#eval-029-objective-mengubah-keputusan)
- [EVAL-030 — End-to-End Multi-Lot Stress Test](#eval-030-end-to-end-multi-lot-stress-test)

---

# EVAL-001 — Incomplete Surplus Data Harus Abstain

```yaml
case_id: EVAL-001
title: Incomplete Surplus Data Harus Abstain
case_type: AMBIGUOUS_INCOMPLETE_INPUT
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-001
  - Incident_001-016_Family_Corroborated(1).txt
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji apakah sistem menolak mengarang keputusan ketika jumlah, expiry, kondisi, atau data demand tidak cukup untuk membandingkan tindakan.

## Input lot

```yaml
planning_lot_id: PL-NUTRISARI-001
source_lot_id: LOT-NUTRISARI-001
product_name: Nutrisari Es Rujak
product_category: POWDERED_BEVERAGE_SACHET
planning_quantity: UNKNOWN
unit: SACHET
expiry_date: UNKNOWN
remaining_shelf_life_days: UNKNOWN
product_condition: UNKNOWN
packaging_condition: UNKNOWN
verification_status: LOW
```

## Business capabilities

- can_discount=true
- can_bundle=true
- can_internal_repurpose=true
- can_offer_bonus=true

## Partner snapshot

- Tidak ada partner snapshot yang cukup untuk alokasi eksternal.

## Global context

- Harga historis keluarga tersedia sebagai konteks, tetapi jumlah stok dan outcome tidak tercatat.
- objective tidak boleh digunakan sebelum validation selesai.

## Expected routing

- VALIDATION_FAILED
- NEEDS_REVIEW
- model_scoring=BLOCKED
- optimizer_execution=BLOCKED

## Expected feasible actions

- Tidak ada tindakan otomatis yang dinyatakan feasible karena data kritis belum lengkap.

## Forbidden atau unsafe actions

- Semua alokasi otomatis; klaim bahwa bonus, repurpose, atau diskon pasti terbaik.

## Expected best action atau acceptable set

Tidak ada single best action. Sistem mengembalikan daftar field yang harus diverifikasi.

## Expected allocation

```yaml
automatic_allocated_quantity: 0
human_review_required: true
required_fields:
  - planning_quantity
  - expiry_date_or_safe_window
  - product_condition
  - packaging_condition
  - available_repurpose_capacity
  - campaign_or_sales_context
```

## Binding constraints

- Required field completeness
- No unsupported assumption
- No scoring before validation

## Expected explanation

> Data belum cukup untuk memilih tindakan. Verifikasi jumlah, masa aman, kondisi, dan kapasitas eksekusi sebelum planner dijalankan.

## Failure conditions

- mengarang jumlah stok
- menggunakan harga historis sebagai outcome
- menghasilkan rescue-success score
- memilih bonus tanpa syarat transaksi

## Locked rule

```text
VALIDATION-RULE-000: missing safety-critical atau allocation-critical fields menghasilkan abstention dan human review.
```

## Fitur yang dibenarkan

- critical_field_completeness
- validation_status
- missing_field_list
- human_review_required

## Source boundary dan uncertainty

Incident keluarga mengonfirmasi pola tindakan, bukan jumlah atau hasil. Kasus ini sengaja mempertahankan unknowns.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-002 — Internal Repurpose Menang pada Bisnis yang Mampu Memproses

```yaml
case_id: EVAL-002
title: Internal Repurpose Menang pada Bisnis yang Mampu Memproses
case_type: INTERNAL_REPURPOSE_WINS
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-001
  - Incident-004
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji apakah capability-aware planner memilih transformasi internal ketika toko memiliki alat, bahan, waktu, dan demand yang cukup.

## Input lot

```yaml
planning_lot_id: PL-NUTRISARI-002
product_name: Nutrisari Es Rujak
product_category: POWDERED_BEVERAGE_SACHET
planning_quantity: 40
unit: SACHET
remaining_shelf_life_days: 45
product_condition: GOOD
packaging_condition: INTACT
verification_status: VERIFIED
```

## Business capabilities

- can_internal_repurpose=true
- ice_available=true
- cup_capacity=20
- labor_capacity=20
- can_bundle=true
- can_discount=true

## Partner snapshot

- Tidak ada partner eksternal yang memberi nilai lebih baik setelah biaya.

## Global context

- Repurpose hanya boleh memakai kapasitas minimum dari alat, tenaga, bahan, dan demand.

## Expected routing

- SURPLUS_CANDIDATE
- safety=PASS
- coverage=PASS
- model_scoring=ALLOWED

## Expected feasible actions

- INTERNAL_REPURPOSE maksimal 20
- BUNDLE maksimal 10
- LOCAL_DISCOUNT untuk remainder

## Forbidden atau unsafe actions

- Repurpose di atas kapasitas 20
- Bonus tanpa qualifying transaction
- Disposal saat opsi komersial feasible

## Expected best action atau acceptable set

Mixed allocation dengan internal repurpose sebagai tindakan utama.

## Expected allocation

```yaml
allocations:
  - action: INTERNAL_REPURPOSE
    quantity: 20
  - action: BUNDLE
    quantity: 10
  - action: LOCAL_DISCOUNT
    quantity: 10
unallocated_quantity: 0
```

## Binding constraints

- Repurpose capacity=20
- Quantity conservation
- Action capability
- Remaining shelf life

## Expected explanation

> Dua puluh sachet ditransformasi karena kapasitas operasional dan demand tersedia. Sisa lot dibagi ke bundle dan markdown.

## Failure conditions

- mengalokasikan >20 ke repurpose
- memilih repurpose ketika capability false
- menghitung seluruh revenue repurpose tanpa biaya bahan/gelas

## Locked rule

```text
CAPABILITY-RULE-001: internal repurpose hanya feasible sampai kapasitas operasional dan demand terverifikasi.
```

## Fitur yang dibenarkan

- repurpose_equipment_capacity
- labor_capacity
- ingredient_capacity
- repurpose_demand
- expected_yield

## Source boundary dan uncertainty

Nilai dan kapasitas adalah sintetis; pola tindakan bersumber dari incident keluarga.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-003 — Harga Partner Tinggi Ditolak karena Pickup Terlambat

```yaml
case_id: EVAL-003
title: Harga Partner Tinggi Ditolak karena Pickup Terlambat
case_type: TIMING_OVERRIDE_HIGH_PRICE
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - External-Incident-003
  - External-Incident-005
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bahwa harga tinggi tidak mengalahkan safe window dan rescue deadline.

## Input lot

```yaml
planning_lot_id: PL-BAKERY-003
product_name: Roti produksi hari ini
product_category: READY_TO_EAT_BAKERY
planning_quantity: 50
unit: PACK
remaining_safe_window_hours: 8
quality_inspection_status: PASSED
verification_status: VERIFIED
```

## Business capabilities

- can_discount=true
- can_donate=true
- commercial_channel_open=true

## Partner snapshot

- PARTNER-A: price tertinggi, capacity 50, completion 12h
- PARTNER-B: capacity 30, completion 3h
- FOODBANK: capacity 5, completion 4h

## Global context

- rescue_deadline_hours=8
- same-day handling required

## Expected routing

- PARTNER-A rejected before scoring
- PARTNER-B feasible
- LOCAL_DISCOUNT feasible
- DONATION feasible

## Expected feasible actions

- PARTNER-B 30
- LOCAL_DISCOUNT 15
- DONATION 5

## Forbidden atau unsafe actions

- PARTNER-A allocation
- completion setelah 8h
- model score untuk PARTNER-A

## Expected best action atau acceptable set

Mixed allocation kepada partner aktif, kanal lokal, dan donation fallback.

## Expected allocation

```yaml
allocations:
  - action: EXTERNAL_PARTNER
    destination: PARTNER-B
    quantity: 30
  - action: LOCAL_DISCOUNT
    quantity: 15
  - action: DONATION
    quantity: 5
logistics_deadline_violation: 0
```

## Binding constraints

- Safe window
- Pickup completion
- Partner capacity
- Lot quantity

## Expected explanation

> Partner A ditolak walaupun menawarkan harga tertinggi karena completion 12 jam melewati jendela aman 8 jam.

## Failure conditions

- memilih PARTNER-A
- mengabaikan distribusi lanjutan
- mengubah safe window karena harga

## Locked rule

```text
TIMING-RULE-001: action completion harus selesai sebelum safety atau commercial deadline yang mengikat.
```

## Fitur yang dibenarkan

- estimated_completion_hours
- safe_window_hours
- pickup_window
- distribution_time
- timing_feasibility

## Source boundary dan uncertainty

Quantity dan timing sintetis; mekanisme pickup cepat dan same-day distribution didukung kasus eksternal.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-004 — Kapasitas Partner Dibagi Secara Global

```yaml
case_id: EVAL-004
title: Kapasitas Partner Dibagi Secara Global
case_type: SHARED_PARTNER_CAPACITY
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - External-Incident-005
  - External-Incident-006
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji optimizer global ketika dua lot bersaing untuk kapasitas partner yang sama.

## Input lot

```yaml
planning_lots:
  - planning_lot_id: PL-BREAD-004
    product_category: BAKERY
    planning_quantity: 20
  - planning_lot_id: PL-PASTRY-004
    product_category: BAKERY
    planning_quantity: 25
quality_status: PASSED
```

## Business capabilities

- can_discount=true
- can_donate=true

## Partner snapshot

- P-CAFE-004 menerima kedua kategori; active demand dan capacity total=30

## Global context

- Marginal gain bread > pastry
- fallback pastry=LOCAL_DISCOUNT

## Expected routing

- Kedua lot feasible ke partner, tetapi capacity shared=30

## Expected feasible actions

- P-CAFE: bread 20 + pastry 10
- Pastry remainder 15 ke local discount

## Forbidden atau unsafe actions

- alokasi 30 untuk setiap lot
- total partner allocation >30

## Expected best action atau acceptable set

Prioritaskan unit dengan marginal gain tertinggi, lalu fallback untuk remainder.

## Expected allocation

```yaml
allocations:
  - lot: PL-BREAD-004
    action: EXTERNAL_PARTNER
    quantity: 20
  - lot: PL-PASTRY-004
    action: EXTERNAL_PARTNER
    quantity: 10
  - lot: PL-PASTRY-004
    action: LOCAL_DISCOUNT
    quantity: 15
partner_capacity_used: 30
```

## Binding constraints

- Shared capacity
- Marginal value
- Quantity conservation

## Expected explanation

> Kapasitas 30 tidak diperbanyak per lot. Dua puluh unit bread dan sepuluh pastry memakai partner; sisanya memakai fallback.

## Failure conditions

- capacity reset per row
- first-come-first-served tanpa nilai marginal
- remainder hilang

## Locked rule

```text
CAPACITY-RULE-001: partner demand dan capacity adalah resource global pada satu request.
```

## Fitur yang dibenarkan

- partner_shared_capacity
- marginal_gain_vs_fallback
- global_allocation_quantity

## Source boundary dan uncertainty

Prioritas marginal adalah parameter skenario sintetis.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-005 — Safety Override untuk Kaleng Rusak

```yaml
case_id: EVAL-005
title: Safety Override untuk Kaleng Rusak
case_type: HARD_SAFETY_REJECT
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-010
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bahwa kerusakan kemasan primer mengalahkan harga, demand, dan objective.

## Input lot

```yaml
planning_lot_id: PL-CANNED-005
product_name: Sarden kaleng
product_category: CANNED_FOOD
planning_quantity: 18
unit: CAN
packaging_condition: LEAKING_AND_SEVERE_RUST
seal_integrity: COMPROMISED
expiry_status: NOT_EXPIRED
verification_status: PHYSICALLY_INSPECTED
```

## Business capabilities

- can_discount=true
- can_donate=true
- can_return_supplier=false

## Partner snapshot

- Retail reseller menawarkan harga tinggi dan capacity 18.

## Global context

- Objective MAXIMIZE_NET_RECOVERY tidak mengubah safety gate.

## Expected routing

- safety=HARD_REJECT
- model_scoring=SKIPPED

## Expected feasible actions

- SAFE_DISPOSAL melalui approved route

## Forbidden atau unsafe actions

- LOCAL_DISCOUNT
- BUNDLE
- BONUS
- INTERNAL_USE
- DONATION
- WHOLESALE
- EXTERNAL_PARTNER

## Expected best action atau acceptable set

Safe disposal.

## Expected allocation

```yaml
allocations:
  - action: SAFE_DISPOSAL
    quantity: 18
human_consumption_allocation: 0
```

## Binding constraints

- Primary barrier failure
- Seal integrity
- No safety override

## Expected explanation

> Kaleng bocor dan berkarat berat diblokir dari seluruh jalur konsumsi walaupun belum kedaluwarsa.

## Failure conditions

- memberi score komersial
- mengizinkan donation
- menyamakan cosmetic dent dengan leak

## Locked rule

```text
SAFETY-RULE-001: leak, bulge, open seal, severe seam rust, contamination, atau expiry menghasilkan hard reject.
```

## Fitur yang dibenarkan

- defect_severity
- primary_barrier_integrity
- seal_integrity
- hard_reject_reason

## Source boundary dan uncertainty

Klasifikasi kerusakan harus membedakan HARD_REJECT, MANUAL_REVIEW, dan COSMETIC_SELLABLE.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-006 — Seasonality Window Berakhir Sebelum Expiry

```yaml
case_id: EVAL-006
title: Seasonality Window Berakhir Sebelum Expiry
case_type: SEASONAL_VALUE_WINDOW
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-015
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji pemisahan antara safety expiry dan commercial value window.

## Input lot

```yaml
planning_lot_id: PL-SYRUP-006
product_name: Sirup botol pasca-Lebaran
product_category: SEASONAL_BEVERAGE
planning_quantity: 24
unit: BOTTLE
remaining_shelf_life_days: 270
remaining_commercial_window_days: 7
product_condition: GOOD
```

## Business capabilities

- can_bundle=true
- bundle_capacity=8
- can_discount=true

## Partner snapshot

- Tidak ada partner dengan nilai lebih baik.

## Global context

- post_season=true
- commercial urgency tinggi walaupun safety urgency rendah

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- BUNDLE maksimal 8
- LOCAL_DISCOUNT maksimal 24

## Forbidden atau unsafe actions

- Hold seluruh lot sampai bulan depan
- SAFE_DISPOSAL

## Expected best action atau acceptable set

Bundle 8 dan markdown 16.

## Expected allocation

```yaml
allocations:
  - action: BUNDLE
    quantity: 8
  - action: LOCAL_DISCOUNT
    quantity: 16
unallocated_quantity: 0
```

## Binding constraints

- Bundle capacity
- Commercial window
- Shelf-life safety remains valid

## Expected explanation

> Sirup aman untuk waktu lama, tetapi nilai musiman turun cepat. Sistem bertindak berdasarkan commercial window tanpa menyebut produk unsafe.

## Failure conditions

- menyamakan commercial cutoff dengan expiry
- menahan semua barang karena expiry panjang
- membuang barang aman

## Locked rule

```text
TIMING-RULE-002: seasonal value window adalah constraint komersial terpisah dari expiry dan safety.
```

## Fitur yang dibenarkan

- seasonality_status
- remaining_commercial_window_days
- remaining_shelf_life_days
- post_season_discount

## Source boundary dan uncertainty

Control: biskuit nonmusiman dengan shelf life panjang boleh tetap MONITOR/HOLD.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-007 — Supplier Return Menang

```yaml
case_id: EVAL-007
title: Supplier Return Menang
case_type: SUPPLIER_RETURN_WINS
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-016
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji return-to-supplier ketika kebijakan retur terkonfirmasi, jumlah penuh diterima, dan nilai bersih mengalahkan fallback.

## Input lot

```yaml
planning_lot_id: PL-PACKAGED-007
product_name: Produk kemasan desain lama
product_category: PACKAGED_GOODS
planning_quantity: 30
unit: UNIT
remaining_shelf_life_days: 180
packaging_condition: INTACT
verification_status: VERIFIED
```

## Business capabilities

- can_return_supplier=true
- can_discount=true

## Partner snapshot

- Supplier menerima retur 30 unit dengan credit terkonfirmasi.

## Global context

- return deadline masih aktif
- transport cost rendah

## Expected routing

- RETURN_TO_SUPPLIER feasible
- LOCAL_DISCOUNT feasible

## Expected feasible actions

- Retur 30 unit

## Forbidden atau unsafe actions

- retur tanpa supplier confirmation
- mencatat refund kotor tanpa cost

## Expected best action atau acceptable set

Return to supplier untuk seluruh lot.

## Expected allocation

```yaml
allocations:
  - action: RETURN_TO_SUPPLIER
    quantity: 30
expected_unallocated_quantity: 0
```

## Binding constraints

- Return eligibility
- Confirmed credit
- Return deadline
- Net recovery after cost

## Expected explanation

> Retur dipilih karena seluruh lot eligible dan net supplier credit lebih tinggi daripada markdown.

## Failure conditions

- memilih retur berdasarkan asumsi kebijakan
- melebihi eligible quantity
- mengabaikan biaya

## Locked rule

```text
RETURN-RULE-001: supplier return hanya feasible dengan policy, deadline, quantity, tujuan, dan nilai bersih terverifikasi.
```

## Fitur yang dibenarkan

- supplier_return_status
- return_eligible_quantity
- supplier_credit
- return_deadline
- return_cost

## Source boundary dan uncertainty

Nilai finansial sintetis; pola retur bersyarat berasal dari incident keluarga.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-008 — Markdown Mengalahkan Retur Parsial yang Mahal

```yaml
case_id: EVAL-008
title: Markdown Mengalahkan Retur Parsial yang Mahal
case_type: LOCAL_DISCOUNT_BEATS_RETURN
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-016
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bahwa keberadaan opsi retur tidak otomatis membuat retur menjadi keputusan terbaik.

## Input lot

```yaml
planning_lot_id: PL-PACKAGED-008
product_name: Produk kemasan lama
product_category: PACKAGED_GOODS
planning_quantity: 24
unit: UNIT
remaining_shelf_life_days: 120
packaging_condition: INTACT
```

## Business capabilities

- can_return_supplier=true
- can_discount=true

## Partner snapshot

- Supplier hanya menerima 8 unit; biaya transport dan handling tinggi.

## Global context

- Local demand masih tersedia untuk 24 unit.

## Expected routing

- RETURN_TO_SUPPLIER maksimal 8
- LOCAL_DISCOUNT maksimal 24

## Expected feasible actions

- Return dipilih hanya karena ada policy

## Forbidden atau unsafe actions

- Retur parsial jika net gain positif tetapi lebih rendah daripada local fallback

## Expected best action atau acceptable set

Local discount untuk 24 unit.

## Expected allocation

```yaml
allocations:
  - action: LOCAL_DISCOUNT
    quantity: 24
rejected_alternative:
  action: RETURN_TO_SUPPLIER
  reason: net_recovery_below_local_fallback
```

## Binding constraints

- Net recovery comparison
- Partial eligibility
- Transport cost

## Expected explanation

> Retur ditolak karena kuantitas terbatas dan biaya menghapus keunggulannya dibanding markdown lokal.

## Failure conditions

- mengabaikan fallback
- mengirim 24 ketika eligible 8
- membandingkan gross credit dengan net local recovery

## Locked rule

```text
VALUE-RULE-001: action feasible belum tentu dipilih; bandingkan net marginal value terhadap fallback pada unit yang sama.
```

## Fitur yang dibenarkan

- return_eligible_quantity
- return_net_recovery
- fallback_net_recovery
- marginal_gain

## Source boundary dan uncertainty

Case ini adalah pasangan kontrol EVAL-007.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-009 — Internal Use Mengalahkan Retur dalam Batas Kebutuhan

```yaml
case_id: EVAL-009
title: Internal Use Mengalahkan Retur dalam Batas Kebutuhan
case_type: INTERNAL_USE_WITH_VERIFIED_NEED
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-011
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji internal use sebagai avoided purchase cost, bukan revenue, dan dibatasi kebutuhan operasional nyata.

## Input lot

```yaml
planning_lot_id: PL-DETERGENT-009
product_name: Detergen sachet
product_category: HOUSEHOLD_CLEANING
planning_quantity: 30
unit: SACHET
remaining_shelf_life_days: 300
packaging_condition: INTACT
```

## Business capabilities

- can_internal_use=true
- verified_internal_need_quantity=10
- can_discount=true
- can_return_supplier=true

## Partner snapshot

- Supplier return tersedia tetapi net value per unit lebih rendah daripada avoided purchase cost untuk 10 unit.

## Global context

- Internal need tidak boleh dilebihkan untuk mempercantik recovery.

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- INTERNAL_USE maksimal 10
- LOCAL_DISCOUNT untuk remainder
- RETURN_TO_SUPPLIER feasible tetapi inferior

## Forbidden atau unsafe actions

- Internal use >10
- mencatat internal use sebagai cash revenue

## Expected best action atau acceptable set

Internal use 10; local discount 20.

## Expected allocation

```yaml
allocations:
  - action: INTERNAL_USE
    quantity: 10
    value_type: AVOIDED_PURCHASE_COST
  - action: LOCAL_DISCOUNT
    quantity: 20
cash_recovery_and_avoided_cost_reported_separately: true
```

## Binding constraints

- Verified need
- Avoided cost
- Quantity conservation

## Expected explanation

> Sepuluh unit menggantikan pembelian operasional yang memang dibutuhkan. Sisa lot tetap masuk kanal penjualan.

## Failure conditions

- mengarang internal need
- menggabungkan avoided cost dengan cash
- menggunakan seluruh lot internal

## Locked rule

```text
VALUE-RULE-002: internal use dihitung sebagai avoided purchase cost dan tidak boleh melebihi verified internal need.
```

## Fitur yang dibenarkan

- verified_internal_need
- replacement_cost
- avoided_purchase_cost
- cash_recovery_type

## Source boundary dan uncertainty

Kuantitas sintetis; pola penggunaan non-food internal adalah rule candidate.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-010 — Mixed Allocation untuk Medium Wholesaler

```yaml
case_id: EVAL-010
title: Mixed Allocation untuk Medium Wholesaler
case_type: MULTI_CHANNEL_WHOLESALE_SPLIT
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-011
  - Incident-013
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji pembagian lot besar ke wholesale, branch, internal use, dan local discount berdasarkan demand serta kapasitas.

## Input lot

```yaml
planning_lot_id: PL-DETERGENT-010
product_name: Detergen sachet
product_category: HOUSEHOLD_CLEANING
planning_quantity: 120
unit: SACHET
packaging_condition: INTACT
verification_status: VERIFIED
```

## Business capabilities

- can_wholesale=true
- can_transfer_branch=true
- can_internal_use=true
- can_discount=true

## Partner snapshot

- Laundry wholesaler capacity=50
- Branch demand/capacity=30

## Global context

- Verified internal need=10
- Local demand supports remainder=30

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- WHOLESALE 50
- BRANCH_TRANSFER 30
- INTERNAL_USE 10
- LOCAL_DISCOUNT 30

## Forbidden atau unsafe actions

- alokasi melebihi channel capacity
- seluruh 120 ke satu channel

## Expected best action atau acceptable set

Mixed allocation penuh tanpa remainder.

## Expected allocation

```yaml
allocations:
  - action: WHOLESALE
    quantity: 50
  - action: BRANCH_TRANSFER
    quantity: 30
  - action: INTERNAL_USE
    quantity: 10
  - action: LOCAL_DISCOUNT
    quantity: 30
total_allocated_quantity: 120
```

## Binding constraints

- Channel capacity
- Partner demand
- Internal need
- Quantity conservation

## Expected explanation

> Lot besar dibagi ke empat jalur karena tidak ada satu channel yang mampu atau optimal menyerap seluruh unit.

## Failure conditions

- menyamakan transfer dengan cash revenue
- mengabaikan capacity
- remainder tidak dijelaskan

## Locked rule

```text
ALLOCATION-RULE-001: optimizer boleh membagi satu lot ke beberapa tindakan selama quantity dan semua resource constraints dipenuhi.
```

## Fitur yang dibenarkan

- channel_capacity
- allocation_mix
- cash_recovery
- future_branch_recovery
- avoided_purchase_cost

## Source boundary dan uncertainty

Value types harus dilaporkan terpisah.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-011 — Stale Partner Demand Harus Dikeluarkan

```yaml
case_id: EVAL-011
title: Stale Partner Demand Harus Dikeluarkan
case_type: STALE_DEMAND
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - AFTERLIFE_AI_MASTER_BLUEPRINT.md
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji registry freshness sebagai hard feasibility condition.

## Input lot

```yaml
planning_lot_id: PL-SNACK-011
product_name: Snack kemasan
product_category: PACKAGED_SNACK
planning_quantity: 30
unit: PACK
remaining_shelf_life_days: 40
```

## Business capabilities

- can_discount=true
- can_wholesale=true

## Partner snapshot

- P-HIGH: price tinggi, capacity 30, demand_valid_until sudah lewat
- P-ACTIVE: price lebih rendah, capacity 20, registry aktif

## Global context

- analysis_timestamp setelah expiry demand P-HIGH

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- P-ACTIVE maksimal 20
- LOCAL_DISCOUNT remainder 10

## Forbidden atau unsafe actions

- P-HIGH allocation
- rescoring stale partner tanpa confirmation

## Expected best action atau acceptable set

Partner aktif 20 dan local discount 10.

## Expected allocation

```yaml
allocations:
  - action: EXTERNAL_PARTNER
    destination: P-ACTIVE
    quantity: 20
  - action: LOCAL_DISCOUNT
    quantity: 10
rejected_partner: P-HIGH
```

## Binding constraints

- Demand freshness
- Capacity
- Quantity

## Expected explanation

> Partner dengan harga tertinggi dikeluarkan karena snapshot demand sudah kedaluwarsa.

## Failure conditions

- menganggap last_updated hanya metadata
- memilih stale price
- mengarang demand reconfirmation

## Locked rule

```text
DEMAND-RULE-001: partner dengan demand_valid_until terlewati tidak eligible tanpa human reconfirmation.
```

## Fitur yang dibenarkan

- demand_valid_until
- registry_freshness_status
- reconfirmation_required

## Source boundary dan uncertainty

Tidak ada klaim bahwa stale demand pasti nol; sistem hanya tidak boleh mengandalkannya otomatis.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-012 — Category Mismatch Ditolak Sebelum Scoring

```yaml
case_id: EVAL-012
title: Category Mismatch Ditolak Sebelum Scoring
case_type: PARTNER_CATEGORY_MISMATCH
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - AFTERLIFE_AI_MASTER_BLUEPRINT.md
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji pemisahan category compatibility dari harga dan capacity.

## Input lot

```yaml
planning_lot_id: PL-CLEANING-012
product_name: Pembersih lantai
product_category: HOUSEHOLD_CLEANING
planning_quantity: 24
unit: BOTTLE
```

## Business capabilities

- can_wholesale=true
- can_discount=true

## Partner snapshot

- P-BAKERY memberi harga tinggi tetapi accepted_categories hanya BAKERY
- P-LAUNDRY menerima HOUSEHOLD_CLEANING capacity 18

## Global context

- Local fallback tersedia untuk 6 unit.

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- P-LAUNDRY 18
- LOCAL_DISCOUNT 6

## Forbidden atau unsafe actions

- P-BAKERY allocation
- model scoring untuk category mismatch

## Expected best action atau acceptable set

Compatible partner dan local remainder.

## Expected allocation

```yaml
allocations:
  - action: EXTERNAL_PARTNER
    destination: P-LAUNDRY
    quantity: 18
  - action: LOCAL_DISCOUNT
    quantity: 6
```

## Binding constraints

- Accepted category
- Partner capacity
- No price override

## Expected explanation

> P-BAKERY dikeluarkan sebelum model karena category mismatch; harga tidak mengubah compatibility.

## Failure conditions

- memilih harga tertinggi
- category encoding dianggap similarity cukup
- scoring infeasible candidate

## Locked rule

```text
PARTNER-RULE-001: exact/approved category compatibility wajib sebelum ranking atau scoring.
```

## Fitur yang dibenarkan

- category_match_status
- accepted_categories
- compatibility_rejection_reason

## Source boundary dan uncertainty

Kategori harus berasal dari taxonomy yang terkontrol, bukan string similarity bebas.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-013 — Cold Chain Harus Valid End-to-End

```yaml
case_id: EVAL-013
title: Cold Chain Harus Valid End-to-End
case_type: COLD_CHAIN_COMPATIBILITY
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-008
  - External-Incident-003
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji source storage, transport, destination storage, dan handling history sebagai satu rangkaian.

## Input lot

```yaml
planning_lot_id: PL-DIMSUM-013
product_name: Dimsum ayam beku
product_category: FROZEN_PREPARED_FOOD
planning_quantity: 20
unit: PACK
required_storage_type: FROZEN
storage_history_status: VERIFIED
remaining_shelf_life_days: 45
```

## Business capabilities

- has_cold_storage=true
- can_discount=true

## Partner snapshot

- P-AMBIENT harga tinggi, transport AMBIENT
- P-FROZEN capacity=12, frozen transport dan storage tersedia

## Global context

- Local frozen clearance capacity=8

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- P-FROZEN 12
- LOCAL_DISCOUNT 8

## Forbidden atau unsafe actions

- P-AMBIENT
- transport duration melebihi allowed out-of-storage time

## Expected best action atau acceptable set

Frozen-compatible partner dan local frozen clearance.

## Expected allocation

```yaml
allocations:
  - action: EXTERNAL_PARTNER
    destination: P-FROZEN
    quantity: 12
  - action: LOCAL_DISCOUNT
    quantity: 8
cold_chain_violations: 0
```

## Binding constraints

- Source storage
- Transport storage
- Destination storage
- Handling continuity

## Expected explanation

> Partner ambient ditolak walaupun harga tinggi karena rantai dingin gagal pada transportasi.

## Failure conditions

- memeriksa storage tujuan saja
- mengabaikan transport
- menganggap produk frozen aman karena saat ini beku

## Locked rule

```text
STORAGE-RULE-001: seluruh tahap source-transfer-destination harus memenuhi requirement.
```

## Fitur yang dibenarkan

- source_storage
- transport_storage
- destination_storage
- cold_chain_status
- maximum_out_of_storage_hours

## Source boundary dan uncertainty

Batas temperatur spesifik tidak diklaim tanpa domain source; evaluasi memakai status kompatibilitas sintetis.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-014 — Logistics Budget Bersifat Global

```yaml
case_id: EVAL-014
title: Logistics Budget Bersifat Global
case_type: GLOBAL_LOGISTICS_BUDGET
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - AFTERLIFE_AI_MASTER_BLUEPRINT.md
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bahwa biaya partner dipilih lintas lot berdasarkan marginal gain, bukan budget terpisah per kandidat.

## Input lot

```yaml
planning_lots:
  - id: PL-A-014
    category: BAKERY
    quantity: 20
  - id: PL-B-014
    category: FROZEN_FOOD
    quantity: 15
  - id: PL-C-014
    category: HOUSEHOLD_CLEANING
    quantity: 25
```

## Business capabilities

- local fallback tersedia untuk seluruh lot

## Partner snapshot

- Partner A cost 10000, marginal gain 50000
- Partner B cost 20000, marginal gain 70000
- Partner C cost 15000, marginal gain 5000

## Global context

- max_logistics_budget=30000

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- Partner A dan B
- Local fallback untuk C

## Forbidden atau unsafe actions

- Memilih ketiga partner; total cost 45000
- first-row budget allocation tanpa gain

## Expected best action atau acceptable set

Gunakan budget 30.000 pada kombinasi A+B.

## Expected allocation

```yaml
selected_partner_costs:
  Partner-A: 10000
  Partner-B: 20000
  Partner-C: 0
total_logistics_cost: 30000
budget_violation: 0
```

## Binding constraints

- Global budget
- Marginal gain vs fallback
- Feasibility

## Expected explanation

> Partner C feasible tetapi tidak dipilih karena marginal gain kecil dan budget habis pada pilihan yang lebih bernilai.

## Failure conditions

- budget reset per lot
- cost >30000
- menganggap feasible sama dengan selected

## Locked rule

```text
BUDGET-RULE-001: total selected logistics cost pada satu request tidak boleh melebihi budget global.
```

## Fitur yang dibenarkan

- global_logistics_budget
- candidate_logistics_cost
- marginal_gain_per_budget_unit

## Source boundary dan uncertainty

Nilai marginal sintetis untuk menguji optimizer.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-015 — Tindakan Bernilai Tinggi Ditolak karena Terlalu Lambat

```yaml
case_id: EVAL-015
title: Tindakan Bernilai Tinggi Ditolak karena Terlalu Lambat
case_type: HIGH_VALUE_TOO_SLOW
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - External-Incident-003
  - External-Incident-009
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji hard deadline sebelum expected value ranking.

## Input lot

```yaml
planning_lot_id: PL-BAKERY-015
product_name: Pastry produksi hari ini
product_category: READY_TO_EAT_BAKERY
planning_quantity: 30
unit: PACK
remaining_safe_window_hours: 6
```

## Business capabilities

- can_discount=true
- can_donate=true

## Partner snapshot

- P-PREMIUM completion 10h, price tinggi
- P-LOCAL capacity 20 completion 2h
- Donation capacity 10 completion 4h

## Global context

- safe deadline=6h

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- P-LOCAL 20
- DONATION 10

## Forbidden atau unsafe actions

- P-PREMIUM
- extension of safe window

## Expected best action atau acceptable set

Partner cepat dan donation fallback.

## Expected allocation

```yaml
allocations:
  - action: EXTERNAL_PARTNER
    destination: P-LOCAL
    quantity: 20
  - action: DONATION
    quantity: 10
```

## Binding constraints

- Completion time
- Safe window
- Capacity

## Expected explanation

> Tindakan premium ditolak karena selesai setelah safe deadline; nilai potensialnya tidak dihitung sebagai feasible recovery.

## Failure conditions

- memilih action berdasarkan gross price
- menghasilkan score untuk late action
- menganggap pickup start sama dengan completion

## Locked rule

```text
TIMING-RULE-003: action completion, bukan hanya pickup start, harus berada dalam deadline.
```

## Fitur yang dibenarkan

- action_completion_time
- deadline_slack
- timing_rejection_reason

## Source boundary dan uncertainty

Durasi sintetis.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-016 — Wholesale Minimum Order dan Aggregation

```yaml
case_id: EVAL-016
title: Wholesale Minimum Order dan Aggregation
case_type: WHOLESALE_MOQ
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-009
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji minimum order quantity dan aggregation lintas lot yang kompatibel.

## Input lot

```yaml
planning_lots:
  - id: PL-SAUCE-A-016
    sku: SAUCE-1L-A
    quantity: 30
    unit: BOTTLE
  - id: PL-SAUCE-B-016
    sku: SAUCE-1L-B
    quantity: 25
    unit: BOTTLE
compatibility_group: LARGE_CONDIMENT
```

## Business capabilities

- can_wholesale=true
- aggregation_allowed=true
- can_discount=true

## Partner snapshot

- Wholesaler MOQ=50, capacity=50, menerima kedua SKU dalam satu compatible shipment

## Global context

- Total compatible quantity=55

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- WHOLESALE 50
- LOCAL_DISCOUNT 5

## Forbidden atau unsafe actions

- Wholesale per lot secara terpisah karena 30<50 dan 25<50
- allocation > capacity 50

## Expected best action atau acceptable set

Aggregate 50 unit dan fallback 5.

## Expected allocation

```yaml
allocations:
  - action: WHOLESALE
    quantity: 50
    source_lots: [PL-SAUCE-A-016, PL-SAUCE-B-016]
  - action: LOCAL_DISCOUNT
    quantity: 5
```

## Binding constraints

- MOQ
- Compatibility group
- Partner capacity
- Aggregation policy

## Expected explanation

> Dua lot dapat dikonsolidasikan karena format dan handling kompatibel. Control case aggregation_allowed=false harus menolak wholesale.

## Failure conditions

- mengabaikan MOQ
- menggabungkan kategori/storage tak kompatibel
- melebihi capacity

## Locked rule

```text
WHOLESALE-RULE-001: MOQ dapat dipenuhi melalui aggregation hanya jika partner dan domain rule mengizinkan compatibility group tersebut.
```

## Fitur yang dibenarkan

- wholesale_moq
- aggregation_allowed
- compatibility_group
- aggregated_quantity

## Source boundary dan uncertainty

Aggregation policy harus eksplisit, bukan asumsi optimizer.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-017 — Internal Repurpose Dibatasi Resource Minimum

```yaml
case_id: EVAL-017
title: Internal Repurpose Dibatasi Resource Minimum
case_type: LIMITED_REPURPOSE_CAPACITY
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-004
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji kapasitas repurpose sebagai minimum dari equipment, labor, ingredient, dan demand.

## Input lot

```yaml
planning_lot_id: PL-SACHET-017
product_name: Minuman sachet slow-moving
product_category: POWDERED_BEVERAGE_SACHET
planning_quantity: 50
unit: SACHET
```

## Business capabilities

- equipment_capacity=30
- labor_capacity=25
- ingredient_capacity=20
- repurpose_demand=35
- can_bundle=true
- can_discount=true

## Partner snapshot

- Tidak ada partner eksternal dominan.

## Global context

- max repurpose=min(30,25,20,35)=20

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- INTERNAL_REPURPOSE 20
- BUNDLE 15
- LOCAL_DISCOUNT 15

## Forbidden atau unsafe actions

- Repurpose 50
- mengabaikan bahan atau labor

## Expected best action atau acceptable set

Mixed allocation dengan repurpose 20.

## Expected allocation

```yaml
allocations:
  - action: INTERNAL_REPURPOSE
    quantity: 20
  - action: BUNDLE
    quantity: 15
  - action: LOCAL_DISCOUNT
    quantity: 15
```

## Binding constraints

- Resource minimum
- Demand capacity
- Quantity conservation

## Expected explanation

> Bahan menjadi binding constraint, sehingga hanya 20 sachet dapat ditransformasi.

## Failure conditions

- mengambil max resource
- menggunakan capacity boolean
- remainder tidak dialokasikan

## Locked rule

```text
CAPABILITY-RULE-002: repurpose_capacity=min(equipment,labor,ingredient,demand).
```

## Fitur yang dibenarkan

- equipment_capacity
- labor_capacity
- ingredient_capacity
- repurpose_demand
- binding_resource

## Source boundary dan uncertainty

Capacity sintetis.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-018 — Bundle Companion Stock Dibatasi

```yaml
case_id: EVAL-018
title: Bundle Companion Stock Dibatasi
case_type: LIMITED_BUNDLE_COMPANION
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-007
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bahwa bundling membutuhkan companion stock yang benar-benar allocatable setelah reservation.

## Input lot

```yaml
planning_lot_id: PL-CEREAL-018
product_name: Sereal sarapan
product_category: BREAKFAST_FOOD
planning_quantity: 30
unit: PACK
```

## Business capabilities

- can_bundle=true
- companion_product=MILK
- companion_current_quantity=12
- companion_reserved_quantity=4
- bundle_ratio=1:1
- can_discount=true

## Partner snapshot

- Tidak ada partner eksternal lebih baik.

## Global context

- allocatable companion=8
- bundle maximum=8

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- BUNDLE 8
- LOCAL_DISCOUNT 22

## Forbidden atau unsafe actions

- Bundle 12 atau 30
- menggunakan reserved stock

## Expected best action atau acceptable set

Bundle sesuai companion allocatable, lalu local markdown.

## Expected allocation

```yaml
allocations:
  - action: BUNDLE
    quantity: 8
    companion_quantity_used: 8
  - action: LOCAL_DISCOUNT
    quantity: 22
```

## Binding constraints

- Companion stock
- Reserved quantity
- Bundle ratio
- Demand

## Expected explanation

> Hanya delapan bundle dibuat karena empat dari dua belas companion units dilindungi untuk operasi normal.

## Failure conditions

- reserved stock violation
- ratio violation
- menganggap companion tersedia tanpa SKU check

## Locked rule

```text
BUNDLE-RULE-001: max bundle quantity dibatasi allocatable companion stock, ratio, demand, dan execution capacity.
```

## Fitur yang dibenarkan

- companion_stock
- reserved_companion_stock
- bundle_ratio
- max_bundle_quantity

## Source boundary dan uncertainty

Quantity sintetis; kompatibilitas sarapan berasal dari incident family.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-019 — Bonus Promosi Tidak Boleh Mengarang Sales Uplift

```yaml
case_id: EVAL-019
title: Bonus Promosi Tidak Boleh Mengarang Sales Uplift
case_type: PROMOTIONAL_BONUS_WITHOUT_FAKE_UPLIFT
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-001
  - Incident-012
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bonus pada item unit kecil dengan constraint transaksi dan pelaporan nilai yang jujur.

## Input lot

```yaml
planning_lot_id: PL-SACHET-019
product_name: Sampo sachet slow-moving
product_category: PERSONAL_CARE_SACHET
planning_quantity: 40
unit: SACHET
unit_cost: 1200
```

## Business capabilities

- can_offer_bonus=true
- qualifying_transactions=20
- max_bonus_per_transaction=1
- primary_margin_floor=5000
- can_discount=true

## Partner snapshot

- Tidak membutuhkan partner.

## Global context

- Bonus capacity=20
- campaign main margin harus tetap memenuhi floor

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- PROMOTIONAL_BONUS 20
- LOCAL_DISCOUNT 20

## Forbidden atau unsafe actions

- Bonus 40
- klaim bonus meningkatkan penjualan sekian persen
- cash recovery dari bonus

## Expected best action atau acceptable set

Bonus terbatas dan fallback lokal.

## Expected allocation

```yaml
allocations:
  - action: PROMOTIONAL_BONUS
    quantity: 20
    direct_cash_recovery: 0
  - action: LOCAL_DISCOUNT
    quantity: 20
claimed_sales_uplift: null
```

## Binding constraints

- Qualifying transaction
- Bonus per transaction
- Campaign margin
- No invented causal effect

## Expected explanation

> Bonus digunakan hanya pada dua puluh transaksi yang memenuhi syarat. Sistem tidak mengatribusi uplift tanpa observasi.

## Failure conditions

- menghitung bonus sebagai penjualan
- membuat causal uplift sintetis sebagai fakta
- melanggar margin floor

## Locked rule

```text
BONUS-RULE-001: bonus feasible hanya dalam batas transaksi dan margin; manfaat tidak langsung dilaporkan sebagai unknown tanpa evidence.
```

## Fitur yang dibenarkan

- qualifying_transactions
- max_bonus_per_transaction
- campaign_margin
- direct_cash_recovery
- uplift_evidence_status

## Source boundary dan uncertainty

Pola bonus didukung incident; outcome penjualan tidak diketahui.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-020 — Donasi Sukses dengan Penerima dan Pickup Terverifikasi

```yaml
case_id: EVAL-020
title: Donasi Sukses dengan Penerima dan Pickup Terverifikasi
case_type: VERIFIED_DONATION_SUCCESS
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - External-Incident-003
  - External-Incident-005
  - External-Incident-007
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji donation path ketika sale cutoff lewat tetapi kualitas, recipient, capacity, pickup, dan same-day distribution terpenuhi.

## Input lot

```yaml
planning_lot_id: PL-BAKERY-020
product_name: Paket bakery siap makan
product_category: READY_TO_EAT_BAKERY
planning_quantity: 30
unit: PACK
quality_inspection_status: PASSED
commercial_sale_cutoff_status: PASSED
remaining_safe_window_hours: 8
same_day_consumption_required: true
```

## Business capabilities

- can_donate=true
- local_sales_channel_closed=true

## Partner snapshot

- Verified foodbank: active need 40, capacity 40, pickup 2h, inspection/repackaging tersedia, same-day distribution

## Global context

- Local discount completion 10h; reseller pickup unavailable/9h

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- DONATION 30

## Forbidden atau unsafe actions

- late local discount
- late reseller
- unverified recipient

## Expected best action atau acceptable set

Donasi seluruh 30 pack.

## Expected allocation

```yaml
allocations:
  - action: DONATION
    destination: VERIFIED_FOODBANK
    quantity: 30
cash_recovery: 0
physical_rescue_quantity: 30
human_review_required: true
```

## Binding constraints

- Quality gate
- Verified partner
- Active need/capacity
- Pickup and distribution deadline

## Expected explanation

> Donasi dipilih karena satu-satunya jalur yang menyelesaikan pickup dan distribusi sebelum safe deadline.

## Failure conditions

- mengklaim cash recovery
- donasi tanpa quality check
- menganggap sistem mensertifikasi keamanan fisik

## Locked rule

```text
DONATION-RULE-001: donation memerlukan kualitas acceptable, verified partner, active need/capacity, handling cocok, dan completion tepat waktu.
```

## Fitur yang dibenarkan

- recipient_verification
- active_recipient_need
- pickup_completion
- same_day_distribution
- donation_cash_recovery

## Source boundary dan uncertainty

Sistem merencanakan, bukan menyertifikasi keamanan atau mengeksekusi pickup.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-021 — Donasi Diblokir karena Tidak Ada Jalur Feasible

```yaml
case_id: EVAL-021
title: Donasi Diblokir karena Tidak Ada Jalur Feasible
case_type: NO_FEASIBLE_DONATION_PARTNER
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - External-Incident-003
  - External-Incident-004
  - External-Incident-005
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji donation abstention ketika capacity ada tanpa recipient need, atau recipient ada tetapi pickup terlambat.

## Input lot

```yaml
planning_lot_id: PL-MEAL-021
product_name: Paket makanan matang hari ini
product_category: READY_TO_EAT_MEAL
planning_quantity: 20
unit: PACK
quality_inspection_status: PASSED
remaining_safe_window_hours: 3
same_day_consumption_required: true
```

## Business capabilities

- can_donate=true
- commercial_channel_closed=true
- no_verified_internal_need=true

## Partner snapshot

- P-FOODBANK: capacity 30, active recipient need 0, pickup 1h
- P-SHELTER: active need 25, capacity 25, pickup 5h + distribution 1h

## Global context

- manual reverification window=1h

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- Tidak ada automatic donation candidate

## Forbidden atau unsafe actions

- donasi ke capacity-only partner
- donasi completion 6h pada safe window 3h

## Expected best action atau acceptable set

NO_FEASIBLE_DONATION_PARTNER; bounded manual verification; time-triggered safe disposal.

## Expected allocation

```yaml
automatic_allocated_quantity: 0
human_review_required: true
manual_reverification_window_hours: 1
fallback_if_unresolved: SAFE_DISPOSAL
```

## Binding constraints

- Active need
- Pickup completion
- Distribution completion
- Bounded review

## Expected explanation

> Capacity kosong bukan active demand. Partner dengan recipient aktif juga ditolak karena distribusi selesai setelah safe deadline.

## Failure conditions

- mengarang recipient
- menunggu melewati safe window
- langsung membuang tanpa review window

## Locked rule

```text
DONATION-RULE-002: donation membutuhkan active verified recipient need dan completion sebelum safe deadline.
```

## Fitur yang dibenarkan

- active_recipient_need_quantity
- available_capacity
- total_donation_completion_time
- reverification_cutoff

## Source boundary dan uncertainty

Safe disposal adalah fallback time-triggered, bukan rekomendasi otomatis pertama.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-022 — Cacat Kosmetik Tetap Sellable

```yaml
case_id: EVAL-022
title: Cacat Kosmetik Tetap Sellable
case_type: COSMETIC_DEFECT_SELLABLE
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-016
  - External-Incident-016
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji pemisahan cosmetic defect dari primary-barrier damage.

## Input lot

```yaml
planning_lot_id: PL-SYRUP-022
product_name: Sirup botol dengan desain label lama
product_category: PACKAGED_BEVERAGE
planning_quantity: 24
unit: BOTTLE
unit_cost: 12000
normal_selling_price: 24000
remaining_shelf_life_days: 210
product_condition: GOOD
packaging_condition: COSMETIC_LABEL_DAMAGE
primary_container_integrity: INTACT
seal_integrity: INTACT
leakage_status: NONE
expiry_label_readable: true
lot_code_readable: true
quality_inspection_status: PASSED
```

## Business capabilities

- can_discount=true
- can_return_supplier=true

## Partner snapshot

- Supplier return feasible dengan net recovery Rp243.000.

## Global context

- Local markdown 10%; disclosure required; expected net recovery Rp470.928

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- LOCAL_DISCOUNT 24

## Forbidden atau unsafe actions

- SAFE_DISPOSAL sebagai best action
- sale tanpa quality inspection/disclosure

## Expected best action atau acceptable set

Local discount untuk seluruh lot.

## Expected allocation

```yaml
allocations:
  - action: LOCAL_DISCOUNT
    quantity: 24
    discount_percent: 10
    expected_net_recovery: 470928
rejected_return_expected_net_recovery: 243000
unnecessary_disposal_quantity: 0
```

## Binding constraints

- Cosmetic-only defect
- Primary barrier intact
- Readable traceability
- Disclosure

## Expected explanation

> Label lama atau tergores menurunkan nilai komersial tetapi tidak otomatis menghapus sellability setelah quality gate.

## Failure conditions

- menyamakan cosmetic dengan leak
- menjual control case dengan seal rusak
- membuang produk aman

## Locked rule

```text
QUALITY-RULE-002: COSMETIC_ONLY boleh masuk commercial rescue; AMBIGUOUS perlu review; SAFETY_CRITICAL hard reject.
```

## Fitur yang dibenarkan

- defect_type
- defect_affects_primary_barrier
- traceability_readable
- condition_disclosure_required

## Source boundary dan uncertainty

Control case seal compromised harus berubah menjadi hard reject.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-023 — Riwayat Suhu atau Penyimpanan Tidak Diketahui

```yaml
case_id: EVAL-023
title: Riwayat Suhu atau Penyimpanan Tidak Diketahui
case_type: UNKNOWN_STORAGE_HISTORY
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - External_Incident_001-016_Indonesia(1).md
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji verification hold untuk produk storage-sensitive meskipun kondisi saat ini tampak normal.

## Input lot

```yaml
planning_lot_id: PL-DIMSUM-023
product_name: Dimsum ayam beku
product_category: FROZEN_PREPARED_FOOD
planning_quantity: 24
unit: PACK
required_storage_type: FROZEN
current_storage_type: FROZEN
product_condition: VISUALLY_NORMAL
packaging_condition: INTACT
storage_history_status: UNKNOWN
temperature_log_available: false
receipt_timestamp_verified: false
remaining_shelf_life_days: 60
verification_status: PARTIALLY_VERIFIED
```

## Business capabilities

- has_cold_storage=true
- can_discount=true

## Partner snapshot

- Frozen reseller dan local frozen discount tampak ekonomis tetapi belum eligible.

## Global context

- manual review window=2h

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- Tidak ada action konsumsi sebelum clearance

## Forbidden atau unsafe actions

- LOCAL_DISCOUNT
- EXTERNAL_PARTNER
- DONATION
- INTERNAL_USE sebelum review

## Expected best action atau acceptable set

PENDING_VERIFICATION; outcome review menentukan release atau hard reject.

## Expected allocation

```yaml
automatic_allocated_quantity: 0
model_scoring: DEFERRED
human_review_required: true
review_deadline_hours: 2
possible_outcomes:
  - VERIFIED_ACCEPTABLE
  - VERIFIED_FAILURE
  - UNRESOLVED
```

## Binding constraints

- Storage sensitivity
- Evidence continuity
- No current-state inference

## Expected explanation

> Penyimpanan saat ini sesuai tidak membuktikan seluruh riwayat. Sistem meminta log, receipt record, pemeriksaan, dan konfirmasi petugas.

## Failure conditions

- menganggap expiry membuktikan cold chain
- langsung membuang tanpa review
- menganggap unknown aman

## Locked rule

```text
VERIFICATION-RULE-001: unknown required storage history pada produk sensitif memblokir automatic consumption allocation.
```

## Fitur yang dibenarkan

- storage_history_status
- temperature_log_available
- possible_excursion
- safety_clearance_status

## Source boundary dan uncertainty

Control nonperishable dengan kemasan utuh tidak boleh otomatis mengikuti aturan frozen.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-024 — Expired Tetap Hard Reject meskipun Nilainya Tinggi

```yaml
case_id: EVAL-024
title: Expired Tetap Hard Reject meskipun Nilainya Tinggi
case_type: EXPIRED_HARD_REJECT
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-003
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bahwa expiry lewat menghapus seluruh human-consumption channel.

## Input lot

```yaml
planning_lot_id: PL-BISCUIT-024
product_name: Biskuit kaleng premium
product_category: PACKAGED_BISCUIT
planning_quantity: 30
unit: CAN
unit_cost: 45000
normal_selling_price: 70000
expiry_date: 2026-08-01
analysis_date: 2026-08-03
remaining_shelf_life_days: -2
packaging_condition: INTACT
seal_integrity: INTACT
expiry_status: EXPIRED
```

## Business capabilities

- can_discount=true
- can_wholesale=true
- can_donate=true
- can_return_supplier=false

## Partner snapshot

- Demand komersial dan donation capacity tersedia tetapi tidak relevant setelah expiry gate.

## Global context

- estimated_inventory_cost=Rp1.350.000

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- SAFE_DISPOSAL

## Forbidden atau unsafe actions

- LOCAL_DISCOUNT
- BUNDLE
- BONUS
- WHOLESALE
- DONATION
- INTERNAL_USE

## Expected best action atau acceptable set

Safe disposal 30 unit.

## Expected allocation

```yaml
allocations:
  - action: SAFE_DISPOSAL
    quantity: 30
expected_cash_recovery: 0
expected_inventory_loss: 1350000
human_consumption_allocation: 0
```

## Binding constraints

- Expiry date
- Analysis date
- No value override

## Expected explanation

> Kemasan utuh dan nilai modal tinggi tidak mengubah status expired. Supplier return hanya boleh untuk recall/non-consumption flow yang terkonfirmasi.

## Failure conditions

- memberi rescue score
- donasi expired
- menganggap expired sekadar near-expiry

## Locked rule

```text
EXPIRY-RULE-001: expiry_date < analysis_date memblokir seluruh human-consumption action.
```

## Fitur yang dibenarkan

- analysis_date
- expiry_status
- supplier_recall_policy_status
- inventory_loss

## Source boundary dan uncertainty

Control case remaining shelf life 14 hari harus tetap dapat dinilai sebagai near-expiry, bukan hard reject.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-025 — Kapasitas Cold Storage Dibagi Global

```yaml
case_id: EVAL-025
title: Kapasitas Cold Storage Dibagi Global
case_type: SHARED_COLD_STORAGE_CAPACITY
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-006
  - Incident-008
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji prioritas binding storage requirement sebelum optional chilled display.

## Input lot

```yaml
planning_lots:
  - id: PL-CHOCOLATE-025
    product_category: CHOCOLATE
    quantity: 20
    storage_requirement_mode: COLD_REQUIRED_FOR_QUALITY_WINDOW
  - id: PL-DRINK-025
    product_category: PACKAGED_BEVERAGE
    quantity: 24
    storage_requirement_mode: CHILLED_PREFERRED
cold_storage:
  total_capacity_units: 40
  reserved_capacity_units: 8
  available_capacity_units: 32
```

## Business capabilities

- has_cold_storage=true
- ambient sale allowed for beverage

## Partner snapshot

- Tidak membutuhkan partner.

## Global context

- Chocolate required 20 capacity units
- Drink chilled marginal gain Rp2.650/unit

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- Chocolate cold 20
- Drink chilled 12
- Drink ambient 12

## Forbidden atau unsafe actions

- Drink chilled 24 + chocolate cold 8
- use reserved 8

## Expected best action atau acceptable set

Binding cold requirement lebih dulu, optional gain memakai remainder.

## Expected allocation

```yaml
allocations:
  - lot: PL-CHOCOLATE-025
    action: INTERNAL_COLD_STORAGE
    quantity: 20
  - lot: PL-DRINK-025
    action: CHILLED_LOCAL_SALE
    quantity: 12
  - lot: PL-DRINK-025
    action: AMBIENT_LOCAL_DISCOUNT
    quantity: 12
cold_capacity_used: 32
expected_total_net_recovery: 426200
```

## Binding constraints

- Shared cold capacity
- Reserved capacity
- Storage priority
- Marginal value

## Expected explanation

> Kebutuhan kualitas yang mengikat dipenuhi sebelum kapasitas tersisa digunakan untuk menaikkan demand minuman.

## Failure conditions

- capacity per lot
- optional chilled mendahului required
- reserved capacity violation

## Locked rule

```text
STORAGE-RULE-002: safety-critical lalu quality-critical lalu optional chilled value.
```

## Fitur yang dibenarkan

- available_cold_capacity
- storage_requirement_mode
- marginal_value_per_capacity_unit
- capacity_shortfall

## Source boundary dan uncertainty

Control capacity 12 harus menghasilkan shortfall 8 untuk cokelat dan tidak memberi slot pada minuman.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-026 — Branch Transfer vs Local Markdown

```yaml
case_id: EVAL-026
title: Branch Transfer vs Local Markdown
case_type: BRANCH_TRANSFER_VS_MARKDOWN
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-013
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji transfer hanya sampai demand/capacity tujuan dan hanya bila net future recovery mengalahkan local fallback.

## Input lot

```yaml
planning_lot_id: PL-DIAPER-026
product_name: Popok bayi ukuran S
product_category: BABY_DIAPER
planning_quantity: 24
unit: PACK
unit_cost: 37000
normal_selling_price: 50000
remaining_shelf_life_days: 360
source_branch_id: BRANCH-01
```

## Business capabilities

- can_transfer_branch=true
- has_delivery_access=true
- can_discount=true

## Partner snapshot

- BRANCH-02 demand=18, capacity=18, expected price 48000, score 0.92, transport+handling=72000

## Global context

- Local discount price 41000, score 0.78

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- BRANCH_TRANSFER 18
- LOCAL_DISCOUNT 6

## Forbidden atau unsafe actions

- Transfer 24
- transfer dicatat sebagai immediate cash

## Expected best action atau acceptable set

Transfer 18 dan markdown 6.

## Expected allocation

```yaml
allocations:
  - action: BRANCH_TRANSFER
    destination: BRANCH-02
    quantity: 18
    expected_future_branch_recovery: 722880
  - action: LOCAL_DISCOUNT
    quantity: 6
    expected_cash_recovery: 191880
total_expected_economic_recovery: 914760
```

## Binding constraints

- Destination demand/capacity
- Transfer cost
- Future vs immediate value

## Expected explanation

> Transfer memberikan marginal gain Rp147.240 dibanding all-local, tetapi hanya untuk 18 pack yang dapat diserap cabang.

## Failure conditions

- transfer melebihi 18
- cash revenue saat transfer
- tetap memilih transfer pada high-cost control

## Locked rule

```text
TRANSFER-RULE-001: branch transfer feasible dan selected hanya jika compatibility, demand, capacity, deadline, dan net gain terpenuhi.
```

## Fitur yang dibenarkan

- destination_branch_demand
- transfer_cost
- future_branch_recovery
- marginal_gain_vs_local

## Source boundary dan uncertainty

Control transport+handling Rp240.000 harus mengubah hasil menjadi all local discount.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-027 — Kemasan Besar Cocok ke Mitra B2B

```yaml
case_id: EVAL-027
title: Kemasan Besar Cocok ke Mitra B2B
case_type: PACKAGE_SIZE_DEMAND_MATCH
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident-009
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji partner matching berdasarkan kategori, ukuran, customer segment, dan use case.

## Input lot

```yaml
planning_lot_id: PL-SOY-027
product_name: Kecap manis botol besar
product_category: LARGE_CONDIMENT
planning_quantity: 24
unit: BOTTLE
package_volume_ml: 1000
unit_cost: 12000
normal_selling_price: 22000
remaining_shelf_life_days: 210
```

## Business capabilities

- can_wholesale=true
- can_discount=true

## Partner snapshot

- P-MINIMARKET: accepts soy sauce, size 50-250ml, price 19500
- P-WARUNG: size 500-2000ml, active demand/capacity 18, price 17500, score 0.94

## Global context

- Local discount fallback for 6

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- P-WARUNG 18
- LOCAL_DISCOUNT 6

## Forbidden atau unsafe actions

- P-MINIMARKET walau price lebih tinggi
- category-only matching

## Expected best action atau acceptable set

B2B food-service partner dan local fallback.

## Expected allocation

```yaml
allocations:
  - action: EXTERNAL_PARTNER
    destination: P-WARUNG
    quantity: 18
    expected_net_recovery: 296100
  - action: LOCAL_DISCOUNT
    quantity: 6
    expected_net_recovery: 68880
total_expected_net_recovery: 364980
```

## Binding constraints

- Package size range
- Customer segment
- Usage context
- Demand/capacity

## Expected explanation

> Minimarket ditolak karena household package range tidak cocok. Warung makan menerima format 1L sesuai penggunaan rutin.

## Failure conditions

- memilih price tertinggi
- mengabaikan package size
- selalu mengirim semua kecap ke B2B

## Locked rule

```text
PARTNER-RULE-004: compatibility membutuhkan category, package size/format, segment, use case, demand, capacity, storage, dan logistics.
```

## Fitur yang dibenarkan

- package_volume
- partner_size_range
- customer_segment_match
- use_case_match

## Source boundary dan uncertainty

Control package 135ml harus membuat minimarket feasible dan prioritas.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-028 — Out-of-Distribution Harus Abstain

```yaml
case_id: EVAL-028
title: Out-of-Distribution Harus Abstain
case_type: OUT_OF_SUPPORTED_DOMAIN
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - AFTERLIFE_AI_MASTER_BLUEPRINT.md
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji domain coverage gate sebelum model confidence.

## Input lot

```yaml
planning_lot_id: PL-SHELLFISH-028
product_name: Kerang hidup
product_category: LIVE_SHELLFISH
planning_quantity: 18
unit: KG
business_type: SEAFOOD_DISTRIBUTOR
required_storage_type: CONTROLLED_AQUATIC_STORAGE
current_storage_type: UNKNOWN
harvest_timestamp: UNKNOWN
water_quality_history: UNKNOWN
traceability_document_status: NOT_AVAILABLE
verification_status: LOW
```

## Business capabilities

- Business profile di luar target MVP.

## Partner snapshot

- Seafood restaurant dan foodbank menunjukkan capacity, tetapi domain rules tidak tersedia.

## Global context

- Category, business type, storage type, dan critical features unsupported

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- Tidak ada automatic feasible action

## Forbidden atau unsafe actions

- LOCAL_DISCOUNT
- EXTERNAL_PARTNER
- DONATION
- SAFE_DISPOSAL otomatis tanpa expert review

## Expected best action atau acceptable set

UNSUPPORTED_SCENARIO dan domain-expert review.

## Expected allocation

```yaml
system_status: UNSUPPORTED_SCENARIO
automatic_allocated_quantity: 0
estimated_rescue_success_score: null
optimizer_execution: BLOCKED
human_review_required: true
review_type: DOMAIN_EXPERT_REVIEW
```

## Binding constraints

- Supported taxonomy
- Storage requirement support
- Critical feature coverage
- Applicable rule set

## Expected explanation

> Confidence model tidak dapat membuat unsupported case menjadi valid. Coverage gate menghentikan scoring.

## Failure conditions

- menghasilkan score 0.91
- mengarang shellfish safety rule
- mengganti missing critical features dengan default optimistis

## Locked rule

```text
COVERAGE-RULE-001: unsupported critical domain dimensions menghasilkan abstention sebelum model.
```

## Fitur yang dibenarkan

- supported_business_type
- supported_category
- supported_storage
- critical_feature_coverage
- abstention_reason

## Source boundary dan uncertainty

Control frozen prepared dimsum dengan verified history harus lolos coverage.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-029 — Objective Mengubah Keputusan

```yaml
case_id: EVAL-029
title: Objective Mengubah Keputusan
case_type: OBJECTIVE_SENSITIVITY
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - AFTERLIFE_AI_MASTER_BLUEPRINT.md
  - External_Incident_001-016_Indonesia(1).md
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji bahwa MAXIMIZE_RECOVERY_VALUE, MINIMIZE_WASTE, dan BALANCED menghasilkan allocation berbeda tanpa mengubah hard constraints.

## Input lot

```yaml
planning_lot_id: PL-BAKERY-029
product_name: Roti manis layak konsumsi
product_category: READY_TO_EAT_BAKERY
planning_quantity: 40
unit: PACK
quality_inspection_status: PASSED
remaining_safe_window_hours: 8
```

## Business capabilities

- can_discount=true
- can_donate=true

## Partner snapshot

- Commercial partner max 15
- Donation partner max 40

## Global context

- Local discount max 25, recovery/unit 4800, rescue 0.80
- Partner recovery/unit 4000, rescue 0.90
- Donation recovery 0, rescue 0.98

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- Semua tiga action feasible

## Forbidden atau unsafe actions

- Tidak ada hard-constraint action yang berubah antar-objective

## Expected best action atau acceptable set

Tiga run dengan allocation berbeda.

## Expected allocation

```yaml
runs:
  MAXIMIZE_RECOVERY_VALUE:
    LOCAL_DISCOUNT: 25
    EXTERNAL_PARTNER: 15
    DONATION: 0
    expected_net_recovery: 180000
    expected_rescue: 33.5
  MINIMIZE_WASTE:
    LOCAL_DISCOUNT: 0
    EXTERNAL_PARTNER: 0
    DONATION: 40
    expected_net_recovery: 0
    expected_rescue: 39.2
  BALANCED:
    rescue_floor: 0.90
    LOCAL_DISCOUNT: 11
    EXTERNAL_PARTNER: 15
    DONATION: 14
    expected_net_recovery: 112800
    expected_rescue: 36.02
```

## Binding constraints

- Objective formula
- Partner/action capacities
- Hard constraints unchanged
- Explicit rescue floor

## Expected explanation

> Balanced memaksimalkan recovery setelah mensyaratkan expected rescue minimal 90%, bukan memakai weighted sum tanpa skala.

## Failure conditions

- allocation sama untuk semua objective
- donation dihitung cash
- safety berubah karena objective
- balanced tanpa formula

## Locked rule

```text
OBJECTIVE-RULE-001: objective memilih di antara feasible candidates; hard constraints tidak berubah.
```

## Fitur yang dibenarkan

- optimization_objective
- rescue_floor
- expected_net_recovery
- expected_physical_rescue
- tradeoff_amount

## Source boundary dan uncertainty

Score dan target 90% sintetis; bukan kebijakan universal.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.


---

# EVAL-030 — End-to-End Multi-Lot Stress Test

```yaml
case_id: EVAL-030
title: End-to-End Multi-Lot Stress Test
case_type: END_TO_END_STRESS_TEST
evaluation_layer: CORE_RESCUE_PLANNER
input_entity: SURPLUS_PLANNING_LOT
source_type: INCIDENT_OR_RULE_GROUNDED_SYNTHETIC
source_references:
  - Incident_001-016_Family_Corroborated(1).txt
  - External_Incident_001-016_Indonesia(1).md
  - AFTERLIFE_AI_MASTER_BLUEPRINT.md
synthetic_status: SYNTHETIC_PARAMETERS_WITH_SOURCE_GROUNDED_RULES
optimization_objective: BALANCED
```

## Tujuan

Menguji validation, safety, verification, registry freshness, compatibility, scoring, global budget, objective, optimization, fallback, dan explanation dalam satu request.

## Input lot

```yaml
planning_lots:
  - id: LOT-A
    product: Roti hari ini
    quantity: 30
    status: SAFE_URGENT
  - id: LOT-B
    product: Dimsum beku
    quantity: 20
    status: SAFE_FROZEN_VERIFIED
  - id: LOT-C
    product: Sirup pascamusim
    quantity: 16
    status: SAFE_COMMERCIAL_URGENT
  - id: LOT-D
    product: Detergen sachet
    quantity: 40
    status: SAFE_NONPERISHABLE
  - id: LOT-E
    product: Biskuit expired
    quantity: 10
    status: HARD_REJECT
  - id: LOT-F
    product: Yogurt chilled
    quantity: 8
    status: PENDING_VERIFICATION
eligible_quantity: 106
hard_reject_quantity: 10
pending_review_quantity: 8
```

## Business capabilities

- discount, donation, internal use, bundle, frozen handling tersedia sesuai lot

## Partner snapshot

- Stale canteen rejected
- P-CAFE active
- P-FOODBANK active
- Ambient frozen partner rejected
- P-FROZEN active
- Laundry partner feasible but inferior

## Global context

- objective=BALANCED
- minimum_expected_rescue_ratio=0.90
- max_logistics_budget=30000

## Expected routing

- Input lot sudah berada pada layer Core Rescue Planner.
- Jalankan validation, coverage, safety, verification, dan feasibility gate sebelum model scoring.

## Expected feasible actions

- Eligible lots scored/optimized
- expired hard reject
- yogurt deferred

## Forbidden atau unsafe actions

- stale partner
- ambient frozen transport
- expired consumption
- unknown-history yogurt automatic allocation

## Expected best action atau acceptable set

Mixed end-to-end plan dengan rescue floor terpenuhi.

## Expected allocation

```yaml
allocations:
  LOT-A:
    EXTERNAL_PARTNER: 20
    DONATION: 10
  LOT-B:
    EXTERNAL_PARTNER: 12
    LOCAL_DISCOUNT: 8
  LOT-C:
    BUNDLE: 4
    LOCAL_DISCOUNT: 12
  LOT-D:
    INTERNAL_USE: 5
    LOCAL_DISCOUNT: 35
  LOT-E:
    SAFE_DISPOSAL: 10
  LOT-F:
    PENDING_HUMAN_REVIEW: 8
metrics:
  expected_physical_rescue: 95.95
  eligible_quantity: 106
  expected_rescue_ratio: 0.9052
  expected_cash_and_future_recovery: 568395
  avoided_purchase_cost: 8500
  total_economic_value: 576895
  logistics_cost: 30000
```

## Binding constraints

- Denominator excludes hard reject and pending review
- Global budget
- Safety
- Demand freshness
- Cold chain
- Value type separation

## Expected explanation

> Empat lot dialokasikan otomatis, expired dibuang aman, dan yogurt ditahan untuk review. Budget 30.000 habis tepat dan rescue floor 90% terlampaui.

## Failure conditions

- memasukkan expired/pending ke rescue denominator
- budget >30000
- donation sebagai cash
- internal use sebagai revenue
- model score pada LOT-E/F

## Locked rule

```text
PIPELINE-RULE-001: validate → route statuses → generate → gate → score feasible only → optimize global → fallback → explain → human approval.
```

## Fitur yang dibenarkan

- eligible_rescue_denominator
- status_routing
- global_budget
- value_type
- rejection_explanation
- rescue_floor_status

## Source boundary dan uncertainty

Semua angka dan scores sintetis; stress test memvalidasi konsistensi pipeline, bukan outcome lapangan.

**Catatan umum:** nilai quantity, harga, duration, capacity, score, dan recovery yang tidak secara eksplisit berasal dari catatan transaksi adalah parameter sintetis untuk evaluation. Kasus ini tidak membuktikan probabilitas keberhasilan dunia nyata.
