from decimal import Decimal
from pathlib import Path

import pytest

from afterlife_ai.scoring.model_provider import ModelScoreProvider


def test_model_score_provider_rejects_missing_artifact(
    tmp_path: Path,
) -> None:
    missing_artifact = tmp_path / "missing.joblib"

    with pytest.raises(
        FileNotFoundError,
        match="Model artifact tidak ditemukan",
    ):
        ModelScoreProvider.from_artifact(
            artifact_path=missing_artifact,
        )
        
def test_model_score_provider_scores_feature_row() -> None:
    provider = ModelScoreProvider.from_artifact(
        artifact_path=Path("models/HGB_E_v1.joblib"),
        schema_path=Path(
            "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
        ),
    )

    features = {
        "product_category": "PACKAGED_BEVERAGE",
        "product_subcategory": "POWDER_DRINK",
        "action_type": "LOCAL_DISCOUNT",
        "business_type": "SMALL_RETAIL",
        "storage_requirement_mode": "AMBIENT_ALLOWED",
        "urgency_level": "HIGH",
        "surplus_source": "CALCULATED",
        "destination_type": "LOCAL_CUSTOMER",
        "seasonality_status": "POST_SEASON",
        "package_format": "SACHET",
        "planning_quantity": 20,
        "remaining_shelf_life_days": 30,
        "remaining_safe_window_hours": 0,
        "remaining_commercial_window_days": 30,
        "unit_cost": 1250,
        "normal_selling_price": 2000,
        "offered_or_selling_price_per_unit": 1500,
        "direct_action_cost": 0,
        "logistics_cost": 0,
        "handling_cost": 0,
        "estimated_completion_hours": 1,
        "active_demand_quantity": 20,
        "available_capacity": 20,
        "minimum_order_quantity": 1,
        "capability_resource_ratio": 1,
        "demand_coverage_ratio": 1,
        "demand_freshness_hours": 0,
        "distance_km": 0,
        "package_volume_ml": 20,
        "package_weight_g": 25,
    }

    first_score = provider.score_features(features)
    second_score = provider.score_features(features)

    assert Decimal("0") <= first_score <= Decimal("1")
    assert second_score == first_score