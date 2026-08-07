"""Tests for the synthetic scenario sampling catalog."""

from afterlife_ai.contracts.enums import ActionType, ProductCategory
from afterlife_ai.synthetic.catalog import (
    ACTION_DESTINATION_TYPES,
    MODEL_SCORED_ACTIONS,
    PRODUCT_PROFILE_BY_CATEGORY,
    PRODUCT_PROFILES,
)


def test_safe_disposal_is_not_model_scored() -> None:
    assert ActionType.SAFE_DISPOSAL not in MODEL_SCORED_ACTIONS


def test_all_non_disposal_actions_have_destination_type() -> None:
    assert set(ACTION_DESTINATION_TYPES) == set(MODEL_SCORED_ACTIONS)


def test_product_profiles_are_unique() -> None:
    categories = [profile.category for profile in PRODUCT_PROFILES]

    assert len(categories) == len(set(categories))


def test_all_concrete_schema_categories_are_covered() -> None:
    concrete_categories = set(ProductCategory) - {
        ProductCategory.OTHER_SUPPORTED,
    }

    assert set(PRODUCT_PROFILE_BY_CATEGORY) == concrete_categories


def test_profiles_have_nonempty_sampling_values() -> None:
    for profile in PRODUCT_PROFILES:
        assert profile.subcategories
        assert profile.storage_requirement_modes
        assert profile.package_formats


def test_other_supported_is_not_sampled_implicitly() -> None:
    assert (
        ProductCategory.OTHER_SUPPORTED
        not in PRODUCT_PROFILE_BY_CATEGORY
    )
