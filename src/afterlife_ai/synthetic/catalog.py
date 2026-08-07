"""Versioned synthetic sampling catalog.

Catalog values define synthetic scenario coverage only. They are not
real-world frequency, demand, pricing, or success-probability claims.
"""

from dataclasses import dataclass

from afterlife_ai.contracts.enums import (
    ActionType,
    ProductCategory,
    StorageRequirementMode,
)


@dataclass(frozen=True)
class ProductSamplingProfile:
    """Supported synthetic product-shape profile."""

    category: ProductCategory
    subcategories: tuple[str, ...]
    storage_requirement_modes: tuple[StorageRequirementMode, ...]
    package_formats: tuple[str, ...]


MODEL_SCORED_ACTIONS: tuple[ActionType, ...] = (
    ActionType.LOCAL_DISCOUNT,
    ActionType.BUNDLE,
    ActionType.PROMOTIONAL_BONUS,
    ActionType.INTERNAL_REPURPOSE,
    ActionType.INTERNAL_USE,
    ActionType.RETURN_TO_SUPPLIER,
    ActionType.BRANCH_TRANSFER,
    ActionType.WHOLESALE,
    ActionType.EXTERNAL_PARTNER,
    ActionType.DONATION,
)


ACTION_DESTINATION_TYPES: dict[ActionType, str] = {
    ActionType.LOCAL_DISCOUNT: "LOCAL_CUSTOMER",
    ActionType.BUNDLE: "LOCAL_CUSTOMER",
    ActionType.PROMOTIONAL_BONUS: "LOCAL_CUSTOMER",
    ActionType.INTERNAL_REPURPOSE: "INTERNAL_OPERATION",
    ActionType.INTERNAL_USE: "INTERNAL_OPERATION",
    ActionType.RETURN_TO_SUPPLIER: "SUPPLIER",
    ActionType.BRANCH_TRANSFER: "BRANCH",
    ActionType.WHOLESALE: "WHOLESALE_BUYER",
    ActionType.EXTERNAL_PARTNER: "EXTERNAL_PARTNER",
    ActionType.DONATION: "DONATION_PARTNER",
}


PRODUCT_PROFILES: tuple[ProductSamplingProfile, ...] = (
    ProductSamplingProfile(
        category=ProductCategory.PACKAGED_FOOD,
        subcategories=("SNACK", "CANNED_FOOD", "DRY_FOOD"),
        storage_requirement_modes=(
            StorageRequirementMode.AMBIENT_ALLOWED,
        ),
        package_formats=("SACHET", "PACK", "BOX", "CAN"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.PACKAGED_BEVERAGE,
        subcategories=("POWDERED_DRINK", "BOTTLED_DRINK", "CANNED_DRINK"),
        storage_requirement_modes=(
            StorageRequirementMode.AMBIENT_ALLOWED,
            StorageRequirementMode.CHILLED_PREFERRED,
        ),
        package_formats=("SACHET", "BOTTLE", "CAN", "BOX"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.BAKERY,
        subcategories=("BREAD", "PASTRY", "CAKE"),
        storage_requirement_modes=(
            StorageRequirementMode.AMBIENT_ALLOWED,
            StorageRequirementMode.COLD_REQUIRED_FOR_QUALITY_WINDOW,
        ),
        package_formats=("PACK", "BOX", "TRAY"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.READY_TO_EAT_MEAL,
        subcategories=("PREPARED_MEAL", "READY_SNACK"),
        storage_requirement_modes=(
            StorageRequirementMode.SAFETY_CRITICAL_COLD_CHAIN,
        ),
        package_formats=("BOX", "TRAY", "CUP"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.FROZEN_PREPARED_FOOD,
        subcategories=("FROZEN_MEAL", "FROZEN_SNACK"),
        storage_requirement_modes=(
            StorageRequirementMode.SAFETY_CRITICAL_COLD_CHAIN,
        ),
        package_formats=("PACK", "BOX"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.CHILLED_DAIRY,
        subcategories=("MILK", "YOGURT", "DAIRY_DESSERT"),
        storage_requirement_modes=(
            StorageRequirementMode.SAFETY_CRITICAL_COLD_CHAIN,
        ),
        package_formats=("BOTTLE", "CUP", "PACK"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.FRESH_PRODUCE,
        subcategories=("FRUIT", "VEGETABLE"),
        storage_requirement_modes=(
            StorageRequirementMode.CHILLED_PREFERRED,
            StorageRequirementMode.COLD_REQUIRED_FOR_QUALITY_WINDOW,
        ),
        package_formats=("KG", "PACK", "TRAY"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.HOUSEHOLD_CLEANING,
        subcategories=("CLEANER", "DETERGENT"),
        storage_requirement_modes=(
            StorageRequirementMode.NONE,
            StorageRequirementMode.AMBIENT_ALLOWED,
        ),
        package_formats=("BOTTLE", "PACK", "SACHET"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.PERSONAL_CARE,
        subcategories=("BODY_CARE", "HAIR_CARE", "HYGIENE"),
        storage_requirement_modes=(
            StorageRequirementMode.NONE,
            StorageRequirementMode.AMBIENT_ALLOWED,
        ),
        package_formats=("BOTTLE", "TUBE", "PACK", "SACHET"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.CONDIMENT,
        subcategories=("SAUCE", "SEASONING", "SPREAD"),
        storage_requirement_modes=(
            StorageRequirementMode.AMBIENT_ALLOWED,
            StorageRequirementMode.CHILLED_PREFERRED,
        ),
        package_formats=("BOTTLE", "SACHET", "JAR"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.BABY_CARE,
        subcategories=("BABY_FOOD", "BABY_HYGIENE"),
        storage_requirement_modes=(
            StorageRequirementMode.AMBIENT_ALLOWED,
        ),
        package_formats=("PACK", "BOX", "BOTTLE"),
    ),
    ProductSamplingProfile(
        category=ProductCategory.CHOCOLATE,
        subcategories=("BAR", "CONFECTIONERY"),
        storage_requirement_modes=(
            StorageRequirementMode.AMBIENT_ALLOWED,
            StorageRequirementMode.COLD_REQUIRED_FOR_QUALITY_WINDOW,
        ),
        package_formats=("BAR", "PACK", "BOX"),
    ),
)


PRODUCT_PROFILE_BY_CATEGORY: dict[
    ProductCategory,
    ProductSamplingProfile,
] = {
    profile.category: profile
    for profile in PRODUCT_PROFILES
}


__all__ = [
    "ACTION_DESTINATION_TYPES",
    "MODEL_SCORED_ACTIONS",
    "PRODUCT_PROFILES",
    "PRODUCT_PROFILE_BY_CATEGORY",
    "ProductSamplingProfile",
]
