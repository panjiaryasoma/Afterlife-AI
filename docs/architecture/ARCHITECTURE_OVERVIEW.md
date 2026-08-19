# Afterlife AI - Architecture Overview

## Purpose

This document defines the canonical interpretation of the two architecture figures used by Afterlife AI.

The figures intentionally serve different audiences and therefore do not need the same level of detail.

## Architecture Figure Roles

### ARCH-01 - Technical Architecture

`docs/architecture/ARCH-01.png` is the detailed technical architecture reference.

Primary audience:

- technical reviewers;
- developers;
- evaluators inspecting implementation details.

ARCH-01 prioritizes technical completeness and implementation fidelity.

It may show internal components, runtime artifacts, dependencies, pipeline stages, configuration, model resources, and supporting evidence in greater detail.

### ARCH-02 - Judge-Facing Architecture

`docs/architecture/ARCH-02.png` is the simplified architecture figure.

Primary audience:

- competition judges;
- proposal readers;
- video viewers;
- product-oriented reviewers.

ARCH-02 intentionally omits implementation detail so the core decision mechanism can be understood quickly.

Its canonical flow is:

1. Inventory XLSX and decision context.
2. Input validation.
3. Deterministic inventory triage.
4. Rescue candidate generation.
5. Deterministic safety and feasibility hard gates.
6. HGB-E rescue-success scoring for eligible candidates only.
7. Expected-value calculation.
8. Constrained global allocation through CP-SAT.
9. Rescue Decision Report.
10. Human review and approval.

## Decision Responsibilities

The architecture separates responsibilities deliberately.

### Deterministic Triage

Deterministic triage protects normal inventory and identifies the quantity that may enter rescue planning.

Only planning quantity proceeds to rescue candidate generation.

### Candidate Generation

Candidate generation creates rescue alternatives supported by the active runtime capability profile, domain rules, and available evidence.

### Deterministic Hard Gates

Hard gates determine whether a rescue candidate is eligible.

They evaluate implementation-level safety and feasibility conditions such as:

- safety;
- verification;
- storage compatibility;
- timing;
- shelf-life;
- action eligibility;
- logistics feasibility;
- partner demand and capacity;
- supported domain coverage.

A failed hard gate cannot be overridden by model scoring.

### HGB-E Rescue-Success Scoring

HGB-E scores only candidates that remain eligible after deterministic hard gates.

The output is an estimated rescue-success score.

The model does not determine safety and cannot revive a blocked candidate.

The score is evaluated using a synthetic benchmark and is not a field-validated real-world rescue probability.

### Expected-Value Calculation

Expected-value calculation converts eligible candidate information into the economic components used by the planner.

### Global Allocation

OR-Tools CP-SAT is the primary constrained global allocation optimizer.

It allocates planning quantity across eligible rescue candidates while respecting applicable request-level and shared constraints.

### Rescue Decision Report

The Rescue Decision Report exposes:

- selected allocations;
- unselected or rejected alternatives;
- allocated and unallocated quantity;
- decision evidence;
- provenance;
- warnings;
- limitations;
- human-review state.

### Human Authority

Afterlife AI remains advisory.

Human review and final approval remain outside automatic execution.

## Decision Context Boundary

Request-level decision context has different responsibilities.

`rescue_deadline` may participate in timing and feasibility evaluation.

The following primarily control allocation policy and optimizer constraints:

- `optimization_objective`;
- `max_logistics_budget`;
- `minimum_expected_rescue_ratio`.

Optimization policy does not override deterministic safety or feasibility decisions.

## Partner Demand Registry

External-partner rescue candidates may use the Partner Demand Registry.

The Technical MVP registry is:

- static;
- offline;
- based on a synthetic demo fixture;
- not real-world verified.

It may provide controlled partner evidence such as demand, capacity, compatibility, timing, and related constraints.

It is not a live marketplace and does not represent verified commercial partner commitments.

## Scoring Fallback

If the production HGB-E artifact cannot be used, the scoring layer may use the documented deterministic scoring fallback.

The fallback cannot:

- bypass deterministic hard gates;
- change a blocked candidate into an eligible candidate;
- create a validated real-world probability claim.

## Optimizer Fallback

CP-SAT remains the primary optimizer.

A deterministic allocation fallback may be used only for documented non-definitive solver outcomes where fallback semantics permit it.

Fallback behavior must preserve applicable constraints and candidate eligibility.

An `INFEASIBLE` CP-SAT result is not converted into a successful fallback allocation.

For an infeasible optimization result:

- no rescue allocation is selected;
- planning quantity remains unallocated;
- human exception review is required.

## Presentation Boundary

The primary submission-facing presentation layer is FastAPI plus Jinja2.

The presentation flow is:

Browser -> FastAPI/Jinja2 -> canonical application pipeline.

The frontend presents:

- inventory upload;
- decision-context controls;
- validation and error states;
- Rescue Decision Report information;
- provenance;
- warnings;
- limitations;
- JSON report download.

Frontend code does not duplicate:

- triage logic;
- safety or feasibility logic;
- model-scoring logic;
- expected-value logic;
- optimizer logic.

The Streamlit implementation remains a challenger/reference adapter that reuses the same core pipeline.

## Runtime Boundary

The Technical MVP is intentionally:

- local-first;
- synchronous;
- database-free at runtime;
- without server-side report history;
- without runtime internet dependency for the core flow;
- without automatic physical rescue execution.

Human final approval remains required.

The system does not automatically execute discounts, transfers, donations, disposal, logistics, or other physical rescue actions.

## Communication Rule

Use `ARCH-01.png` for technical explanation and implementation inspection.

Use `ARCH-02.png` for proposal, video, judging, and high-level product explanation.

ARCH-02 should remain intentionally simpler than ARCH-01.

Technical detail should not be added to ARCH-02 merely to make both diagrams equally complete.

If either figure conflicts with verified runtime behavior, runtime behavior and repository contracts take precedence and the figure must be corrected.

## Supported Architecture Claims

The current architecture supports claims about:

- deterministic inventory triage;
- hard-gate-before-model ordering;
- learned rescue-success scoring;
- constrained global allocation;
- static synthetic Partner Demand Registry integration;
- advisory reporting;
- human decision authority;
- local synchronous execution.

## Unsupported Architecture Claims

The architecture does not establish:

- real-world rescue effectiveness;
- field-calibrated rescue probabilities;
- live partner marketplace operation;
- automatic physical rescue execution;
- optimizer superiority over greedy;
- production multi-user deployment.
