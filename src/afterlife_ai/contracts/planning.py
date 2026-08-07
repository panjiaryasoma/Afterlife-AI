"""Contracts for surplus rescue planning lots."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from afterlife_ai.contracts.enums import (
    DefectSeverity,
    PackagingCondition,
    ProductCategory,
    ProductCondition,
    QualityInspectionStatus,
    SeasonalityStatus,
    StorageHistoryStatus,
    StorageRequirementMode,
    StorageType,
    SurplusSource,
    UnitCode,
    UrgencyLevel,
    VerificationStatus,
)


class SurplusPlanningLot(BaseModel):
    """Internal snapshot emitted only for planner-eligible surplus quantity."""

    model_config = ConfigDict(extra="forbid")

    planning_lot_id: str
    source_lot_id: str

    sku: str
    product_name: str
    product_category: ProductCategory
    product_subcategory: str | None = None

    planning_quantity: Decimal = Field(gt=Decimal("0"))
    unit: UnitCode

    unit_cost: Decimal = Field(ge=Decimal("0"))
    normal_selling_price: Decimal = Field(ge=Decimal("0"))
    minimum_recovery_price: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    source_location: str

    remaining_shelf_life_days: int | None = None
    remaining_safe_window_hours: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    remaining_commercial_window_days: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )

    urgency_level: UrgencyLevel
    surplus_source: SurplusSource
    seasonality_status: SeasonalityStatus | None = None

    storage_type: StorageType
    storage_requirement_mode: StorageRequirementMode
    storage_history_status: StorageHistoryStatus | None = None

    product_condition: ProductCondition | None = None
    packaging_condition: PackagingCondition | None = None
    defect_severity: DefectSeverity
    quality_inspection_status: QualityInspectionStatus | None = None
    verification_status: VerificationStatus

    package_volume_ml: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    package_weight_g: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
    )
    package_format: str | None = None

    estimated_current_value: Decimal = Field(
        ge=Decimal("0"),
    )


__all__ = ["SurplusPlanningLot"]
