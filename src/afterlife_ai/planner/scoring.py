"""Deterministic fixture-only scoring for planner evaluation."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    CoverageStatus,
    FeasibilityStatus,
    ModelScoringStatus,
    SafetyStatus,
    ValidationStatus,
)


class FixtureScoreProvenance(BaseModel):
    """Explicit provenance for a synthetic evaluation fixture score."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider_name: str = "FixtureScoreProvider"
    score_type: str = "FIXTURE_EXPECTED_SCORE"
    source_type: str = "EVALUATION_FIXTURE"
    fixture_version: str


class FixtureScoreResult(BaseModel):
    """Candidate plus immutable fixture-score provenance."""

    model_config = ConfigDict(extra="forbid")

    candidate: CandidateAction
    provenance: FixtureScoreProvenance


class FixtureScoreProvider(BaseModel):
    """Provide deterministic scores for evaluation fixtures only."""

    model_config = ConfigDict(extra="forbid")

    scores: dict[str, Decimal]
    fixture_version: str

    @model_validator(mode="after")
    def validate_scores(self) -> Self:
        """Ensure every fixture score remains in probability range."""

        for candidate_id, score in self.scores.items():
            if score < Decimal("0") or score > Decimal("1"):
                raise ValueError(
                    f"Fixture score untuk {candidate_id} "
                    "harus berada pada rentang 0 sampai 1."
                )

        return self

    def score(
        self,
        candidate: CandidateAction,
    ) -> FixtureScoreResult:
        """Attach fixture-only score to a hard-gate eligible candidate."""

        if not self._is_fixture_score_eligible(candidate):
            raise ValueError(
                f"Candidate {candidate.candidate_id} tidak eligible "
                "untuk fixture scoring."
            )

        if candidate.candidate_id not in self.scores:
            raise KeyError(
                f"Fixture score tidak ditemukan untuk "
                f"{candidate.candidate_id}."
            )

        fixture_score = self.scores[candidate.candidate_id]

        scored_candidate = candidate.model_copy(
            update={
                "fixture_rescue_success_score": fixture_score,
            }
        )

        provenance = FixtureScoreProvenance(
            fixture_version=self.fixture_version,
        )

        return FixtureScoreResult(
            candidate=scored_candidate,
            provenance=provenance,
        )

    @staticmethod
    def _is_fixture_score_eligible(
        candidate: CandidateAction,
    ) -> bool:
        """Return whether hard-gate output permits fixture scoring."""

        return (
            candidate.validation_status is ValidationStatus.PASSED
            and candidate.coverage_status is CoverageStatus.SUPPORTED
            and candidate.safety_status
            in {
                SafetyStatus.ACCEPTABLE,
                SafetyStatus.ACCEPTABLE_WITH_URGENCY,
            }
            and candidate.feasibility_status
            is FeasibilityStatus.FEASIBLE
            and candidate.model_scoring_status
            is not ModelScoringStatus.BLOCKED
            and not candidate.rejection_reason_codes
        )


__all__ = [
    "FixtureScoreProvider",
    "FixtureScoreProvenance",
    "FixtureScoreResult",
]
