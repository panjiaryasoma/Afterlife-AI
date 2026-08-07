"""Leakage-safe row contracts for synthetic model training data."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from afterlife_ai.synthetic.schema_contract import ModelFeatureContract

FeatureValue = str | int | float | None


class SyntheticCandidateRow(BaseModel):
    """One flat candidate row before serialization to the training table."""

    model_config = ConfigDict(extra="forbid")

    scenario_group_id: str
    business_profile_id: str
    request_id: str
    lot_id: str
    candidate_id: str

    source_type: Literal["SYNTHETIC_GENERATED"] = "SYNTHETIC_GENERATED"
    simulated_rescue_outcome: Literal[0, 1]

    feature_values: dict[str, FeatureValue]

    def validate_against(
        self,
        contract: ModelFeatureContract,
    ) -> None:
        """Validate exact feature coverage and leakage boundaries."""

        actual = set(self.feature_values)
        expected = set(contract.model_features)

        missing = expected - actual
        unexpected = actual - expected

        if missing:
            raise ValueError(
                "Synthetic candidate kehilangan required model features: "
                f"{sorted(missing)}"
            )

        if unexpected:
            raise ValueError(
                "Synthetic candidate memiliki unexpected model features: "
                f"{sorted(unexpected)}"
            )

        forbidden_overlap = actual & set(contract.forbidden_model_inputs)

        if forbidden_overlap:
            raise ValueError(
                "Synthetic candidate feature_values mengandung forbidden "
                f"model inputs: {sorted(forbidden_overlap)}"
            )

    def to_training_record(
        self,
        contract: ModelFeatureContract,
    ) -> dict[str, object]:
        """Export one leakage-safe flat training record."""

        self.validate_against(contract)

        record: dict[str, object] = {
            "scenario_group_id": self.scenario_group_id,
            "business_profile_id": self.business_profile_id,
            "request_id": self.request_id,
            "lot_id": self.lot_id,
            "candidate_id": self.candidate_id,
            "source_type": self.source_type,
            **self.feature_values,
            "simulated_rescue_outcome": self.simulated_rescue_outcome,
        }

        return record


class SyntheticOracleRow(BaseModel):
    """Generator-only latent truth kept outside the estimator input table."""

    model_config = ConfigDict(extra="forbid")

    scenario_group_id: str
    business_profile_id: str
    request_id: str
    lot_id: str
    candidate_id: str

    source_type: Literal["SYNTHETIC_GENERATED"] = "SYNTHETIC_GENERATED"

    generator_success_probability: float = Field(
        ge=0.0,
        le=1.0,
    )

    def to_oracle_record(self) -> dict[str, object]:
        """Export one generator-only oracle record."""

        return {
            "scenario_group_id": self.scenario_group_id,
            "business_profile_id": self.business_profile_id,
            "request_id": self.request_id,
            "lot_id": self.lot_id,
            "candidate_id": self.candidate_id,
            "source_type": self.source_type,
            "generator_success_probability": (
                self.generator_success_probability
            ),
        }


__all__ = [
    "SyntheticCandidateRow",
    "SyntheticOracleRow",
]
