"""Leakage-safe HistGradientBoosting training."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
import yaml
from pydantic import BaseModel, ConfigDict, Field
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from afterlife_ai.synthetic.schema_contract import ModelFeatureContract


class HistGradientBoostingConfig(BaseModel):
    """Configuration for the nonlinear candidate model."""

    model_config = ConfigDict(extra="forbid")

    model_id: Literal["M1_HIST_GRADIENT_BOOSTING"]
    learning_rate: float = Field(gt=0.0)
    max_iter: int = Field(gt=0)
    max_leaf_nodes: int = Field(gt=1)
    min_samples_leaf: int = Field(gt=0)
    l2_regularization: float = Field(ge=0.0)
    max_bins: int = Field(ge=2, le=255)
    early_stopping: Literal[False]
    random_state: int


@dataclass(frozen=True)
class TrainedHistGradientModel:
    """Fitted HGB pipeline and training metadata."""

    pipeline: Pipeline
    model_id: str
    training_rows: int


def load_hist_gradient_config(
    path: Path,
) -> HistGradientBoostingConfig:
    """Load HGB configuration from the shared modeling YAML."""

    payload = yaml.safe_load(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(payload, dict):
        raise ValueError("Modeling config harus berupa YAML mapping.")

    section = payload.get("hist_gradient_boosting")

    if not isinstance(section, dict):
        raise ValueError(
            "Section hist_gradient_boosting tidak ditemukan."
        )

    return HistGradientBoostingConfig.model_validate(section)


def build_hist_gradient_pipeline(
    *,
    contract: ModelFeatureContract,
    config: HistGradientBoostingConfig,
) -> Pipeline:
    """Build categorical encoding plus HistGradientBoosting."""

    categorical = list(
        contract.allowed_categorical_features
    )
    numeric = list(
        contract.allowed_numeric_features
    )

    if set(categorical) & set(numeric):
        raise ValueError(
            "Categorical dan numeric feature contract overlap."
        )

    if set(categorical) | set(numeric) != set(contract.model_features):
        raise ValueError(
            "HGB preprocessing tidak sama dengan model feature contract."
        )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    encoded_missing_value=-1,
                ),
                categorical,
            ),
            (
                "numeric",
                "passthrough",
                numeric,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    categorical_indices = list(
        range(len(categorical))
    )

    classifier = HistGradientBoostingClassifier(
        learning_rate=config.learning_rate,
        max_iter=config.max_iter,
        max_leaf_nodes=config.max_leaf_nodes,
        min_samples_leaf=config.min_samples_leaf,
        l2_regularization=config.l2_regularization,
        max_bins=config.max_bins,
        categorical_features=categorical_indices,
        early_stopping=config.early_stopping,
        random_state=config.random_state,
    )

    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("classifier", classifier),
        ]
    )


def fit_hist_gradient_boosting(
    train: pd.DataFrame,
    *,
    contract: ModelFeatureContract,
    config: HistGradientBoostingConfig,
) -> TrainedHistGradientModel:
    """Fit HGB using training rows only."""

    if "split" in train.columns:
        observed_splits = set(
            train["split"].astype(str)
        )

        if observed_splits != {"train"}:
            raise ValueError(
                "HistGradientBoosting hanya boleh di-fit "
                "pada train split."
            )

    required = set(contract.model_features) | {
        contract.canonical_target
    }

    missing = required - set(train.columns)

    if missing:
        raise ValueError(
            f"Training frame kehilangan columns: {sorted(missing)}"
        )

    target = train[contract.canonical_target]

    if set(int(value) for value in target.unique()) != {0, 1}:
        raise ValueError(
            "Training target harus mengandung kedua kelas 0 dan 1."
        )

    pipeline = build_hist_gradient_pipeline(
        contract=contract,
        config=config,
    )

    pipeline.fit(
        train[contract.model_features],
        target,
    )

    return TrainedHistGradientModel(
        pipeline=pipeline,
        model_id=config.model_id,
        training_rows=len(train),
    )


def predict_hist_gradient_probabilities(
    model: TrainedHistGradientModel,
    frame: pd.DataFrame,
    *,
    contract: ModelFeatureContract,
) -> pd.DataFrame:
    """Return candidate-level HGB success probabilities."""

    missing = set(contract.model_features) - set(frame.columns)

    if missing:
        raise ValueError(
            f"Scoring frame kehilangan features: {sorted(missing)}"
        )

    probabilities = model.pipeline.predict_proba(
        frame[contract.model_features]
    )[:, 1]

    result = frame[
        [
            "scenario_group_id",
            "candidate_id",
            "action_type",
            contract.canonical_target,
        ]
    ].copy()

    result["model_id"] = model.model_id
    result["model_score"] = probabilities
    result["score_semantics"] = (
        "ESTIMATED_SUCCESS_PROBABILITY"
    )

    return result


__all__ = [
    "HistGradientBoostingConfig",
    "TrainedHistGradientModel",
    "build_hist_gradient_pipeline",
    "fit_hist_gradient_boosting",
    "load_hist_gradient_config",
    "predict_hist_gradient_probabilities",
]
