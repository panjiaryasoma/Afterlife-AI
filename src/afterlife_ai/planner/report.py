"""Canonical Rescue Decision Report contracts and builder."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from afterlife_ai.contracts.enums import (
    ActionType,
    ApprovalStatus,
    OptimizationObjective,
    SolverStatus,
    SourceType,
    ValidationStatus,
)

ZERO = Decimal("0")

class ReportValidationSummary(BaseModel):
    """Summary of successful intake and canonical validation."""

    model_config = ConfigDict(extra="forbid")

    status: ValidationStatus
    input_lots: int = Field(ge=0)
    canonical_records: int = Field(ge=0)


class ReportTriageSummary(BaseModel):
    """Quantity summary produced by deterministic inventory triage."""

    model_config = ConfigDict(extra="forbid")

    protected_quantity: Decimal = Field(ge=ZERO)
    monitor_quantity: Decimal = Field(ge=ZERO)
    planning_quantity: Decimal = Field(ge=ZERO)
    expired_quantity: Decimal = Field(ge=ZERO)
    review_quantity: Decimal = Field(ge=ZERO)

class ReportScoreProvenance(BaseModel):
    """Traceable provenance for the score source used in a report."""

    model_config = ConfigDict(extra="forbid")

    provider_name: str
    score_type: str
    source_type: SourceType
    fixture_version: str | None = None

    @model_validator(mode="after")
    def validate_fixture_metadata(self) -> Self:
        if (
            self.source_type is SourceType.EVALUATION_FIXTURE
            and not self.fixture_version
        ):
            raise ValueError(
                "fixture_version wajib untuk evaluation fixture."
            )

        return self


class ReportAllocation(BaseModel):
    """User-visible selected rescue allocation."""

    model_config = ConfigDict(extra="forbid")

    allocation_id: str
    candidate_id: str
    planning_lot_id: str
    source_lot_id: str
    action_type: ActionType

    destination_id: str | None = None
    destination_type: str | None = None

    allocated_quantity: Decimal = Field(gt=ZERO)

    offered_or_selling_price_per_unit: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )
    estimated_rescue_success_score: Decimal | None = Field(
        default=None,
        ge=ZERO,
        le=Decimal("1"),
    )

    direct_action_cost: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )
    logistics_cost: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )
    handling_cost: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )

    estimated_completion_hours: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )
    distance_km: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )

    expected_value_per_unit: Decimal = ZERO
    binding_constraint_codes: list[str] = Field(
        default_factory=list
    )

    expected_cash_recovery: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )
    expected_future_branch_recovery: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )
    expected_avoided_purchase_cost: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )
    expected_physical_rescue_quantity: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )
    expected_waste_quantity: Decimal = Field(
        default=ZERO,
        ge=ZERO,
    )

    expected_net_recovery: Decimal


class RejectedCandidateReportItem(BaseModel):
    """Candidate rejected before final allocation."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    planning_lot_id: str
    action_type: ActionType
    rejection_reason_codes: list[str]


class ReviewRequiredLotReportItem(BaseModel):
    """Quantity held outside rescue planning for human review."""

    model_config = ConfigDict(extra="forbid")

    source_lot_id: str
    review_quantity: Decimal = Field(gt=ZERO)
    reason_codes: list[str]


class FallbackChainReportItem(BaseModel):
    """Traceable fallback step recorded for a rescue plan."""

    model_config = ConfigDict(extra="allow")

    step: str | None = None
    reason: str | None = None


class ReportBatchMetrics(BaseModel):
    """Batch-level quantity and economic reconciliation."""

    model_config = ConfigDict(extra="forbid")

    input_lots: int = Field(ge=0)
    input_quantity: Decimal = Field(ge=ZERO)

    protected_quantity: Decimal = Field(ge=ZERO)
    monitor_quantity: Decimal = Field(ge=ZERO)
    planning_quantity: Decimal = Field(ge=ZERO)
    expired_quantity: Decimal = Field(ge=ZERO)
    review_quantity: Decimal = Field(ge=ZERO)

    allocated_planning_quantity: Decimal = Field(ge=ZERO)
    unallocated_planning_quantity: Decimal = Field(ge=ZERO)

    expected_total_economic_value: Decimal

    expected_physical_rescue_quantity: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )
    expected_waste_quantity: Decimal | None = Field(
        default=None,
        ge=ZERO,
    )
    expected_rescue_ratio: Decimal | None = Field(
        default=None,
        ge=ZERO,
        le=Decimal("1"),
    )


class RescueDecisionReport(BaseModel):
    """Single advisory user-visible rescue decision report."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    analysis_timestamp: datetime

    feature_schema_version: str
    input_snapshot_sha256: str = Field(
        pattern=r"^[0-9a-fA-F]{64}$"
    )
    model_version: str
    model_sha256: str = Field(
        pattern=r"^[0-9a-fA-F]{64}$"
    )
    ruleset_version: str
    capability_snapshot_version: str

    partner_registry_snapshot_id: str | None = None
    partner_registry_snapshot_timestamp: datetime | None = None
    partner_registry_source_type: str | None = None
    partner_registry_real_world_verified: bool | None = None

    objective_policy_version: str
    optimization_objective: OptimizationObjective
    optimization_solver_status: SolverStatus

    validation_summary: ReportValidationSummary
    triage_summary: ReportTriageSummary

    score_provenance: ReportScoreProvenance
    model_execution_performed: bool

    deterministic_execution: bool | None = None
    optimizer_random_seed: int | None = None
    optimizer_num_search_workers: int | None = Field(
        default=None,
        ge=1,
    )

    batch_metrics: ReportBatchMetrics

    review_required_lots: list[
        ReviewRequiredLotReportItem
    ]
    selected_allocations: list[ReportAllocation]
    rejected_candidates: list[
        RejectedCandidateReportItem
    ]

    fallback_chain: list[FallbackChainReportItem]
    limitations: list[str]

    human_exception_review_required: bool
    human_final_approval_status: ApprovalStatus

    execution_performed: bool

    @model_validator(mode="after")
    def validate_report_contract(self) -> Self:
        """Enforce reconciliation and report claim boundaries."""

        metrics = self.batch_metrics

        if (
            metrics.allocated_planning_quantity
            + metrics.unallocated_planning_quantity
            != metrics.planning_quantity
        ):
            raise ValueError(
                "quantity reconciliation failed: "
                "allocated planning quantity + unallocated "
                "planning quantity must equal planning quantity."
            )

        allocation_total = sum(
            (
                item.allocated_quantity
                for item in self.selected_allocations
            ),
            ZERO,
        )

        if (
            allocation_total
            != metrics.allocated_planning_quantity
        ):
            raise ValueError(
                "quantity reconciliation failed: "
                "selected allocation total must equal "
                "allocated planning quantity."
            )

        review_total = sum(
            (
                item.review_quantity
                for item in self.review_required_lots
            ),
            ZERO,
        )

        if review_total != metrics.review_quantity:
            raise ValueError(
                "quantity reconciliation failed: "
                "review-required quantity must equal "
                "reported review quantity."
            )

        routed_total = (
            metrics.protected_quantity
            + metrics.monitor_quantity
            + metrics.planning_quantity
            + metrics.expired_quantity
            + metrics.review_quantity
        )

        if routed_total != metrics.input_quantity:
            raise ValueError(
                "quantity reconciliation failed: "
                "protected + monitor + planning + expired "
                "+ review must equal input quantity."
            )

        if (
            self.score_provenance.source_type
            is SourceType.EVALUATION_FIXTURE
            and self.model_execution_performed
        ):
            raise ValueError(
                "fixture provenance cannot claim that "
                "a trained model was executed."
            )

        if self.execution_performed:
            raise ValueError(
                "Rescue Decision Report is advisory; "
                "execution_performed must remain false."
            )

        return self


def build_rescue_decision_report(
    *,
    request_id: str,
    feature_schema_version: str,
    input_snapshot_sha256: str,
    model_version: str,
    model_sha256: str,
    ruleset_version: str,
    capability_snapshot_version: str,
    partner_registry_snapshot_id: str | None = None,
    partner_registry_snapshot_timestamp: datetime | None = None,
    partner_registry_source_type: str | None = None,
    partner_registry_real_world_verified: bool | None = None,
    objective_policy_version: str,
    optimization_objective: OptimizationObjective,
    optimization_solver_status: SolverStatus,
    validation_summary: dict[str, Any],
    triage_summary: dict[str, Any],
    score_provenance: dict[str, Any],
    model_execution_performed: bool,
    deterministic_execution: bool | None = None,
    optimizer_random_seed: int | None = None,
    optimizer_num_search_workers: int | None = None,
    analysis_timestamp: datetime,
    batch_metrics: dict[str, Any],
    selected_allocations: list[dict[str, Any]],
    rejected_candidates: list[dict[str, Any]],
    review_required_lots: list[dict[str, Any]],
    fallback_chain: list[dict[str, Any]],
    limitations: list[str],
    human_exception_review_required: bool,
    human_final_approval_status: ApprovalStatus,
    execution_performed: bool,
) -> RescueDecisionReport:
    """Build the canonical advisory Rescue Decision Report."""

    return RescueDecisionReport(
        request_id=request_id,
        analysis_timestamp=analysis_timestamp,
        feature_schema_version=feature_schema_version,
        input_snapshot_sha256=input_snapshot_sha256,
        model_version=model_version,
        model_sha256=model_sha256,
        ruleset_version=ruleset_version,
        capability_snapshot_version=(
            capability_snapshot_version
        ),
        partner_registry_snapshot_id=(
            partner_registry_snapshot_id
        ),
        partner_registry_snapshot_timestamp=(
            partner_registry_snapshot_timestamp
        ),
        partner_registry_source_type=(
            partner_registry_source_type
        ),
        partner_registry_real_world_verified=(
            partner_registry_real_world_verified
        ),
        objective_policy_version=objective_policy_version,
        optimization_objective=optimization_objective,
        optimization_solver_status=(
            optimization_solver_status
        ),
        validation_summary=ReportValidationSummary(
            **validation_summary
        ),
        triage_summary=ReportTriageSummary(
            **triage_summary
        ),
        score_provenance=ReportScoreProvenance(
            **score_provenance
        ),
        model_execution_performed=model_execution_performed,
        deterministic_execution=deterministic_execution,
        optimizer_random_seed=optimizer_random_seed,
        optimizer_num_search_workers=(
            optimizer_num_search_workers
        ),
        batch_metrics=ReportBatchMetrics(
            **batch_metrics
        ),
        selected_allocations=[
            ReportAllocation(**item)
            for item in selected_allocations
        ],
        rejected_candidates=[
            RejectedCandidateReportItem(**item)
            for item in rejected_candidates
        ],
        review_required_lots=[
            ReviewRequiredLotReportItem(**item)
            for item in review_required_lots
        ],
        fallback_chain=[
            FallbackChainReportItem(**item)
            for item in fallback_chain
        ],
        limitations=limitations,
        human_exception_review_required=(
            human_exception_review_required
        ),
        human_final_approval_status=(
            human_final_approval_status
        ),
        execution_performed=execution_performed,
    )


__all__ = [
    "ReportScoreProvenance",
    "ReportAllocation",
    "RejectedCandidateReportItem",
    "ReviewRequiredLotReportItem",
    "FallbackChainReportItem",
    "ReportBatchMetrics",
    "RescueDecisionReport",
    "build_rescue_decision_report",
    "ReportValidationSummary",
    "ReportTriageSummary",
]
