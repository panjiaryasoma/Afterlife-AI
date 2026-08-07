from decimal import Decimal

from afterlife_ai.contracts.enums import (
    ActionType,
    DefectSeverity,
    ProductCategory,
    StorageHistoryStatus,
    StorageRequirementMode,
    StorageType,
    SurplusSource,
    UnitCode,
    UrgencyLevel,
    VerificationStatus,
)
from afterlife_ai.contracts.planning import SurplusPlanningLot
from afterlife_ai.planner.candidates import (
    CandidateActionSpec,
    generate_candidates,
)


def build_planning_lot() -> SurplusPlanningLot:
    return SurplusPlanningLot(
        planning_lot_id="PLAN-LOT-003",
        source_lot_id="LOT-003",
        sku="PBEV-003",
        product_name="Minuman Serbuk Rasa Mangga",
        product_category=ProductCategory.PACKAGED_BEVERAGE,
        product_subcategory=None,
        planning_quantity=Decimal("10"),
        unit=UnitCode.SACHET,
        unit_cost=Decimal("1500"),
        normal_selling_price=Decimal("2000"),
        minimum_recovery_price=Decimal("1000"),
        source_location="Toko Utama",
        remaining_shelf_life_days=146,
        remaining_safe_window_hours=None,
        remaining_commercial_window_days=None,
        urgency_level=UrgencyLevel.MEDIUM,
        surplus_source=SurplusSource.CALCULATED,
        seasonality_status=None,
        storage_type=StorageType.DRY_AMBIENT,
        storage_requirement_mode=StorageRequirementMode.AMBIENT_ALLOWED,
        storage_history_status=StorageHistoryStatus.NOT_APPLICABLE,
        product_condition=None,
        packaging_condition=None,
        defect_severity=DefectSeverity.NONE,
        quality_inspection_status=None,
        verification_status=VerificationStatus.VERIFIED,
        package_volume_ml=None,
        package_weight_g=Decimal("10"),
        package_format="SACHET",
        estimated_current_value=Decimal("15000"),
    )


def build_action_specs() -> list[CandidateActionSpec]:
    return [
        CandidateActionSpec(
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity=Decimal("10"),
            offered_or_selling_price_per_unit=Decimal("1500"),
        ),
        CandidateActionSpec(
            action_type=ActionType.BUNDLE,
            maximum_quantity=Decimal("4"),
            offered_or_selling_price_per_unit=Decimal("1600"),
        ),
        CandidateActionSpec(
            action_type=ActionType.INTERNAL_REPURPOSE,
            maximum_quantity=Decimal("6"),
            offered_or_selling_price_per_unit=Decimal("2400"),
        ),
    ]


def test_generator_creates_only_supplied_actions() -> None:
    candidates = generate_candidates(
        build_planning_lot(),
        build_action_specs(),
    )

    assert [candidate.action_type for candidate in candidates] == [
        ActionType.INTERNAL_REPURPOSE,
        ActionType.BUNDLE,
        ActionType.LOCAL_DISCOUNT,
    ]

    assert ActionType.EXTERNAL_PARTNER not in {
        candidate.action_type for candidate in candidates
    }
    assert ActionType.DONATION not in {
        candidate.action_type for candidate in candidates
    }


def test_generator_caps_quantity_by_action_and_planning_quantity() -> None:
    candidates = generate_candidates(
        build_planning_lot(),
        build_action_specs(),
    )

    quantities = {
        candidate.action_type: candidate.maximum_feasible_quantity
        for candidate in candidates
    }

    assert quantities[ActionType.INTERNAL_REPURPOSE] == Decimal("6")
    assert quantities[ActionType.BUNDLE] == Decimal("4")
    assert quantities[ActionType.LOCAL_DISCOUNT] == Decimal("10")


def test_generator_uses_deterministic_candidate_ids() -> None:
    candidates = generate_candidates(
        build_planning_lot(),
        build_action_specs(),
    )

    assert [candidate.candidate_id for candidate in candidates] == [
        "CAND-003-REPURPOSE",
        "CAND-003-BUNDLE",
        "CAND-003-DISCOUNT",
    ]


def test_generator_is_deterministic_across_reruns() -> None:
    first = generate_candidates(
        build_planning_lot(),
        build_action_specs(),
    )
    second = generate_candidates(
        build_planning_lot(),
        list(reversed(build_action_specs())),
    )

    assert first == second


def test_generator_skips_zero_capacity_action() -> None:
    specs = build_action_specs() + [
        CandidateActionSpec(
            action_type=ActionType.PROMOTIONAL_BONUS,
            maximum_quantity=Decimal("0"),
        )
    ]

    candidates = generate_candidates(
        build_planning_lot(),
        specs,
    )

    assert ActionType.PROMOTIONAL_BONUS not in {
        candidate.action_type for candidate in candidates
    }


def test_generator_never_exceeds_planning_quantity() -> None:
    specs = [
        CandidateActionSpec(
            action_type=ActionType.LOCAL_DISCOUNT,
            maximum_quantity=Decimal("999"),
        )
    ]

    candidates = generate_candidates(
        build_planning_lot(),
        specs,
    )

    assert candidates[0].maximum_feasible_quantity == Decimal("10")
