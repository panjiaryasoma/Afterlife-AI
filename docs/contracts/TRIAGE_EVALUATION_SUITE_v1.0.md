# Afterlife AI — Triage Evaluation Suite v1.0

**Status:** `LOCKED_LOGIC_WITH_OPEN_POLICY_DEPENDENCIES`  
**Phase:** Preproduction  
**Production implementation:** Blocked  
**Cases:** `TRIAGE-001` sampai `TRIAGE-008`

## 1. Purpose

Suite ini mengunci perilaku Inventory Triage Gate sebelum implementasi dimulai. Triage menentukan:

1. top-level routing status untuk satu lot;
2. pembagian kuantitas secara MECE;
3. berapa unit yang boleh masuk Rescue Planner;
4. kapan sistem harus berhenti dan meminta review;
5. kapan model dan optimizer dilarang berjalan.

Suite ini tidak menguji candidate-action feasibility, rescue-success model, final allocation, atau optimizer.

## 2. Locked architecture principles

### 2.1 Top-Level Routing Status berbeda dari Quantity Buckets

`inventory_status` menentukan jalur utama lot:

```text
HEALTHY_STOCK
MONITOR
SURPLUS_CANDIDATE
EXPIRED
NEEDS_REVIEW
```

Quantity buckets menentukan nasib setiap unit:

```text
protected_normal_stock_quantity
monitor_quantity
planning_quantity
expired_quantity
review_quantity
```

Status hibrida seperti `SURPLUS_WITH_MONITOR` tidak digunakan. Kondisi campuran direpresentasikan melalui quantity buckets.

### 2.2 MECE quantity invariant

```text
protected_normal_stock_quantity
+ monitor_quantity
+ planning_quantity
+ expired_quantity
+ review_quantity
= current_quantity
```

### 2.3 Planner dan model memiliki boundary berbeda

```text
Triage
→ membuka atau menutup planner

Planner
→ membangkitkan candidate action

Hard gates
→ menyaring candidate

Model
→ memberi score hanya pada candidate feasible

Optimizer
→ memilih allocation dari candidate valid
```

`planner_entry: true` tidak berarti model langsung berjalan.

### 2.4 Monitor semantics

`monitor_quantity` adalah **Protected Stock with Early Warning**:

- tetap boleh melalui penjualan normal;
- tidak boleh masuk Rescue Planner;
- tidak boleh menghasilkan candidate action;
- tidak boleh diberi model score;
- harus dipantau dan dinilai ulang.

### 2.5 Safety and compliance precedence

Expiry dan hard safety evidence mengalahkan harga, demand, sales velocity, declared surplus, model score, dan optimization objective.

### 2.6 Abstention principle

```text
missing safety evidence
→ NEEDS_REVIEW

missing surplus evidence
→ NEEDS_REVIEW
```

`unknown` bukan otomatis safe dan bukan otomatis unsafe.

### 2.7 Evidence authority boundary

| Evidence | Boleh menentukan | Tidak boleh menentukan |
|---|---|---|
| Safety/expiry evidence | Aman, review, hard reject | Besarnya surplus |
| Verification/coverage | Bukti cukup atau tidak | Demand nyata |
| Declared surplus | Declared quantity | Remainder, safety, final action |
| Sales evidence | Calculated surplus | Safety |
| Fixture assumption | Logika acceptance case | Kebijakan bisnis nyata |

## 3. Coverage matrix

| Case | Protected | Monitor | Planning | Expired | Review | Top-level status | Planner |
|---|---:|---:|---:|---:|---:|---|---|
| TRIAGE-001 | 15 | 0 | 0 | 0 | 0 | `HEALTHY_STOCK` | Closed |
| TRIAGE-002 | 15 | 0 | 10 | 0 | 0 | `SURPLUS_CANDIDATE` | Open for 10 |
| TRIAGE-003 | 0 | 10 | 0 | 0 | 0 | `MONITOR` | Closed |
| TRIAGE-004 | 0 | 10 | 15 | 0 | 0 | `SURPLUS_CANDIDATE` | Open for 15 |
| TRIAGE-005 | 0 | 0 | 0 | 12 | 0 | `EXPIRED` | Closed |
| TRIAGE-006 | 0 | 0 | 0 | 0 | 20 | `NEEDS_REVIEW` | Closed |
| TRIAGE-007 | 0 | 0 | 0 | 0 | 24 | `NEEDS_REVIEW` | Closed |
| TRIAGE-008 | 0 | 0 | 8 | 0 | 12 | `SURPLUS_CANDIDATE` | Open for 8 |

## 4. Acceptance Cases

---

# TRIAGE-001 — Healthy Stock Tidak Boleh Masuk Rescue Planner

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-001
title: Healthy Stock Tidak Boleh Masuk Rescue Planner
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: Stok yang seluruhnya masih dibutuhkan untuk penjualan normal dan safety stock harus dilindungi dari Rescue Planner.
test_scope:
  validates:
  - deterministic triage calculation
  - healthy stock routing
  - quantity conservation
  - planner exclusion
  - model exclusion
  does_not_validate:
  - realism of the 10-day window
  - category default policy
  - shelf-life window derivation
  - fallback when policy is missing
policy_context:
  effective_sales_window_days: 10
  value_source: FIXTURE_ASSUMPTION
  policy_status: NOT_CATEGORY_DEFAULT
  notes: Nilai 10 hari hanya digunakan sebagai parameter sintetis pada acceptance case dan belum menjadi default policy untuk kategori PACKAGED_BEVERAGE.
input:
  product:
    lot_id: LOT-HEALTHY-001
    sku: DRINK-001
    product_name: Minuman Serbuk Kemasan
    product_category: PACKAGED_BEVERAGE
  inventory:
    current_quantity: 15
    unit: sachet
  sales_evidence:
    units_sold_observation_window: 30
    observation_days: 30
    effective_sales_window_days: 10
    safety_stock: 5
  condition:
    expiry_status: VALID
    packaging_condition: INTACT
    storage_history: VERIFIED
    verification_status: VERIFIED
  user_declaration:
    declared_surplus: false
    declared_surplus_quantity: 0
calculations:
  average_daily_sales:
    formula: units_sold_observation_window / observation_days
    expression: 30 / 30
    result: 1.0
  expected_normal_sales:
    formula: average_daily_sales * effective_sales_window_days
    expression: 1.0 * 10
    result: 10
  normal_stock_requirement_quantity:
    formula: expected_normal_sales + safety_stock
    expression: 10 + 5
    result: 15
  surplus_candidate_quantity:
    formula: max(0, current_quantity - normal_stock_requirement_quantity)
    expression: max(0, 15 - 15)
    result: 0
  planning_quantity: 0
expected:
  inventory_status: HEALTHY_STOCK
  quantities:
    protected_normal_stock_quantity: 15
    monitor_quantity: 0
    planning_quantity: 0
    expired_quantity: 0
    review_quantity: 0
  routing:
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    human_review_required: false
  reporting:
    reason_code: WITHIN_PROTECTED_NORMAL_STOCK
    explanation: Seluruh 15 sachet masih dibutuhkan untuk memenuhi estimasi penjualan normal dan safety stock. Tidak terdapat excess quantity yang dapat diperlakukan sebagai surplus.
quantity_invariant:
  formula: protected_normal_stock_quantity + monitor_quantity + planning_quantity + expired_quantity + review_quantity == current_quantity
  assertion: 15 + 0 + 0 + 0 + 0 == 15
  expected_result: PASS
planner_boundary:
  planner_eligible_quantity: 0
  planner_excluded_quantity: 15
failure_conditions:
- inventory_status != HEALTHY_STOCK
- planning_quantity > 0
- candidate_generation == true
- model_scoring != NOT_APPLICABLE
- optimizer_entry == true
- human_review_required == true
- protected_normal_stock_quantity != 15
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

# TRIAGE-002 — Partial Surplus Harus Masuk Planner Tanpa Menyentuh Stok Normal

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-002
title: Partial Surplus Harus Masuk Planner Tanpa Menyentuh Stok Normal
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: Hanya excess quantity yang boleh masuk Rescue Planner; stok normal tetap dilindungi.
test_scope:
  validates:
  - deterministic surplus calculation
  - partial-surplus routing
  - normal-stock protection
  - quantity conservation
  - planner transition
  - downstream model eligibility boundary
  does_not_validate:
  - realism of the 10-day window
  - category default policy
  - action feasibility
  - rescue-success scoring
  - final allocation
  - optimizer behavior
policy_context:
  effective_sales_window_days: 10
  value_source: FIXTURE_ASSUMPTION
  policy_status: NOT_CATEGORY_DEFAULT
  notes: Nilai 10 hari digunakan hanya untuk menguji kalkulasi partial surplus.
input:
  product:
    lot_id: LOT-PARTIAL-SURPLUS-001
    sku: DRINK-002
    product_name: Minuman Serbuk Kemasan
    product_category: PACKAGED_BEVERAGE
  inventory:
    current_quantity: 25
    unit: sachet
  sales_evidence:
    units_sold_observation_window: 30
    observation_days: 30
    effective_sales_window_days: 10
    safety_stock: 5
  condition:
    expiry_status: VALID
    packaging_condition: INTACT
    storage_history: VERIFIED
    verification_status: VERIFIED
  user_declaration:
    declared_surplus: false
    declared_surplus_quantity: 0
calculations:
  average_daily_sales:
    expression: 30 / 30
    result: 1.0
  expected_normal_sales:
    expression: 1.0 * 10
    result: 10
  normal_stock_requirement_quantity:
    expression: 10 + 5
    result: 15
  surplus_candidate_quantity:
    expression: max(0, 25 - 15)
    result: 10
  planning_quantity:
    source: CALCULATED_SURPLUS
    result: 10
expected:
  inventory_status: SURPLUS_CANDIDATE
  quantities:
    protected_normal_stock_quantity: 15
    monitor_quantity: 0
    planning_quantity: 10
    expired_quantity: 0
    review_quantity: 0
  routing:
    planner_entry: true
    planner_eligible_quantity: 10
    candidate_generation: ALLOWED_DOWNSTREAM
    model_scoring: PENDING_DOWNSTREAM_GATES
    optimizer_entry: NOT_YET_APPLICABLE
    human_review_required: false
  reporting:
    reason_code: PARTIAL_EXCESS_ABOVE_PROTECTED_STOCK
    explanation: Dari 25 sachet tersedia, 15 sachet dilindungi dan hanya 10 sachet excess diteruskan ke Rescue Planner.
quantity_invariant:
  assertion: 15 + 0 + 10 + 0 + 0 == 25
  expected_result: PASS
planner_partition_invariant:
  planner_eligible_quantity: 10
  planner_excluded_quantity: 15
  forbidden_planner_quantity: 25
failure_conditions:
- inventory_status != SURPLUS_CANDIDATE
- protected_normal_stock_quantity != 15
- planning_quantity != 10
- planner_entry != true
- planner menerima seluruh current_quantity
- protected stock ikut masuk planning_quantity
- model langsung memberi score sebelum downstream gates
- optimizer langsung menerima lot sebelum candidate generation
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

# TRIAGE-003 — Near-Window Stock Harus Dipantau Tanpa Masuk Rescue Planner

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-003
title: Near-Window Stock Harus Dipantau Tanpa Masuk Rescue Planner
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: MONITOR adalah protected stock with early warning, bukan surplus.
test_scope:
  validates:
  - monitor-status routing
  - mutual exclusivity between protected_normal_stock and monitor_quantity
  - zero-surplus planner exclusion
  - quantity conservation
  - model exclusion
  - explicit monitoring trigger reporting
  does_not_validate:
  - realism of the 14-day monitor threshold
  - category-specific expiry policy
  - commercial cutoff policy
  - shelf-life policy for all packaged beverages
  - rescue action feasibility
  - model scoring
  - optimizer behavior
policy_context:
  effective_sales_window_days: 10
  expiry_monitor_threshold_days: 14
  value_source:
    effective_sales_window_days: FIXTURE_ASSUMPTION
    expiry_monitor_threshold_days: FIXTURE_ASSUMPTION
  policy_status: NOT_CATEGORY_DEFAULT
  monitor_rule_under_test: Jika remaining_shelf_life_days <= expiry_monitor_threshold_days, lot aman, valid, dan surplus nol, lot dirutekan ke MONITOR.
input:
  product:
    lot_id: LOT-MONITOR-001
    sku: DRINK-003
    product_name: Minuman Serbuk Kemasan
    product_category: PACKAGED_BEVERAGE
  inventory:
    current_quantity: 10
    unit: sachet
  sales_evidence:
    units_sold_observation_window: 30
    observation_days: 30
    effective_sales_window_days: 10
    safety_stock: 0
  shelf_life:
    remaining_shelf_life_days: 12
    expiry_monitor_threshold_days: 14
  condition:
    expiry_status: VALID
    packaging_condition: INTACT
    storage_history: VERIFIED
    verification_status: VERIFIED
  user_declaration:
    declared_surplus: false
    declared_surplus_quantity: 0
calculations:
  average_daily_sales:
    expression: 30 / 30
    result: 1.0
  expected_normal_sales:
    expression: 1.0 * 10
    result: 10
  normal_stock_requirement_quantity:
    expression: 10 + 0
    result: 10
  surplus_candidate_quantity:
    expression: max(0, 10 - 10)
    result: 0
  monitoring_reclassification_quantity: 10
  planning_quantity: 0
expected:
  inventory_status: MONITOR
  quantities:
    protected_normal_stock_quantity: 0
    monitor_quantity: 10
    planning_quantity: 0
    expired_quantity: 0
    review_quantity: 0
  routing:
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    human_review_required: false
  monitor_semantics:
    protection_class: PROTECTED_FROM_RESCUE_INTERVENTION
    normal_sales_allowed: true
    planner_eligible: false
    model_eligible: false
    optimizer_eligible: false
    operational_action: OBSERVE_AND_REASSESS
  monitoring:
    monitor_trigger: EXPIRY_WINDOW_APPROACHING
    recommended_review_interval_days: null
    next_review_policy: PENDING_POLICY_CONFIGURATION
  reporting:
    reason_code: WITHIN_EXPIRY_MONITOR_WINDOW
    explanation: Seluruh 10 sachet masih diperkirakan terserap normal, tetapi telah berada dalam monitoring window. Lot dipantau dan tidak masuk planner.
quantity_invariant:
  assertion: 0 + 10 + 0 + 0 + 0 == 10
  expected_result: PASS
planner_partition_invariant:
  planner_eligible_quantity: 0
  planner_excluded_quantity: 10
failure_conditions:
- inventory_status != MONITOR
- monitor_quantity != 10
- protected_normal_stock_quantity > 0
- planning_quantity > 0
- planner_entry == true
- candidate_generation == true
- model_scoring != NOT_APPLICABLE
- optimizer_entry == true
- status menjadi SURPLUS_CANDIDATE hanya karena monitoring window
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

# TRIAGE-004 — Partial Surplus Near Expiry Harus Memisahkan Monitor dan Planning Quantity

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-004
title: Partial Surplus Near Expiry Harus Memisahkan Monitor dan Planning Quantity
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: Top-level routing status menentukan jalur utama lot; quantity buckets menentukan nasib unit secara MECE.
test_scope:
  validates:
  - mixed quantity partition
  - partial-surplus routing
  - monitor protection semantics
  - planner eligibility limited to planning quantity
  - quantity conservation
  - model eligibility boundary
  does_not_validate:
  - realism of the 10-day sales window
  - realism of the 14-day monitor threshold
  - category-specific expiry policy
  - candidate action feasibility
  - rescue-success scoring
  - optimizer allocation
policy_context:
  effective_sales_window_days: 10
  expiry_monitor_threshold_days: 14
  value_source:
    effective_sales_window_days: FIXTURE_ASSUMPTION
    expiry_monitor_threshold_days: FIXTURE_ASSUMPTION
  policy_status: NOT_CATEGORY_DEFAULT
  mixed_routing_rule_under_test: Excess quantity masuk planning_quantity; kebutuhan stok normal yang berada dalam monitoring window masuk monitor_quantity.
  hybrid_status_policy: FORBIDDEN
input:
  product:
    lot_id: LOT-MIXED-001
    sku: DRINK-004
    product_name: Minuman Serbuk Kemasan
    product_category: PACKAGED_BEVERAGE
  inventory:
    current_quantity: 25
    unit: sachet
  sales_evidence:
    units_sold_observation_window: 30
    observation_days: 30
    effective_sales_window_days: 10
    safety_stock: 0
  shelf_life:
    remaining_shelf_life_days: 12
    expiry_monitor_threshold_days: 14
  condition:
    expiry_status: VALID
    packaging_condition: INTACT
    storage_history: VERIFIED
    verification_status: VERIFIED
  user_declaration:
    declared_surplus: false
    declared_surplus_quantity: 0
calculations:
  average_daily_sales:
    expression: 30 / 30
    result: 1.0
  expected_normal_sales:
    expression: 1.0 * 10
    result: 10
  normal_stock_requirement_quantity:
    expression: 10 + 0
    result: 10
  surplus_candidate_quantity:
    expression: max(0, 25 - 10)
    result: 15
  monitoring_reclassification_quantity:
    source: normal_stock_requirement_quantity
    result: 10
  planning_quantity:
    source: surplus_candidate_quantity
    result: 15
expected:
  inventory_status: SURPLUS_CANDIDATE
  quantities:
    protected_normal_stock_quantity: 0
    monitor_quantity: 10
    planning_quantity: 15
    expired_quantity: 0
    review_quantity: 0
  routing:
    planner_entry: true
    planner_eligible_quantity: 15
    candidate_generation: ALLOWED_DOWNSTREAM
    model_scoring: PENDING_DOWNSTREAM_GATES
    optimizer_entry: NOT_YET_APPLICABLE
    human_review_required: false
  monitoring:
    monitor_trigger: EXPIRY_WINDOW_APPROACHING
    monitored_quantity: 10
    protection_class: PROTECTED_FROM_RESCUE_INTERVENTION
    operational_action: OBSERVE_AND_REASSESS
  reporting:
    reason_code: PARTIAL_EXCESS_WITH_MONITORED_NORMAL_STOCK
    explanation: Sepuluh sachet tetap dilindungi sebagai monitored stock dan 15 sachet excess diteruskan ke planner.
quantity_invariant:
  assertion: 0 + 10 + 15 + 0 + 0 == 25
  expected_result: PASS
planner_partition_invariant:
  planner_eligible_quantity: 15
  planner_excluded_quantity: 10
  assertion: 15 + 10 == 25
model_boundary:
  eligible_source_quantity: 15
  assertions:
  - monitor_quantity tidak menghasilkan candidate action
  - model tidak menerima monitored stock
  - hanya candidate dari planning_quantity dapat dinilai
  - scoring menunggu downstream gates
failure_conditions:
- inventory_status != SURPLUS_CANDIDATE
- monitor_quantity != 10
- planning_quantity != 15
- planner menerima seluruh 25 unit
- monitor_quantity ikut candidate generation
- model langsung memberi score sebelum downstream gates
- inventory_status menjadi SURPLUS_WITH_MONITOR
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

# TRIAGE-005 — Expired Stock Harus Keluar dari Jalur Rescue Konsumsi

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-005
title: Expired Stock Harus Keluar dari Jalur Rescue Konsumsi
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: Safety and compliance selalu mengalahkan commercial signals.
test_scope:
  validates:
  - explicit-expiry hard routing
  - expiry precedence over sales and value signals
  - full expired-quantity assignment
  - rescue-planner exclusion
  - model exclusion
  - optimizer exclusion
  - quantity conservation
  does_not_validate:
  - legal disposal procedure
  - recall logistics
  - category-specific disposal method
  - mixed-expiry rows
  - unreadable or uncertain expiry date
  - hazardous-waste handling
policy_context:
  analysis_date: '2026-08-04'
  expiry_rule_source: EXPLICIT_EXPIRY_DATE
  expiry_hard_reject_status: LOCKED
  open_policy:
  - final disposal instruction
  - supplier recall eligibility
  - category-specific legal handling
  notes: Fixture menguji expiry precedence dan terminal routing, bukan metode disposal final.
input:
  product:
    lot_id: LOT-EXPIRED-001
    sku: DRINK-005
    product_name: Minuman Serbuk Kemasan
    product_category: PACKAGED_BEVERAGE
  inventory:
    current_quantity: 12
    unit: sachet
  shelf_life:
    expiry_date: '2026-08-03'
    expiry_date_readability: VERIFIED
  sales_evidence:
    units_sold_observation_window: 60
    observation_days: 30
    safety_stock: 5
  commercial_context:
    unit_cost: 2000
    normal_selling_price: 3500
  condition:
    packaging_condition: INTACT
    storage_history: VERIFIED
    verification_status: VERIFIED
  user_declaration:
    declared_surplus: false
    declared_surplus_quantity: 0
calculations:
  remaining_shelf_life_days:
    formula: expiry_date - analysis_date
    expression: 2026-08-03 - 2026-08-04
    result: -1
  expiry_status:
    rule: remaining_shelf_life_days < 0
    result: EXPIRED
  sales_based_surplus_calculation:
    execution_status: SKIPPED
    reason: EXPIRED_PRECEDENCE
  planning_quantity: 0
expected:
  inventory_status: EXPIRED
  quantities:
    protected_normal_stock_quantity: 0
    monitor_quantity: 0
    planning_quantity: 0
    expired_quantity: 12
    review_quantity: 0
  routing:
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    human_review_required: false
  terminal_routing:
    route: NON_CONSUMPTION_PATH
    consumption_channels_allowed: false
    safe_disposal_instruction: PENDING_DETERMINISTIC_POLICY
    supplier_recall_check: OPTIONAL_DOWNSTREAM_RULE
  reporting:
    reason_code: EXPIRED_HARD_REJECT
    explanation: Tanggal kedaluwarsa telah lewat. Seluruh 12 sachet dikeluarkan dari planner, model, optimizer, dan kanal konsumsi.
quantity_invariant:
  assertion: 0 + 0 + 0 + 12 + 0 == 12
  expected_result: PASS
expiry_precedence_invariant:
  if:
    expiry_status: EXPIRED
  then:
    inventory_status: EXPIRED
    planning_quantity: 0
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    consumption_channels_allowed: false
failure_conditions:
- inventory_status != EXPIRED
- expired_quantity != 12
- planning_quantity > 0
- planner_entry == true
- candidate_generation == true
- model_scoring != NOT_APPLICABLE
- optimizer_entry == true
- consumption_channels_allowed == true
- status berubah karena sales atau commercial value
- sistem memilih disposal method tanpa policy
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

# TRIAGE-006 — Missing Critical Storage Evidence Harus Menghasilkan NEEDS_REVIEW

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-006
title: Missing Critical Storage Evidence Harus Menghasilkan NEEDS_REVIEW
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: Unknown bukan safe, tetapi unknown juga bukan otomatis unsafe; critical uncertainty memerlukan abstention.
test_scope:
  validates:
  - conservative routing under missing critical evidence
  - NEEDS_REVIEW top-level status
  - full review-quantity assignment
  - planner exclusion
  - model exclusion
  - optimizer exclusion
  - human-review requirement
  - quantity conservation
  does_not_validate:
  - whether the product is actually safe or unsafe
  - final disposal decision
  - cold-chain legal standard
  - category-specific temperature threshold
  - result of human inspection
  - action feasibility after review
policy_context:
  storage_evidence_required: true
  value_source: FIXTURE_POLICY_ASSUMPTION
  policy_status: NOT_GLOBAL_CATEGORY_DEFAULT
  critical_evidence_under_test:
  - storage_history
  - temperature_evidence
  review_rule_under_test: Jika cold-chain evidence yang diwajibkan tidak tersedia, seluruh lot masuk NEEDS_REVIEW sebelum surplus calculation, planner, model, atau optimizer.
input:
  product:
    lot_id: LOT-REVIEW-001
    sku: FROZEN-001
    product_name: Frozen Prepared Food
    product_category: FROZEN_PREPARED_FOOD
  inventory:
    current_quantity: 20
    unit: pack
  shelf_life:
    expiry_date: '2026-09-15'
    expiry_date_readability: VERIFIED
  sales_evidence:
    units_sold_observation_window: 12
    observation_days: 30
    safety_stock: 4
  condition:
    packaging_condition: INTACT
    seal_integrity: INTACT
    storage_history: UNKNOWN
    temperature_evidence: MISSING
    verification_status: VERIFIED
    verification_scope: LOT_IDENTITY_AND_BASIC_FIELDS_ONLY
  user_declaration:
    declared_surplus: false
    declared_surplus_quantity: 0
evaluation:
  expiry_check:
    result: VALID
  packaging_check:
    result: INTACT
  critical_storage_evidence_check:
    required: true
    storage_history: UNKNOWN
    temperature_evidence: MISSING
    result: INSUFFICIENT_EVIDENCE
  sales_based_surplus_calculation:
    execution_status: SKIPPED
    reason: CRITICAL_STORAGE_EVIDENCE_MISSING
  planning_quantity: 0
expected:
  inventory_status: NEEDS_REVIEW
  quantities:
    protected_normal_stock_quantity: 0
    monitor_quantity: 0
    planning_quantity: 0
    expired_quantity: 0
    review_quantity: 20
  routing:
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    human_review_required: true
  review:
    review_trigger: CRITICAL_STORAGE_EVIDENCE_MISSING
    missing_evidence:
    - storage_history
    - temperature_evidence
    required_review_actions:
    - verify cold-chain or storage history
    - inspect available temperature records
    - obtain category-appropriate safety confirmation
    automatic_resolution_allowed: false
    review_deadline: null
    review_deadline_policy: PENDING_POLICY_CONFIGURATION
  reporting:
    reason_code: UNKNOWN_STORAGE_HISTORY
    explanation: Riwayat penyimpanan dan bukti suhu tidak tersedia. Seluruh 20 pack ditahan dalam NEEDS_REVIEW.
quantity_invariant:
  assertion: 0 + 0 + 0 + 0 + 20 == 20
  expected_result: PASS
abstention_invariant:
  if:
    critical_evidence_status: INSUFFICIENT
  then:
    inventory_status: NEEDS_REVIEW
    planning_quantity: 0
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    human_review_required: true
failure_conditions:
- inventory_status != NEEDS_REVIEW
- review_quantity != 20
- planning_quantity > 0
- planner_entry == true
- candidate_generation == true
- model_scoring != NOT_APPLICABLE
- optimizer_entry == true
- human_review_required != true
- sistem mengasumsikan storage history aman
- sistem mengimputasi temperature evidence
- sistem memilih disposal sebelum review
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

# TRIAGE-007 — Missing Sales Evidence Harus Menghasilkan NEEDS_REVIEW

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-007
title: Missing Sales Evidence Harus Menghasilkan NEEDS_REVIEW
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: Safety validation bukan surplus validation; tanpa demand evidence, sistem dilarang menebak healthy atau surplus.
test_scope:
  validates:
  - abstention when surplus evidence is insufficient
  - separation between safety validation and surplus validation
  - NEEDS_REVIEW routing
  - full review-quantity assignment
  - planner exclusion
  - model exclusion
  - optimizer exclusion
  - quantity conservation
  does_not_validate:
  - minimum observation period per category
  - imputation strategy for sales history
  - realism of future sales demand
  - validity of user-declared surplus
  - action feasibility
  - rescue-success scoring
  - optimizer behavior
policy_context:
  calculated_surplus_requires_sales_evidence: true
  minimum_required_evidence:
  - units_sold_observation_window
  - observation_days
  alternative_surplus_source:
    source: USER_DECLARED
    allowed_if_valid: true
  value_source: CONTRACT_RULE
  policy_status: PARTIALLY_OPEN
  open_policy:
  - minimum observation days per category
  - minimum transaction completeness
  - acceptable sales-history source
  - treatment of temporary stockout periods
  rule_under_test: Tanpa sales evidence dan tanpa declared surplus valid, seluruh lot masuk NEEDS_REVIEW.
input:
  product:
    lot_id: LOT-SALES-REVIEW-001
    sku: DRINK-007
    product_name: Minuman Serbuk Kemasan
    product_category: PACKAGED_BEVERAGE
  inventory:
    current_quantity: 24
    unit: sachet
  shelf_life:
    expiry_date: '2026-12-31'
    expiry_date_readability: VERIFIED
  sales_evidence:
    units_sold_observation_window: null
    observation_days: null
    sales_evidence_status: MISSING
    safety_stock: 5
  condition:
    packaging_condition: INTACT
    storage_history: VERIFIED
    verification_status: VERIFIED
  user_declaration:
    declared_surplus: false
    declared_surplus_quantity: 0
evaluation:
  expiry_check:
    result: VALID
  safety_check:
    result: PASSED
  verification_check:
    result: PASSED
  declared_surplus_check:
    declared_surplus: false
    valid_declared_surplus_available: false
  calculated_surplus_evidence_check:
    units_sold_observation_window: MISSING
    observation_days: MISSING
    result: INSUFFICIENT_EVIDENCE
  surplus_calculation:
    execution_status: SKIPPED
    reason: SALES_EVIDENCE_MISSING
  planning_quantity: 0
expected:
  inventory_status: NEEDS_REVIEW
  quantities:
    protected_normal_stock_quantity: 0
    monitor_quantity: 0
    planning_quantity: 0
    expired_quantity: 0
    review_quantity: 24
  routing:
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    human_review_required: true
  review:
    review_trigger: SURPLUS_EVIDENCE_INSUFFICIENT
    missing_evidence:
    - units_sold_observation_window
    - observation_days
    acceptable_resolution_paths:
    - provide valid sales history
    - provide valid user-declared surplus quantity
    automatic_imputation_allowed: false
    automatic_surplus_assumption_allowed: false
    automatic_healthy_assumption_allowed: false
  reporting:
    reason_code: SALES_EVIDENCE_MISSING
    explanation: Kondisi dan expiry terverifikasi, tetapi data penjualan tidak tersedia. Seluruh 24 sachet ditahan dalam NEEDS_REVIEW.
quantity_invariant:
  assertion: 0 + 0 + 0 + 0 + 24 == 24
  expected_result: PASS
surplus_abstention_invariant:
  if:
    calculated_surplus_evidence: INSUFFICIENT
    valid_declared_surplus_available: false
  then:
    inventory_status: NEEDS_REVIEW
    planning_quantity: 0
    planner_entry: false
    candidate_generation: false
    model_scoring: NOT_APPLICABLE
    optimizer_entry: false
    human_review_required: true
failure_conditions:
- inventory_status != NEEDS_REVIEW
- review_quantity != 24
- planning_quantity > 0
- planner_entry == true
- candidate_generation == true
- model_scoring != NOT_APPLICABLE
- optimizer_entry == true
- human_review_required != true
- sistem mengimputasi sales evidence
- sistem menganggap seluruh lot HEALTHY_STOCK
- sistem menganggap seluruh lot SURPLUS_CANDIDATE
- sistem menghitung surplus hanya dari current_quantity dan safety_stock
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

# TRIAGE-008 — Valid Declared Surplus Harus Membatasi Planner pada Kuantitas yang Dideklarasikan

**Status:** `LOCKED_LOGIC`  
**Policy dependency:** `OPEN`

```yaml
case_id: TRIAGE-008
title: Valid Declared Surplus Harus Membatasi Planner pada Kuantitas yang Dideklarasikan
status: LOCKED_LOGIC
policy_dependency: OPEN
governing_principle: Bukti hanya berlaku dalam ruang lingkup yang dibuktikannya; declared surplus tidak membuktikan remainder sehat dan tidak mengalahkan safety.
test_scope:
  validates:
  - valid user-declared surplus routing
  - partial planning quantity from declaration
  - conservative treatment of undeclared remainder
  - separation between declared evidence and calculated evidence
  - quantity conservation
  - planner eligibility boundary
  - downstream model eligibility boundary
  does_not_validate:
  - who is authorized to declare surplus
  - business realism of the declared quantity
  - documentary evidence required for declaration
  - category-specific demand policy
  - action feasibility
  - rescue-success scoring
  - optimizer allocation
policy_context:
  declared_surplus_allowed: true
  sales_evidence_required_for_calculated_surplus: true
  declaration_rule_under_test: Jika sales evidence tidak tersedia tetapi declared surplus valid, hanya declared quantity yang menjadi planning_quantity.
  undeclared_remainder_rule_under_test: Remainder tanpa sales evidence masuk review_quantity, bukan otomatis HEALTHY_STOCK.
  validity_conditions:
  - declared_surplus == true
  - declared_surplus_quantity > 0
  - declared_surplus_quantity <= current_quantity
  - declaration_verification_status == VERIFIED
  - safety and expiry checks pass
  open_policy:
  - authorized declaration role
  - minimum declaration evidence
  - declaration expiry or freshness
  - audit and approval procedure
input:
  product:
    lot_id: LOT-DECLARED-001
    sku: DRINK-008
    product_name: Minuman Serbuk Kemasan
    product_category: PACKAGED_BEVERAGE
  inventory:
    current_quantity: 20
    unit: sachet
  shelf_life:
    expiry_date: '2026-12-31'
    expiry_date_readability: VERIFIED
  sales_evidence:
    units_sold_observation_window: null
    observation_days: null
    sales_evidence_status: MISSING
    safety_stock: null
  condition:
    packaging_condition: INTACT
    storage_history: VERIFIED
    verification_status: VERIFIED
  user_declaration:
    declared_surplus: true
    declared_surplus_quantity: 8
    declaration_verification_status: VERIFIED
evaluation:
  expiry_check:
    result: VALID
  safety_check:
    result: PASSED
  verification_check:
    result: PASSED
  calculated_surplus_evidence_check:
    result: INSUFFICIENT_EVIDENCE
  declared_surplus_check:
    declared_surplus: true
    declared_surplus_quantity: 8
    quantity_is_positive: true
    quantity_within_current_stock: true
    declaration_verified: true
    result: VALID
  planning_quantity:
    source: USER_DECLARED
    result: 8
  undeclared_remainder_quantity:
    formula: current_quantity - planning_quantity
    expression: 20 - 8
    result: 12
expected:
  inventory_status: SURPLUS_CANDIDATE
  quantities:
    protected_normal_stock_quantity: 0
    monitor_quantity: 0
    planning_quantity: 8
    expired_quantity: 0
    review_quantity: 12
  routing:
    planner_entry: true
    planner_eligible_quantity: 8
    candidate_generation: ALLOWED_DOWNSTREAM
    model_scoring: PENDING_DOWNSTREAM_GATES
    optimizer_entry: NOT_YET_APPLICABLE
    human_review_required: true
  review:
    review_quantity: 12
    review_trigger: UNDECLARED_REMAINDER_WITHOUT_SALES_EVIDENCE
    required_action: Sediakan sales evidence atau deklarasi tambahan valid untuk mengklasifikasikan remainder.
  reporting:
    reason_code: VALID_PARTIAL_USER_DECLARED_SURPLUS
    explanation: Delapan dari 20 sachet diteruskan ke planner berdasarkan deklarasi valid. Sisa 12 sachet ditahan dalam review_quantity.
declaration_precedence_boundary:
  declaration_may_replace_missing_sales_evidence: true
  declaration_may_classify_declared_quantity: true
  declaration_may_prove_remainder_is_healthy: false
  declaration_may_override_expiry: false
  declaration_may_override_hard_safety_reject: false
  declaration_may_override_missing_critical_safety_evidence: false
  declaration_may_select_final_action: false
quantity_invariant:
  assertion: 0 + 0 + 8 + 0 + 12 == 20
  expected_result: PASS
planner_partition_invariant:
  planner_eligible_quantity: 8
  planner_excluded_quantity: 12
  assertion: 8 + 12 == 20
failure_conditions:
- inventory_status != SURPLUS_CANDIDATE
- planning_quantity != 8
- review_quantity != 12
- planner menerima seluruh 20 unit
- sisa 12 unit otomatis dianggap HEALTHY_STOCK
- sisa 12 unit masuk candidate generation
- model langsung memberi score sebelum downstream gates
- declaration mengalahkan expiry atau hard safety reject
- human_review_required != true
- quantity_invariant_passed == false
traceability:
  primary_sources:
  - SIMPLE_PRD_v1.1_UPDATED.md
  - FEATURE_SCHEMA_FINAL_v1.1.yaml
  - SCHEMA_FINALIZATION_DECISION_v1.1.md
  suite_role: CORE_TRIAGE_ACCEPTANCE
  production_status: NOT_IMPLEMENTED
```

---

## 5. Suite status

```yaml
suite_status: LOCKED_LOGIC_WITH_OPEN_POLICY_DEPENDENCIES
core_cases:
  TRIAGE-001: LOCKED_LOGIC
  TRIAGE-002: LOCKED_LOGIC
  TRIAGE-003: LOCKED_LOGIC
  TRIAGE-004: LOCKED_LOGIC
  TRIAGE-005: LOCKED_LOGIC
  TRIAGE-006: LOCKED_LOGIC
  TRIAGE-007: LOCKED_LOGIC
  TRIAGE-008: LOCKED_LOGIC

open_policy_dependencies:
  - effective sales window per category
  - expiry monitor threshold per category
  - monitor review interval
  - disposal and recall policy
  - cold-chain evidence policy
  - minimum sales-history policy
  - declaration authority
  - declaration evidence and freshness

not_covered_by_this_suite:
  physical_damage_hard_routing:
    preferred_suite: SAFETY_ACCEPTANCE
    existing_reference: EVAL-005
  invalid_user_declaration:
    preferred_suite: VALIDATION_ACCEPTANCE
    proposed_case: VALIDATION-DECL-001
  raw_inventory_end_to_end:
    preferred_suite: INTEGRATION
    proposed_case: INTEGRATION-001
```

## 6. Next preproduction gate

```text
INTEGRATION-001: RAW_INVENTORY_TO_RESCUE_PLAN
```

Setelah integration contract selesai, proyek dapat diaudit melalui `PREPRODUCTION_READINESS_GATE`. Production tetap diblokir sampai ada persetujuan eksplisit.
