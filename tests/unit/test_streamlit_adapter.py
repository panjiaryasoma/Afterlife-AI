from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

import pytest

from afterlife_ai.contracts.enums import OptimizationObjective


def test_streamlit_adapter_uses_canonical_production_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from frontend.streamlit import adapter

    pipeline_result = Mock()

    pipeline_mock = Mock(
        return_value=pipeline_result
    )

    monkeypatch.setattr(
        adapter,
        "run_production_pipeline",
        pipeline_mock,
    )

    analysis_at = datetime(
        2026,
        8,
        16,
        12,
        0,
        tzinfo=UTC,
    )

    result = adapter.run_streamlit_analysis(
        workbook_bytes=b"fake-xlsx-content",
        inventory_file_name="inventory.xlsx",
        analysis_at=analysis_at,
        request_id="REQ-STREAMLIT-001",
        optimization_objective=(
            OptimizationObjective.BALANCED
        ),
        max_logistics_budget=Decimal("30000"),
        minimum_expected_rescue_ratio=(
            Decimal("0.90")
        ),
        rescue_deadline_at=None,
    )

    assert result is pipeline_result

    pipeline_mock.assert_called_once()

    call = pipeline_mock.call_args

    assert (
        call.kwargs["runtime_config_path"]
        == Path("configs/runtime_v1.yaml")
    )

    assert (
        call.kwargs["partner_registry_path"]
        == Path(
            "configs/partner_registry_demo_v1.yaml"
        )
    )

    assert (
        call.kwargs["analysis_at"]
        == analysis_at
    )

    assert (
        call.kwargs["request_id"]
        == "REQ-STREAMLIT-001"
    )

    assert (
        call.kwargs["optimization_objective"]
        is OptimizationObjective.BALANCED
    )

    assert (
        call.kwargs["max_logistics_budget"]
        == Decimal("30000")
    )

    assert (
        call.kwargs[
            "minimum_expected_rescue_ratio"
        ]
        == Decimal("0.90")
    )

    workbook_path = call.kwargs[
        "workbook_path"
    ]

    assert isinstance(
        workbook_path,
        Path,
    )

    assert workbook_path.suffix == ".xlsx"

    assert not workbook_path.exists()

def test_streamlit_adapter_rejects_non_xlsx() -> None:
    from frontend.streamlit.adapter import (
        run_streamlit_analysis,
    )

    with pytest.raises(
        ValueError,
        match=r"\.xlsx",
    ):
        run_streamlit_analysis(
            workbook_bytes=b"not-empty",
            inventory_file_name="inventory.csv",
            analysis_at=datetime(
                2026,
                8,
                16,
                12,
                0,
                tzinfo=UTC,
            ),
            request_id="REQ-STREAMLIT-INVALID",
            optimization_objective=(
                OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
            ),
            max_logistics_budget=None,
            minimum_expected_rescue_ratio=None,
            rescue_deadline_at=None,
        )


def test_streamlit_adapter_rejects_empty_upload() -> None:
    from frontend.streamlit.adapter import (
        run_streamlit_analysis,
    )

    with pytest.raises(
        ValueError,
        match="tidak boleh kosong",
    ):
        run_streamlit_analysis(
            workbook_bytes=b"",
            inventory_file_name="inventory.xlsx",
            analysis_at=datetime(
                2026,
                8,
                16,
                12,
                0,
                tzinfo=UTC,
            ),
            request_id="REQ-STREAMLIT-EMPTY",
            optimization_objective=(
                OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
            ),
            max_logistics_budget=None,
            minimum_expected_rescue_ratio=None,
            rescue_deadline_at=None,
        )

def test_streamlit_adapter_cleanup_does_not_mask_pipeline_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from frontend.streamlit import adapter

    pipeline_mock = Mock(
        side_effect=ValueError(
            "canonical inventory validation failed"
        )
    )

    monkeypatch.setattr(
        adapter,
        "run_production_pipeline",
        pipeline_mock,
    )

    original_unlink = Path.unlink

    def locked_unlink(
        path: Path,
        missing_ok: bool = False,
    ) -> None:
        if path.suffix == ".xlsx":
            raise PermissionError(
                32,
                "file is being used by another process",
            )

        original_unlink(
            path,
            missing_ok=missing_ok,
        )

    monkeypatch.setattr(
        Path,
        "unlink",
        locked_unlink,
    )

    with pytest.raises(
        ValueError,
        match="canonical inventory validation failed",
    ):
        adapter.run_streamlit_analysis(
            workbook_bytes=b"fake-xlsx-content",
            inventory_file_name="inventory.xlsx",
            analysis_at=datetime(
                2026,
                8,
                16,
                12,
                0,
                tzinfo=UTC,
            ),
            request_id="REQ-CLEANUP-ERROR",
            optimization_objective=(
                OptimizationObjective.MAXIMIZE_RECOVERY_VALUE
            ),
            max_logistics_budget=None,
            minimum_expected_rescue_ratio=None,
            rescue_deadline_at=None,
        )