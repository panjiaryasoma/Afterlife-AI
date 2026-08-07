from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AssertionType = Literal[
    "CASE_ID_MATCHES_FILE",
    "HAS_RULE_TRACEABILITY",
    "EXPECTED_ALLOCATION",
    "NO_AUTOMATIC_ALLOCATION",
    "NO_HUMAN_CONSUMPTION_ALLOCATION",
    "STATUS_EQUALS",
    "HUMAN_REVIEW_REQUIRED",
    "EXPECTED_METRIC",
    "OBJECTIVE_RUN_PRESENT",
    "OBJECTIVE_ACTION_QUANTITY",
    "QUANTITY_CONSERVATION",
    "BATCH_QUANTITY_CONSERVATION",
    "BATCH_ROUTING_CONSERVATION",
]


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class PlannerLotFixture(StrictContractModel):
    lot_id: str
    source_lot_id: str | None = None
    quantity: int | float | str | None = None
    unit: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class PartnerFixture(StrictContractModel):
    partner_id: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    description: str | None = None


class PlannerFixtures(StrictContractModel):
    lots: list[PlannerLotFixture]
    batch_context: dict[str, Any] = Field(default_factory=dict)
    capability_facts: dict[str, Any] = Field(default_factory=dict)
    capability_notes: list[str] = Field(default_factory=list)
    partners: list[PartnerFixture] = Field(default_factory=list)
    context_notes: list[str] = Field(default_factory=list)


class ExpectedRoute(StrictContractModel):
    statuses: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class ExpectedAllocation(StrictContractModel):
    lot_id: str | None = None
    source_lot_ids: list[str] = Field(default_factory=list)
    action: str
    quantity: int | float | None = None
    destination: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class PlannerExpectedResult(StrictContractModel):
    route: ExpectedRoute
    allocations: list[ExpectedAllocation] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    objective_runs: dict[str, Any] = Field(default_factory=dict)
    required_fields: list[str] = Field(default_factory=list)
    rejected_alternative: Any = None
    rejected_partner: Any = None
    possible_outcomes: list[str] = Field(default_factory=list)
    feasible_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    acceptable_decision: str | None = None
    binding_constraints: list[str] = Field(default_factory=list)
    explanation: str | None = None
    failure_conditions: list[str] = Field(default_factory=list)


class PlannerTraceability(StrictContractModel):
    rule_ids: list[str]
    feature_terms: list[str] = Field(default_factory=list)
    source_markdown: str | None = None
    source_references: list[str] = Field(default_factory=list)
    source_type: str | None = None
    synthetic_status: str | None = None
    uncertainty_and_source_boundary: str | None = None


class ContractAssertion(StrictContractModel):
    type: AssertionType
    params: dict[str, Any] = Field(default_factory=dict)


class PlannerEvaluationCase(StrictContractModel):
    contract_version: str
    case_id: str = Field(pattern=r"^EVAL-\d{3}$")
    title: str
    case_type: str
    evaluation_layer: Literal["CORE_RESCUE_PLANNER"]
    input_entity: Literal["SURPLUS_PLANNING_LOT"]
    purpose: str
    optimization_objective: str
    fixtures: PlannerFixtures
    expected: PlannerExpectedResult
    traceability: PlannerTraceability
    assertions: list[ContractAssertion]

    @model_validator(mode="after")
    def validate_case_contract(self) -> PlannerEvaluationCase:
        if not self.fixtures.lots:
            raise ValueError("at least one lot fixture is required")
        if not self.traceability.rule_ids:
            raise ValueError("at least one rule_id is required")
        if not self.assertions:
            raise ValueError("at least one executable assertion is required")
        return self


class PlannerObservation(StrictContractModel):
    """Normalized planner output consumed by the assertion engine.

    The model-stub pipeline will produce this shape in the next milestone. For now,
    contracts can compile their expected result into an observation to prove every
    assertion is executable and internally consistent.
    """

    case_id: str
    statuses: dict[str, Any] = Field(default_factory=dict)
    allocations: list[ExpectedAllocation] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    objective_runs: dict[str, Any] = Field(default_factory=dict)
    human_review_required: bool = False
    rule_ids: list[str] = Field(default_factory=list)

    @classmethod
    def from_expected(cls, case: PlannerEvaluationCase) -> PlannerObservation:
        human_review = bool(case.expected.metrics.get("human_review_required", False))
        if case.expected.route.statuses.get("decision_status") == "NEEDS_REVIEW":
            human_review = True
        return cls(
            case_id=case.case_id,
            statuses=dict(case.expected.route.statuses),
            allocations=list(case.expected.allocations),
            metrics=dict(case.expected.metrics),
            objective_runs=dict(case.expected.objective_runs),
            human_review_required=human_review,
            rule_ids=list(case.traceability.rule_ids),
        )
