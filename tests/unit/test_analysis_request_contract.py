from decimal import Decimal

import pytest
from pydantic import ValidationError

from afterlife_ai.contracts import OptimizationObjective
from afterlife_ai.contracts.request import AnalysisRequest


def valid_request_payload() -> dict[str, object]:
    return {
        "inventory_file_name": "inventory.xlsx",
        "optimization_objective": (
            OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
        ),
        "objective_policy_version": "objective-policy-v1",
    }


def test_valid_analysis_request_is_accepted() -> None:
    request = AnalysisRequest.model_validate(valid_request_payload())

    assert request.inventory_file_name == "inventory.xlsx"
    assert request.random_seed == 42


def test_negative_logistics_budget_is_rejected() -> None:
    payload = valid_request_payload()
    payload["max_logistics_budget"] = Decimal("-1")

    with pytest.raises(ValidationError):
        AnalysisRequest.model_validate(payload)


def test_balanced_objective_requires_rescue_ratio() -> None:
    payload = valid_request_payload()
    payload["optimization_objective"] = OptimizationObjective.BALANCED

    with pytest.raises(ValidationError):
        AnalysisRequest.model_validate(payload)


def test_rescue_ratio_cannot_exceed_one() -> None:
    payload = valid_request_payload()
    payload["optimization_objective"] = OptimizationObjective.BALANCED
    payload["minimum_expected_rescue_ratio"] = Decimal("1.1")

    with pytest.raises(ValidationError):
        AnalysisRequest.model_validate(payload)


def test_invalid_request_id_is_rejected() -> None:
    payload = valid_request_payload()
    payload["request_id"] = "request id with spaces"

    with pytest.raises(ValidationError):
        AnalysisRequest.model_validate(payload)


def test_unknown_field_is_rejected() -> None:
    payload = valid_request_payload()
    payload["invented_field"] = "not allowed"

    with pytest.raises(ValidationError):
        AnalysisRequest.model_validate(payload)
