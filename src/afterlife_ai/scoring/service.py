"""Production scoring orchestration for eligible rescue candidates."""

from __future__ import annotations

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import (
    BusinessType,
    CoverageStatus,
    FeasibilityStatus,
    ModelScoringStatus,
    SafetyStatus,
    ValidationStatus,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.scoring.features import build_model_feature_row
from afterlife_ai.scoring.model_provider import ModelScoreProvider


def score_candidate(
    *,
    planning_lot: SurplusPlanningLot,
    candidate: CandidateAction,
    business_type: BusinessType,
    provider: ModelScoreProvider,
) -> CandidateAction:
    """Score one hard-gate-eligible candidate with the production model."""

    eligible = (
        candidate.validation_status is ValidationStatus.PASSED
        and candidate.coverage_status is CoverageStatus.SUPPORTED
        and candidate.safety_status
        in {
            SafetyStatus.ACCEPTABLE,
            SafetyStatus.ACCEPTABLE_WITH_URGENCY,
        }
        and candidate.feasibility_status is FeasibilityStatus.FEASIBLE
        and candidate.model_scoring_status is ModelScoringStatus.DEFERRED
        and not candidate.rejection_reason_codes
    )

    if not eligible:
        raise ValueError(
            f"Candidate {candidate.candidate_id} "
            "tidak eligible untuk model scoring."
        )

    features = build_model_feature_row(
        planning_lot=planning_lot,
        candidate=candidate,
        business_type=business_type,
    )

    probability = provider.score_features(features)

    return candidate.model_copy(
        update={
            "estimated_rescue_success_score": probability,
            "model_version": provider.model.model_id,
            "model_scoring_status": ModelScoringStatus.ALLOWED,
        }
    )


__all__ = ["score_candidate"]