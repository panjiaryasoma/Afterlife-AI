"""Tests for leakage-safe Logistic Regression training."""

from pathlib import Path

import pandas as pd
import pytest

from afterlife_ai.modeling.training import (
    build_logistic_pipeline,
    fit_logistic_regression,
    load_modeling_config,
    predict_logistic_probabilities,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

CONFIG_PATH = Path("configs/modeling_v1.yaml")
SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")


def _contract():
    return load_model_feature_contract(SCHEMA_PATH)


def _training_frame() -> pd.DataFrame:
    contract = _contract()

    rows: list[dict[str, object]] = []

    for index in range(20):
        row: dict[str, object] = {}

        for feature in contract.allowed_categorical_features:
            row[feature] = "TEST_CATEGORY"

        for feature in contract.allowed_numeric_features:
            row[feature] = float(index + 1)

        row["scenario_group_id"] = f"SG-{index:03d}"
        row["candidate_id"] = f"C-{index:03d}"
        row["action_type"] = "LOCAL_DISCOUNT"
        row["simulated_rescue_outcome"] = index % 2
        row["split"] = "train"

        rows.append(row)

    return pd.DataFrame(rows)


def test_modeling_config_keeps_test_locked() -> None:
    config = load_modeling_config(CONFIG_PATH)

    assert config.development_policy.fit_split == "train"
    assert config.development_policy.selection_split == "validation"
    assert config.development_policy.test_access_allowed is False


def test_logistic_pipeline_uses_exact_feature_contract() -> None:
    config = load_modeling_config(CONFIG_PATH)
    contract = _contract()

    pipeline = build_logistic_pipeline(
        contract=contract,
        config=config.logistic_regression,
    )

    preprocess = pipeline.named_steps["preprocess"]

    used: set[str] = set()

    for _, _, columns in preprocess.transformers:
        used.update(columns)

    assert used == set(contract.model_features)


def test_logistic_fit_rejects_non_train_rows() -> None:
    config = load_modeling_config(CONFIG_PATH)
    contract = _contract()
    frame = _training_frame()

    frame.loc[0, "split"] = "validation"

    with pytest.raises(
        ValueError,
        match="train split",
    ):
        fit_logistic_regression(
            frame,
            contract=contract,
            config=config.logistic_regression,
        )


def test_logistic_prediction_returns_probabilities() -> None:
    config = load_modeling_config(CONFIG_PATH)
    contract = _contract()
    train = _training_frame()

    model = fit_logistic_regression(
        train,
        contract=contract,
        config=config.logistic_regression,
    )

    scored = predict_logistic_probabilities(
        model,
        train,
        contract=contract,
    )

    assert len(scored) == len(train)
    assert scored["model_score"].between(0.0, 1.0).all()
    assert set(scored["model_id"]) == {
        "B2_LOGISTIC_REGRESSION"
    }
