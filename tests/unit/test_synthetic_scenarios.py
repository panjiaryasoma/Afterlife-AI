"""Tests for deterministic synthetic scenario feature generation."""

from pathlib import Path

import pytest

from afterlife_ai.synthetic.scenarios import (
    generate_scenario_candidates,
)
from afterlife_ai.synthetic.schema_contract import (
    ModelFeatureContract,
    load_model_feature_contract,
)

SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")


def _contract() -> ModelFeatureContract:
    return load_model_feature_contract(SCHEMA_PATH)


def test_generator_is_deterministic_for_same_seed() -> None:
    contract = _contract()

    first = generate_scenario_candidates(
        seed=42,
        scenario_groups=5,
        candidates_per_group_min=2,
        candidates_per_group_max=4,
        contract=contract,
    )
    second = generate_scenario_candidates(
        seed=42,
        scenario_groups=5,
        candidates_per_group_min=2,
        candidates_per_group_max=4,
        contract=contract,
    )

    assert first == second


def test_different_seed_changes_generated_scenarios() -> None:
    contract = _contract()

    first = generate_scenario_candidates(
        seed=42,
        scenario_groups=5,
        candidates_per_group_min=2,
        candidates_per_group_max=4,
        contract=contract,
    )
    second = generate_scenario_candidates(
        seed=137,
        scenario_groups=5,
        candidates_per_group_min=2,
        candidates_per_group_max=4,
        contract=contract,
    )

    assert first != second


def test_each_candidate_has_exact_schema_feature_set() -> None:
    contract = _contract()

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=10,
        candidates_per_group_min=2,
        candidates_per_group_max=5,
        contract=contract,
    )

    for candidate in candidates:
        assert set(candidate.feature_values) == set(
            contract.model_features
        )


def test_each_group_has_candidate_count_within_bounds() -> None:
    contract = _contract()

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=20,
        candidates_per_group_min=2,
        candidates_per_group_max=6,
        contract=contract,
    )

    counts: dict[str, int] = {}

    for candidate in candidates:
        counts[candidate.scenario_group_id] = (
            counts.get(candidate.scenario_group_id, 0) + 1
        )

    assert len(counts) == 20
    assert all(2 <= count <= 6 for count in counts.values())


def test_candidate_ids_are_unique() -> None:
    contract = _contract()

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=50,
        candidates_per_group_min=2,
        candidates_per_group_max=8,
        contract=contract,
    )

    ids = [candidate.candidate_id for candidate in candidates]

    assert len(ids) == len(set(ids))


def test_safe_disposal_is_never_generated_for_model_scoring() -> None:
    contract = _contract()

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=100,
        candidates_per_group_min=2,
        candidates_per_group_max=8,
        contract=contract,
    )

    actions = {
        candidate.feature_values["action_type"]
        for candidate in candidates
    }

    assert "SAFE_DISPOSAL" not in actions


def test_generated_candidates_satisfy_model_eligibility_invariants() -> None:
    contract = _contract()

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=200,
        candidates_per_group_min=2,
        candidates_per_group_max=8,
        contract=contract,
    )

    for candidate in candidates:
        features = candidate.feature_values

        planning_quantity = float(
            features["planning_quantity"]
        )
        demand_quantity = float(
            features["active_demand_quantity"]
        )
        available_capacity = float(
            features["available_capacity"]
        )

        assert (
            float(features["remaining_safe_window_hours"])
            <= float(features["remaining_shelf_life_days"]) * 24.0
        )

        assert (
            float(features["estimated_completion_hours"])
            <= float(features["remaining_safe_window_hours"])
        )

        assert (
            float(features["estimated_completion_hours"])
            <= float(
                features["remaining_commercial_window_days"]
            )
            * 24.0
        )

        allocatable_quantity = min(
            planning_quantity,
            demand_quantity,
            available_capacity,
        )

        assert (
            float(features["minimum_order_quantity"])
            <= allocatable_quantity
        )

        assert float(
            features["capability_resource_ratio"]
        ) == pytest.approx(
            available_capacity / planning_quantity,
            abs=0.0001,
        )

        assert float(
            features["demand_coverage_ratio"]
        ) == pytest.approx(
            demand_quantity / planning_quantity,
            abs=0.0001,
        )



@pytest.mark.parametrize(
    ("minimum", "maximum"),
    [
        (1, 4),
        (2, 9),
        (5, 4),
    ],
)
def test_invalid_candidate_bounds_are_rejected(
    minimum: int,
    maximum: int,
) -> None:
    contract = _contract()

    with pytest.raises(ValueError):
        generate_scenario_candidates(
            seed=42,
            scenario_groups=1,
            candidates_per_group_min=minimum,
            candidates_per_group_max=maximum,
            contract=contract,
        )
