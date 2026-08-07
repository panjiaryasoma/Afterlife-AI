"""Tests for leakage-safe synthetic dataset rows."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from afterlife_ai.synthetic.rows import (
    SyntheticCandidateRow,
    SyntheticOracleRow,
)
from afterlife_ai.synthetic.schema_contract import (
    ModelFeatureContract,
    load_model_feature_contract,
)

SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")


def _contract() -> ModelFeatureContract:
    return load_model_feature_contract(SCHEMA_PATH)


def _valid_feature_values(
    contract: ModelFeatureContract,
) -> dict[str, str | int | float | None]:
    values: dict[str, str | int | float | None] = {}

    for field in contract.allowed_categorical_features:
        values[field] = "SYNTHETIC_TEST_VALUE"

    for field in contract.allowed_numeric_features:
        values[field] = 1.0

    return values


def _candidate(
    contract: ModelFeatureContract,
) -> SyntheticCandidateRow:
    return SyntheticCandidateRow(
        scenario_group_id="SCENARIO-GROUP-001",
        business_profile_id="BUSINESS-001",
        request_id="REQUEST-001",
        lot_id="LOT-001",
        candidate_id="CANDIDATE-001",
        simulated_rescue_outcome=1,
        feature_values=_valid_feature_values(contract),
    )


def test_candidate_row_exports_exact_model_feature_set() -> None:
    contract = _contract()
    candidate = _candidate(contract)

    record = candidate.to_training_record(contract)

    exported_model_features = {
        field
        for field in record
        if field in contract.model_features
    }

    assert exported_model_features == set(contract.model_features)
    assert len(exported_model_features) == 30

    assert record["simulated_rescue_outcome"] == 1
    assert "generator_success_probability" not in record
    assert "estimated_rescue_success_score" not in record


def test_missing_required_model_feature_is_rejected() -> None:
    contract = _contract()
    candidate = _candidate(contract)

    missing_field = contract.model_features[0]
    del candidate.feature_values[missing_field]

    with pytest.raises(
        ValueError,
        match="kehilangan required model features",
    ):
        candidate.to_training_record(contract)


def test_unexpected_or_forbidden_feature_is_rejected() -> None:
    contract = _contract()
    candidate = _candidate(contract)

    candidate.feature_values[
        "estimated_rescue_success_score"
    ] = 0.99

    with pytest.raises(
        ValueError,
        match="unexpected model features",
    ):
        candidate.to_training_record(contract)


def test_oracle_probability_is_exported_separately() -> None:
    oracle = SyntheticOracleRow(
        scenario_group_id="SCENARIO-GROUP-001",
        business_profile_id="BUSINESS-001",
        request_id="REQUEST-001",
        lot_id="LOT-001",
        candidate_id="CANDIDATE-001",
        generator_success_probability=0.73,
    )

    record = oracle.to_oracle_record()

    assert record["generator_success_probability"] == pytest.approx(0.73)
    assert "simulated_rescue_outcome" not in record
    assert "estimated_rescue_success_score" not in record


def test_oracle_probability_outside_unit_interval_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SyntheticOracleRow(
            scenario_group_id="SCENARIO-GROUP-001",
            business_profile_id="BUSINESS-001",
            request_id="REQUEST-001",
            lot_id="LOT-001",
            candidate_id="CANDIDATE-001",
            generator_success_probability=1.01,
        )


def test_target_must_be_binary() -> None:
    contract = _contract()

    with pytest.raises(ValidationError):
        SyntheticCandidateRow(
            scenario_group_id="SCENARIO-GROUP-001",
            business_profile_id="BUSINESS-001",
            request_id="REQUEST-001",
            lot_id="LOT-001",
            candidate_id="CANDIDATE-001",
            simulated_rescue_outcome=2,
            feature_values=_valid_feature_values(contract),
        )
