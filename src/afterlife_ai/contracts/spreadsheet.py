"""Spreadsheet contract aligned with FEATURE_SCHEMA_FINAL_v2.0.yaml."""

SHEET_NAME = "inventory_lots"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "lot_id",
    "sku",
    "product_name",
    "product_category",
    "current_quantity",
    "unit",
    "unit_cost",
    "normal_selling_price",
    "source_location",
    "storage_type",
    "verification_status",
)

CONDITIONAL_COLUMNS: tuple[str, ...] = (
    "batch_or_reference_id",
    "product_subcategory",
    "purchase_date",
    "last_receipt_date",
    "production_date",
    "expiry_date",
    "safe_use_by_at",
    "commercial_sale_cutoff_at",
    "units_sold_observation_window",
    "observation_days",
    "safety_stock",
    "minimum_recovery_price",
    "declared_surplus",
    "declared_surplus_quantity",
    "storage_history_status",
    "temperature_log_available",
    "product_condition",
    "packaging_condition",
    "quality_inspection_status",
    "seal_integrity",
    "primary_container_integrity",
    "expiry_label_readable",
    "lot_code_readable",
    "package_volume_ml",
    "package_weight_g",
    "package_format",
)

EXTENSION_COLUMN_PREFIX = "x_"

UNKNOWN_COLUMN_POLICY = (
    "REJECT_BY_DEFAULT; allow only explicitly documented extension "
    "columns prefixed with x_"
)

EMPTY_ROW_POLICY = "DROP fully empty rows; report count"

DUPLICATE_POLICY = (
    "Exact duplicate rows are validation errors; repeated SKU is allowed "
    "only when lot_id or batch differs"
)

ALL_CANONICAL_COLUMNS: tuple[str, ...] = (
    *REQUIRED_COLUMNS,
    *CONDITIONAL_COLUMNS,
)

__all__ = [
    "ALL_CANONICAL_COLUMNS",
    "CONDITIONAL_COLUMNS",
    "DUPLICATE_POLICY",
    "EMPTY_ROW_POLICY",
    "EXTENSION_COLUMN_PREFIX",
    "REQUIRED_COLUMNS",
    "SHEET_NAME",
    "UNKNOWN_COLUMN_POLICY",
]
