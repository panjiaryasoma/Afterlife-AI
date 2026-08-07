"""Normalize raw spreadsheet values before contract validation."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

TEXT_FIELDS = {
    "lot_id",
    "sku",
    "batch_or_reference_id",
    "product_name",
    "product_category",
    "product_subcategory",
    "unit",
    "source_location",
    "storage_type",
    "storage_history_status",
    "product_condition",
    "packaging_condition",
    "quality_inspection_status",
    "seal_integrity",
    "primary_container_integrity",
    "package_format",
    "verification_status",
}

NUMERIC_FIELDS = {
    "current_quantity",
    "unit_cost",
    "normal_selling_price",
    "minimum_recovery_price",
    "units_sold_observation_window",
    "observation_days",
    "safety_stock",
    "declared_surplus_quantity",
    "package_volume_ml",
    "package_weight_g",
}

BOOLEAN_FIELDS = {
    "declared_surplus",
    "temperature_log_available",
    "expiry_label_readable",
    "lot_code_readable",
}

DATE_FIELDS = {
    "purchase_date",
    "last_receipt_date",
    "production_date",
    "expiry_date",
}

DATETIME_FIELDS = {
    "safe_use_by_at",
    "commercial_sale_cutoff_at",
}

TRUE_VALUES = {"true", "1", "yes", "y"}
FALSE_VALUES = {"false", "0", "no", "n"}

DEFAULT_ON_BLANK_FIELDS = {
    "safety_stock",
    "declared_surplus",
}


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def _normalize_decimal(field_name: str, value: Any) -> Decimal | None:
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(
            f"Field '{field_name}' harus berupa angka: {value!r}"
        ) from exc


def _normalize_boolean(field_name: str, value: Any) -> bool | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if not normalized:
        return None

    if normalized in TRUE_VALUES:
        return True

    if normalized in FALSE_VALUES:
        return False

    raise ValueError(
        f"Field '{field_name}' harus berupa nilai boolean "
        f"true/false, yes/no, atau 1/0: {value!r}"
    )


def _normalize_date(field_name: str, value: Any) -> date | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    normalized = str(value).strip()

    if not normalized:
        return None

    try:
        return date.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            f"Field '{field_name}' harus menggunakan tanggal ISO YYYY-MM-DD: "
            f"{value!r}"
        ) from exc


def _normalize_datetime(
    field_name: str,
    value: Any,
) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    normalized = str(value).strip()

    if not normalized:
        return None

    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            f"Field '{field_name}' harus menggunakan datetime ISO: {value!r}"
        ) from exc


def normalize_inventory_row(
    raw_row: dict[str, object],
) -> dict[str, object]:
    """Normalize one raw inventory row without validating business rules."""

    normalized: dict[str, object] = {}

    for field_name, value in raw_row.items():
        normalized_value: object

        if field_name in TEXT_FIELDS:
            normalized_value = _normalize_text(value)
        elif field_name in NUMERIC_FIELDS:
            normalized_value = _normalize_decimal(
                field_name,
                value,
            )
        elif field_name in BOOLEAN_FIELDS:
            normalized_value = _normalize_boolean(
                field_name,
                value,
            )
        elif field_name in DATE_FIELDS:
            normalized_value = _normalize_date(
                field_name,
                value,
            )
        elif field_name in DATETIME_FIELDS:
            normalized_value = _normalize_datetime(
                field_name,
                value,
            )
        else:
            normalized_value = value

        # A blank spreadsheet cell must not override a
        # non-nullable contract field that already owns a default.
        #
        # Example:
        # safety_stock blank -> omit field -> RawInventoryLot uses 0.
        if (
            normalized_value is None
            and field_name in DEFAULT_ON_BLANK_FIELDS
        ):
            continue

        normalized[field_name] = normalized_value

    return normalized


__all__ = ["normalize_inventory_row"]
