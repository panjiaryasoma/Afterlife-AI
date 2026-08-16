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

def _format_quantity(
    value: Decimal | None,
) -> str:
    """Format a report quantity with at most two decimals."""
    if value is None:
        return "—"

    formatted = f"{value:.2f}"

    return formatted.rstrip("0").rstrip(".")


def _format_ratio(
    value: Decimal | None,
) -> str:
    """Format a zero-to-one ratio as a percentage."""
    if value is None:
        return "—"

    return f"{value * Decimal('100'):.2f}%"

def _format_currency(
    value: Decimal | None,
) -> str:
    """Format monetary report values for presentation."""
    if value is None:
        return "—"

    return f"Rp {value:,.0f}"


def _format_score(
    value: Decimal | None,
) -> str:
    """Format a zero-to-one score as a percentage."""
    if value is None:
        return "Not estimated"

    return f"{value * Decimal('100'):.2f}%"

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

    st.subheader("Validation")

    validation = report.validation_summary

    validation_columns = st.columns(3)

    validation_columns[0].metric(
        "Validation status",
        validation.status.value,
    )

    validation_columns[1].metric(
        "Input lots",
        validation.input_lots,
    )

    validation_columns[2].metric(
        "Canonical records",
        validation.canonical_records,
    )

    st.subheader("Inventory triage")

    triage = report.triage_summary

    triage_columns = st.columns(5)

    triage_columns[0].metric(
        "Protected",
        _format_quantity(
            triage.protected_quantity
        ),
    )

    triage_columns[1].metric(
        "Monitor",
        _format_quantity(
            triage.monitor_quantity
        ),
    )

    triage_columns[2].metric(
        "Planning",
        _format_quantity(
            triage.planning_quantity
        ),
    )

    triage_columns[3].metric(
        "Expired",
        _format_quantity(
            triage.expired_quantity
        ),
    )

    triage_columns[4].metric(
        "Needs review",
        _format_quantity(
            triage.review_quantity
        ),
    )

    st.subheader("Rescue summary")

    batch = report.batch_metrics

    summary_columns = st.columns(4)

    summary_columns[0].metric(
        "Allocated",
        _format_quantity(
            batch.allocated_planning_quantity
        ),
    )

    summary_columns[1].metric(
        "Unallocated",
        _format_quantity(
            batch.unallocated_planning_quantity
        ),
    )

    summary_columns[2].metric(
        "Expected rescue",
        _format_quantity(
            batch.expected_physical_rescue_quantity
        ),
    )

    summary_columns[3].metric(
        "Expected rescue ratio",
        _format_ratio(
            batch.expected_rescue_ratio
        ),
    )

    st.subheader("Selected rescue allocations")

    if not report.selected_allocations:
        st.info(
            "No rescue allocation was selected "
            "under the current constraints."
        )

    for index, allocation in enumerate(
        report.selected_allocations,
        start=1,
    ):
        action_label = (
            allocation.action_type.value
            .replace("_", " ")
            .title()
        )

        with st.expander(
            (
                f"{index}. {action_label} · "
                f"{allocation.source_lot_id}"
            ),
            expanded=index == 1,
        ):
            route_columns = st.columns(3)

            route_columns[0].metric(
                "Allocated quantity",
                _format_quantity(
                    allocation.allocated_quantity
                ),
            )

            route_columns[1].metric(
                "Rescue success",
                _format_score(
                    allocation.estimated_rescue_success_score
                ),
            )

            route_columns[2].metric(
                "Expected net recovery",
                _format_currency(
                    allocation.expected_net_recovery
                ),
            )

            st.write(
                "**Destination:**",
                allocation.destination_id
                or "No external destination",
            )

            st.write(
                "**Destination type:**",
                allocation.destination_type
                or "Not reported",
            )

            detail_columns = st.columns(3)

            detail_columns[0].metric(
                "Completion",
                (
                    f"{allocation.estimated_completion_hours} h"
                    if allocation.estimated_completion_hours
                    is not None
                    else "—"
                ),
            )

            detail_columns[1].metric(
                "Distance",
                (
                    f"{allocation.distance_km} km"
                    if allocation.distance_km
                    is not None
                    else "—"
                ),
            )

            detail_columns[2].metric(
                "Expected value / unit",
                _format_currency(
                    allocation.expected_value_per_unit
                ),
            )

            st.markdown("**Value components**")

            value_columns = st.columns(3)

            value_columns[0].metric(
                "Cash recovery",
                _format_currency(
                    allocation.expected_cash_recovery
                ),
            )

            value_columns[1].metric(
                "Future branch recovery",
                _format_currency(
                    allocation.expected_future_branch_recovery
                ),
            )

            value_columns[2].metric(
                "Avoided purchase cost",
                _format_currency(
                    allocation.expected_avoided_purchase_cost
                ),
            )

            cost_columns = st.columns(3)

            cost_columns[0].metric(
                "Direct action cost",
                _format_currency(
                    allocation.direct_action_cost
                ),
            )

            cost_columns[1].metric(
                "Logistics cost",
                _format_currency(
                    allocation.logistics_cost
                ),
            )

            cost_columns[2].metric(
                "Handling cost",
                _format_currency(
                    allocation.handling_cost
                ),
            )

            outcome_columns = st.columns(2)

            outcome_columns[0].metric(
                "Expected rescued quantity",
                _format_quantity(
                    allocation.expected_physical_rescue_quantity
                ),
            )

            outcome_columns[1].metric(
                "Expected waste quantity",
                _format_quantity(
                    allocation.expected_waste_quantity
                ),
            )

            st.markdown("**Binding constraints**")

            if allocation.binding_constraint_codes:
                st.code(
                    "\n".join(
                        allocation.binding_constraint_codes
                    ),
                    language=None,
                )
            else:
                st.caption(
                    "No binding constraint code reported."
                )

    st.subheader("Human review")

    review_status_columns = st.columns(2)

    review_status_columns[0].metric(
        "Exception review required",
        (
            "YES"
            if report.human_exception_review_required
            else "NO"
        ),
    )

    review_status_columns[1].metric(
        "Final approval",
        report.human_final_approval_status.value,
    )

    if report.human_exception_review_required:
        st.warning(
            "This report contains inventory that requires "
            "human exception review before any physical action."
        )
    else:
        st.success(
            "No exception-review quantity was reported."
        )

    if report.review_required_lots:
        for index, review_item in enumerate(
            report.review_required_lots,
            start=1,
        ):
            with st.expander(
                (
                    f"{index}. {review_item.source_lot_id} · "
                    f"{_format_quantity(review_item.review_quantity)} "
                    "units"
                ),
            ):
                st.write(
                    "**Review quantity:**",
                    _format_quantity(
                        review_item.review_quantity
                    ),
                )

                st.markdown("**Reason codes**")

                if review_item.reason_codes:
                    st.code(
                        "\n".join(
                            review_item.reason_codes
                        ),
                        language=None,
                    )
                else:
                    st.caption(
                        "No review reason code reported."
                    )

    else:
        st.info(
            "No manual-review lot was reported."
        )

    st.subheader("Warnings and limitations")

    if report.fallback_chain:
        st.warning(
            "The analysis used one or more fallback steps. "
            "Review the details below."
        )

        with st.expander(
            "Fallback chain",
        ):
            for index, fallback in enumerate(
                report.fallback_chain,
                start=1,
            ):
                step = (
                    fallback.step
                    or "UNSPECIFIED_STEP"
                )

                reason = (
                    fallback.reason
                    or "No reason reported."
                )

                st.markdown(
                    f"**{index}. {step}**"
                )

                st.write(reason)

    if report.limitations:
        with st.expander(
            "Report limitations",
            expanded=True,
        ):
            for limitation in report.limitations:
                st.warning(
                    limitation
                )
    else:
        st.caption(
            "No report limitation was provided."
        )

    st.subheader("Execution boundary")

    execution_columns = st.columns(2)

    execution_columns[0].metric(
        "Execution performed",
        (
            "YES"
            if report.execution_performed
            else "NO"
        ),
    )

    execution_columns[1].metric(
        "Human final approval",
        report.human_final_approval_status.value,
    )

    if not report.execution_performed:
        st.info(
            "This Rescue Decision Report is advisory only. "
            "No physical rescue action has been executed."
        )

    st.subheader("Scoring provenance")

    provenance = report.score_provenance

    provenance_columns = st.columns(2)

    provenance_columns[0].write(
        "**Provider:**"
    )
    provenance_columns[0].write(
        provenance.provider_name
    )

    provenance_columns[1].write(
        "**Score type:**"
    )
    provenance_columns[1].write(
        provenance.score_type
    )

    provenance_columns = st.columns(2)

    provenance_columns[0].write(
        "**Source type:**"
    )
    provenance_columns[0].write(
        provenance.source_type.value
    )

    provenance_columns[1].write(
        "**Fixture version:**"
    )
    provenance_columns[1].write(
        provenance.fixture_version
        or "Not applicable"
    )

    model_columns = st.columns(2)

    model_columns[0].write(
        "**Model version:**"
    )
    model_columns[0].code(
        report.model_version,
        language=None,
    )

    model_columns[1].write(
        "**Model execution performed:**"
    )
    model_columns[1].write(
        
            "YES"
            if report.model_execution_performed
            else "NO"
        
    )

    with st.expander(
        "Technical provenance",
    ):
        st.write(
            "**Model SHA-256:**"
        )
        st.code(
            report.model_sha256,
            language=None,
        )

        st.write(
            "**Feature schema version:**",
            report.feature_schema_version,
        )

        st.write(
            "**Ruleset version:**",
            report.ruleset_version,
        )

        st.write(
            "**Capability snapshot:**",
            report.capability_snapshot_version,
        )

        st.write(
            "**Deterministic execution:**",
            report.deterministic_execution,
        )

        st.write(
            "**Optimizer random seed:**",
            report.optimizer_random_seed,
        )

        st.write(
            "**Optimizer search workers:**",
            report.optimizer_num_search_workers,
        )

    st.subheader("Download report")

    report_json = report.model_dump_json(
        indent=2,
    )

    st.download_button(
        label="Download Rescue Decision Report",
        data=report_json,
        file_name=(
            "rescue_decision_report_"
            f"{report.request_id}.json"
        ),
        mime="application/json",
        type="primary",
    )

    st.caption(
        "The downloaded JSON is serialized directly "
        "from the canonical Rescue Decision Report."
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