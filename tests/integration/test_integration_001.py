from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import (
    ActionType,
    ApprovalStatus,
    InventoryStatus,
    ModelScoringStatus,
    SolverStatus,
)
from afterlife_ai.integration.pipeline import (
    run_integration_001,
)

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)


def run_case():
    return run_integration_001(
        fixture_dir=FIXTURE_DIR,
    )


def test_integration_001_reads_canonical_six_lot_workbook() -> None:
    result = run_case()

    assert len(result.raw_inventory_lots) == 6

    assert {
        lot.lot_id
        for lot in result.raw_inventory_lots
    } == {
        "LOT-001",
        "LOT-002",
        "LOT-003",
        "LOT-004",
        "LOT-005",
        "LOT-006",
    }

    assert sum(
        lot.current_quantity
        for lot in result.raw_inventory_lots
    ) == Decimal("102")


def test_integration_001_matches_locked_triage_partition() -> None:
    result = run_case()

    triage = {
        item.source_lot_id: item
        for item in result.triage_results
    }

    assert triage["LOT-001"].inventory_status is (
        InventoryStatus.HEALTHY_STOCK
    )
    assert (
        triage["LOT-001"].protected_normal_stock_quantity
        == Decimal("15")
    )

    assert triage["LOT-002"].inventory_status is (
        InventoryStatus.MONITOR
    )
    assert (
        triage["LOT-002"].monitor_quantity
        == Decimal("10")
    )

    assert triage["LOT-003"].inventory_status is (
        InventoryStatus.SURPLUS_CANDIDATE
    )
    assert (
        triage["LOT-003"].protected_normal_stock_quantity
        == Decimal("15")
    )
    assert (
        triage["LOT-003"].planning_quantity
        == Decimal("10")
    )

    assert triage["LOT-004"].inventory_status is (
        InventoryStatus.EXPIRED
    )
    assert (
        triage["LOT-004"].expired_quantity
        == Decimal("12")
    )

    assert triage["LOT-005"].inventory_status is (
        InventoryStatus.NEEDS_REVIEW
    )
    assert (
        triage["LOT-005"].review_quantity
        == Decimal("20")
    )

    assert triage["LOT-006"].inventory_status is (
        InventoryStatus.SURPLUS_CANDIDATE
    )
    assert (
        triage["LOT-006"].planning_quantity
        == Decimal("8")
    )
    assert (
        triage["LOT-006"].review_quantity
        == Decimal("12")
    )

    totals = {
        "protected": sum(
            item.protected_normal_stock_quantity
            for item in result.triage_results
        ),
        "monitor": sum(
            item.monitor_quantity
            for item in result.triage_results
        ),
        "planning": sum(
            item.planning_quantity
            for item in result.triage_results
        ),
        "expired": sum(
            item.expired_quantity
            for item in result.triage_results
        ),
        "review": sum(
            item.review_quantity
            for item in result.triage_results
        ),
    }

    assert totals == {
        "protected": Decimal("30"),
        "monitor": Decimal("10"),
        "planning": Decimal("18"),
        "expired": Decimal("12"),
        "review": Decimal("32"),
    }

    assert sum(
        totals.values(),
        Decimal("0"),
    ) == Decimal("102")


def test_integration_001_only_emits_two_planning_lots() -> None:
    result = run_case()

    planning = {
        lot.planning_lot_id: lot
        for lot in result.planning_lots
    }

    assert set(planning) == {
        "PLAN-LOT-003",
        "PLAN-LOT-006",
    }

    assert (
        planning["PLAN-LOT-003"].planning_quantity
        == Decimal("10")
    )
    assert (
        planning["PLAN-LOT-006"].planning_quantity
        == Decimal("8")
    )

    assert sum(
        lot.planning_quantity
        for lot in result.planning_lots
    ) == Decimal("18")


def test_integration_001_generates_only_locked_candidates() -> None:
    result = run_case()

    assert {
        candidate.candidate_id
        for candidate in result.candidates
    } == {
        "CAND-003-REPURPOSE",
        "CAND-003-BUNDLE",
        "CAND-003-DISCOUNT",
        "CAND-006-REPURPOSE",
        "CAND-006-DISCOUNT",
        "CAND-006-BONUS",
    }

    assert not any(
        candidate.action_type
        in {
            ActionType.EXTERNAL_PARTNER,
            ActionType.WHOLESALE,
            ActionType.BRANCH_TRANSFER,
            ActionType.RETURN_TO_SUPPLIER,
            ActionType.DONATION,
            ActionType.SAFE_DISPOSAL,
        }
        for candidate in result.candidates
    )


def test_integration_001_blocks_bonus_before_scoring() -> None:
    result = run_case()

    candidates = {
        candidate.candidate_id: candidate
        for candidate in result.scored_candidates
    }

    bonus = candidates["CAND-006-BONUS"]

    assert (
        bonus.model_scoring_status
        is ModelScoringStatus.BLOCKED
    )
    assert (
        "NO_QUALIFYING_TRANSACTION"
        in bonus.rejection_reason_codes
    )
    assert bonus.fixture_rescue_success_score is None

    expected_scores = {
        "CAND-003-REPURPOSE": Decimal("0.86"),
        "CAND-003-BUNDLE": Decimal("0.80"),
        "CAND-003-DISCOUNT": Decimal("0.74"),
        "CAND-006-REPURPOSE": Decimal("0.79"),
        "CAND-006-DISCOUNT": Decimal("0.76"),
    }

    assert {
        candidate_id:
        candidates[
            candidate_id
        ].fixture_rescue_success_score
        for candidate_id in expected_scores
    } == expected_scores


def test_integration_001_matches_global_allocation() -> None:
    result = run_case()

    optimization = result.optimization_result

    assert optimization.solver_status in {
        SolverStatus.OPTIMAL,
        SolverStatus.FEASIBLE,
    }

    allocations = {
        allocation.candidate_id:
        allocation.allocated_quantity
        for allocation in optimization.allocations
    }

    assert allocations == {
        "CAND-003-REPURPOSE": Decimal("6"),
        "CAND-003-BUNDLE": Decimal("4"),
        "CAND-006-DISCOUNT": Decimal("8"),
    }

    assert optimization.unallocated_quantities == {
        "PLAN-LOT-003": Decimal("0"),
        "PLAN-LOT-006": Decimal("0"),
    }

    assert (
        optimization.objective_value
        == Decimal("26624")
    )


def test_integration_001_builds_locked_rescue_decision_report() -> None:
    result = run_case()
    report = result.report

    assert report.batch_metrics.input_lots == 6
    assert (
        report.batch_metrics.input_quantity
        == Decimal("102")
    )
    assert (
        report.batch_metrics.planning_quantity
        == Decimal("18")
    )
    assert (
        report.batch_metrics.review_quantity
        == Decimal("32")
    )
    assert (
        report.batch_metrics.allocated_planning_quantity
        == Decimal("18")
    )
    assert (
        report.batch_metrics.unallocated_planning_quantity
        == Decimal("0")
    )
    assert (
        report.batch_metrics.expected_total_economic_value
        == Decimal("26624")
    )

    assert {
        item.candidate_id: item.allocated_quantity
        for item in report.selected_allocations
    } == {
        "CAND-003-REPURPOSE": Decimal("6"),
        "CAND-003-BUNDLE": Decimal("4"),
        "CAND-006-DISCOUNT": Decimal("8"),
    }

    assert {
        item.candidate_id:
        item.rejection_reason_codes
        for item in report.rejected_candidates
    } == {
        "CAND-006-BONUS": [
            "NO_QUALIFYING_TRANSACTION"
        ],
    }

    assert sum(
        item.review_quantity
        for item in report.review_required_lots
    ) == Decimal("32")

    assert (
        report.score_provenance.provider_name
        == "FixtureScoreProvider"
    )
    assert (
        report.score_provenance.score_type
        == "FIXTURE_EXPECTED_SCORE"
    )

    assert report.model_execution_performed is False
    assert (
        report.human_final_approval_status
        is ApprovalStatus.PENDING
    )
    assert report.execution_performed is False
