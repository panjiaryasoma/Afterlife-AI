"""Streamlit challenger presentation layer for Afterlife AI."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4
from zipfile import BadZipFile
from zoneinfo import ZoneInfo

import streamlit as st
from openpyxl.utils.exceptions import InvalidFileException
from pydantic import ValidationError

from afterlife_ai.contracts.enums import OptimizationObjective
from frontend.streamlit.adapter import (
    run_streamlit_analysis,
)

TIMEZONE_OPTIONS = {
    "WIB — Asia/Jakarta": ZoneInfo("Asia/Jakarta"),
    "UTC": UTC,
}


def _optional_decimal(
    value: float | None,
) -> Decimal | None:
    """Convert optional Streamlit numeric input to Decimal safely."""
    if value is None:
        return None

    return Decimal(str(value))


def main() -> None:
    """Render the Streamlit challenger interface."""
    st.set_page_config(
        page_title="Afterlife AI",
        page_icon="♻️",
        layout="wide",
    )

    st.title("Afterlife AI")
    st.caption(
        "Streamlit challenger presentation layer"
    )

    st.info(
        "This interface reuses the canonical "
        "Afterlife AI production pipeline."
    )

    st.subheader("Decision context")

    inventory_file = st.file_uploader(
        "Inventory workbook",
        type=["xlsx"],
        accept_multiple_files=False,
    )

    objective_value = st.selectbox(
        "Optimization objective",
        options=[
            objective.value
            for objective in OptimizationObjective
        ],
        index=0,
    )

    max_logistics_budget = st.number_input(
        "Maximum logistics budget",
        min_value=0.0,
        value=None,
        step=1000.0,
        placeholder="Optional",
    )

    minimum_rescue_ratio = st.number_input(
        "Minimum expected rescue ratio",
        min_value=0.0,
        max_value=1.0,
        value=None,
        step=0.01,
        placeholder="Required for BALANCED",
        disabled=(
            objective_value
            != OptimizationObjective.BALANCED.value
        ),
    )

    rescue_deadline = st.datetime_input(
        "Rescue deadline",
        value=None,
        help="Optional request-level rescue deadline.",
    )

    timezone_label = st.selectbox(
        "Deadline timezone",
        options=list(TIMEZONE_OPTIONS),
        index=0,
        disabled=rescue_deadline is None,
    )

    analyze_clicked = st.button(
        "Analyze inventory",
        type="primary",
    )

    if not analyze_clicked:
        return

    if inventory_file is None:
        st.error(
            "Pilih satu file inventory .xlsx terlebih dahulu."
        )
        return

    objective = OptimizationObjective(
        objective_value
    )

    deadline_at = None

    if rescue_deadline is not None:
        deadline_timezone = TIMEZONE_OPTIONS[
            timezone_label
        ]

        deadline_at = rescue_deadline.replace(
            tzinfo=deadline_timezone
        )

    analysis_at = datetime.now(UTC)

    try:
        result = run_streamlit_analysis(
            workbook_bytes=inventory_file.getvalue(),
            inventory_file_name=inventory_file.name,
            analysis_at=analysis_at,
            request_id=(
                f"REQ-ST-{uuid4().hex}"
            ),
            optimization_objective=objective,
            max_logistics_budget=_optional_decimal(
                max_logistics_budget
            ),
            minimum_expected_rescue_ratio=(
                _optional_decimal(
                    minimum_rescue_ratio
                )
            ),
            rescue_deadline_at=deadline_at,
        )

    except ValidationError as exc:
        st.error(
            "Decision context tidak valid."
        )

        for error in exc.errors(
            include_url=False,
            include_input=False,
        ):
            st.write(
                f"- {error['msg']}"
            )

        return

    except (
        BadZipFile,
        InvalidFileException,
        ValueError,
    ) as exc:
        st.error(
            f"Inventory tidak valid: {exc}"
        )
        return

    report = result.report

    st.success(
        "Analysis complete."
    )

    st.subheader(
        "Rescue Decision Report"
    )

    st.write(
        f"Request ID: `{report.request_id}`"
    )

    st.write(
        "Optimization objective:",
        report.optimization_objective.value,
    )

    st.write(
        "Solver status:",
        report.optimization_solver_status.value,
    )

    st.write(
        "Selected allocations:",
        len(report.selected_allocations),
    )

    st.write(
        "Manual-review items:",
        len(report.review_required_lots),
    )


if __name__ == "__main__":
    main()