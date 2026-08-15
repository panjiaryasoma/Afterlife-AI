from datetime import UTC, datetime
from decimal import Decimal

import pytest

from afterlife_ai.contracts.enums import (
    ActionType,
    ApprovalStatus,
    OptimizationObjective,
    SolverStatus,
)
from afterlife_ai.planner.report import (
    build_rescue_decision_report,
)

MODEL_VERSION = "HGB_E_v1"
MODEL_SHA256 = (
    "a318a2550d97ea0861b85fd7af5f9b2"
    "be0291eb29f57b07a00b32ab5ea5295d9"
)

def build_report():
    return build_rescue_decision_report(
        request_id="REQ-INTEGRATION-001",
        feature_schema_version="2.0.0",
        input_snapshot_sha256=(
            "0123456789abcdef"
            "0123456789abcdef"
            "0123456789abcdef"
            "0123456789abcdef"
        ),
        model_version=MODEL_VERSION,
        model_sha256=MODEL_SHA256,
        ruleset_version="domain_rules_v1.0",
        capability_snapshot_version="INTEGRATION-001-fixture-v1",
        objective_policy_version="BALANCED_FIXTURE_v1",
        optimization_objective=OptimizationObjective.BALANCED,
        optimization_solver_status=SolverStatus.OPTIMAL,
        score_provenance={
            "provider_name": "FixtureScoreProvider",
            "score_type": "FIXTURE_EXPECTED_SCORE",
            "source_type": "EVALUATION_FIXTURE",
            "fixture_version": "INTEGRATION-001-v1",
        },
        model_execution_performed=False,
        analysis_timestamp=datetime(
            2026,
            8,
            7,
            9,
            0,
            tzinfo=UTC,
        ),
        batch_metrics={
            "input_lots": 6,
            "input_quantity": Decimal("102"),
            "protected_quantity": Decimal("30"),
            "monitor_quantity": Decimal("10"),
            "planning_quantity": Decimal("18"),
            "expired_quantity": Decimal("12"),
            "review_quantity": Decimal("32"),
            "allocated_planning_quantity": Decimal("18"),
            "unallocated_planning_quantity": Decimal("0"),
            "expected_total_economic_value": Decimal("26624"),
        },
        selected_allocations=[
            {
                "allocation_id": "ALLOC-003-REPURPOSE",
                "candidate_id": "CAND-003-REPURPOSE",
                "planning_lot_id": "PLAN-LOT-003",
                "source_lot_id": "LOT-003",
                "action_type": ActionType.INTERNAL_REPURPOSE,
                "allocated_quantity": Decimal("6"),
                "expected_net_recovery": Decimal("12384"),
            },
            {
                "allocation_id": "ALLOC-003-BUNDLE",
                "candidate_id": "CAND-003-BUNDLE",
                "planning_lot_id": "PLAN-LOT-003",
                "source_lot_id": "LOT-003",
                "action_type": ActionType.BUNDLE,
                "allocated_quantity": Decimal("4"),
                "expected_net_recovery": Decimal("5120"),
            },
            {
                "allocation_id": "ALLOC-006-DISCOUNT",
                "candidate_id": "CAND-006-DISCOUNT",
                "planning_lot_id": "PLAN-LOT-006",
                "source_lot_id": "LOT-006",
                "action_type": ActionType.LOCAL_DISCOUNT,
                "allocated_quantity": Decimal("8"),
                "expected_net_recovery": Decimal("9120"),
            },
        ],
        rejected_candidates=[
            {
                "candidate_id": "CAND-006-BONUS",
                "planning_lot_id": "PLAN-LOT-006",
                "action_type": ActionType.PROMOTIONAL_BONUS,
                "rejection_reason_codes": [
                    "NO_QUALIFYING_TRANSACTION"
                ],
            }
        ],
        review_required_lots=[
            {
                "source_lot_id": "LOT-005",
                "review_quantity": Decimal("20"),
                "reason_codes": [
                    "COLD_CHAIN_EVIDENCE_REVIEW"
                ],
            },
            {
                "source_lot_id": "LOT-006",
                "review_quantity": Decimal("12"),
                "reason_codes": [
                    "DEMAND_EVIDENCE_REVIEW"
                ],
            },
        ],
        fallback_chain=[],
        limitations=[
            (
                "Fixture scores are synthetic evaluation "
                "parameters and are not validated real-world "
                "probabilities."
            ),
            (
                "No automatic logistics or transaction execution "
                "is performed."
            ),
        ],
        human_exception_review_required=True,
        human_final_approval_status=ApprovalStatus.PENDING,
        execution_performed=False,
    )


def test_report_contains_canonical_sections() -> None:
    report = build_report()

    assert report.request_id == "REQ-INTEGRATION-001"
    assert len(report.selected_allocations) == 3
    assert len(report.rejected_candidates) == 1
    assert len(report.review_required_lots) == 2
    assert report.fallback_chain == []
    assert len(report.limitations) == 2


def test_report_matches_expected_fixture_allocations() -> None:
    report = build_report()

    allocations = {
        item.candidate_id: item.allocated_quantity
        for item in report.selected_allocations
    }

    assert allocations == {
        "CAND-003-REPURPOSE": Decimal("6"),
        "CAND-003-BUNDLE": Decimal("4"),
        "CAND-006-DISCOUNT": Decimal("8"),
    }


def test_report_preserves_rejected_candidate_reason() -> None:
    report = build_report()

    rejected = report.rejected_candidates[0]

    assert rejected.candidate_id == "CAND-006-BONUS"
    assert rejected.rejection_reason_codes == [
        "NO_QUALIFYING_TRANSACTION"
    ]


def test_report_preserves_review_quantities() -> None:
    report = build_report()

    review_total = sum(
        item.review_quantity
        for item in report.review_required_lots
    )

    assert review_total == Decimal("32")


def test_report_batch_metrics_match_integration_fixture() -> None:
    report = build_report()

    assert report.batch_metrics.input_lots == 6
    assert report.batch_metrics.input_quantity == Decimal("102")
    assert report.batch_metrics.planning_quantity == Decimal("18")
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


def test_report_requires_human_approval_and_never_executes() -> None:
    report = build_report()

    assert report.human_exception_review_required is True
    assert (
        report.human_final_approval_status
        is ApprovalStatus.PENDING
    )
    assert report.execution_performed is False


def test_report_serialization_is_deterministic() -> None:
    first = build_report().model_dump_json()
    second = build_report().model_dump_json()

    assert first == second


def test_report_rejects_broken_quantity_reconciliation() -> None:
    with pytest.raises(
        ValueError,
        match="quantity reconciliation",
    ):
        build_rescue_decision_report(
            request_id="REQ-BROKEN",
            feature_schema_version="2.0.0",
            input_snapshot_sha256=(
                "0123456789abcdef"
                "0123456789abcdef"
                "0123456789abcdef"
                "0123456789abcdef"
            ),
            model_version=MODEL_VERSION,
            model_sha256=MODEL_SHA256,
            ruleset_version="domain_rules_v1.0",
            capability_snapshot_version="INTEGRATION-001-fixture-v1",
            objective_policy_version="BALANCED_FIXTURE_v1",
            optimization_objective=OptimizationObjective.BALANCED,
            optimization_solver_status=SolverStatus.OPTIMAL,
            score_provenance={
                "provider_name": "FixtureScoreProvider",
                "score_type": "FIXTURE_EXPECTED_SCORE",
                "source_type": "EVALUATION_FIXTURE",
                "fixture_version": "INTEGRATION-001-v1",
            },
            model_execution_performed=False,
            analysis_timestamp=datetime(
                2026,
                8,
                7,
                9,
                0,
                tzinfo=UTC,
            ),
            batch_metrics={
                "input_lots": 1,
                "input_quantity": Decimal("10"),
                "protected_quantity": Decimal("0"),
                "monitor_quantity": Decimal("0"),
                "planning_quantity": Decimal("10"),
                "expired_quantity": Decimal("0"),
                "review_quantity": Decimal("0"),
                "allocated_planning_quantity": Decimal("8"),
                "unallocated_planning_quantity": Decimal("1"),
                "expected_total_economic_value": Decimal("1000"),
            },
            selected_allocations=[],
            rejected_candidates=[],
            review_required_lots=[],
            fallback_chain=[],
            limitations=[],
            human_exception_review_required=False,
            human_final_approval_status=ApprovalStatus.PENDING,
            execution_performed=False,
        )



def test_report_contains_fixture_score_provenance() -> None:
    report = build_report()

    assert (
        report.score_provenance.provider_name
        == "FixtureScoreProvider"
    )
    assert (
        report.score_provenance.score_type
        == "FIXTURE_EXPECTED_SCORE"
    )
    assert (
        report.score_provenance.source_type
        == "EVALUATION_FIXTURE"
    )
    assert (
        report.score_provenance.fixture_version
        == "INTEGRATION-001-v1"
    )


def test_report_contains_contract_versions() -> None:
    report = build_report()

    assert report.feature_schema_version == "2.0.0"
    assert report.ruleset_version == "domain_rules_v1.0"
    assert (
        report.capability_snapshot_version
        == "INTEGRATION-001-fixture-v1"
    )
    assert (
        report.objective_policy_version
        == "BALANCED_FIXTURE_v1"
    )
    assert (
        report.optimization_objective
        is OptimizationObjective.BALANCED
    )

    assert (
        report.optimization_solver_status
        is SolverStatus.OPTIMAL
    )


def test_report_marks_that_no_trained_model_was_executed() -> None:
    report = build_report()

    assert report.model_execution_performed is False


def test_report_requires_valid_sha256_snapshot_hash() -> None:
    with pytest.raises(
        ValueError,
        match="input_snapshot_sha256",
    ):
        build_rescue_decision_report(
            request_id="REQ-BAD-HASH",
            feature_schema_version="2.0.0",
            input_snapshot_sha256="not-a-sha256",
            model_version=MODEL_VERSION,
            model_sha256=MODEL_SHA256,
            ruleset_version="domain_rules_v1.0",
            capability_snapshot_version="fixture-v1",
            objective_policy_version="BALANCED_FIXTURE_v1",
            optimization_objective=OptimizationObjective.BALANCED,
            optimization_solver_status=SolverStatus.OPTIMAL,
            score_provenance={
                "provider_name": "FixtureScoreProvider",
                "score_type": "FIXTURE_EXPECTED_SCORE",
                "source_type": "EVALUATION_FIXTURE",
                "fixture_version": "INTEGRATION-001-v1",
            },
            model_execution_performed=False,
            analysis_timestamp=datetime(
                2026,
                8,
                7,
                9,
                0,
                tzinfo=UTC,
            ),
            batch_metrics={
                "input_lots": 0,
                "input_quantity": Decimal("0"),
                "protected_quantity": Decimal("0"),
                "monitor_quantity": Decimal("0"),
                "planning_quantity": Decimal("0"),
                "expired_quantity": Decimal("0"),
                "review_quantity": Decimal("0"),
                "allocated_planning_quantity": Decimal("0"),
                "unallocated_planning_quantity": Decimal("0"),
                "expected_total_economic_value": Decimal("0"),
            },
            selected_allocations=[],
            rejected_candidates=[],
            review_required_lots=[],
            fallback_chain=[],
            limitations=[],
            human_exception_review_required=False,
            human_final_approval_status=ApprovalStatus.PENDING,
            execution_performed=False,
        )


def test_fixture_provenance_cannot_claim_trained_model() -> None:
    with pytest.raises(
        ValueError,
        match="fixture provenance",
    ):
        report = build_report().model_copy(
            update={"model_execution_performed": True}
        )

        report.__class__.model_validate(
            report.model_dump()
        )

def test_report_contains_model_artifact_provenance() -> None:
    report = build_report()

    assert report.model_version == MODEL_VERSION
    assert report.model_sha256 == MODEL_SHA256