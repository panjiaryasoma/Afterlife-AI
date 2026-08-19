# Afterlife AI — Proposal Evidence Map

**Competition:** COMPFEST 18 AI Innovation Challenge  
**Project:** Afterlife AI  
**Purpose:** map every major proposal section and competition criterion to evidence that already exists in the repository.

This file is not the final proposal. It is the writing contract for the proposal so claims stay traceable, technically honest, and consistent with the implemented MVP.

---

## 1. Rulebook Proposal Contract

The preliminary-round proposal must contain at least:

1. team name and innovation title;
2. background;
3. development objectives and benefits;
4. methodology, including:
   - dataset acquisition / generation flow;
   - model-development flow for each feature;
   - model-integration flow into the code environment;
5. other supporting methods used to justify development decisions;
6. conclusion.

Maximum proposal length:

```text
20 pages
excluding:
- cover
- bibliography
- appendices
```

The proposal should therefore explain **why the system exists, how it was built, how it was evaluated, and what the evidence actually supports**.

---

## 2. Recommended Proposal Structure

Recommended page budget:

```text
Cover                                  excluded

1. Executive Summary                    1 page
2. Background & Problem                 2 pages
3. User, Use Case, Objectives            1 page
4. Solution & Innovation                2 pages
5. System Architecture                  2 pages
6. Dataset & Evaluation Design          3 pages
7. Model Development                    3 pages
8. Rescue Planning & Optimization       2 pages
9. Integration & MVP Implementation     2 pages
10. Evaluation Results                  2 pages
11. Limitations, Governance, Roadmap     1 page
12. Conclusion                           1 page

Target body total                       20 pages max
```

Do not force every section to consume its entire allowance. The page budget exists to prevent the common hackathon disease where methodology receives eleven pages and the actual problem gets three sentences.

---

# 3. Section-to-Evidence Map

## 3.1 Executive Summary

### Proposal message

Afterlife AI is an AI-assisted decision-support system for retail and F&B surplus inventory.

Core interaction:

```text
one inventory XLSX
→ deterministic inventory triage
→ feasible rescue options
→ rescue-success scoring
→ constrained global allocation
→ one Rescue Decision Report
→ human review
```

### Evidence

```text
README.md
PROBLEM_BRIEF_v1.0.md
SIMPLE_PRD_v1.1_UPDATED.md
reports/evidence/TECHNICAL_MVP_RC_VERIFICATION.md
```

### Recommended visual

```text
ARCH-02 simplified system overview
```

### Claim boundary

Do not call Afterlife AI:

- an autonomous inventory-management platform;
- a live surplus marketplace;
- an automatic logistics executor;
- a field-validated probability engine.

The MVP is advisory and locally reproducible.

---

## 3.2 Background and Problem

### Proposal message

Retail and F&B businesses may face inventory that is still physically usable but commercially difficult to sell under the original plan. The operational problem is not simply detecting that stock exists, but deciding what should happen to surplus while protecting normal stock and respecting safety, timing, capacity, and economic constraints.

The problem definition was informed by:

```text
16 family-business incidents
+
16 external comparison incidents
```

These incidents were used as discovery and domain evidence, not as a transaction dataset.

### Evidence

```text
PROBLEM_BRIEF_v1.0.md
Incident_001-016_Family_Corroborated
External_Incident_001-016_Indonesia
domain rule artifacts
evaluation cases
```

### Use in proposal

Use the incidents to support:

- problem relevance;
- action vocabulary;
- domain constraints;
- examples of why simple markdown-only handling is insufficient.

### Do not claim

The incident set does not establish:

- national prevalence;
- average Indonesian retail waste rates;
- rescue-action success probabilities;
- statistically representative merchant behavior.

If national-scale statistics are later added, they require external cited sources and must be separated from project-generated evidence.

---

## 3.3 User, Use Case, Objectives, and Benefits

### Primary user

```text
business operator / inventory decision owner
```

### Job to be done

```text
Given a mixed inventory file,
identify what quantity should remain protected,
what quantity can enter rescue planning,
which rescue options are safe and feasible,
and how limited rescue capacity should be allocated.
```

### MVP objective

Produce one advisory Rescue Decision Report that makes the decision auditable rather than automatically executing actions.

### Evidence

```text
PROBLEM_BRIEF_v1.0.md
SIMPLE_PRD_v1.1_UPDATED.md
README.md
Rescue Decision Report contract
```

### Benefit claims that are supportable

- structured rescue planning;
- protection of normal inventory before surplus allocation;
- explicit hard safety / feasibility constraints;
- globally constrained allocation rather than per-candidate isolated scoring;
- traceable limitations and provenance;
- decision support without automatic physical execution.

### Claims still unvalidated

- merchant willingness to pay;
- adoption rate;
- percentage reduction in real-world waste;
- percentage increase in real-world revenue;
- operational labor savings.

---

## 3.4 Solution and Innovation

### Proposal message

The innovation is not “using AI to predict surplus.”

The MVP instead combines:

```text
deterministic triage
+
deterministic safety / feasibility gates
+
learned rescue-success ranking
+
expected-value calculation
+
global constrained allocation
+
human-review reporting
```

This division of responsibility is intentional:

```text
rules decide what is allowed
model estimates which allowed option is more promising
optimizer allocates limited rescue capacity
human retains final authority
```

### Evidence

```text
README.md
SIMPLE_PRD_v1.1_UPDATED.md
docs/contracts/
src/afterlife_ai/pipeline/
reports/evidence/modeling/
reports/evidence/rescue_planner/
```

### Differentiation angle

Proposal should emphasize the **decision architecture**, not generic “AI automation.”

Useful framing:

```text
A surplus item is not automatically waste.
The decision is whether another feasible use still exists,
under real operational constraints.
```

### Avoid

Do not position novelty as:

- first AI waste solution in the world;
- first surplus optimizer;
- guaranteed novel research algorithm.

Those claims would require a separate literature / competitor review.

---

## 3.5 System Architecture

### Proposal message

Afterlife AI uses a modular local architecture:

```text
Frontend
Jinja2 + HTML/CSS/JavaScript

        ↓

Application / API
FastAPI

        ↓

Core decision pipeline
validation
triage
candidate generation
hard gates
scoring
expected value
optimization
report

        ↓

Local model + static runtime configuration
```

### Canonical visual

```text
ARCH-01 full technical architecture
```

### Simplified visual

```text
ARCH-02 simplified system overview
```

### Evidence

```text
README.md
docs/architecture/ARCHITECTURE_OVERVIEW.md
docs/architecture/ARCH-01.mmd
docs/architecture/ARCH-01.png
docs/architecture/ARCH-02.mmd
docs/architecture/ARCH-02.png
backend/
frontend/
src/afterlife_ai/
configs/runtime_v1.yaml
configs/partner_registry_demo_v1.yaml
models/HGB_E_v1.joblib
compose.yaml
Dockerfile
```

### Why this matters for judging

The architecture directly demonstrates:

- proportional technology selection;
- separation between frontend, API, core logic, and model;
- local reproducibility;
- synchronous MVP scope;
- static core inference;
- no unnecessary database, authentication, or background-worker layer.

---

## 3.6 Dataset and Evaluation Design

### Proposal message

Afterlife AI uses synthetic training and evaluation data because the available real-world discovery evidence is useful for domain design but insufficient as a large supervised transaction dataset.

The synthetic benchmark is not presented as real merchant transaction data.

### Dataset architecture

```text
Discovery incidents
→ domain patterns and constraints

Domain / evaluation contracts
→ scenario definitions

Synthetic generator
→ candidate-level benchmark

Grouped split by scenario_group_id
→ train / validation / locked final test
```

### Canonical evidence

```text
reports/evidence/synthetic_dataset/SPLIT_MANIFEST_v2.json
reports/evidence/synthetic_dataset/
src/afterlife_ai/synthetic/
docs/evaluation_source_v1.0/
```

### Verified dataset facts

```yaml
total_rows: 12020
total_scenario_groups: 2400

split_unit: scenario_group_id
group_leakage: false

train:
  groups: 1680
  rows: 8435

validation:
  groups: 360
  rows: 1805

test:
  groups: 360
  rows: 1780

test_policy: LOCKED_FINAL_EVALUATION
```

### Proposal explanation required

Explain why random row splitting was rejected:

Candidates belonging to the same scenario group can share scenario-specific structure. Grouped splitting prevents related candidates from leaking across train, validation, and test partitions.

### Claim boundary

Synthetic benchmark performance:

```text
≠ field performance
≠ national business evidence
≠ real-world probability calibration
```

---

## 3.7 Model Development

### Selected model

```yaml
model_family: HistGradientBoostingClassifier
configuration: HGB-E
model_id: M1_HIST_GRADIENT_BOOSTING
```

### Selection logic

The model was selected using validation evidence before accessing the locked final test.

Canonical records:

```text
configs/selected_model_v1.yaml
reports/evidence/modeling/MODEL_SELECTION_AND_AI_VALUE_GATE_DECISION_v1.md
```

### Validation evidence

```yaml
HGB_E:
  pr_auc: 0.853664
  brier: 0.155145

AI_VALUE_GATE: PASS
```

Robustness evidence:

```yaml
seeds:
  - 42
  - 137
  - 2026

mean_HGB_E_pr_auc: 0.856632
mean_B1_pr_auc: 0.834086
mean_pr_auc_delta: 0.022546

aggregate_bootstrap_95pct_CI:
  lower: 0.012832
  upper: 0.032417

consistency: 3/3
```

### Why the AI component exists

The AI Value Gate is the key argument.

Proposal should state:

> A learned model was retained because it demonstrated measurable predictive value over the action-prior baseline on the frozen synthetic benchmark under the registered robustness protocol.

Do not write:

> AI was used because AI is better than rules.

That would be both intellectually lazy and contradicted by the architecture, where deterministic rules deliberately remain responsible for safety.

---

## 3.8 Final Model Evaluation

### Canonical evidence

```text
reports/evidence/modeling/final_test/FINAL_LOCKED_TEST_v1.json
```

### Final locked synthetic-test metrics

```yaml
HGB_E:
  PR_AUC: 0.874229
  Brier: 0.151383

B1:
  PR_AUC: 0.834923
  Brier: 0.156801
```

Ranking:

```yaml
HGB_E:
  MRR: 0.930093
  NDCG_at_3: 0.890749
  top1_success_rate: 0.872222
  pairwise_accuracy: 0.663004

B1:
  MRR: 0.915972
  NDCG_at_3: 0.869309
  top1_success_rate: 0.844444
  pairwise_accuracy: 0.596337
```

Allocation diagnostic:

```yaml
HGB_E:
  mean_regret: 9454.805111
  oracle_value_retained: 0.998591

B1:
  mean_regret: 20545.045250
  oracle_value_retained: 0.996938
```

Safety:

```yaml
quantity_conservation: PASS
hard_constraint_violations: 0
```

### Recommended proposal figures

Use no more than three:

1. HGB-E vs B1 final PR-AUC;
2. HGB-E vs B1 Brier or reliability visualization;
3. ranking / allocation diagnostic.

Do not dump every notebook figure into the body.

---

## 3.9 Rescue Planning and Optimization

### Proposal message

Model scores do not directly become execution decisions.

After scoring, candidate economic value is calculated and a constrained global optimizer allocates planning quantity.

Core constraints include:

```text
planning quantity
shared capacity
action-specific feasibility
logistics constraints
request objective
optional logistics budget
optional minimum rescue ratio
```

A request-level rescue deadline is enforced in the deterministic hard-gate stage.

### Evidence

```text
src/afterlife_ai/pipeline/gates.py
src/afterlife_ai/pipeline/value.py
src/afterlife_ai/pipeline/optimizer.py
src/afterlife_ai/planner/
reports/evidence/rescue_planner/
reports/evidence/TECHNICAL_MVP_RC_VERIFICATION.md
```

### Verified evidence

```yaml
planner_evaluation: 30/30 PASS
quantity_conservation: PASS
hard_constraint_violations: 0
```

### Important claim restriction

Do not claim:

```text
“Our optimizer empirically outperforms greedy.”
```

The current evidence does not establish that comparison.

Correct language:

```text
“The MVP uses global constrained optimization to allocate planning quantity
across feasible rescue candidates.”
```

---

## 3.10 Partner Demand Registry

### Proposal message

External partner rescue is represented through a Partner Demand Registry used during candidate generation.

Current MVP implementation:

```text
static
offline
synthetic demo fixture
timestamped
not real-world verified
```

### Evidence

```text
configs/partner_registry_demo_v1.yaml
src/afterlife_ai/pipeline/partner_registry.py
src/afterlife_ai/pipeline/candidates.py
Rescue Decision Report partner-registry provenance
```

### Supported claim

Partner-demand semantics are integrated into the MVP runtime and can influence external-partner candidate availability and capacity.

### Unsupported claim

Do not state:

- live partner network;
- verified buyer commitments;
- marketplace liquidity;
- real-time partner demand;
- internet-connected matching.

---

## 3.11 Integration Into the Code Environment

### Proposal flow

```text
XLSX upload
→ POST /api/analyze
→ AnalysisRequest validation
→ run_production_pipeline()
→ triage
→ planning lots
→ candidate generation
→ hard gates
→ HGB-E scoring
→ expected value
→ CP-SAT optimizer
→ Rescue Decision Report
→ Jinja2 UI / JSON download
```

### Evidence

```text
backend/api/routes.py
src/afterlife_ai/pipeline/application.py
frontend/
tests/api/
tests/integration/
compose.yaml
Dockerfile
```

### Runtime boundary

```yaml
processing: synchronous
database: none
server_side_history: none
runtime_internet: none
automatic_execution: none
```

This is a feature of scope discipline, not a missing-enterprise-stack apology.

---

## 3.12 MVP Implementation and Reproducibility

### Proposal message

The project deliberately follows the preliminary-round boundary:

```text
one core input
one synchronous analysis
one core output
local Docker execution
static inference/runtime parameters
no auth/history/distributed database
```

### Evidence

```text
README.md
compose.yaml
Dockerfile
reports/evidence/TECHNICAL_MVP_RC_VERIFICATION.md
```

### RC evidence

```yaml
technical_mvp_release_candidate: READY

triage: 8/8
planner: 30/30
integration: 1/1
quantity_conservation: PASS
hard_constraint_violations: 0
clean_clone: PASS
docker_compose: PASS
```

### Important timing note

The RC verification is historical checkpoint evidence.

The proposal should use final submission verification numbers only after G10 final release audit has been completed.

Until then:

```text
final test count        = PENDING FINAL AUDIT
final clean clone       = PENDING FINAL AUDIT
final Docker smoke      = PENDING FINAL AUDIT
final UI smoke          = PENDING FINAL AUDIT
```

---

## 3.13 Explainability and Governance

### Proposal message

Every recommendation is designed to remain auditable.

The Rescue Decision Report includes:

```text
selected allocations
unselected / rejected alternatives
reason codes
batch rescue / waste metrics
score provenance
ruleset / capability provenance
partner-registry provenance
fallback information
limitations
human-review requirements
```

### Governance boundary

```text
model cannot override hard gates
optimizer cannot revive blocked candidates
report is advisory
human approval remains pending
execution_performed = false
```

### Evidence

```text
src/afterlife_ai/planner/report.py
README.md
technical_mvp_rc_example_report.json
SUBMISSION_EVIDENCE_INDEX.md
```

### Bonus-criterion angle

Responsible-AI discussion should focus on **actual architecture controls**, not generic ethics paragraphs pasted from a consultancy brochure.

---

## 3.14 Limitations and Future Development

### Current limitations to disclose

```text
synthetic training benchmark
no real-world probability calibration
static MVP operating parameters
static synthetic partner registry
no verified live demand network
business adoption unvalidated
willingness-to-pay unvalidated
no automatic execution
single synchronous request workflow
no authentication / multi-user isolation
```

### Why disclosure helps

The MVP-readiness criteria explicitly reward awareness of meaningful areas for future improvement.

A limitation section is therefore not an admission that the project failed. It demonstrates scope control and architectural awareness.

### Future directions

Use restrained roadmap items:

```text
real merchant calibration
verified partner-demand integration
additional domain/category rule packs
real adoption study
live operational validation
```

Avoid promising ten integrations, blockchain, multi-agent negotiation, OCR, WhatsApp automation, and a planetary logistics network before breakfast.

---

# 4. Judging-Criterion Evidence Map

## 4.1 Originality and Social Impact — 20%

### Proposal evidence

Use:

```text
problem incidents
Problem Brief
decision architecture
human / safety boundary
surplus-rescue framing
```

### Strongest argument

Afterlife AI treats surplus as a constrained allocation problem rather than simply a disposal problem or binary sale/no-sale classification.

### Evidence gap

Real-world social and business impact remains unvalidated.

Do not fabricate impact percentages.

---

## 4.2 Technology Implementation and Architecture Maturity — 25%

### Evidence

```text
ARCH-01
README.md
FastAPI + Jinja2 separation
src/afterlife_ai/
HGB-E model
deterministic hard gates
CP-SAT optimizer
Docker Compose
tests
```

### Strongest story

The model, deterministic rules, optimization, API, and presentation layer have distinct responsibilities.

This is probably the proposal section where Afterlife AI currently has its strongest objective evidence.

---

## 4.3 MVP Readiness — 15%

### Evidence

```text
Technical MVP RC verification
one-XLSX-to-report flow
Docker
UI
JSON report download
319-pass current local regression before final audit
known limitations
```

### Final evidence dependency

Replace current-local regression language with the exact G10 final audit result before submission.

---

## 4.4 Video Promotion — 15%

Handled primarily in G7.

Proposal should keep terminology consistent with video:

```text
problem
rescue planning
deterministic safety
AI ranking
global allocation
human decision
```

Do not let proposal and video describe two different products, an oddly common competitive strategy.

---

## 4.5 Proposal Quality and Development Process — 15%

### Evidence

This criterion should be attacked directly through the narrative:

```text
discovery evidence
→ problem brief
→ evaluation contracts
→ schema / baseline
→ synthetic benchmark
→ model selection before final test
→ AI Value Gate
→ production implementation
→ Technical MVP RC
→ hardening
→ submission polish
```

### Strongest process evidence

```text
model selection frozen before locked test
grouped split with zero leakage
AI Value Gate
30 planner cases
8 triage cases
integration test
clean-clone verification
claim-boundary documentation
```

This demonstrates iterative development driven by evaluation rather than feature accumulation.

---

## 4.6 Theme Relevance — 10%

### Proposal framing

Primary:

```text
Smart Commerce
```

Supporting:

```text
Smart Logistics
```

The connection should be made through inventory recovery decisions, demand/capacity matching, and constrained allocation.

Avoid claiming a broader supply-chain platform than the MVP actually implements.

---

## 4.7 Business Value and Governance — Bonus 3.5%

### Governance

Strong evidence:

```text
hard safety gates
synthetic-data disclosure
provenance
human approval
no automatic execution
limitations
```

### Business value

Current position:

```text
plausible mechanism
not yet externally validated
```

The proposal may discuss how recovery-value planning could support merchant decisions, but must distinguish this mechanism from validated adoption or ROI.

---

# 5. Proposal Figures to Curate

Recommended proposal body figures:

```text
FIG-01  Problem / rescue decision framing
FIG-02  ARCH-02 simplified system overview
FIG-03  Dataset generation + grouped split flow
FIG-04  HGB-E vs B1 final locked evaluation
FIG-05  ARCH-01 technical architecture
FIG-06  Rescue Decision Report screenshot
```

Optional appendix figures:

```text
calibration / reliability
ranking evaluation
allocation diagnostic
evaluation-contract summary
```

Six body figures are enough.

A proposal is not improved by turning it into a sticker album of every PNG generated during development.

---

# 6. Proposal Claim Register

## Green — can state directly

```text
Afterlife AI processes one XLSX into one Rescue Decision Report.
Safety / feasibility decisions occur before model scoring.
HGB-E is the selected rescue-success model.
Model selection was frozen before final-test access.
The synthetic benchmark uses grouped splitting with zero group leakage.
HGB-E passed the registered AI Value Gate against B1.
Final synthetic-test HGB-E PR-AUC is approximately 0.874.
Planner evaluation includes 30 passing evaluation cases.
Locked evaluation records zero hard-constraint violations.
The system uses constrained global allocation.
The current MVP is advisory and requires human review.
The Partner Demand Registry is integrated as a static synthetic demo fixture.
```

## Yellow — state with qualification

```text
AI improves candidate ranking.
→ on the synthetic benchmark, relative to B1.

The optimizer improves rescue planning.
→ architectural mechanism, not a completed optimizer-vs-greedy superiority result.

Afterlife AI can reduce waste.
→ intended outcome / hypothesis, not validated field impact.

Partner matching expands rescue options.
→ demonstrated through static synthetic registry semantics, not a live partner network.
```

## Red — do not state

```text
Real-world rescue probability is validated.
Real merchants achieved X% waste reduction.
Real merchants achieved X% revenue recovery.
Partner demand is live or commercially committed.
Optimizer is proven superior to greedy.
The application autonomously executes rescue actions.
The system is production-deployed.
The solution is globally unique / first in the world.
```

---

# 7. Writing Source Priority

When drafting the final proposal, use this priority order:

```text
1. final locked evaluation artifacts
2. final submission audit artifacts
3. frozen model-selection records
4. active runtime code and config
5. Simple PRD / Problem Brief
6. discovery incidents
7. historical sprint records
```

If old documentation conflicts with current runtime behavior:

```text
current executable implementation + passing contracts
wins
```

If a claim has no evidence:

```text
remove it
or label it as hypothesis / limitation / roadmap
```

---

# 8. G5 Completion Gate

```yaml
proposal_required_sections_mapped: true
judging_criteria_mapped: true
technical_evidence_mapped: true
model_evidence_mapped: true
dataset_evidence_mapped: true
governance_evidence_mapped: true
claim_register_defined: true

final_proposal_written: false
final_figures_inserted: false
final_release_metrics_inserted: false

dependency:
  final_release_metrics: G10
```

**G5 Decision: PROPOSAL EVIDENCE MAP READY.**

The actual PDF proposal should be written after G6–G8 are aligned so repository, proof-of-work, promotion video, screenshots, and proposal all tell the same implemented story.
