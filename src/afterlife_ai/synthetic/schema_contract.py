"""Adapter for the locked schema-v2 model feature contract."""

from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, model_validator


class ModelFeatureContract(BaseModel):
    """Model-training feature contract sourced from schema v2."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    row_granularity: str
    canonical_target: Literal["simulated_rescue_outcome"]
    target_type: str
    deprecated_target_alias: str | None = None
    latent_generator_field: Literal["generator_success_probability"]
    inference_output: Literal["estimated_rescue_success_score"]
    acceptance_fixture_score: str

    group_split_fields: list[str]
    allowed_categorical_features: list[str]
    allowed_numeric_features: list[str]
    forbidden_model_inputs: list[str]

    claim_boundary: str | None = None

    @property
    def model_features(self) -> list[str]:
        """Return the ordered estimator feature allowlist."""

        return [
            *self.allowed_categorical_features,
            *self.allowed_numeric_features,
        ]

    @model_validator(mode="after")
    def validate_feature_contract(self) -> Self:
        categorical = self.allowed_categorical_features
        numeric = self.allowed_numeric_features
        forbidden = self.forbidden_model_inputs
        groups = self.group_split_fields

        if len(categorical) != len(set(categorical)):
            raise ValueError(
                "allowed_categorical_features tidak boleh duplikat."
            )

        if len(numeric) != len(set(numeric)):
            raise ValueError(
                "allowed_numeric_features tidak boleh duplikat."
            )

        if len(forbidden) != len(set(forbidden)):
            raise ValueError(
                "forbidden_model_inputs tidak boleh duplikat."
            )

        overlap = set(categorical) & set(numeric)
        if overlap:
            raise ValueError(
                "Categorical dan numeric feature tidak boleh overlap: "
                f"{sorted(overlap)}"
            )

        leaked_features = set(self.model_features) & set(forbidden)
        if leaked_features:
            raise ValueError(
                "Model feature tidak boleh berada dalam forbidden inputs: "
                f"{sorted(leaked_features)}"
            )

        required_forbidden = {
            self.canonical_target,
            self.latent_generator_field,
            self.inference_output,
        }
        missing_forbidden = required_forbidden - set(forbidden)

        if missing_forbidden:
            raise ValueError(
                "Target/oracle/output wajib berada dalam forbidden inputs: "
                f"{sorted(missing_forbidden)}"
            )

        group_leakage = set(groups) - set(forbidden)
        if group_leakage:
            raise ValueError(
                "Grouping identifiers wajib forbidden sebagai estimator input: "
                f"{sorted(group_leakage)}"
            )

        return self


def load_model_feature_contract(
    schema_path: Path,
) -> ModelFeatureContract:
    """Load model_feature_contract directly from the locked schema."""

    payload = yaml.safe_load(schema_path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Feature schema harus berupa YAML mapping.")

    contract_payload = payload.get("model_feature_contract")

    if not isinstance(contract_payload, dict):
        raise ValueError(
            "model_feature_contract tidak ditemukan pada feature schema."
        )

    return ModelFeatureContract.model_validate(contract_payload)


__all__ = [
    "ModelFeatureContract",
    "load_model_feature_contract",
]
