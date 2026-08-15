"""Production orchestration for model scoring after hard gates."""

from __future__ import annotations

from decimal import Decimal

from afterlife_ai.contracts.candidate import CandidateAction
from afterlife_ai.contracts.enums import ModelScoringStatus
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.pipeline.runtime_config import RuntimeConfig
from afterlife_ai.scoring.model_provider import ModelScoreProvider
from afterlife_ai.scoring.service import score_candidate

FALLBACK_SCORE = Decimal("0.50")
FALLBACK_MODEL_VERSION = "DETERMINISTIC_FALLBACK_V1"


def _load_provider(
    config: RuntimeConfig,
) -> ModelScoreProvider | None:
    """Load production model, falling back only on provider-load failure."""

    try:
        return ModelScoreProvider.from_artifact(
            artifact_path=config.model.artifact_path,
            schema_path=config.model.feature_schema_path,
            manifest_path=config.model.manifest_path,
        )
    except (FileNotFoundError, ValueError, OSError):
        return None


def _apply_fallback_score(
    candidate: CandidateAction,
) -> CandidateAction:
    """Apply deterministic neutral fallback to one eligible candidate."""

    return candidate.model_copy(
        update={
            "estimated_rescue_success_score": FALLBACK_SCORE,
            "model_version": FALLBACK_MODEL_VERSION,
            "model_scoring_status": ModelScoringStatus.ALLOWED,
        }
    )


def score_production_candidates(
    *,
    candidates: list[CandidateAction],
    planning_lots: list[SurplusPlanningLot],
    config: RuntimeConfig,
) -> list[CandidateAction]:
    """Score gate-eligible candidates with HGB-E or deterministic fallback."""

    planning_by_id = {
        planning_lot.planning_lot_id: planning_lot
        for planning_lot in planning_lots
    }

    provider = _load_provider(config)

    scored: list[CandidateAction] = []

    for candidate in candidates:
        if (
            candidate.model_scoring_status
            is ModelScoringStatus.BLOCKED
        ):
            scored.append(candidate)
            continue

        if (
            candidate.model_scoring_status
            is not ModelScoringStatus.DEFERRED
        ):
            raise ValueError(
                "Production scoring menerima candidate "
                f"{candidate.candidate_id} dengan status "
                f"{candidate.model_scoring_status.value}; "
                "expected DEFERRED atau BLOCKED."
            )

        planning_lot = planning_by_id.get(
            candidate.planning_lot_id
        )

        if planning_lot is None:
            raise ValueError(
                "Planning lot tidak ditemukan untuk candidate "
                f"{candidate.candidate_id}."
            )

        if provider is None:
            scored.append(
                _apply_fallback_score(candidate)
            )
            continue

        scored.append(
            score_candidate(
                planning_lot=planning_lot,
                candidate=candidate,
                business_type=(
                    config.business.business_type
                ),
                provider=provider,
            )
        )

    return scored


__all__ = ["score_production_candidates"]
