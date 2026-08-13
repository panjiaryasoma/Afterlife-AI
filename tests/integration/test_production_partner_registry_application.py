from datetime import UTC, datetime
from pathlib import Path

import yaml

from afterlife_ai.contracts.enums import ActionType
from afterlife_ai.pipeline.application import (
    run_production_pipeline,
)

ANALYSIS_AT = datetime(
    2026,
    8,
    5,
    12,
    0,
    tzinfo=UTC,
)


def _enabled_runtime_config(
    tmp_path: Path,
) -> Path:
    source = Path(
        "configs/runtime_v1.yaml"
    )

    payload = yaml.safe_load(
        source.read_text(
            encoding="utf-8"
        )
    )

    payload[
        "capabilities"
    ][
        "supported_actions"
    ][
        "EXTERNAL_PARTNER"
    ] = True

    target = (
        tmp_path
        / "runtime_partner_enabled.yaml"
    )

    target.write_text(
        yaml.safe_dump(
            payload,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    return target


def _partner_registry(
    tmp_path: Path,
) -> Path:
    target = (
        tmp_path
        / "partner_registry.yaml"
    )

    target.write_text(
        """registry_snapshot_id: PDR-DEMO-APP-001
snapshot_mode: STATIC_OFFLINE
source_type: SYNTHETIC_DEMO_FIXTURE
real_world_verified: false
runtime_internet_required: false

matching_records:
  - source_lot_id: LOT-003
    partner_id: PARTNER-DEMO-001
    destination_type: EXTERNAL_PARTNER

    maximum_quantity: 6
    offered_or_selling_price_per_unit: 1800

    direct_action_cost: 0
    logistics_cost: 0
    handling_cost: 0

    estimated_completion_hours: 6

    active_demand_quantity: 6
    available_capacity: 6
    minimum_order_quantity: 1

    distance_km: 3

    demand_valid_until: 2026-08-31T23:59:59Z

    category_match_status: MATCH
    package_size_match_status: MATCH
    customer_segment_match_status: MATCH
    storage_compatibility_status: MATCH
""",
        encoding="utf-8",
    )

    return target


def test_production_pipeline_loads_static_partner_registry(
    tmp_path: Path,
) -> None:
    runtime_config_path = (
        _enabled_runtime_config(
            tmp_path
        )
    )

    partner_registry_path = (
        _partner_registry(
            tmp_path
        )
    )

    result = run_production_pipeline(
        workbook_path=Path(
            "tests/fixtures/integration_001/"
            "RAW_INVENTORY_FIXTURE.xlsx"
        ),
        runtime_config_path=(
            runtime_config_path
        ),
        partner_registry_path=(
            partner_registry_path
        ),
        analysis_at=ANALYSIS_AT,
        request_id=(
            "PRODUCTION-PARTNER-REGISTRY"
        ),
    )

    partner_candidates = [
        candidate
        for candidate
        in result.valued_candidates
        if (
            candidate.action_type
            is ActionType.EXTERNAL_PARTNER
        )
    ]

    assert len(partner_candidates) == 1

    candidate = partner_candidates[0]

    assert candidate.destination_id == (
        "PARTNER-DEMO-001"
    )
    assert candidate.active_demand_quantity == 6
    assert candidate.available_capacity == 6

    assert (
        "STALE_PARTNER_DEMAND"
        not in candidate.rejection_reason_codes
    )
