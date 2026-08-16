"""Single production entry point from XLSX intake to Rescue Decision Report."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    ActionType,
    ApprovalStatus,
    FeasibilityStatus,
    ModelScoringStatus,
    OptimizationObjective,
    SolverStatus,
    SourceType,
    ValidationStatus,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.contracts.triage import InventoryTriageResult
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
    generate_safe_disposal_candidates,
)
from afterlife_ai.pipeline.gates import (
    apply_production_hard_gates,
)
from afterlife_ai.pipeline.optimizer import (
    optimize_production_candidates,
)
from afterlife_ai.pipeline.partner_registry import (
    PartnerDemandRegistry,
    load_partner_registry,
)
from afterlife_ai.pipeline.planning import (
    build_production_planning_lots,
)
from afterlife_ai.pipeline.runtime_config import (
    RuntimeConfig,
    load_runtime_config,
)
from afterlife_ai.pipeline.scoring import (
    score_production_candidates,
)
from afterlife_ai.pipeline.triage_pipeline import (
    run_triage_pipeline,
)
from afterlife_ai.pipeline.value import (
    apply_production_expected_values,
)
from afterlife_ai.planner import optimizer as planner_optimizer
from afterlife_ai.planner.optimizer import OptimizationResult
from afterlife_ai.planner.report import (
    RescueDecisionReport,
    build_rescue_decision_report,
)
from afterlife_ai.scoring.model_provider import (
    load_frozen_model_identity,
)

ZERO = Decimal("0")
FALLBACK_MODEL_VERSION = "DETERMINISTIC_FALLBACK_V1"
DEFAULT_PARTNER_REGISTRY_PATH = Path(
    "configs/partner_registry_empty_v1.yaml"
)

class ProductionPipelineResult(BaseModel):
    """Observable outputs from the complete production analysis pipeline."""

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    raw_inventory_lots: list[RawInventoryLot]
    canonical_inventory_records: list[dict[str, Any]]
    triage_results: list[InventoryTriageResult]
    planning_lots: list[SurplusPlanningLot]

    candidates: list[CandidateAction]
    gated_candidates: list[CandidateAction]
    scored_candidates: list[CandidateAction]
    valued_candidates: list[CandidateAction]

    optimization_result: OptimizationResult
    report: RescueDecisionReport


def _load_feature_schema_version(
    config: RuntimeConfig,
) -> str:
    """Read report schema version from the locked feature contract."""

    path = config.source_of_truth.feature_schema

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        payload = yaml.safe_load(handle)

    if not isinstance(payload, dict):
        raise ValueError(
            f"Feature schema harus berupa mapping: {path}"
        )

    version = payload.get("version")

    if version is None:
        raise ValueError(
            f"Feature schema tidak memiliki version: {path}"
        )

    return str(version)


def _build_review_items(
    triage_results: list[InventoryTriageResult],
) -> list[dict[str, Any]]:
    """Build user-visible review-required quantity items."""

    items: list[dict[str, Any]] = []

    for triage in triage_results:
        if triage.review_quantity <= ZERO:
            continue

        reasons = list(
            triage.triage_reason_codes
        )

        if not reasons:
            reasons = ["REVIEW_REQUIRED"]

        items.append(
            {
                "source_lot_id": triage.source_lot_id,
                "review_quantity": triage.review_quantity,
                "reason_codes": reasons,
            }
        )

    return items


def _score_report_metadata(
    candidates: list[CandidateAction],
) -> tuple[
    dict[str, Any],
    bool,
    list[dict[str, Any]],
    list[str],
]:
    """Describe the actual scoring path used by this request."""

    model_versions = {
        candidate.model_version
        for candidate in candidates
        if (
            candidate.model_scoring_status
            is ModelScoringStatus.ALLOWED
            and candidate.model_version is not None
        )
    }

    base_limitations = [
        (
            "Runtime capability, cost, capacity, and pricing "
            "parameters are static MVP defaults and are not "
            "validated real-world operating thresholds."
        ),
        (
            "This Rescue Decision Report is advisory only. "
            "No discount, repurpose, bundle, transfer, donation, "
            "disposal, or other physical action is automatically executed."
        ),
    ]

    if not model_versions:
        return (
            {
                "provider_name": "NO_SCORING_REQUIRED",
                "score_type": "NO_ELIGIBLE_CANDIDATE_SCORE",
                "source_type": SourceType.STATIC_POLICY,
            },
            False,
            [],
            base_limitations,
        )

    if model_versions == {
        FALLBACK_MODEL_VERSION
    }:
        return (
            {
                "provider_name": FALLBACK_MODEL_VERSION,
                "score_type": "DETERMINISTIC_FALLBACK_SCORE",
                "source_type": SourceType.STATIC_POLICY,
            },
            False,
            [
                {
                    "step": "SCORING",
                    "reason": (
                        "TRAINED_MODEL_PROVIDER_UNAVAILABLE; "
                        "deterministic neutral fallback score 0.50 used."
                    ),
                }
            ],
            [
                (
                    "The trained rescue-success model was unavailable "
                    "for this request, so deterministic fallback score "
                    "0.50 was used for gate-eligible candidates."
                ),
                *base_limitations,
            ],
        )

    if len(model_versions) != 1:
        raise RuntimeError(
            "Satu request production tidak boleh mencampur "
            f"beberapa scoring provider: {sorted(model_versions)}"
        )

    provider_name = next(
        iter(model_versions)
    )

    return (
        {
            "provider_name": provider_name,
            "score_type": "MODEL_ESTIMATED_RESCUE_SUCCESS",
            "source_type": SourceType.SYNTHETIC_GENERATED,
        },
        True,
        [],
        [
            (
                "Rescue-success probabilities come from a model "
                "trained on the frozen synthetic benchmark and must "
                "not be interpreted as validated real-world probabilities."
            ),
            *base_limitations,
        ],
    )


def _build_report(
    *,
    request_id: str,
    workbook_path: Path,
    analysis_at: datetime,
    config: RuntimeConfig,
    raw_inventory_lots: list[RawInventoryLot],
    canonical_inventory_records: list[dict[str, Any]],
    triage_results: list[InventoryTriageResult],
    planning_lots: list[SurplusPlanningLot],
    valued_candidates: list[CandidateAction],
    optimization_result: OptimizationResult,
    optimization_objective: OptimizationObjective,
    partner_registry: PartnerDemandRegistry,
) -> RescueDecisionReport:
    """Adapt production outputs into the canonical report contract."""

    planning_by_id = {
        planning_lot.planning_lot_id: planning_lot
        for planning_lot in planning_lots
    }

    candidate_by_id = {
        candidate.candidate_id: candidate
        for candidate in valued_candidates
    }

    selected_allocations: list[dict[str, Any]] = []

    for allocation in optimization_result.allocations:
        candidate = candidate_by_id[
            allocation.candidate_id
        ]

        allocation_ratio = (
            allocation.allocated_quantity
            / candidate.maximum_feasible_quantity
        )

        selected_allocations.append(
            {
                "allocation_id": allocation.allocation_id,
                "candidate_id": allocation.candidate_id,
                "planning_lot_id": (
                    allocation.planning_lot_id
                ),
                "source_lot_id": (
                    planning_by_id[
                        allocation.planning_lot_id
                    ].source_lot_id
                ),
                "action_type": allocation.action_type,
                "destination_id": (
                    candidate.destination_id
                ),
                "destination_type": (
                    candidate.destination_type
                ),
                "allocated_quantity": (
                    allocation.allocated_quantity
                ),
                "offered_or_selling_price_per_unit": (
                    candidate
                    .offered_or_selling_price_per_unit
                ),
                "estimated_rescue_success_score": (
                    candidate
                    .estimated_rescue_success_score
                ),
                "direct_action_cost": (
                    candidate.direct_action_cost
                    * allocation_ratio
                ),
                "logistics_cost": (
                    candidate.logistics_cost
                    * allocation_ratio
                ),
                "handling_cost": (
                    candidate.handling_cost
                    * allocation_ratio
                ),
                "estimated_completion_hours": (
                    candidate.estimated_completion_hours
                ),
                "distance_km": candidate.distance_km,
                "expected_value_per_unit": (
                    allocation.expected_value_per_unit
                ),
                "binding_constraint_codes": list(
                    allocation.binding_constraint_codes
                ),
                "expected_cash_recovery": (
                    candidate.expected_cash_recovery
                    * allocation_ratio
                ),
                "expected_future_branch_recovery": (
                    candidate
                    .expected_future_branch_recovery
                    * allocation_ratio
                ),
                "expected_avoided_purchase_cost": (
                    candidate
                    .expected_avoided_purchase_cost
                    * allocation_ratio
                ),
                "expected_physical_rescue_quantity": (
                    candidate
                    .expected_physical_rescue_quantity
                    * allocation_ratio
                ),
                "expected_waste_quantity": (
                    candidate.expected_waste_quantity
                    * allocation_ratio
                ),
                "expected_net_recovery": (
                    allocation.expected_net_recovery
                ),
            }
        )

    selected_candidate_ids = {
        allocation.candidate_id
        for allocation in optimization_result.allocations
    }

    rejected_candidates = [
        {
            "candidate_id": candidate.candidate_id,
            "planning_lot_id": candidate.planning_lot_id,
            "action_type": candidate.action_type,
            "rejection_reason_codes": (
                list(candidate.rejection_reason_codes)
                if candidate.rejection_reason_codes
                else (
                    ["OPTIMIZER_INFEASIBLE"]
                    if (
                        optimization_result.solver_status
                        is SolverStatus.INFEASIBLE
                    )
                    else ["OPTIMIZER_NOT_SELECTED"]
                )
            ),
        }
        for candidate in valued_candidates
        if (
            candidate.rejection_reason_codes
            or candidate.candidate_id
            not in selected_candidate_ids
        )
    ]

    review_required_lots = (
        _build_review_items(
            triage_results
        )
    )

    protected_quantity = sum(
        (
            triage.protected_normal_stock_quantity
            for triage in triage_results
        ),
        ZERO,
    )

    monitor_quantity = sum(
        (
            triage.monitor_quantity
            for triage in triage_results
        ),
        ZERO,
    )

    planning_quantity = sum(
        (
            triage.planning_quantity
            for triage in triage_results
        ),
        ZERO,
    )

    no_feasible_candidate = (
        planning_quantity > ZERO
        and not any(
            candidate.feasibility_status
            is FeasibilityStatus.FEASIBLE
            for candidate in valued_candidates
        )
    )

    expired_quantity = sum(
        (
            triage.expired_quantity
            for triage in triage_results
        ),
        ZERO,
    )

    review_quantity = sum(
        (
            triage.review_quantity
            for triage in triage_results
        ),
        ZERO,
    )

    input_quantity = sum(
        (
            lot.current_quantity
            for lot in raw_inventory_lots
        ),
        ZERO,
    )

    allocated_quantity = sum(
        (
            allocation.allocated_quantity
            for allocation in optimization_result.allocations
        ),
        ZERO,
    )

    unallocated_quantity = sum(
        optimization_result.unallocated_quantities.values(),
        ZERO,
    )

    (
        score_provenance,
        model_execution_performed,
        fallback_chain,
        limitations,
    ) = _score_report_metadata(
        valued_candidates
    )
    if (
        optimization_result.solver_status
        is SolverStatus.INFEASIBLE
    ):
        limitations = [
            *limitations,
            (
                "Global optimization found no feasible "
                "allocation for the current planning "
                "quantities and constraints. No rescue "
                "allocation was automatically selected."
            ),
        ]
    if no_feasible_candidate:
        limitations = [
            *limitations,
            (
                "No feasible candidate remained after "
                "deterministic safety and feasibility "
                "gates for the current planning quantity. "
                "No rescue allocation was automatically "
                "selected."
            ),
        ]

    input_hash = sha256(
        workbook_path.read_bytes()
    ).hexdigest()

    model_version, model_sha256 = (
        load_frozen_model_identity(
            config.model.manifest_path
        )
    )

    return build_rescue_decision_report(
        request_id=request_id,
        feature_schema_version=(
            _load_feature_schema_version(
                config
            )
        ),
        input_snapshot_sha256=input_hash,
        model_version=model_version,
        model_sha256=model_sha256,
        ruleset_version=(
            config.triage.policy_version
        ),
        capability_snapshot_version=(
            config.capabilities.profile_version
        ),
        partner_registry_snapshot_id=(
            partner_registry.registry_snapshot_id
        ),
        partner_registry_snapshot_timestamp=(
            partner_registry.registry_snapshot_timestamp
        ),
        partner_registry_source_type=(
            partner_registry.source_type
        ),
        partner_registry_real_world_verified=(
            partner_registry.real_world_verified
        ),
        objective_policy_version=(
            "runtime-objective-v1.0"
        ),
        optimization_objective=(
            optimization_objective
        ),
        optimization_solver_status=(
            optimization_result.solver_status
        ),
        validation_summary={
            "status": ValidationStatus.PASSED,
            "input_lots": len(raw_inventory_lots),
            "canonical_records": len(
                canonical_inventory_records
            ),
        },
        triage_summary={
            "protected_quantity": protected_quantity,
            "monitor_quantity": monitor_quantity,
            "planning_quantity": planning_quantity,
            "expired_quantity": expired_quantity,
            "review_quantity": review_quantity,
        },
        healthy_stock=[
            {
                "source_lot_id": triage.source_lot_id,
                "routed_quantity": (
                    triage.protected_normal_stock_quantity
                ),
                "triage_reason_codes": (
                    triage.triage_reason_codes
                ),
                "urgency_level": triage.urgency_level,
            }
            for triage in triage_results
            if (
                triage.protected_normal_stock_quantity
                > ZERO
            )
        ],
        monitor_only=[
            {
                "source_lot_id": triage.source_lot_id,
                "routed_quantity": (
                    triage.monitor_quantity
                ),
                "triage_reason_codes": (
                    triage.triage_reason_codes
                ),
                "urgency_level": triage.urgency_level,
            }
            for triage in triage_results
            if triage.monitor_quantity > ZERO
        ],
        surplus_planning_lots=[
            {
                "planning_lot_id": (
                    lot.planning_lot_id
                ),
                "source_lot_id": lot.source_lot_id,
                "planning_quantity": (
                    lot.planning_quantity
                ),
            }
            for lot in planning_lots
        ],
        expired_routes=[
            {
                "source_lot_id": triage.source_lot_id,
                "routed_quantity": (
                    triage.expired_quantity
                ),
                "triage_reason_codes": (
                    triage.triage_reason_codes
                ),
                "urgency_level": triage.urgency_level,
            }
            for triage in triage_results
            if triage.expired_quantity > ZERO
        ],
        score_provenance=score_provenance,
        model_execution_performed=(
            model_execution_performed
        ),
        deterministic_execution=True,
        optimizer_random_seed=(
            planner_optimizer.OPTIMIZER_RANDOM_SEED
        ),
        optimizer_num_search_workers=(
            planner_optimizer
            .OPTIMIZER_NUM_SEARCH_WORKERS
        ),
        analysis_timestamp=analysis_at,
        batch_metrics={
            "input_lots": len(
                raw_inventory_lots
            ),
            "input_quantity": input_quantity,
            "protected_quantity": protected_quantity,
            "monitor_quantity": monitor_quantity,
            "planning_quantity": planning_quantity,
            "expired_quantity": expired_quantity,
            "review_quantity": review_quantity,
            "allocated_planning_quantity": (
                allocated_quantity
            ),
            "unallocated_planning_quantity": (
                unallocated_quantity
            ),
            "expected_total_economic_value": (
                optimization_result.objective_value
            ),
            "expected_physical_rescue_quantity": (
                optimization_result
                .expected_physical_rescue_quantity
            ),
            "expected_waste_quantity": (
                planning_quantity
                - optimization_result
                .expected_physical_rescue_quantity
            ),
            "expected_rescue_ratio": (
                optimization_result
                .expected_physical_rescue_quantity
                / planning_quantity
                if planning_quantity > ZERO
                else ZERO
            ),
        },
        selected_allocations=selected_allocations,
        rejected_candidates=rejected_candidates,
        review_required_lots=(
            review_required_lots
        ),
        fallback_chain=fallback_chain,
        limitations=limitations,
        human_exception_review_required=(
            bool(review_required_lots)
            or (
                optimization_result.solver_status
                is SolverStatus.INFEASIBLE
            )
            or no_feasible_candidate
        ),
        human_final_approval_status=(
            ApprovalStatus.PENDING
        ),
        execution_performed=False,
    )


def run_production_pipeline(
    *,
    workbook_path: str | Path,
    runtime_config_path: str | Path,
    analysis_at: datetime,
    request_id: str,
    optimization_objective: OptimizationObjective = (
        OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
    ),
    max_logistics_budget: Decimal | None = None,
    minimum_expected_rescue_ratio: Decimal | None = None,
    rescue_deadline_at: datetime | None = None,
    partner_registry_path: str | Path = (
        DEFAULT_PARTNER_REGISTRY_PATH
    ),
) -> ProductionPipelineResult:
    """Run one synchronous XLSX request through the complete MVP pipeline."""

    workbook_path = Path(
        workbook_path
    )

    runtime_config_path = Path(
        runtime_config_path
    )

    if not request_id.strip():
        raise ValueError(
            "request_id tidak boleh kosong."
        )

    if analysis_at.tzinfo is None:
        raise ValueError(
            "analysis_at wajib timezone-aware."
        )

    config = load_runtime_config(
        runtime_config_path
    )

    partner_registry = (
        load_partner_registry(
            partner_registry_path
        )
    )

    triage = run_triage_pipeline(
        workbook_path=workbook_path,
        runtime_config_path=runtime_config_path,
        analysis_at=analysis_at,
    )

    planning_lots = (
        build_production_planning_lots(
            lots=triage.raw_inventory_lots,
            triage_results=triage.triage_results,
            config=config,
        )
    )

    candidates = (
        generate_production_candidates(
            planning_lots=planning_lots,
            config=config,
            partner_registry=partner_registry,
            analysis_at=analysis_at,
        )
    )

    gated_candidates = (
        apply_production_hard_gates(
            candidates=candidates,
            planning_lots=planning_lots,
            raw_inventory_lots=(
                triage.raw_inventory_lots
            ),
            config=config,
            analysis_at=analysis_at,
            rescue_deadline_at=(
                rescue_deadline_at
            ),
        )
    )

    feasible_planning_lot_ids = {
        candidate.planning_lot_id
        for candidate in gated_candidates
        if (
            candidate.feasibility_status
            is FeasibilityStatus.FEASIBLE
        )
    }

    existing_disposal_planning_lot_ids = {
        candidate.planning_lot_id
        for candidate in gated_candidates
        if (
            candidate.action_type
            is ActionType.SAFE_DISPOSAL
        )
    }

    second_pass_planning_lots = [
        planning_lot
        for planning_lot in planning_lots
        if (
            planning_lot.planning_lot_id
            not in feasible_planning_lot_ids
            and planning_lot.planning_lot_id
            not in existing_disposal_planning_lot_ids
        )
    ]

    disposal_candidates = (
        generate_safe_disposal_candidates(
            planning_lots=second_pass_planning_lots,
            config=config,
        )
    )

    if disposal_candidates:
        gated_disposal_candidates = (
            apply_production_hard_gates(
                candidates=disposal_candidates,
                planning_lots=planning_lots,
                raw_inventory_lots=(
                    triage.raw_inventory_lots
                ),
                config=config,
                analysis_at=analysis_at,
                rescue_deadline_at=(
                    rescue_deadline_at
                ),
            )
        )

        gated_candidates = [
            *gated_candidates,
            *gated_disposal_candidates,
        ]


    scored_candidates = (
        score_production_candidates(
            candidates=gated_candidates,
            planning_lots=planning_lots,
            config=config,
        )
    )

    valued_candidates = (
        apply_production_expected_values(
            candidates=scored_candidates,
        )
    )

    optimization_result = (
        optimize_production_candidates(
            candidates=valued_candidates,
            planning_lots=planning_lots,
            config=config,
            optimization_objective=(
                optimization_objective
            ),
            max_logistics_budget=(
                max_logistics_budget
            ),
            minimum_expected_rescue_ratio=(
                minimum_expected_rescue_ratio
            ),
        )
    )

    report = _build_report(
        request_id=request_id,
        workbook_path=workbook_path,
        analysis_at=analysis_at,
        config=config,
        raw_inventory_lots=(
            triage.raw_inventory_lots
        ),
        triage_results=(
            triage.triage_results
        ),
        planning_lots=planning_lots,
        valued_candidates=valued_candidates,
        optimization_result=(
            optimization_result
        ),
        optimization_objective=(
            optimization_objective
        ),
        partner_registry=partner_registry,
        canonical_inventory_records=(
            triage.canonical_inventory_records
        ),
    )

    return ProductionPipelineResult(
        raw_inventory_lots=(
            triage.raw_inventory_lots
        ),
        canonical_inventory_records=(
            triage.canonical_inventory_records
        ),
        triage_results=(
            triage.triage_results
        ),
        planning_lots=planning_lots,
        candidates=candidates,
        gated_candidates=gated_candidates,
        scored_candidates=scored_candidates,
        valued_candidates=valued_candidates,
        optimization_result=(
            optimization_result
        ),
        report=report,
    )


__all__ = [
    "ProductionPipelineResult",
    "run_production_pipeline",
]
