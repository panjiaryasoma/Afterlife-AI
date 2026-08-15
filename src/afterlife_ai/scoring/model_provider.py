"""Production scoring provider for the selected rescue-success model."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from afterlife_ai.modeling.hist_gradient import TrainedHistGradientModel
from afterlife_ai.synthetic.schema_contract import (
    ModelFeatureContract,
    load_model_feature_contract,
)


class ModelIntegrityError(RuntimeError):
    """Raised when runtime model identity differs from the frozen manifest."""


def _sha256_file(path: Path) -> str:
    digest = sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()

def _sha256_canonical_text_file(path: Path) -> str:
    data = path.read_bytes().replace(
        b"\r\n",
        b"\n",
    )

    return sha256(data).hexdigest()

def _require_sha256(
    value: Any,
    *,
    field_name: str,
) -> str:
    text = str(value).lower()

    if len(text) != 64:
        raise ModelIntegrityError(
            f"{field_name} bukan SHA-256 yang valid."
        )

    try:
        int(text, 16)
    except ValueError as exc:
        raise ModelIntegrityError(
            f"{field_name} bukan SHA-256 yang valid."
        ) from exc

    return text

def load_frozen_model_identity(
    manifest_path: Path,
) -> tuple[str, str]:
    """Read frozen model version and artifact SHA-256."""

    if not manifest_path.is_file():
        raise ModelIntegrityError(
            f"Model manifest tidak ditemukan: {manifest_path}"
        )

    try:
        payload = json.loads(
            manifest_path.read_text(
                encoding="utf-8",
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelIntegrityError(
            f"Model manifest tidak valid: {manifest_path}"
        ) from exc

    if not isinstance(payload, dict):
        raise ModelIntegrityError(
            "Model manifest harus berupa JSON object."
        )

    artifact = payload.get("artifact")

    if not isinstance(artifact, dict):
        raise ModelIntegrityError(
            "Model manifest tidak memiliki artifact contract."
        )

    artifact_path = artifact.get("path")

    if (
        not isinstance(artifact_path, str)
        or not artifact_path.strip()
    ):
        raise ModelIntegrityError(
            "Model manifest tidak memiliki artifact path."
        )

    model_sha256 = _require_sha256(
        artifact.get("sha256"),
        field_name="artifact.sha256",
    )

    return (
        Path(artifact_path).stem,
        model_sha256,
    )

def verify_frozen_model_integrity(
    *,
    artifact_path: Path,
    schema_path: Path,
    manifest_path: Path,
) -> None:
    """Verify selected artifact and feature schema before deserialization."""

    if not manifest_path.is_file():
        raise ModelIntegrityError(
            f"Model manifest tidak ditemukan: {manifest_path}"
        )

    try:
        payload = json.loads(
            manifest_path.read_text(
                encoding="utf-8",
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelIntegrityError(
            f"Model manifest tidak valid: {manifest_path}"
        ) from exc

    if not isinstance(payload, dict):
        raise ModelIntegrityError(
            "Model manifest harus berupa JSON object."
        )

    artifact = payload.get("artifact")
    inputs = payload.get("inputs")

    if (
        not isinstance(artifact, dict)
        or not isinstance(inputs, dict)
    ):
        raise ModelIntegrityError(
            "Model manifest tidak memiliki artifact/inputs contract."
        )

    feature_schema = inputs.get("feature_schema")

    if not isinstance(feature_schema, dict):
        raise ModelIntegrityError(
            "Model manifest tidak memiliki feature_schema contract."
        )

    expected_artifact_path = Path(
        str(artifact.get("path", ""))
    )
    expected_schema_path = Path(
        str(feature_schema.get("path", ""))
    )

    if (
        artifact_path.resolve()
        != expected_artifact_path.resolve()
    ):
        raise ModelIntegrityError(
            "Model artifact path tidak cocok dengan frozen manifest."
        )

    if (
        schema_path.resolve()
        != expected_schema_path.resolve()
    ):
        raise ModelIntegrityError(
            "Feature schema path tidak cocok dengan frozen manifest."
        )

    expected_artifact_sha = _require_sha256(
        artifact.get("sha256"),
        field_name="artifact.sha256",
    )
    expected_schema_sha = _require_sha256(
        feature_schema.get("sha256"),
        field_name="inputs.feature_schema.sha256",
    )

    if _sha256_file(artifact_path) != expected_artifact_sha:
        raise ModelIntegrityError(
            "Model artifact SHA-256 tidak cocok dengan frozen manifest."
        )

    if (
        _sha256_canonical_text_file(schema_path)
        != expected_schema_sha
    ):
        raise ModelIntegrityError(
            "Feature schema SHA-256 tidak cocok dengan frozen manifest."
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
        manifest_path: Path = Path(
            "reports/evidence/modeling/SELECTED_MODEL_MANIFEST_v1.json"
        ),
    ) -> ModelScoreProvider:
        """Load the frozen model only after integrity verification."""

        if not artifact_path.is_file():
            raise FileNotFoundError(
                f"Model artifact tidak ditemukan: {artifact_path}"
            )

        if not schema_path.is_file():
            raise FileNotFoundError(
                f"Feature schema tidak ditemukan: {schema_path}"
            )

        verify_frozen_model_integrity(
            artifact_path=artifact_path,
            schema_path=schema_path,
            manifest_path=manifest_path,
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


__all__ = [
    "ModelIntegrityError",
    "ModelScoreProvider",
    "load_frozen_model_identity",
    "verify_frozen_model_integrity",
]