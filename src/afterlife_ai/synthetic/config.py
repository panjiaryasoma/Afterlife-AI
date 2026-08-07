"""Configuration contract for the synthetic rescue dataset generator."""

from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FeatureSchemaConfig(BaseModel):
    """Reference to the locked production feature schema."""

    model_config = ConfigDict(extra="forbid")

    path: str
    version: Literal["2.0.0"]


class TargetConfig(BaseModel):
    """Synthetic training target and generator-only oracle field."""

    model_config = ConfigDict(extra="forbid")

    field: Literal["simulated_rescue_outcome"]
    latent_oracle_field: Literal["generator_success_probability"]


class RandomnessConfig(BaseModel):
    """Seeds used for deterministic generation and robustness checks."""

    model_config = ConfigDict(extra="forbid")

    primary_seed: int
    robustness_seeds: list[int]

    @model_validator(mode="after")
    def validate_seeds(self) -> Self:
        if self.primary_seed not in self.robustness_seeds:
            raise ValueError(
                "primary_seed harus termasuk dalam robustness_seeds."
            )

        if len(self.robustness_seeds) != len(set(self.robustness_seeds)):
            raise ValueError("robustness_seeds tidak boleh duplikat.")

        return self


class GenerationConfig(BaseModel):
    """Size boundaries for the initial production dataset."""

    model_config = ConfigDict(extra="forbid")

    scenario_groups: int = Field(ge=2000)
    candidate_rows_min: int = Field(gt=0)
    candidate_rows_max: int = Field(gt=0)
    candidates_per_planning_lot_min: int = Field(ge=2)
    candidates_per_planning_lot_max: int = Field(le=8)

    @model_validator(mode="after")
    def validate_ranges(self) -> Self:
        if self.candidate_rows_max < self.candidate_rows_min:
            raise ValueError(
                "candidate_rows_max tidak boleh lebih kecil "
                "daripada candidate_rows_min."
            )

        if (
            self.candidates_per_planning_lot_max
            < self.candidates_per_planning_lot_min
        ):
            raise ValueError(
                "candidates_per_planning_lot_max tidak boleh lebih kecil "
                "daripada candidates_per_planning_lot_min."
            )

        return self


class SplitConfig(BaseModel):
    """Grouped train/validation/test split contract."""

    model_config = ConfigDict(extra="forbid")

    train: float = Field(gt=0, lt=1)
    validation: float = Field(gt=0, lt=1)
    test: float = Field(gt=0, lt=1)
    unit: Literal["scenario_group_id"]
    random_row_split_allowed: Literal[False]
    test_split_policy: Literal["LOCKED_FINAL_EVALUATION"]

    @model_validator(mode="after")
    def validate_split_total(self) -> Self:
        total = self.train + self.validation + self.test

        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                "Train, validation, dan test split harus berjumlah 1.0."
            )

        return self


class ArtifactConfig(BaseModel):
    """Canonical artifact locations for generated dataset evidence."""

    model_config = ConfigDict(extra="forbid")

    candidate_table: str
    oracle_table: str
    split_manifest: str
    dataset_manifest: str


class SyntheticDatasetConfig(BaseModel):
    """Top-level generator configuration."""

    model_config = ConfigDict(extra="forbid")

    config_version: Literal["1.0.0"]
    feature_schema: FeatureSchemaConfig
    target: TargetConfig
    randomness: RandomnessConfig
    generation: GenerationConfig
    split: SplitConfig
    artifacts: ArtifactConfig


def load_synthetic_dataset_config(path: Path) -> SyntheticDatasetConfig:
    """Load and validate one synthetic dataset YAML configuration."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Synthetic dataset config harus berupa YAML mapping.")

    return SyntheticDatasetConfig.model_validate(payload)


__all__ = [
    "SyntheticDatasetConfig",
    "load_synthetic_dataset_config",
]
