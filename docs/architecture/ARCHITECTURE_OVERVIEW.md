# Afterlife AI - Architecture Overview

## Purpose

This document defines the canonical interpretation of Afterlife AI's final NextStep architecture and flow figures.

The repository now uses four final judge-facing / engineering-facing visuals with matching Mermaid sources. They describe the same verified runtime from different levels of abstraction rather than competing architectures.

The final diagram set is:

- `docs/architecture/E2E-DIAGRAM.png`
- `docs/architecture/FLOWCHART.png`
- `docs/architecture/ARCH SIMPLE FINAL.png`
- `docs/architecture/ARCH FULL FINAL.png`

Matching Mermaid sources:

- `docs/architecture/E2E-DIAGRAM.mmd`
- `docs/architecture/FLOWCHART.mmd`
- `docs/architecture/ARCH-SIMPLE-FINAL.mmd`
- `docs/architecture/ARCH-FULL-FINAL.mmd`

The older `ARCH-01.*` and `ARCH-02.*` files are retained as historical / legacy architecture artifacts. They are no longer the primary source for the current NextStep architecture narrative.

If a diagram conflicts with verified runtime behavior or executable contracts, verified runtime behavior and repository contracts take precedence and the diagram must be corrected.

---

## Final Diagram Roles

### 1. End-to-End Diagram

`E2E-DIAGRAM.png` is the complete lifecycle view from operator input to confirmed outcome reconciliation.

Primary audience:

- competition judges;
- product reviewers;
- developers who need the full business-to-runtime sequence;
- demo and submission readers.

Canonical lifecycle:

1. Business operator provides an inventory workbook and decision context.
2. Input is structurally and semantically validated.
3. Deterministic inventory triage protects healthy stock and identifies rescue scope.
4. Surplus planning lots and rescue candidates are constructed.
5. Deterministic safety and feasibility gates reject ineligible actions.
6. HGB-E scores only gate-eligible rescue candidates.
7. Expected-value components are calculated.
8. OR-Tools CP-SAT performs constrained global allocation.
9. The canonical Rescue Decision Report is produced.
10. A Sustainability Summary derives expected rescue / waste quantities and evidence-bounded mass metrics.
11. Human review remains the authority boundary before any physical action.
12. Physical rescue execution occurs outside Afterlife AI.
13. Operator-confirmed outcomes may be reconciled against the original planning scope.
14. The human-readable Markdown report can combine the plan, sustainability summary, and confirmed outcome.

This diagram is the best single figure for explaining what the system does from beginning to end.

### 2. Operational Flowchart

`FLOWCHART.png` is the procedural decision-flow view.

It emphasizes branches and runtime outcomes such as:

- valid vs invalid input;
- rescue scope present vs absent;
- feasible vs infeasible rescue candidates;
- HGB-E available vs deterministic scoring fallback;
- usable CP-SAT outcome vs documented fallback vs infeasible result;
- complete vs partial / missing mass evidence;
- approved physical action vs advisory-only completion;
- confirmed outcome reconciliation when an observed result exists.

The flowchart is intended for reviewers who want to understand the system's control flow and failure / fallback behavior rather than only its component structure.

### 3. Simple Final Architecture

`ARCH SIMPLE FINAL.png` is the judge-facing system architecture.

Primary audience:

- competition judges;
- proposal and README readers;
- video viewers;
- product-oriented reviewers.

It intentionally compresses implementation detail into the following responsibility chain:

1. Inventory workbook + decision context.
2. Input validation.
3. Deterministic inventory triage.
4. Rescue-option generation.
5. Safety and feasibility hard gates.
6. HGB-E rescue-success scoring.
7. Expected-value calculation.
8. Global CP-SAT allocation.
9. Rescue Decision Report.
10. Sustainability Summary.
11. Human review.
12. External physical rescue action when approved.
13. Operator-confirmed outcome.
14. Outcome Reconciliation.
15. Markdown report export.

Supporting runtime artifacts remain visible only where they materially affect the decision path:

- Runtime Capability Profile;
- Partner Demand Registry;
- HGB-E model;
- objective, budget, and deadline context.

### 4. Full Final Architecture

`ARCH FULL FINAL.png` is the implementation-oriented architecture reference.

Primary audience:

- technical reviewers;
- developers;
- evaluators inspecting implementation fidelity;
- reviewers tracing application boundaries and runtime artifacts.

It separates the system into seven layers:

1. Presentation Layer.
2. Shared Intake & Validation.
3. Canonical Rescue Planning Pipeline.
4. NextStep Sustainability Extension.
5. Outcome Reconciliation.
6. Human-Facing Output.
7. Runtime Artifacts.

The full architecture should be used when discussing endpoint boundaries, canonical report contracts, NextStep wrapping, model and optimizer fallbacks, runtime configuration, and the separation between internal decision support and external physical execution.

---

## Architectural Responsibility Boundaries

Afterlife AI deliberately separates responsibilities that should not be collapsed into one opaque AI decision.

```text
rules determine eligibility
model estimates rescue success
optimizer allocates constrained resources
impact layer measures expected / confirmed outcomes
report exposes evidence
human retains authority
```

### Deterministic Intake and Validation

The primary web analysis endpoint is:

`POST /api/analyze-nextstep`

The legacy compatibility endpoint remains:

`POST /api/analyze`

Both reuse the shared analysis service for upload handling, temporary-file lifecycle, request construction, validation, and error mapping.

The intake layer validates:

- workbook and worksheet structure;
- schema and required fields;
- datatypes;
- semantic constraints;
- request-level decision context.

Invalid input stops before triage, model scoring, or optimization and returns controlled HTTP 400 / 422 feedback.

### Deterministic Inventory Triage

Deterministic triage protects normal inventory and determines what quantity may enter rescue planning.

Runtime triage states include:

- `HEALTHY_STOCK`;
- `MONITOR`;
- `SURPLUS_CANDIDATE`;
- `EXPIRED`;
- `NEEDS_REVIEW`.

Only eligible planning quantity proceeds to planning-lot construction and rescue candidate generation.

### Rescue Candidate Generation

Candidate generation creates rescue alternatives supported by:

- the active Runtime Capability Profile;
- domain rules;
- source inventory condition;
- supported actions;
- Partner Demand Registry evidence where applicable;
- shared capacity and request context.

Candidate generation does not itself establish feasibility.

### Deterministic Safety and Feasibility Hard Gates

Hard gates determine whether a candidate is eligible to reach the learned scoring layer.

They evaluate implementation-level constraints including:

- safety;
- verification sufficiency;
- timing and rescue deadline;
- storage and action compatibility;
- partner demand and capacity;
- logistics feasibility;
- shared operational constraints;
- supported domain coverage.

A blocked candidate cannot be revived by model scoring.

### HGB-E Rescue-Success Scoring

HGB-E scores only candidates that remain eligible after deterministic hard gates.

The output is an estimated rescue-success score used as decision-support evidence.

The score is evaluated on a controlled synthetic benchmark and is not a field-calibrated real-world rescue probability.

If the production HGB-E artifact cannot be used, the documented deterministic scoring fallback may be used for already-eligible rescue candidates.

The scoring fallback cannot:

- bypass deterministic hard gates;
- convert a blocked candidate into an eligible candidate;
- create a validated real-world probability claim.

### Expected-Value Calculation

Expected-value calculation converts eligible candidate information into the economic and physical quantities used by the global planner and report.

Expected quantities remain estimates. They are not operator-confirmed realized outcomes.

### Global CP-SAT Allocation

OR-Tools CP-SAT is the primary constrained global allocation optimizer.

It allocates planning quantity across eligible candidates while respecting applicable constraints such as:

- quantity conservation;
- candidate eligibility;
- action and partner capacity;
- shared operational resources;
- logistics budget;
- optimization objective;
- minimum expected rescue ratio where applicable.

A deterministic optimizer fallback may be used only for documented non-definitive solver outcomes where the applicable constraints can still be preserved.

A definitive infeasible result is not converted into a successful rescue allocation. Affected planning quantity remains unallocated and requires human review.

---

## Canonical Rescue Decision Report

The pre-NextStep `RescueDecisionReport` remains the canonical rescue-planning contract.

It exposes information including:

- selected allocations;
- unselected or rejected alternatives;
- allocated and unallocated quantity;
- expected rescue and waste quantities;
- economic-value components;
- decision evidence and provenance;
- model and optimizer provenance;
- warnings;
- limitations;
- manual-review / human-review state.

The NextStep extension does not silently redefine this historical contract.

---

## NextStep Sustainability Extension

The NextStep layer wraps the canonical rescue output rather than replacing it.

`run_nextstep_pipeline()` produces a `NextStepDecisionReport` envelope containing:

- `rescue_decision_report`;
- `sustainability_summary`.

The Sustainability Summary exposes:

- expected rescue quantity;
- expected waste quantity;
- expected rescue ratio;
- optional rescue / waste mass metrics when sufficient `package_weight_g` evidence exists;
- mass-evidence coverage: `COMPLETE`, `PARTIAL`, or `NONE`.

Mass evidence is deliberately conservative:

- missing package weight is not imputed;
- mixed package weights are aggregated per source lot;
- partial coverage is not presented as a complete batch-mass claim.

The NextStep report envelope validates that sustainability quantities remain consistent with the canonical Rescue Decision Report.

---

## Outcome Reconciliation

Outcome reconciliation is exposed through:

`POST /api/outcomes/reconcile`

The endpoint is stateless in the current MVP.

The operator may provide confirmed:

- actual rescued quantity;
- actual waste quantity.

The reconciliation layer derives:

- confirmed quantity;
- unresolved quantity;
- realized diversion ratio from confirmed outcomes only;
- rescue delta;
- waste delta.

The reconciliation result does not mutate the original rescue plan and does not imply that the observation was persisted.

Expected impact and realized impact remain separate claim classes.

---

## Presentation and Export Boundary

The primary competition-facing presentation layer is:

FastAPI + Jinja2 + HTML + CSS + vanilla JavaScript.

The primary web analysis flow uses `POST /api/analyze-nextstep` and renders:

- inventory and decision-context input;
- validation feedback;
- rescue plan and alternatives;
- Sustainability Summary;
- mass-evidence coverage;
- Outcome Reconciliation when an operator observation is supplied;
- provenance;
- warnings;
- limitations;
- human-review state.

The primary human-facing export is a Markdown report containing the applicable canonical plan, sustainability summary, and confirmed reconciliation result.

Typed JSON responses remain available through the application APIs for programmatic use.

Frontend code does not duplicate:

- triage logic;
- safety or feasibility logic;
- model-scoring logic;
- expected-value logic;
- optimizer logic;
- canonical impact calculations.

The Streamlit implementation remains a challenger / reference adapter that reuses the same core planning pipeline and is not the primary submission-facing architecture.

---

## Human Authority and Physical Execution Boundary

Afterlife AI remains advisory.

Human review and final approval remain outside automatic execution.

The system does not automatically execute:

- discounts;
- inventory transfers;
- product transformation;
- external partner transactions;
- donation;
- disposal;
- pickup;
- delivery;
- other physical rescue actions.

When a human approves a physical action, execution occurs outside Afterlife AI. Any later observed result must be explicitly entered by an operator before it becomes confirmed outcome evidence inside the reconciliation layer.

---

## Runtime Artifact Roles

The full architecture exposes the runtime artifacts that influence the canonical pipeline:

### Runtime Triage Policy

Supplies deterministic triage rules.

### Runtime Capability Profile

Controls supported actions and applicable shared-capacity semantics used by candidate generation, hard gates, and allocation.

### Partner Demand Registry

May provide controlled partner evidence for external-partner rescue candidates.

The current Technical MVP registry is:

- static;
- offline;
- based on a synthetic demo fixture;
- not real-world verified.

It is not a live marketplace and does not represent verified commercial partner commitments.

### Frozen HGB-E Model Artifact and Selected Model Manifest

Provide the learned scoring artifact, feature / provenance contract, and selected-model metadata used by the scoring layer.

### Decision Configuration and Rescue Deadline

Request-level context has different responsibilities.

`rescue_deadline_at` may affect timing and feasibility gates.

The following primarily control allocation policy and optimizer constraints:

- `optimization_objective`;
- `max_logistics_budget`;
- `minimum_expected_rescue_ratio`.

Optimization policy cannot override deterministic safety or feasibility decisions.

---

## Runtime Boundary

The current Technical MVP is intentionally:

- local-first in its core design;
- synchronous;
- database-free at runtime;
- without server-side report history;
- without runtime internet dependency for the core decision pipeline;
- without automatic physical rescue execution;
- without automatic outcome persistence in the NextStep MVP.

The hosted competition deployment is a presentation / execution environment for the same bounded application flow; it does not change the core advisory authority model.

---

## Communication Rule

Use the figures according to the question being answered:

- `E2E-DIAGRAM.png` for the complete business-to-outcome lifecycle.
- `FLOWCHART.png` for procedural decisions, branches, fallbacks, and stop conditions.
- `ARCH SIMPLE FINAL.png` for judging, proposal, README, and high-level product explanation.
- `ARCH FULL FINAL.png` for technical explanation and implementation inspection.

Do not add technical detail to the simple architecture merely to make it visually equivalent to the full architecture.

The diagrams should remain complementary views of one canonical runtime.

---

## Supported Architecture Claims

The current final architecture supports claims about:

- deterministic inventory validation and triage;
- hard-gate-before-model ordering;
- learned HGB-E rescue-success scoring for eligible candidates;
- constrained global allocation through CP-SAT;
- deterministic scoring and optimizer fallbacks within documented boundaries;
- static synthetic Partner Demand Registry integration;
- canonical Rescue Decision Report generation;
- typed Sustainability Summary generation;
- evidence-bounded mass accounting;
- stateless operator-confirmed outcome reconciliation;
- human-readable Markdown report export;
- separation of expected and realized impact;
- advisory reporting and human decision authority;
- physical rescue execution remaining outside Afterlife AI.

## Unsupported Architecture Claims

The architecture does not establish:

- real-world rescue effectiveness;
- field-calibrated rescue probabilities;
- verified real-world waste reduction;
- verified merchant revenue improvement;
- live partner marketplace operation;
- automatic physical rescue execution;
- automatic outcome verification;
- persisted production outcome history;
- optimizer superiority over greedy;
- production multi-user / enterprise deployment.
