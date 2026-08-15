from decimal import Decimal
from pathlib import Path

import pytest

from afterlife_ai.contracts.enums import (
    BusinessType,
    ProductCategory,
)
from afterlife_ai.pipeline.runtime_config import (
    load_runtime_config,
)


def test_load_runtime_config_reads_static_mvp_defaults() -> None:
    config = load_runtime_config(
        Path("configs/runtime_v1.yaml")
    )

    assert config.runtime_mode == "LOCAL_SYNCHRONOUS"

    assert (
        config.business.business_type
        is BusinessType.SMALL_RETAIL
    )

    packaged_beverage = config.triage.category_policies[
        ProductCategory.PACKAGED_BEVERAGE
    ]

    assert (
        packaged_beverage.effective_sales_window_days
        == Decimal("10")
    )
    assert packaged_beverage.expiry_monitor_threshold_days == 14
    assert packaged_beverage.cold_chain_evidence_required is False

    frozen_food = config.triage.category_policies[
        ProductCategory.FROZEN_PREPARED_FOOD
    ]

    assert (
        frozen_food.effective_sales_window_days
        == Decimal("7")
    )
    assert frozen_food.expiry_monitor_threshold_days == 7
    assert frozen_food.cold_chain_evidence_required is True

    assert config.model.artifact_path == Path(
        "models/HGB_E_v1.joblib"
    )
    assert config.model.manifest_path == Path(
        "reports/evidence/modeling/SELECTED_MODEL_MANIFEST_v1.json"
    )

def test_load_runtime_config_reads_capability_defaults() -> None:
    config = load_runtime_config(
        Path("configs/runtime_v1.yaml")
    )

    capabilities = config.capabilities

    assert capabilities.profile_version == "runtime-capability-v1.0"
    assert capabilities.real_world_validated is False

    assert (
        capabilities.supported_actions["INTERNAL_REPURPOSE"]
        is True
    )
    assert capabilities.supported_actions["BUNDLE"] is True
    assert capabilities.supported_actions["LOCAL_DISCOUNT"] is True
    assert capabilities.supported_actions["SAFE_DISPOSAL"] is True
    assert capabilities.supported_actions["PROMOTIONAL_BONUS"] is False

    assert (
        capabilities.internal_repurpose.maximum_quantity
        == Decimal("6")
    )
    assert (
        capabilities.bundle.maximum_quantity
        == Decimal("4")
    )
    assert (
        capabilities.local_discount.price_fraction_of_normal
        == Decimal("0.75")
    )
def test_load_runtime_config_rejects_duplicate_yaml_keys(
    tmp_path: Path,
) -> None:
    source = Path(
        "configs/runtime_v1.yaml"
    ).read_text(
        encoding="utf-8-sig"
    )

    duplicate_source = source.replace(
        "config_name: Afterlife AI Runtime Configuration",
        (
            "config_name: Afterlife AI Runtime Configuration\n"
            "config_name: Duplicate Runtime Configuration"
        ),
        1,
    )

    config_path = tmp_path / "runtime_duplicate.yaml"

    config_path.write_text(
        duplicate_source,
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate YAML key",
    ):
        load_runtime_config(config_path)

def test_load_runtime_config_rejects_nested_duplicate_yaml_keys(
    tmp_path: Path,
) -> None:
    source = Path(
        "configs/runtime_v1.yaml"
    ).read_text(
        encoding="utf-8-sig"
    )

    duplicate_source = source.replace(
        (
            "  real_world_validated: false\n"
            "\n"
            "  supported_actions:"
        ),
        (
            "  real_world_validated: false\n"
            "  real_world_validated: true\n"
            "\n"
            "  supported_actions:"
        ),
        1,
    )

    config_path = (
        tmp_path / "runtime_nested_duplicate.yaml"
    )

    config_path.write_text(
        duplicate_source,
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate YAML key",
    ):
        load_runtime_config(config_path)