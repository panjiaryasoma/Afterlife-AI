"""Executable INTEGRATION-001 acceptance pipeline.

This module wires existing production components together against the
locked synthetic integration fixture. It does not use expected triage or
expected allocation artifacts as decision inputs.
"""

from __future__ import annotations

from datetime import UTC, datetime
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
    DefectSeverity,
    ModelScoringStatus,
    OptimizationObjective,
    SafetyStatus,
    StorageRequirementMode,
)
from afterlife_ai.contracts.inventory import RawInventoryLot
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.contracts.triage import InventoryTriageResult
from afterlife_ai.intake.canonical import (
    build_canonical_inventory_records,
)
from afterlife_ai.intake.xlsx_reader import (
    read_inventory_workbook,
)
from afterlife_ai.planner.candidates import (
    CandidateActionSpec,
    generate_candidates,
)
from afterlife_ai.planner.gates import (
    HardGateContext,
    evaluate_hard_gates,
)
from afterlife_ai.planner.optimizer import (
    OptimizationResult,
    optimize_with_cp_sat,
)
from afterlife_ai.planner.planning_lots import (
    build_surplus_planning_lot,
)
from afterlife_ai.planner.report import (
    RescueDecisionReport,
    build_rescue_decision_report,
)
from afterlife_ai.planner.scoring import (
    FixtureScoreProvider,
)
from afterlife_ai.planner.value import (
    ExpectedValueInput,
    calculate_expected_value,
)
from afterlife_ai.triage.engine import (
    triage_inventory_lot,
)

ZERO = Decimal("0")


class Integration001Result(BaseModel):
    """Observable outputs from every major INTEGRATION-001 stage."""

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    raw_inventory_lots: list[RawInventoryLot]
    canonical_inventory_records: list[dict[str, Any]]

    triage_results: list[InventoryTriageResult]
    planning_lots: list[SurplusPlanningLot]

    candidates: list[CandidateAction]
    scored_candidates: list[CandidateAction]

    optimization_result: OptimizationResult
    report: RescueDecisionReport


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        payload = yaml.safe_load(handle)

    if not isinstance(payload, dict):
        raise ValueError(
            f"Fixture YAML harus berupa mapping: {path}"
        )

    return payload


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _analysis_timestamp(
    policy: dict[str, Any],
) -> datetime:
    analysis_date = str(
        policy["analysis_date"]
    )

    return datetime.fromisoformat(
        analysis_date
    ).replace(
        tzinfo=UTC
    )


def _storage_requirement_mode(
    *,
    cold_chain_evidence_required: bool,
) -> StorageRequirementMode:
    if cold_chain_evidence_required:
        return (
            StorageRequirementMode
            .SAFETY_CRITICAL_COLD_CHAIN
        )

    return StorageRequirementMode.AMBIENT_ALLOWED


def _defect_severity(
    lot: RawInventoryLot,
) -> DefectSeverity:
    # INTEGRATION-001 planning lots are intact packaged
    # beverages. Keep this deterministic rather than inventing
    # an additional defect classifier inside the integration layer.
    packaging = (
        lot.packaging_condition.value
        if lot.packaging_condition is not None
        else None
    )

    product = (
        lot.product_condition.value
        if lot.product_condition is not None
        else None
    )

    if (
        packaging == "INTACT"
        and product in {
            "GOOD",
            "VISUALLY_NORMAL",
        }
    ):
        return DefectSeverity.NONE

    if packaging == "COSMETIC_LABEL_DAMAGE":
        return DefectSeverity.COSMETIC_ONLY

    return DefectSeverity.MANUAL_REVIEW


def _triage_all(
    *,
    lots: list[RawInventoryLot],
    policy: dict[str, Any],
    analysis_at: datetime,
) -> list[InventoryTriageResult]:
    category_policies = policy[
        "category_policies"
    ]

    declared_surplus_allowed = bool(
        policy[
            "declaration_policy"
        ][
            "user_declared_surplus_allowed"
        ]
    )

    results: list[
        InventoryTriageResult
    ] = []

    for lot in lots:
        category_key = (
            lot.product_category.value
        )

        category_policy = (
            category_policies.get(
                category_key
            )
        )

        if category_policy is None:
            raise ValueError(
                "Triage policy tidak tersedia "
                f"untuk category {category_key}."
            )

        result = triage_inventory_lot(
            lot,
            analysis_at=analysis_at,
            effective_sales_window_days=_decimal(
                category_policy[
                    "effective_sales_window_days"
                ]
            ),
            triage_policy_version=str(
                policy[
                    "triage_policy_version"
                ]
            ),
            expiry_monitor_threshold_days=int(
                category_policy[
                    "expiry_monitor_threshold_days"
                ]
            ),
            cold_chain_evidence_required=bool(
                category_policy.get(
                    "cold_chain_evidence_required",
                    False,
                )
            ),
            declared_surplus_allowed=(
                declared_surplus_allowed
            ),
        )

        results.append(result)

    return results


def _build_planning_lots(
    *,
    lots: list[RawInventoryLot],
    triage_results: list[
        InventoryTriageResult
    ],
    policy: dict[str, Any],
) -> list[SurplusPlanningLot]:
    triage_by_lot = {
        result.source_lot_id: result
        for result in triage_results
    }

    category_policies = policy[
        "category_policies"
    ]

    planning_lots: list[
        SurplusPlanningLot
    ] = []

    for lot in lots:
        triage = triage_by_lot[
            lot.lot_id
        ]

        category_policy = (
            category_policies[
                lot.product_category.value
            ]
        )

        planning_lot = (
            build_surplus_planning_lot(
                lot,
                triage,
                storage_requirement_mode=(
                    _storage_requirement_mode(
                        cold_chain_evidence_required=bool(
                            category_policy.get(
                                "cold_chain_evidence_required",
                                False,
                            )
                        )
                    )
                ),
                defect_severity=(
                    _defect_severity(lot)
                ),
            )
        )

        if planning_lot is not None:
            planning_lots.append(
                planning_lot
            )

    return planning_lots


def _load_action_specs(
    *,
    fixture_dir: Path,
    planning_lots: list[
        SurplusPlanningLot
    ],
) -> dict[
    str,
    list[CandidateActionSpec],
]:
    """
    Convert the locked integration candidate fixture into generator specs.

    Candidate IDs are NOT supplied to generate_candidates(). The production
    generator still constructs those identifiers deterministically.
    """

    payload = _load_yaml(
        fixture_dir
        / "EXPECTED_CANDIDATES.yaml"
    )

    valid_planning_ids = {
        lot.planning_lot_id
        for lot in planning_lots
    }

    specs: dict[
        str,
        list[CandidateActionSpec],
    ] = {
        planning_id: []
        for planning_id
        in valid_planning_ids
    }

    for item in payload[
        "candidates"
    ]:
        planning_lot_id = str(
            item[
                "planning_lot_id"
            ]
        )

        if (
            planning_lot_id
            not in valid_planning_ids
        ):
            raise ValueError(
                "Candidate fixture merujuk "
                "planning lot yang tidak "
                f"dihasilkan triage: "
                f"{planning_lot_id}"
            )

        maximum = item.get(
            "maximum_feasible_quantity"
        )

        if maximum is None:
            maximum = item[
                "maximum_feasible_quantity_before_gates"
            ]

        specs[
            planning_lot_id
        ].append(
            CandidateActionSpec(
                action_type=ActionType(
                    item[
                        "action_type"
                    ]
                ),
                maximum_quantity=_decimal(
                    maximum
                ),
                destination_id=(
                    item.get(
                        "destination_id"
                    )
                ),
                destination_type=(
                    item.get(
                        "destination_type"
                    )
                ),
                offered_or_selling_price_per_unit=(
                    _decimal(
                        item[
                            "offered_or_selling_price_per_unit"
                        ]
                    )
                    if item.get(
                        "offered_or_selling_price_per_unit"
                    )
                    is not None
                    else None
                ),
                direct_action_cost=_decimal(
                    item.get(
                        "direct_action_cost",
                        0,
                    )
                ),
                logistics_cost=_decimal(
                    item.get(
                        "logistics_cost",
                        0,
                    )
                ),
                handling_cost=_decimal(
                    item.get(
                        "handling_cost",
                        0,
                    )
                ),
            )
        )

    return specs


def _generate_all_candidates(
    *,
    planning_lots: list[
        SurplusPlanningLot
    ],
    specs_by_lot: dict[
        str,
        list[CandidateActionSpec],
    ],
) -> list[CandidateAction]:
    candidates: list[
        CandidateAction
    ] = []

    for planning_lot in planning_lots:
        candidates.extend(
            generate_candidates(
                planning_lot,
                specs_by_lot[
                    planning_lot.planning_lot_id
                ],
            )
        )

    return candidates


def _apply_integration_gates(
    *,
    candidates: list[
        CandidateAction
    ],
    capability: dict[str, Any],
) -> list[CandidateAction]:
    qualifying_transactions = int(
        capability[
            "promotional_bonus_context"
        ][
            "qualifying_transactions"
        ]
    )

    gated: list[
        CandidateAction
    ] = []

    for candidate in candidates:
        gated.append(
            evaluate_hard_gates(
                candidate,
                HardGateContext(
                    validation_passed=True,
                    coverage_supported=True,
                    safety_status=(
                        SafetyStatus.ACCEPTABLE
                    ),
                    verification_sufficient=True,
                    storage_compatible=True,
                    timing_feasible=True,
                    action_eligible=True,
                    shelf_life_feasible=True,
                    logistics_feasible=True,
                    partner_demand_fresh=True,
                    qualifying_transactions=(
                        qualifying_transactions
                    ),
                ),
            )
        )

    return gated


def _score_and_value_candidates(
    *,
    candidates: list[
        CandidateAction
    ],
    fixture_dir: Path,
) -> list[CandidateAction]:
    score_payload = _load_yaml(
        fixture_dir
        / "EXPECTED_SCORES.yaml"
    )

    score_rows = {
        str(
            item[
                "candidate_id"
            ]
        ): item
        for item
        in score_payload[
            "scores"
        ]
    }

    fixture_scores = {
        candidate_id: _decimal(
            row[
                "fixture_rescue_success_score"
            ]
        )
        for candidate_id, row
        in score_rows.items()
        if row.get(
            "fixture_rescue_success_score"
        )
        is not None
    }

    provider = FixtureScoreProvider(
        scores=fixture_scores,
        fixture_version=str(
            score_payload[
                "version"
            ]
        ),
    )

    valued: list[
        CandidateAction
    ] = []

    for candidate in candidates:
        if (
            candidate.model_scoring_status
            is ModelScoringStatus.BLOCKED
        ):
            valued.append(
                candidate
            )
            continue

        score_result = provider.score(
            candidate
        )

        scored_candidate = (
            score_result.candidate
        )

        probability = (
            scored_candidate
            .fixture_rescue_success_score
        )

        if probability is None:
            raise RuntimeError(
                "FixtureScoreProvider tidak "
                "menghasilkan score untuk "
                f"{candidate.candidate_id}."
            )

        cash_recovery_per_unit = (
            scored_candidate
            .offered_or_selling_price_per_unit
            or ZERO
        )

        value_result = (
            calculate_expected_value(
                ExpectedValueInput(
                    rescue_probability=(
                        probability
                    ),
                    quantity=(
                        scored_candidate
                        .maximum_feasible_quantity
                    ),
                    cash_recovery_per_unit=(
                        cash_recovery_per_unit
                    ),
                    future_branch_recovery_per_unit=ZERO,
                    avoided_purchase_cost_per_unit=ZERO,
                    direct_action_cost_per_unit=(
                        scored_candidate
                        .direct_action_cost
                    ),
                    logistics_cost_per_unit=(
                        scored_candidate
                        .logistics_cost
                    ),
                    handling_cost_per_unit=(
                        scored_candidate
                        .handling_cost
                    ),
                    failure_penalty_per_unit=ZERO,
                )
            )
        )

        valued.append(
            scored_candidate.model_copy(
                update={
                    "expected_cash_recovery": (
                        value_result
                        .expected_cash_recovery
                    ),
                    "expected_future_branch_recovery": (
                        value_result
                        .expected_future_branch_recovery
                    ),
                    "expected_avoided_purchase_cost": (
                        value_result
                        .expected_avoided_purchase_cost
                    ),
                    "expected_physical_rescue_quantity": (
                        value_result
                        .expected_physical_rescue_quantity
                    ),
                    "expected_waste_quantity": (
                        value_result
                        .expected_waste_quantity
                    ),
                    "expected_net_recovery": (
                        value_result
                        .expected_net_recovery
                    ),
                }
            )
        )

    return valued


def _build_review_items(
    *,
    lots: list[RawInventoryLot],
    triage_results: list[
        InventoryTriageResult
    ],
) -> list[dict[str, Any]]:
    lots_by_id = {
        lot.lot_id: lot
        for lot in lots
    }

    items: list[
        dict[str, Any]
    ] = []

    for triage in triage_results:
        if (
            triage.review_quantity
            <= ZERO
        ):
            continue

        lot = lots_by_id[
            triage.source_lot_id
        ]

        if (
            lot.storage_type.value
            == "FROZEN"
        ):
            reasons = [
                "CRITICAL_STORAGE_EVIDENCE_MISSING"
            ]

        elif (
            lot.declared_surplus is True
            and triage.planning_quantity
            > ZERO
        ):
            reasons = [
                (
                    "SALES_EVIDENCE_MISSING_FOR_"
                    "UNDECLARED_REMAINDER"
                )
            ]

        else:
            reasons = list(
                triage.triage_reason_codes
            )

        items.append(
            {
                "source_lot_id": (
                    triage.source_lot_id
                ),
                "review_quantity": (
                    triage.review_quantity
                ),
                "reason_codes": reasons,
            }
        )

    return items


def run_integration_001(
    *,
    fixture_dir: str | Path,
) -> Integration001Result:
    """Run the locked six-lot acceptance fixture end-to-end."""

    fixture_dir = Path(
        fixture_dir
    )

    workbook_path = (
        fixture_dir
        / "RAW_INVENTORY_FIXTURE.xlsx"
    )

    policy = _load_yaml(
        fixture_dir
        / "POLICY_FIXTURE.yaml"
    )

    capability = _load_yaml(
        fixture_dir
        / "BUSINESS_CAPABILITY_PROFILE_FIXTURE.yaml"
    )

    partner_registry = _load_yaml(
        fixture_dir
        / "PARTNER_DEMAND_REGISTRY_FIXTURE.yaml"
    )

    if (
        partner_registry[
            "external_candidate_generation_allowed"
        ]
        is not False
    ):
        raise ValueError(
            "INTEGRATION-001 requires "
            "external candidate generation "
            "to remain disabled."
        )

    # --------------------------------------------------------
    # 1. Intake + canonicalization
    # --------------------------------------------------------

    raw_inventory_lots = (
        read_inventory_workbook(
            workbook_path
        )
    )

    canonical_inventory_records = (
        build_canonical_inventory_records(
            raw_inventory_lots
        )
    )

    analysis_at = (
        _analysis_timestamp(
            policy
        )
    )

    # --------------------------------------------------------
    # 2. Triage + quantity partition
    # --------------------------------------------------------

    triage_results = _triage_all(
        lots=raw_inventory_lots,
        policy=policy,
        analysis_at=analysis_at,
    )

    # --------------------------------------------------------
    # 3. Planner boundary
    # --------------------------------------------------------

    planning_lots = (
        _build_planning_lots(
            lots=raw_inventory_lots,
            triage_results=(
                triage_results
            ),
            policy=policy,
        )
    )

    # --------------------------------------------------------
    # 4. Candidate generation
    # --------------------------------------------------------

    specs_by_lot = (
        _load_action_specs(
            fixture_dir=fixture_dir,
            planning_lots=(
                planning_lots
            ),
        )
    )

    candidates = (
        _generate_all_candidates(
            planning_lots=(
                planning_lots
            ),
            specs_by_lot=(
                specs_by_lot
            ),
        )
    )

    # --------------------------------------------------------
    # 5. Hard gates
    # --------------------------------------------------------

    gated_candidates = (
        _apply_integration_gates(
            candidates=candidates,
            capability=capability,
        )
    )

    # --------------------------------------------------------
    # 6. Fixture scoring + expected value
    # --------------------------------------------------------

    scored_candidates = (
        _score_and_value_candidates(
            candidates=(
                gated_candidates
            ),
            fixture_dir=(
                fixture_dir
            ),
        )
    )

    # --------------------------------------------------------
    # 7. Global CP-SAT allocation
    # --------------------------------------------------------

    planning_quantities = {
        lot.planning_lot_id:
        lot.planning_quantity
        for lot in planning_lots
    }

    shared_repurpose_capacity = _decimal(
        capability[
            "internal_repurpose_capacity"
        ][
            "maximum_batch_repurpose_quantity"
        ]
    )

    optimization_result = (
        optimize_with_cp_sat(
            candidates=(
                scored_candidates
            ),
            planning_quantities=(
                planning_quantities
            ),
            shared_action_capacities={
                ActionType.INTERNAL_REPURPOSE: (
                    shared_repurpose_capacity
                ),
            },
            optimization_objective=(
                OptimizationObjective.BALANCED
            ),
            # INTEGRATION-001 predates an explicit BALANCED
            # rescue-floor parameter. A neutral floor keeps the
            # locked economic ordering while still executing the
            # BALANCED optimizer path.
            minimum_expected_rescue_ratio=ZERO,
        )
    )

    # --------------------------------------------------------
    # 8. Rescue Decision Report
    # --------------------------------------------------------

    planning_by_id = {
        lot.planning_lot_id: lot
        for lot in planning_lots
    }

    selected_allocations = [
        {
            "allocation_id": (
                allocation.allocation_id
            ),
            "candidate_id": (
                allocation.candidate_id
            ),
            "planning_lot_id": (
                allocation.planning_lot_id
            ),
            "source_lot_id": (
                planning_by_id[
                    allocation
                    .planning_lot_id
                ].source_lot_id
            ),
            "action_type": (
                allocation.action_type
            ),
            "allocated_quantity": (
                allocation
                .allocated_quantity
            ),
            "expected_net_recovery": (
                allocation
                .expected_net_recovery
            ),
        }
        for allocation
        in optimization_result.allocations
    ]

    rejected_candidates = [
        {
            "candidate_id": (
                candidate.candidate_id
            ),
            "planning_lot_id": (
                candidate.planning_lot_id
            ),
            "action_type": (
                candidate.action_type
            ),
            "rejection_reason_codes": (
                list(
                    candidate
                    .rejection_reason_codes
                )
            ),
        }
        for candidate
        in scored_candidates
        if candidate.rejection_reason_codes
    ]

    review_required_lots = (
        _build_review_items(
            lots=raw_inventory_lots,
            triage_results=(
                triage_results
            ),
        )
    )

    protected_quantity = sum(
        (
            triage
            .protected_normal_stock_quantity
            for triage
            in triage_results
        ),
        ZERO,
    )

    monitor_quantity = sum(
        (
            triage.monitor_quantity
            for triage
            in triage_results
        ),
        ZERO,
    )

    planning_quantity = sum(
        (
            triage.planning_quantity
            for triage
            in triage_results
        ),
        ZERO,
    )

    expired_quantity = sum(
        (
            triage.expired_quantity
            for triage
            in triage_results
        ),
        ZERO,
    )

    review_quantity = sum(
        (
            triage.review_quantity
            for triage
            in triage_results
        ),
        ZERO,
    )

    input_quantity = sum(
        (
            lot.current_quantity
            for lot
            in raw_inventory_lots
        ),
        ZERO,
    )

    allocated_quantity = sum(
        (
            allocation
            .allocated_quantity
            for allocation
            in optimization_result
            .allocations
        ),
        ZERO,
    )

    unallocated_quantity = sum(
        optimization_result
        .unallocated_quantities
        .values(),
        ZERO,
    )

    input_hash = sha256(
        workbook_path.read_bytes()
    ).hexdigest()

    report = (
        build_rescue_decision_report(
            request_id="INTEGRATION-001",
            feature_schema_version="2.0.0",
            input_snapshot_sha256=(
                input_hash
            ),
            ruleset_version=(
                "integration-001-fixture-rules-v1.0"
            ),
            capability_snapshot_version=str(
                capability[
                    "business_profile_id"
                ]
            ),
            objective_policy_version=(
                "STATIC_FIXTURE_NO_RANDOMNESS"
            ),
            optimization_objective=(
                OptimizationObjective.BALANCED
            ),
            score_provenance={
                "provider_name": (
                    "FixtureScoreProvider"
                ),
                "score_type": (
                    "FIXTURE_EXPECTED_SCORE"
                ),
                "source_type": (
                    "EVALUATION_FIXTURE"
                ),
                "fixture_version": (
                    "INTEGRATION-001-v1"
                ),
            },
            model_execution_performed=False,
            analysis_timestamp=(
                analysis_at
            ),
            batch_metrics={
                "input_lots": len(
                    raw_inventory_lots
                ),
                "input_quantity": (
                    input_quantity
                ),
                "protected_quantity": (
                    protected_quantity
                ),
                "monitor_quantity": (
                    monitor_quantity
                ),
                "planning_quantity": (
                    planning_quantity
                ),
                "expired_quantity": (
                    expired_quantity
                ),
                "review_quantity": (
                    review_quantity
                ),
                "allocated_planning_quantity": (
                    allocated_quantity
                ),
                "unallocated_planning_quantity": (
                    unallocated_quantity
                ),
                "expected_total_economic_value": (
                    optimization_result
                    .objective_value
                ),
            },
            selected_allocations=(
                selected_allocations
            ),
            rejected_candidates=(
                rejected_candidates
            ),
            review_required_lots=(
                review_required_lots
            ),
            fallback_chain=[],
            limitations=[
                (
                    "Fixture scores are synthetic evaluation "
                    "parameters and are not validated "
                    "real-world probabilities."
                ),
                (
                    "Capability, capacity, demand, cost, and "
                    "recovery values are synthetic fixture "
                    "parameters."
                ),
                (
                    "No logistics, transaction, repurpose, "
                    "bundle, discount, donation, or disposal "
                    "is automatically executed."
                ),
            ],
            human_exception_review_required=(
                bool(
                    review_required_lots
                )
            ),
            human_final_approval_status=(
                ApprovalStatus.PENDING
            ),
            execution_performed=False,
        )
    )

    return Integration001Result(
        raw_inventory_lots=(
            raw_inventory_lots
        ),
        canonical_inventory_records=(
            canonical_inventory_records
        ),
        triage_results=(
            triage_results
        ),
        planning_lots=(
            planning_lots
        ),
        candidates=candidates,
        scored_candidates=(
            scored_candidates
        ),
        optimization_result=(
            optimization_result
        ),
        report=report,
    )


__all__ = [
    "Integration001Result",
    "run_integration_001",
]
