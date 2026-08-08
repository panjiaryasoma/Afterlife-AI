"""Leakage-safe model training for Afterlife AI."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Self

import pandas as pd
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from afterlife_ai.synthetic.schema_contract import ModelFeatureContract


class DevelopmentPolicy(BaseModel):
    """Locked train/validation development policy."""

    model_config = ConfigDict(extra="forbid")

    fit_split: Literal["train"]
    selection_split: Literal["validation"]
    test_access_allowed: Literal[False]


class LogisticRegressionConfig(BaseModel):
    """Configuration for the linear ML baseline."""

    model_config = ConfigDict(extra="forbid")

    model_id: Literal["B2_LOGISTIC_REGRESSION"]
    solver: Literal["lbfgs"]
    l1_ratio: float = Field(ge=0.0, le=1.0)
    C: float = Field(gt=0.0)
    max_iter: int = Field(gt=0)
    class_weight: None = None
    random_state: int


class ModelingConfig(BaseModel):
    """Top-level model-development configuration."""

    model_config = ConfigDict(extra="forbid")

    config_version: Literal["1.0.0"]
    development_policy: DevelopmentPolicy
    logistic_regression: LogisticRegressionConfig

    @model_validator(mode="after")
    def validate_test_lock(self) -> Self:
        if self.development_policy.test_access_allowed:
            raise ValueError(
                "Test access tidak boleh aktif selama model development."
            )

        return self


@dataclass(frozen=True)
class TrainedLogisticModel:
    """Fitted LR pipeline and training metadata."""

    pipeline: Pipeline
    model_id: str
    training_rows: int


def load_modeling_config(path: Path) -> ModelingConfig:
    """Load model-development configuration."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Modeling config harus berupa YAML mapping.")

    return ModelingConfig.model_validate(payload)


def build_logistic_pipeline(
    *,
    contract: ModelFeatureContract,
    config: LogisticRegressionConfig,
) -> Pipeline:
    """Build train-fitted preprocessing plus Logistic Regression."""

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
            "Preprocessing feature sets tidak sama dengan model contract."
        )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
                categorical,
            ),
            (
                "numeric",
                StandardScaler(),
                numeric,
            ),
        ],
        remainder="drop",
    )

    classifier = LogisticRegression(
        solver=config.solver,
        l1_ratio=config.l1_ratio,
        C=config.C,
        max_iter=config.max_iter,
        class_weight=config.class_weight,
        random_state=config.random_state,
    )

    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("classifier", classifier),
        ]
    )


def fit_logistic_regression(
    train: pd.DataFrame,
    *,
    contract: ModelFeatureContract,
    config: LogisticRegressionConfig,
) -> TrainedLogisticModel:
    """Fit LR using train rows only."""

    if "split" in train.columns:
        observed_splits = set(train["split"].astype(str))

        if observed_splits != {"train"}:
            raise ValueError(
                "Logistic Regression hanya boleh di-fit pada train split."
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

    pipeline = build_logistic_pipeline(
        contract=contract,
        config=config,
    )

    pipeline.fit(
        train[contract.model_features],
        target,
    )

    return TrainedLogisticModel(
        pipeline=pipeline,
        model_id=config.model_id,
        training_rows=len(train),
    )


def predict_logistic_probabilities(
    model: TrainedLogisticModel,
    frame: pd.DataFrame,
    *,
    contract: ModelFeatureContract,
) -> pd.DataFrame:
    """Return candidate-level LR probabilities."""

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
    result["score_semantics"] = "ESTIMATED_SUCCESS_PROBABILITY"

    return result


__all__ = [
    "ModelingConfig",
    "TrainedLogisticModel",
    "build_logistic_pipeline",
    "fit_logistic_regression",
    "load_modeling_config",
    "predict_logistic_probabilities",
]
