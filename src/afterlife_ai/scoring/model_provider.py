"""Production scoring provider for the selected rescue-success model."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from afterlife_ai.modeling.hist_gradient import TrainedHistGradientModel
from afterlife_ai.synthetic.schema_contract import (
    ModelFeatureContract,
    load_model_feature_contract,
)


@dataclass(frozen=True)
class ModelScoreProvider:
    """Production inference provider for the selected HGB-E model."""

    artifact_path: Path
    schema_path: Path
    model: TrainedHistGradientModel
    contract: ModelFeatureContract

    @classmethod
    def from_artifact(
        cls,
        *,
        artifact_path: Path,
        schema_path: Path = Path(
            "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
        ),
    ) -> ModelScoreProvider:
        """Load the frozen model artifact and its feature contract."""

        if not artifact_path.is_file():
            raise FileNotFoundError(
                f"Model artifact tidak ditemukan: {artifact_path}"
            )

        if not schema_path.is_file():
            raise FileNotFoundError(
                f"Feature schema tidak ditemukan: {schema_path}"
            )

        try:
            loaded_model = joblib.load(artifact_path)
        except Exception as exc:
            raise ValueError(
                f"Model artifact tidak valid: {artifact_path}"
            ) from exc

        if not isinstance(
            loaded_model,
            TrainedHistGradientModel,
        ):
            raise ValueError(
                "Model artifact tidak valid: "
                "expected TrainedHistGradientModel."
            )

        contract = load_model_feature_contract(
            schema_path,
        )

        return cls(
            artifact_path=artifact_path,
            schema_path=schema_path,
            model=loaded_model,
            contract=contract,
        )

    def score_features(
        self,
        features: Mapping[str, Any],
    ) -> Decimal:
        """Return rescue-success probability for one feature row."""

        expected_features = self.contract.model_features
        expected_set = set(expected_features)
        supplied_set = set(features)

        missing = expected_set - supplied_set

        if missing:
            raise ValueError(
                "Scoring features kurang: "
                f"{sorted(missing)}"
            )

        unexpected = supplied_set - expected_set

        if unexpected:
            raise ValueError(
                "Scoring features tidak dikenal: "
                f"{sorted(unexpected)}"
            )

        frame = pd.DataFrame(
            [
                {
                    feature_name: features[feature_name]
                    for feature_name in expected_features
                }
            ]
        )

        probabilities = (
            self.model.pipeline.predict_proba(
                frame
            )
        )

        probability = float(
            probabilities[0, 1]
        )

        if not 0.0 <= probability <= 1.0:
            raise RuntimeError(
                "Model menghasilkan probability "
                "di luar rentang 0 sampai 1."
            )

        return Decimal(str(probability))


__all__ = ["ModelScoreProvider"]