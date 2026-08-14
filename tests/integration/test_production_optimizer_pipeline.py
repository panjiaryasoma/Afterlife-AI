from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from pytest import MonkeyPatch

from afterlife_ai.contracts.enums import (
    ActionType,
    OptimizationObjective,
    SolverStatus,
)
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
)
from afterlife_ai.pipeline.gates import (
    apply_production_hard_gates,
)
from afterlife_ai.pipeline.optimizer import (
    OptimizationResult,
    optimize_production_candidates,
)
from afterlife_ai.pipeline.planning import (
    build_production_planning_lots,
)
from afterlife_ai.pipeline.runtime_config import (
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

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)

WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def test_production_optimizer_enforces_shared_capacity_and_quantity() -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    result = optimize_production_candidates(
        candidates=valued,
        planning_lots=planning_lots,
        config=config,
    )

    assert result.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }

    planning_quantities = {
        lot.planning_lot_id: lot.planning_quantity
        for lot in planning_lots
    }

    allocated_by_lot = defaultdict(
        lambda: Decimal("0")
    )

    repurpose_quantity = Decimal("0")

    for allocation in result.allocations:
        allocated_by_lot[
            allocation.planning_lot_id
        ] += allocation.allocated_quantity

        if (
            allocation.action_type
            is ActionType.INTERNAL_REPURPOSE
        ):
            repurpose_quantity += (
                allocation.allocated_quantity
            )

    assert repurpose_quantity <= Decimal("6")

    for planning_lot_id, quantity in (
        planning_quantities.items()
    ):
        assert (
            allocated_by_lot[planning_lot_id]
            + result.unallocated_quantities[
                planning_lot_id
            ]
            == quantity
        )

def test_production_optimizer_uses_deterministic_fallback_when_cp_sat_unknown(
    monkeypatch: MonkeyPatch,
) -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    planning_quantities = {
        lot.planning_lot_id: lot.planning_quantity
        for lot in planning_lots
    }

    def fake_cp_sat(**_: object) -> OptimizationResult:
        return OptimizationResult(
            solver_status=SolverStatus.UNKNOWN,
            objective_value=Decimal("0"),
            allocations=[],
            unallocated_quantities=planning_quantities,
        )

    monkeypatch.setattr(
        "afterlife_ai.pipeline.optimizer.optimize_with_cp_sat",
        fake_cp_sat,
    )

    result = optimize_production_candidates(
        candidates=valued,
        planning_lots=planning_lots,
        config=config,
    )

    assert (
        result.solver_status
        is SolverStatus.FALLBACK_USED
    )

    assert result.allocations

    allocated_by_lot = defaultdict(
        lambda: Decimal("0")
    )

    repurpose_quantity = Decimal("0")

    for allocation in result.allocations:
        allocated_by_lot[
            allocation.planning_lot_id
        ] += allocation.allocated_quantity

        if (
            allocation.action_type
            is ActionType.INTERNAL_REPURPOSE
        ):
            repurpose_quantity += (
                allocation.allocated_quantity
            )

    assert repurpose_quantity <= Decimal("6")

    for planning_lot_id, quantity in (
        planning_quantities.items()
    ):
        assert (
            allocated_by_lot[planning_lot_id]
            + result.unallocated_quantities[
                planning_lot_id
            ]
            == quantity
        )

def test_production_optimizer_fallback_preserves_shared_destination_capacity(
    monkeypatch: MonkeyPatch,
) -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=(
            triage.raw_inventory_lots
        ),
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    assert len(planning_lots) >= 2

    source_by_lot = {}

    for candidate in valued:
        source_by_lot.setdefault(
            candidate.planning_lot_id,
            candidate,
        )

    first_lot = planning_lots[0]
    second_lot = planning_lots[1]

    first_source = source_by_lot[
        first_lot.planning_lot_id
    ]

    second_source = source_by_lot[
        second_lot.planning_lot_id
    ]

    shared_partner_candidates = [
        first_source.model_copy(
            update={
                "candidate_id": (
                    "CAND-FALLBACK-PARTNER-A"
                ),
                "action_type": (
                    ActionType.EXTERNAL_PARTNER
                ),
                "destination_id": (
                    "PARTNER-FALLBACK-SHARED"
                ),
                "maximum_feasible_quantity": (
                    Decimal("6")
                ),
                "active_demand_quantity": (
                    Decimal("6")
                ),
                "available_capacity": (
                    Decimal("6")
                ),
                "expected_net_recovery": (
                    Decimal("60000")
                ),
            }
        ),
        second_source.model_copy(
            update={
                "candidate_id": (
                    "CAND-FALLBACK-PARTNER-B"
                ),
                "action_type": (
                    ActionType.EXTERNAL_PARTNER
                ),
                "destination_id": (
                    "PARTNER-FALLBACK-SHARED"
                ),
                "maximum_feasible_quantity": (
                    Decimal("6")
                ),
                "active_demand_quantity": (
                    Decimal("6")
                ),
                "available_capacity": (
                    Decimal("6")
                ),
                "expected_net_recovery": (
                    Decimal("60000")
                ),
            }
        ),
    ]

    planning_quantities = {
        lot.planning_lot_id:
        lot.planning_quantity
        for lot in planning_lots
    }

    def fake_cp_sat(
        **_: object,
    ) -> OptimizationResult:
        return OptimizationResult(
            solver_status=SolverStatus.UNKNOWN,
            objective_value=Decimal("0"),
            allocations=[],
            unallocated_quantities=(
                planning_quantities
            ),
        )

    monkeypatch.setattr(
        (
            "afterlife_ai.pipeline.optimizer."
            "optimize_with_cp_sat"
        ),
        fake_cp_sat,
    )

    result = optimize_production_candidates(
        candidates=shared_partner_candidates,
        planning_lots=planning_lots,
        config=config,
    )

    assert (
        result.solver_status
        is SolverStatus.FALLBACK_USED
    )

    shared_partner_quantity = sum(
        (
            allocation.allocated_quantity
            for allocation in result.allocations
            if allocation.candidate_id
            in {
                "CAND-FALLBACK-PARTNER-A",
                "CAND-FALLBACK-PARTNER-B",
            }
        ),
        Decimal("0"),
    )

    assert (
        shared_partner_quantity
        == Decimal("6")
    )

def test_production_optimizer_does_not_fallback_when_cp_sat_infeasible(
    monkeypatch: MonkeyPatch,
) -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    planning_quantities = {
        lot.planning_lot_id: lot.planning_quantity
        for lot in planning_lots
    }

    def fake_cp_sat(**_: object) -> OptimizationResult:
        return OptimizationResult(
            solver_status=SolverStatus.INFEASIBLE,
            objective_value=Decimal("0"),
            allocations=[],
            unallocated_quantities=planning_quantities,
        )

    def forbidden_fallback(**_: object) -> object:
        raise AssertionError(
            "Deterministic fallback must not run "
            "for an INFEASIBLE CP-SAT result."
        )

    monkeypatch.setattr(
        "afterlife_ai.pipeline.optimizer.optimize_with_cp_sat",
        fake_cp_sat,
    )

    monkeypatch.setattr(
        (
            "afterlife_ai.pipeline.optimizer."
            "allocate_with_deterministic_fallback"
        ),
        forbidden_fallback,
    )

    result = optimize_production_candidates(
        candidates=valued,
        planning_lots=planning_lots,
        config=config,
    )

    assert (
        result.solver_status
        is SolverStatus.INFEASIBLE
    )

    assert result.allocations == []

    assert (
        result.unallocated_quantities
        == planning_quantities
    )

def test_production_optimizer_forwards_request_constraints_to_cp_sat(
    monkeypatch: MonkeyPatch,
) -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    captured_kwargs: dict[str, object] = {}

    def fake_cp_sat(**kwargs: object) -> OptimizationResult:
        captured_kwargs.update(kwargs)

        planning_quantities = {
            lot.planning_lot_id: lot.planning_quantity
            for lot in planning_lots
        }

        return OptimizationResult(
            solver_status=SolverStatus.OPTIMAL,
            objective_value=Decimal("0"),
            allocations=[],
            unallocated_quantities=planning_quantities,
        )

    monkeypatch.setattr(
        "afterlife_ai.pipeline.optimizer.optimize_with_cp_sat",
        fake_cp_sat,
    )

    result = optimize_production_candidates(
        candidates=valued,
        planning_lots=planning_lots,
        config=config,
        optimization_objective=(
            OptimizationObjective.BALANCED
        ),
        max_logistics_budget=Decimal("30000"),
        minimum_expected_rescue_ratio=Decimal("0.50"),
    )

    assert result.solver_status is SolverStatus.OPTIMAL

    assert (
        captured_kwargs["optimization_objective"]
        is OptimizationObjective.BALANCED
    )

    assert (
        captured_kwargs["max_logistics_budget"]
        == Decimal("30000")
    )

    assert (
        captured_kwargs[
            "minimum_expected_rescue_ratio"
        ]
        == Decimal("0.50")
    )

def test_production_optimizer_does_not_fallback_when_request_constraints_cannot_be_preserved(
    monkeypatch: MonkeyPatch,
) -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    valued = apply_production_expected_values(
        candidates=scored,
    )

    planning_quantities = {
        lot.planning_lot_id: lot.planning_quantity
        for lot in planning_lots
    }

    def fake_cp_sat(**_: object) -> OptimizationResult:
        return OptimizationResult(
            solver_status=SolverStatus.UNKNOWN,
            objective_value=Decimal("0"),
            allocations=[],
            unallocated_quantities=planning_quantities,
        )

    def forbidden_fallback(**_: object) -> object:
        raise AssertionError(
            "Fallback must not run when dynamic "
            "request constraints cannot be preserved."
        )

    monkeypatch.setattr(
        "afterlife_ai.pipeline.optimizer.optimize_with_cp_sat",
        fake_cp_sat,
    )

    monkeypatch.setattr(
        (
            "afterlife_ai.pipeline.optimizer."
            "allocate_with_deterministic_fallback"
        ),
        forbidden_fallback,
    )

    result = optimize_production_candidates(
        candidates=valued,
        planning_lots=planning_lots,
        config=config,
        optimization_objective=(
            OptimizationObjective.BALANCED
        ),
        max_logistics_budget=Decimal("30000"),
        minimum_expected_rescue_ratio=Decimal("0.50"),
    )

    assert (
        result.solver_status
        is SolverStatus.UNKNOWN
    )

    assert result.allocations == []

    assert (
        result.unallocated_quantities
        == planning_quantities
    )