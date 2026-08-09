from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from afterlife_ai.contracts.enums import ModelScoringStatus
from afterlife_ai.pipeline.candidates import (
    generate_production_candidates,
)
from afterlife_ai.pipeline.gates import (
    apply_production_hard_gates,
)
from afterlife_ai.pipeline.planning import (
    build_production_planning_lots,
)
from afterlife_ai.pipeline.runtime_config import (
    load_runtime_config,
)
from afterlife_ai.pipeline.scoring import (
    score_production_candidates,
)
from afterlife_ai.pipeline.triage_pipeline import (
    run_triage_pipeline,
)

FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "integration_001"
)

WORKBOOK_PATH = FIXTURE_DIR / "RAW_INVENTORY_FIXTURE.xlsx"
RUNTIME_CONFIG_PATH = Path("configs/runtime_v1.yaml")


def test_missing_model_artifact_uses_deterministic_fallback() -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    config = load_runtime_config(
        RUNTIME_CONFIG_PATH
    )

    missing_model_config = config.model.model_copy(
        update={
            "artifact_path": Path(
                "models/DOES_NOT_EXIST.joblib"
            )
        }
    )

    config = config.model_copy(
        update={
            "model": missing_model_config
        }
    )

    triage = run_triage_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        analysis_at=analysis_at,
    )

    planning_lots = build_production_planning_lots(
        lots=triage.raw_inventory_lots,
        triage_results=triage.triage_results,
        config=config,
    )

    candidates = generate_production_candidates(
        planning_lots=planning_lots,
        config=config,
    )

    gated = apply_production_hard_gates(
        candidates=candidates,
        planning_lots=planning_lots,
        raw_inventory_lots=triage.raw_inventory_lots,
        config=config,
        analysis_at=analysis_at,
    )

    scored = score_production_candidates(
        candidates=gated,
        planning_lots=planning_lots,
        config=config,
    )

    assert len(scored) == 5

    assert all(
        candidate.model_scoring_status
        is ModelScoringStatus.ALLOWED
        for candidate in scored
    )

    assert all(
        candidate.estimated_rescue_success_score
        == Decimal("0.50")
        for candidate in scored
    )

    assert all(
        candidate.model_version
        == "DETERMINISTIC_FALLBACK_V1"
        for candidate in scored
    )
