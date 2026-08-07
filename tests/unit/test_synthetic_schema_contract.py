"""Tests for the schema-v2 model feature adapter."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from afterlife_ai.synthetic.schema_contract import (
    ModelFeatureContract,
    load_model_feature_contract,
)

SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")


def _load_raw_contract() -> dict[str, object]:
    payload = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)

    contract = payload["model_feature_contract"]
    assert isinstance(contract, dict)

    return contract


def test_locked_schema_model_feature_contract_loads() -> None:
    contract = load_model_feature_contract(SCHEMA_PATH)

    assert contract.canonical_target == "simulated_rescue_outcome"
    assert (
        contract.latent_generator_field
        == "generator_success_probability"
    )
    assert (
        contract.inference_output
        == "estimated_rescue_success_score"
    )

    assert len(contract.allowed_categorical_features) == 10
    assert len(contract.allowed_numeric_features) == 20
    assert len(contract.model_features) == 30

    assert contract.group_split_fields == [
        "scenario_group_id",
        "business_profile_id",
    ]

    assert "product_category" in contract.allowed_categorical_features
    assert "action_type" in contract.allowed_categorical_features
    assert "planning_quantity" in contract.allowed_numeric_features
    assert "distance_km" in contract.allowed_numeric_features


def test_schema_has_no_model_input_leakage() -> None:
    contract = load_model_feature_contract(SCHEMA_PATH)

    assert (
        set(contract.model_features)
        & set(contract.forbidden_model_inputs)
        == set()
    )

    assert contract.canonical_target in contract.forbidden_model_inputs
    assert (
        contract.latent_generator_field
        in contract.forbidden_model_inputs
    )

    for field in contract.group_split_fields:
        assert field in contract.forbidden_model_inputs


def test_forbidden_feature_overlap_is_rejected() -> None:
    payload = _load_raw_contract()

    categorical = list(payload["allowed_categorical_features"])
    categorical.append("simulated_rescue_outcome")
    payload["allowed_categorical_features"] = categorical

    with pytest.raises(
        ValidationError,
        match="forbidden inputs",
    ):
        ModelFeatureContract.model_validate(payload)


def test_duplicate_numeric_feature_is_rejected() -> None:
    payload = _load_raw_contract()

    numeric = list(payload["allowed_numeric_features"])
    numeric.append(numeric[0])
    payload["allowed_numeric_features"] = numeric

    with pytest.raises(
        ValidationError,
        match="numeric_features tidak boleh duplikat",
    ):
        ModelFeatureContract.model_validate(payload)
