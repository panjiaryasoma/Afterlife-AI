"""Inventory input contracts aligned with FEATURE_SCHEMA_FINAL_v2.0.yaml."""

from datetime import date, datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import (
    IntegrityStatus,
    PackagingCondition,
    ProductCategory,
    ProductCondition,
    QualityInspectionStatus,
    StorageHistoryStatus,
    StorageType,
    UnitCode,
    VerificationStatus,
)


class RawInventoryLot(BaseModel):
    """One raw inventory row submitted through the inventory workbook."""

    model_config = ConfigDict(extra="forbid")

    lot_id: str
    sku: str
    batch_or_reference_id: str | None = None
    product_name: str
    product_category: ProductCategory
    product_subcategory: str | None = None

    current_quantity: Decimal = Field(ge=0)
    unit: UnitCode
    unit_cost: Decimal = Field(ge=0)
    normal_selling_price: Decimal = Field(ge=0)
    minimum_recovery_price: Decimal | None = Field(default=None, ge=0)

    source_location: str

    purchase_date: date | None = None
    last_receipt_date: date | None = None
    production_date: date | None = None
    expiry_date: date | None = None
    safe_use_by_at: datetime | None = None
    commercial_sale_cutoff_at: datetime | None = None

    units_sold_observation_window: Decimal | None = Field(default=None, ge=0)
    observation_days: int | None = Field(default=None, gt=0)
    safety_stock: Decimal = Field(default=Decimal("0"), ge=0)

    declared_surplus: bool = False
    declared_surplus_quantity: Decimal | None = Field(default=None, ge=0)

    storage_type: StorageType
    storage_history_status: StorageHistoryStatus | None = None
    temperature_log_available: bool | None = None

    product_condition: ProductCondition | None = None
    packaging_condition: PackagingCondition | None = None
    quality_inspection_status: QualityInspectionStatus | None = None
    seal_integrity: IntegrityStatus | None = None
    primary_container_integrity: IntegrityStatus | None = None
    expiry_label_readable: bool | None = None
    lot_code_readable: bool | None = None

    package_volume_ml: Decimal | None = Field(default=None, ge=0)
    package_weight_g: Decimal | None = Field(default=None, ge=0)
    package_format: str | None = None

    verification_status: VerificationStatus

    @model_validator(mode="after")
    def validate_cross_field_contracts(self) -> Self:
        """Validate constraints involving more than one inventory field."""

        if self.declared_surplus and self.declared_surplus_quantity is None:
            raise ValueError(
                "declared_surplus_quantity wajib diisi ketika "
                "declared_surplus bernilai true"
            )

        if (
            self.declared_surplus_quantity is not None
            and self.declared_surplus_quantity > self.current_quantity
        ):
            raise ValueError(
                "declared_surplus_quantity tidak boleh melebihi "
                "current_quantity"
            )

        if (
            self.units_sold_observation_window is not None
            and self.observation_days is None
        ):
            raise ValueError(
                "observation_days wajib diisi ketika "
                "units_sold_observation_window tersedia"
            )

        if (
            self.minimum_recovery_price is not None
            and self.minimum_recovery_price > self.normal_selling_price
        ):
            raise ValueError(
                "minimum_recovery_price tidak boleh melebihi "
                "normal_selling_price tanpa premium recovery policy"
            )

        return self


    @model_validator(mode="after")
    def validate_production_and_expiry_dates(
        self,
    ) -> "RawInventoryLot":
        """Ensure expiry does not precede production."""

        if (
            self.production_date is not None
            and self.expiry_date is not None
            and self.expiry_date < self.production_date
        ):
            raise ValueError(
                "expiry_date tidak boleh lebih awal "
                "daripada production_date."
            )

        return self


__all__ = ["RawInventoryLot"]
