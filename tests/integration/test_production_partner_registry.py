from datetime import UTC, datetime
from pathlib import Path

from afterlife_ai.contracts.enums import (
    ActionType,
    FeasibilityStatus,
    MatchStatus,
    ModelScoringStatus,
)
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
)
from afterlife_ai.pipeline.gates import (
    apply_production_hard_gates,
)
from afterlife_ai.pipeline.partner_registry import (
    load_partner_registry,
)
from afterlife_ai.pipeline.planning import (
    build_production_planning_lots,
)
from afterlife_ai.pipeline.runtime_config import (
    load_runtime_config,
)
from afterlife_ai.pipeline.triage_pipeline import (
    run_triage_pipeline,
)

ANALYSIS_AT = datetime(
    2026,
    8,
    5,
    12,
    0,
    tzinfo=UTC,
)


def _production_context():
    config = load_runtime_config(
        Path("configs/runtime_v1.yaml")
    )

    supported_actions = dict(
        config.capabilities.supported_actions
    )
    supported_actions[
        ActionType.EXTERNAL_PARTNER
    ] = True

    config = config.model_copy(
        update={
            "capabilities": (
                config.capabilities.model_copy(
                    update={
                        "supported_actions": (
                            supported_actions
                        )
                    }
                )
            )
        }
    )

    triage = run_triage_pipeline(
        workbook_path=Path(
            "tests/fixtures/integration_001/"
            "RAW_INVENTORY_FIXTURE.xlsx"
        ),
        runtime_config_path=Path(
            "configs/runtime_v1.yaml"
        ),
        analysis_at=ANALYSIS_AT,
    )

    planning_lots = (
        build_production_planning_lots(
            lots=triage.raw_inventory_lots,
            triage_results=(
                triage.triage_results
            ),
            config=config,
        )
    )

    return config, triage, planning_lots


def _write_registry(
    path: Path,
    *,
    demand_valid_until: str,
    category_match_status: str = "MATCH",
) -> Path:
    path.write_text(
        f"""registry_snapshot_id: PDR-DEMO-TEST-001
snapshot_mode: STATIC_OFFLINE
source_type: SYNTHETIC_DEMO_FIXTURE
real_world_verified: false
runtime_internet_required: false

matching_records:
  - source_lot_id: LOT-003
    partner_id: PARTNER-DEMO-001
    destination_type: EXTERNAL_PARTNER

    maximum_quantity: 6
    offered_or_selling_price_per_unit: 1800

    direct_action_cost: 0
    logistics_cost: 0
    handling_cost: 0

    estimated_completion_hours: 6

    active_demand_quantity: 6
    available_capacity: 6
    minimum_order_quantity: 1

    distance_km: 3

    demand_valid_until: {demand_valid_until}

    category_match_status: {category_match_status}
    package_size_match_status: MATCH
    customer_segment_match_status: MATCH
    storage_compatibility_status: MATCH
""",
        encoding="utf-8",
    )

    return path


def _partner_candidates(
    tmp_path: Path,
    *,
    demand_valid_until: str,
    category_match_status: str = "MATCH",
):
    config, triage, planning_lots = (
        _production_context()
    )

    registry_path = _write_registry(
        tmp_path / "partner_registry.yaml",
        demand_valid_until=(
            demand_valid_until
        ),
        category_match_status=(
            category_match_status
        ),
    )

    registry = load_partner_registry(
        registry_path
    )

    candidates = (
        generate_production_candidates(
            planning_lots=planning_lots,
            config=config,
            partner_registry=registry,
            analysis_at=ANALYSIS_AT,
        )
    )

    partner_candidates = [
        candidate
        for candidate in candidates
        if (
            candidate.action_type
            is ActionType.EXTERNAL_PARTNER
        )
    ]

    return (
        config,
        triage,
        planning_lots,
        partner_candidates,
    )


def test_static_partner_registry_generates_fresh_feasible_candidate(
    tmp_path: Path,
) -> None:
    (
        config,
        triage,
        planning_lots,
        partner_candidates,
    ) = _partner_candidates(
        tmp_path,
        demand_valid_until=(
            "2026-08-31T23:59:59Z"
        ),
    )

    assert len(partner_candidates) == 1

    candidate = partner_candidates[0]

    assert candidate.planning_lot_id == (
        "PLAN-LOT-003"
    )
    assert candidate.destination_id == (
        "PARTNER-DEMO-001"
    )
    assert candidate.destination_type == (
        "EXTERNAL_PARTNER"
    )

    assert (
        candidate.maximum_feasible_quantity
        == 6
    )
    assert candidate.active_demand_quantity == 6
    assert candidate.available_capacity == 6

    assert (
        candidate.demand_freshness_hours
        is not None
    )
    assert (
        candidate.demand_freshness_hours
        > 0
    )

    assert (
        candidate.category_match_status
        is MatchStatus.MATCH
    )
    assert (
        candidate.package_size_match_status
        is MatchStatus.MATCH
    )
    assert (
        candidate.customer_segment_match_status
        is MatchStatus.MATCH
    )

    gated = apply_production_hard_gates(
        candidates=partner_candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=(
            triage.raw_inventory_lots
        ),
        config=config,
        analysis_at=ANALYSIS_AT,
    )

    assert len(gated) == 1

    result = gated[0]

    assert (
        result.feasibility_status
        is FeasibilityStatus.FEASIBLE
    )
    assert (
        result.model_scoring_status
        is ModelScoringStatus.DEFERRED
    )
    assert (
        "STALE_PARTNER_DEMAND"
        not in result.rejection_reason_codes
    )


def test_static_partner_registry_stale_demand_is_blocked(
    tmp_path: Path,
) -> None:
    (
        config,
        triage,
        planning_lots,
        partner_candidates,
    ) = _partner_candidates(
        tmp_path,
        demand_valid_until=(
            "2026-08-04T23:59:59Z"
        ),
    )

    assert len(partner_candidates) == 1

    gated = apply_production_hard_gates(
        candidates=partner_candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=(
            triage.raw_inventory_lots
        ),
        config=config,
        analysis_at=ANALYSIS_AT,
    )

    result = gated[0]

    assert (
        result.feasibility_status
        is FeasibilityStatus.INFEASIBLE
    )
    assert (
        result.model_scoring_status
        is ModelScoringStatus.BLOCKED
    )
    assert (
        "STALE_PARTNER_DEMAND"
        in result.rejection_reason_codes
    )


def test_static_partner_registry_category_mismatch_is_blocked(
    tmp_path: Path,
) -> None:
    (
        config,
        triage,
        planning_lots,
        partner_candidates,
    ) = _partner_candidates(
        tmp_path,
        demand_valid_until=(
            "2026-08-31T23:59:59Z"
        ),
        category_match_status="MISMATCH",
    )

    assert len(partner_candidates) == 1

    gated = apply_production_hard_gates(
        candidates=partner_candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=(
            triage.raw_inventory_lots
        ),
        config=config,
        analysis_at=ANALYSIS_AT,
    )

    result = gated[0]

    assert (
        result.feasibility_status
        is FeasibilityStatus.INFEASIBLE
    )
    assert (
        result.model_scoring_status
        is ModelScoringStatus.BLOCKED
    )
    assert (
        "PARTNER_CATEGORY_MISMATCH"
        in result.rejection_reason_codes
    )



def test_static_partner_registry_storage_mismatch_is_blocked(
    tmp_path: Path,
) -> None:
    config, triage, planning_lots = (
        _production_context()
    )

    registry_path = _write_registry(
        tmp_path / "partner_registry.yaml",
        demand_valid_until=(
            "2026-08-31T23:59:59Z"
        ),
    )

    registry_text = registry_path.read_text(
        encoding="utf-8"
    )

    registry_path.write_text(
        registry_text.replace(
            "storage_compatibility_status: MATCH",
            "storage_compatibility_status: MISMATCH",
            1,
        ),
        encoding="utf-8",
    )

    registry = load_partner_registry(
        registry_path
    )

    candidates = (
        generate_production_candidates(
            planning_lots=planning_lots,
            config=config,
            partner_registry=registry,
            analysis_at=ANALYSIS_AT,
        )
    )

    partner_candidates = [
        candidate
        for candidate in candidates
        if (
            candidate.action_type
            is ActionType.EXTERNAL_PARTNER
        )
    ]

    assert len(partner_candidates) == 1
    assert (
        partner_candidates[
            0
        ].storage_compatibility_status
        is MatchStatus.MISMATCH
    )

    gated = apply_production_hard_gates(
        candidates=partner_candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=(
            triage.raw_inventory_lots
        ),
        config=config,
        analysis_at=ANALYSIS_AT,
    )

    result = gated[0]

    assert (
        result.feasibility_status
        is FeasibilityStatus.INFEASIBLE
    )
    assert (
        result.model_scoring_status
        is ModelScoringStatus.BLOCKED
    )
    assert (
        "STORAGE_INCOMPATIBLE"
        in result.rejection_reason_codes
    )
