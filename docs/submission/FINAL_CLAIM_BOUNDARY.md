# Afterlife AI — Final Claim Boundary

**Project:** Afterlife AI  
**Purpose:** canonical submission claim boundary for proposal, README, proof-of-work, promotion material, presentation, and judging Q&A.

This document answers one question:

> What may Afterlife AI claim based on the current implemented system and recorded evidence?

If another document, slide, video, or verbal explanation conflicts with this file, use the narrower claim unless stronger evidence has been added and this boundary has been explicitly updated.

---

# 1. Product Identity

## Canonical description

Afterlife AI is:

> An AI-assisted rescue-planning decision-support system for surplus inventory that combines deterministic triage, deterministic safety and feasibility gates, learned rescue-success scoring, expected-value calculation, constrained global allocation, and human-reviewed advisory reporting.

Short version:

> Afterlife AI helps decide how surplus inventory can be rescued safely and feasibly before it becomes waste.

## Afterlife AI is not currently

```text
an autonomous inventory-management platform
a live marketplace
a real-time logistics network
an automatic pricing/negotiation agent
a production-deployed enterprise system
an automatic physical execution system
```

---

# 2. Input and Runtime Scope

## Supported claim

The Technical MVP accepts:

```text
one XLSX inventory workbook
+
request-level decision context
```

Current decision context may include:

```text
optimization objective
maximum logistics budget
minimum expected rescue ratio
rescue deadline
```

Processing is:

```text
local-first
synchronous
single-request
```

## Do not claim

```text
streaming inventory ingestion
real-time ERP synchronization
continuous background processing
multi-tenant production operation
server-side report history
```

unless these are implemented and verified later.

---

# 3. Inventory Triage Claim

## Supported claim

The system performs deterministic inventory triage before rescue planning.

The triage stage can route inventory quantities into categories including:

```text
HEALTHY_STOCK
MONITOR
SURPLUS_CANDIDATE
EXPIRED
NEEDS_REVIEW
```

Only planning quantity enters rescue planning.

This supports the claim:

> Afterlife AI protects normal inventory before attempting rescue allocation.

## Important boundary

The AI model does not decide whether unsafe or non-eligible inventory becomes safe.

---

# 4. Safety and Feasibility Claim

## Supported claim

Rescue candidates pass deterministic hard gates before model scoring.

Hard-gate logic covers implementation-level conditions such as:

```text
runtime action support
safety status
verification sufficiency
storage compatibility
timing feasibility
shelf-life feasibility
logistics feasibility
partner-demand freshness
domain coverage
```

A request rescue deadline can participate in timing feasibility.

## Strong canonical statement

> Deterministic safety and feasibility logic has authority over model scoring.

## Do not claim

```text
AI autonomously certifies food safety
model confidence can override a failed hard gate
the system replaces regulatory inspection
```

---

# 5. Rescue Actions Claim

## Supported runtime action vocabulary

The broader domain vocabulary contains multiple rescue actions.

The runtime MVP only enables and operationalizes a narrower action profile through configuration.

Implemented runtime candidates currently include the supported configured actions, including:

```text
INTERNAL_REPURPOSE
BUNDLE
LOCAL_DISCOUNT
EXTERNAL_PARTNER
SAFE_DISPOSAL
```

subject to runtime configuration and feasibility.

## Important boundary

`capabilities.supported_actions` means:

> actions enabled in the current runtime profile.

It does not mean:

```text
every domain action is implemented
every enabled action is feasible for every lot
every action is externally operational
```

Candidate generation, action-specific capacities, partner evidence, hard gates, and optimizer constraints still apply.

---

# 6. Partner Demand Registry Claim

## Supported claim

Afterlife AI includes Partner Demand Registry semantics in the runtime flow for external-partner candidates.

The current demo registry is:

```yaml
mode: static
runtime_internet: false
source: synthetic demo fixture
real_world_verified: false
```

The registry can provide candidate-level information such as:

```text
partner identity
active demand quantity
available capacity
maximum quantity
minimum order quantity
offered price
completion time
distance
compatibility indicators
demand validity
```

## Correct wording

> External-partner matching is demonstrated using a static synthetic Partner Demand Registry fixture.

## Do not claim

```text
live partner marketplace
real-time buyer demand
verified partner commitments
commercial partner network
internet-connected partner discovery
```

---

# 7. AI Model Claim

## Supported claim

The selected rescue-success model is:

```yaml
model: HGB-E
family: HistGradientBoostingClassifier
model_id: M1_HIST_GRADIENT_BOOSTING
```

Model selection was frozen before locked final-test access.

The model passed the registered AI Value Gate against the B1 action-prior baseline on the frozen synthetic benchmark.

## Validation / robustness evidence

Canonical recorded evidence includes:

```yaml
mean_HGB_E_pr_auc: 0.856632
mean_B1_pr_auc: 0.834086
mean_pr_auc_delta: 0.022546

aggregate_bootstrap_95pct_CI:
  lower: 0.012832
  upper: 0.032417

robustness_consistency: 3/3
AI_VALUE_GATE: PASS
```

## Locked final synthetic test

Canonical final-test evidence includes:

```yaml
HGB_E:
  pr_auc: 0.874229
  brier: 0.151383
  mrr: 0.930093
  ndcg_at_3: 0.890749
  top1_success_rate: 0.872222
  pairwise_accuracy: 0.663004

B1:
  pr_auc: 0.834923
  brier: 0.156801
  mrr: 0.915972
  ndcg_at_3: 0.869309
  top1_success_rate: 0.844444
  pairwise_accuracy: 0.596337
```

## Correct wording

> HGB-E demonstrates measurable improvement over the B1 action-prior baseline on the frozen synthetic benchmark.

## Do not claim

```text
validated real-world rescue probability
real merchant predictive accuracy
field-calibrated probability
general performance across all retail categories
statistical significance on every individual robustness seed
```

---

# 8. Synthetic Data Claim

## Supported claim

The model benchmark is synthetic and intentionally disclosed as synthetic.

Canonical grouped split evidence:

```yaml
total_rows: 12020
total_scenario_groups: 2400
split_unit: scenario_group_id

train_groups: 1680
validation_groups: 360
test_groups: 360

group_leakage: false
group_leakage_count: 0

test_policy: LOCKED_FINAL_EVALUATION
```

## Correct wording

> Synthetic data is used to evaluate the technical decision pipeline under controlled scenarios.

## Do not claim

```text
synthetic data represents national Indonesian merchant statistics
synthetic benchmark results equal field performance
synthetic outcomes prove business adoption
```

---

# 9. Optimization Claim

## Supported claim

Afterlife AI uses constrained global allocation through CP-SAT.

Current optimizer semantics include constraints such as:

```text
planning quantity
shared action capacity
candidate feasibility
request objective
optional logistics budget
optional minimum expected rescue ratio
```

The pipeline also preserves deterministic fallback behavior when the optimizer outcome cannot be used and request constraints permit fallback.

## Supported evidence

Recorded evaluation evidence supports:

```yaml
quantity_conservation: PASS
hard_constraint_violations: 0
```

## Correct wording

> The MVP uses constrained global optimization to allocate planning quantity across feasible rescue candidates.

## Explicitly prohibited claim

Do not claim:

> The optimizer is empirically superior to greedy.

No completed evidence currently supports optimizer-vs-greedy superiority.

Also do not claim generic “optimal business outcome” beyond the defined solver objective and constraints.

---

# 10. Explainability Claim

## Supported claim

The Rescue Decision Report exposes decision evidence including:

```text
selected allocations
unselected / rejected alternatives
reason codes
batch metrics
rescue / waste estimates
score provenance
feature-schema version
ruleset version
runtime capability version
partner-registry provenance
optimizer metadata
fallback information
limitations
human-review status
```

## Correct wording

> Afterlife AI exposes the evidence and constraints behind its advisory rescue plan.

## Do not claim

```text
complete causal explanation
human-level reasoning trace
proof that every model prediction is interpretable
```

---

# 11. Human Governance Claim

## Supported claim

The Rescue Decision Report is advisory.

Canonical runtime state:

```yaml
human_final_approval_status: PENDING
execution_performed: false
```

The report contract prohibits claiming automatic execution.

## Correct wording

> Human approval remains outside automatic execution.

## Do not claim

```text
automatic discount execution
automatic transfer execution
automatic donation execution
automatic disposal execution
automatic logistics execution
```

---

# 12. Reproducibility Claim

## Supported historical Technical MVP evidence

A Technical MVP Release Candidate checkpoint recorded:

```yaml
clean_clone: PASS
locked_dependency_install: PASS
docker_build: PASS
docker_compose_runtime: PASS
container_health: PASS

triage_cases: 8/8
planner_cases: 30/30
integration_cases: 1/1
quantity_conservation: PASS
hard_constraint_violations: 0
```

## Boundary

Those results prove the recorded RC checkpoint.

They do not automatically prove the future final submission commit.

The final submission may only claim final repository verification after G10 is executed on the exact frozen final commit.

---

# 13. UI Claim

## Supported claim

The MVP includes a FastAPI + Jinja2 competition-facing decision workspace.

Current UI exposes implemented report and decision-context behavior.

## Correct wording

> The interface is the presentation layer for the same production decision pipeline.

## Do not claim

```text
production SaaS dashboard
multi-user application
persistent merchant workspace
analytics platform
```

---

# 14. Real-World Impact Claim

## Current status

```yaml
technical_mechanism: implemented
synthetic_evaluation: implemented
real_world_field_validation: not established
business_adoption_validation: not established
willingness_to_pay_validation: not established
```

## Permitted language

```text
designed to reduce avoidable waste
intended to improve rescue decision quality
can support operators in comparing feasible rescue options
potential business and environmental value
```

## Prohibited language without future evidence

```text
reduces waste by X%
increases merchant revenue by X%
saves X tons of food
used successfully by X merchants
improves operational efficiency by X%
```

---

# 15. Discovery Evidence Claim

The project includes internal and external incident evidence used during discovery.

This evidence supports:

```text
problem framing
action vocabulary
constraint discovery
evaluation-case design
```

It does not establish:

```text
population prevalence
national statistics
probability of rescue success
representative merchant economics
```

---

# 16. Architecture Claim

## Canonical high-level flow

```text
Inventory XLSX + Decision Context
→ Validation
→ Deterministic Triage
→ Rescue Candidate Generation
→ Deterministic Hard Gates
→ HGB-E Rescue-Success Scoring
→ Expected Value Calculation
→ CP-SAT Global Allocation
→ Rescue Decision Report
→ Human Review
```

## Canonical architecture interpretation

```text
rules determine eligibility
model estimates rescue success for eligible candidates
optimizer allocates constrained resources
report exposes evidence
human retains authority
```

This is the architecture story that README, proposal, videos, diagrams, and Q&A must share.

---

# 17. Claim Register

## GREEN — Directly supported

```text
Afterlife AI accepts one XLSX and produces one advisory Rescue Decision Report.

Deterministic triage occurs before rescue planning.

Only planning quantity enters rescue planning.

Deterministic hard gates precede model scoring.

HGB-E is the selected rescue-success model.

HGB-E was frozen before locked final-test access.

The benchmark uses grouped splitting with zero recorded group leakage.

HGB-E passed the registered AI Value Gate against B1 on the synthetic benchmark.

Final locked synthetic-test HGB-E PR-AUC is approximately 0.874.

The planner uses constrained global allocation.

Recorded evaluation evidence contains zero hard-constraint violations.

The Partner Demand Registry is integrated through a static synthetic demo fixture.

Selected and unselected alternatives can be represented in the Rescue Decision Report.

The MVP is advisory.

Automatic physical execution is not performed.
```

---

## YELLOW — Must carry qualification

```text
“AI improves ranking.”
→ Say: on the frozen synthetic benchmark relative to B1.

“Afterlife AI reduces waste.”
→ Say: this is the intended outcome / mechanism; real-world reduction is not yet validated.

“Partner matching finds demand.”
→ Say: demonstrated against the static synthetic demo registry.

“The optimizer improves decisions.”
→ Say: it performs constrained global allocation; optimizer-vs-greedy superiority has not been established.

“Rescue-success probability.”
→ Say: model-estimated score trained and evaluated on synthetic benchmark, not validated field probability.

“Technical MVP is reproducible.”
→ Historical RC is verified; final submission reproducibility must be re-verified at G10.
```

---

## RED — Do not use

```text
real-world calibrated rescue probabilities
live partner marketplace
verified real partner commitments
automatic physical rescue execution
automatic logistics execution
optimizer proven superior to greedy
production deployment
nationally representative merchant data
verified real-world waste reduction percentage
verified merchant revenue improvement percentage
real-world adoption rate
validated willingness-to-pay
globally first / globally unique solution
```

---

# 18. Claim-Change Rule

A RED or YELLOW claim may only be promoted when:

```text
1. the corresponding feature/evidence actually exists;
2. automated or documented verification is added;
3. the evidence is committed;
4. this file is updated;
5. README / proposal / video maps are updated consistently.
```

A new feature does not automatically create a new permitted claim.

Implementation and evidence both matter.

---

# 19. Final G9 Decision

```yaml
canonical_product_claim: defined
runtime_claim_boundary: defined
model_claim_boundary: defined
synthetic_data_boundary: defined
partner_registry_boundary: defined
optimizer_boundary: defined
human_governance_boundary: defined
real_world_impact_boundary: defined

green_claims: locked
yellow_claims: qualification_required
red_claims: prohibited_without_new_evidence

G9_status: PASS
```

**G9 Decision: FINAL CLAIM BOUNDARY DEFINED.**
