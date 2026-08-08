"""Tests for HistGradientBoosting candidate training."""

from pathlib import Path

import pandas as pd
import pytest

from afterlife_ai.modeling.hist_gradient import (
    build_hist_gradient_pipeline,
    fit_hist_gradient_boosting,
    load_hist_gradient_config,
    predict_hist_gradient_probabilities,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

CONFIG_PATH = Path("configs/modeling_v1.yaml")
SCHEMA_PATH = Path(
    "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
)


def _contract():
    return load_model_feature_contract(SCHEMA_PATH)


def _training_frame() -> pd.DataFrame:
    contract = _contract()

    rows: list[dict[str, object]] = []

    for index in range(80):
        row: dict[str, object] = {}

        for feature_number, feature in enumerate(
            contract.allowed_categorical_features
        ):
            row[feature] = (
                f"CATEGORY-{(index + feature_number) % 3}"
            )

        for feature_number, feature in enumerate(
            contract.allowed_numeric_features
        ):
            row[feature] = float(
                index + feature_number + 1
            )

        row["scenario_group_id"] = f"SG-{index:03d}"
        row["candidate_id"] = f"C-{index:03d}"
        row["action_type"] = "LOCAL_DISCOUNT"
        row["simulated_rescue_outcome"] = index % 2
        row["split"] = "train"

        rows.append(row)

    return pd.DataFrame(rows)


def test_hist_gradient_config_loads() -> None:
    config = load_hist_gradient_config(CONFIG_PATH)

    assert config.model_id == "M1_HIST_GRADIENT_BOOSTING"
    assert config.early_stopping is False
    assert config.random_state == 42


def test_hist_gradient_pipeline_uses_feature_contract() -> None:
    config = load_hist_gradient_config(CONFIG_PATH)
    contract = _contract()

    pipeline = build_hist_gradient_pipeline(
        contract=contract,
        config=config,
    )

    preprocess = pipeline.named_steps["preprocess"]

    used: set[str] = set()

    for _, _, columns in preprocess.transformers:
        used.update(columns)

    assert used == set(contract.model_features)


def test_hist_gradient_fit_rejects_non_train_rows() -> None:
    config = load_hist_gradient_config(CONFIG_PATH)
    contract = _contract()
    frame = _training_frame()

    frame.loc[0, "split"] = "validation"

    with pytest.raises(
        ValueError,
        match="train split",
    ):
        fit_hist_gradient_boosting(
            frame,
            contract=contract,
            config=config,
        )


def test_hist_gradient_predictions_are_probabilities() -> None:
    config = load_hist_gradient_config(CONFIG_PATH)
    contract = _contract()
    train = _training_frame()

    model = fit_hist_gradient_boosting(
        train,
        contract=contract,
        config=config,
    )

    scored = predict_hist_gradient_probabilities(
        model,
        train,
        contract=contract,
    )

    assert len(scored) == len(train)
    assert scored["model_score"].between(0.0, 1.0).all()

    assert set(scored["model_id"]) == {
        "M1_HIST_GRADIENT_BOOSTING"
    }
