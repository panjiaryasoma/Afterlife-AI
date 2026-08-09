from decimal import Decimal
from pathlib import Path

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