"""Build JSON-safe canonical inventory records."""

from typing import TypeAlias

from afterlife_ai.contracts.inventory import RawInventoryLot

CanonicalInventoryRecord: TypeAlias = dict[str, object]

CANONICAL_INVENTORY_FIELDS = tuple(RawInventoryLot.model_fields)


def build_canonical_inventory_records(
    inventory_lots: list[RawInventoryLot],
) -> list[CanonicalInventoryRecord]:
    """Convert validated inventory lots into ordered JSON-safe records."""

    canonical_records: list[CanonicalInventoryRecord] = []

    for inventory_lot in inventory_lots:
        serialized = inventory_lot.model_dump(
            mode="json",
            exclude_none=False,
        )

        canonical_record = {
            field_name: serialized[field_name]
            for field_name in CANONICAL_INVENTORY_FIELDS
        }

        canonical_records.append(canonical_record)

    return canonical_records


__all__ = [
    "CANONICAL_INVENTORY_FIELDS",
    "CanonicalInventoryRecord",
    "build_canonical_inventory_records",
]
