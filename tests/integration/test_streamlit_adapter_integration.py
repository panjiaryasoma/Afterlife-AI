from datetime import UTC, datetime
from pathlib import Path

from frontend.streamlit.adapter import (
    PARTNER_REGISTRY_PATH,
    RUNTIME_CONFIG_PATH,
    run_streamlit_analysis,
)

from afterlife_ai.contracts.enums import (
    OptimizationObjective,
)
from afterlife_ai.pipeline.application import (
    run_production_pipeline,
)

WORKBOOK_PATH = Path(
    "tests/fixtures/integration_001/"
    "RAW_INVENTORY_FIXTURE.xlsx"
)


def test_streamlit_adapter_matches_canonical_pipeline_report() -> None:
    analysis_at = datetime(
        2026,
        8,
        5,
        tzinfo=UTC,
    )

    workbook_bytes = WORKBOOK_PATH.read_bytes()

    streamlit_result = run_streamlit_analysis(
        workbook_bytes=workbook_bytes,
        inventory_file_name=WORKBOOK_PATH.name,
        analysis_at=analysis_at,
        request_id="REQ-STREAMLIT-PARITY-001",
        optimization_objective=(
            OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
        ),
        max_logistics_budget=None,
        minimum_expected_rescue_ratio=None,
        rescue_deadline_at=None,
    )

    canonical_result = run_production_pipeline(
        workbook_path=WORKBOOK_PATH,
        runtime_config_path=RUNTIME_CONFIG_PATH,
        partner_registry_path=PARTNER_REGISTRY_PATH,
        analysis_at=analysis_at,
        request_id="REQ-STREAMLIT-PARITY-001",
        optimization_objective=(
            OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
        ),
        max_logistics_budget=None,
        minimum_expected_rescue_ratio=None,
        rescue_deadline_at=None,
    )

    assert (
        streamlit_result.report.model_dump(mode="json")
        == canonical_result.report.model_dump(mode="json")
    )