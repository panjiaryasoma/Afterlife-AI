"""Tests for synthetic latent probability generation."""

from pathlib import Path

import numpy as np
import pytest

from afterlife_ai.synthetic.outcome import (
    load_outcome_recipe,
    sample_synthetic_outcome,
    synthetic_success_probability,
)
from afterlife_ai.synthetic.scenarios import (
    SyntheticScenarioCandidate,
    generate_scenario_candidates,
)
from afterlife_ai.synthetic.schema_contract import (
    ModelFeatureContract,
    load_model_feature_contract,
)

SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")
RECIPE_PATH = Path("configs/synthetic_outcome_v1.yaml")


def _contract() -> ModelFeatureContract:
    return load_model_feature_contract(SCHEMA_PATH)


def _candidate() -> SyntheticScenarioCandidate:
    contract = _contract()

    return generate_scenario_candidates(
        seed=42,
        scenario_groups=1,
        candidates_per_group_min=2,
        candidates_per_group_max=2,
        contract=contract,
    )[0]


def test_recipe_loads() -> None:
    recipe = load_outcome_recipe(RECIPE_PATH)

    assert recipe.recipe_version == "1.0.0"
    assert recipe.probability_bounds.minimum == pytest.approx(0.03)
    assert recipe.probability_bounds.maximum == pytest.approx(0.97)


def test_probability_is_deterministic() -> None:
    contract = _contract()
    recipe = load_outcome_recipe(RECIPE_PATH)
    candidate = _candidate()

    first = synthetic_success_probability(
        candidate,
        recipe=recipe,
        contract=contract,
    )
    second = synthetic_success_probability(
        candidate,
        recipe=recipe,
        contract=contract,
    )

    assert first == pytest.approx(second)


def test_probability_respects_configured_bounds() -> None:
    contract = _contract()
    recipe = load_outcome_recipe(RECIPE_PATH)

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=100,
        candidates_per_group_min=2,
        candidates_per_group_max=8,
        contract=contract,
    )

    probabilities = [
        synthetic_success_probability(
            candidate,
            recipe=recipe,
            contract=contract,
        )
        for candidate in candidates
    ]

    assert min(probabilities) >= recipe.probability_bounds.minimum
    assert max(probabilities) <= recipe.probability_bounds.maximum


def test_probability_does_not_modify_candidate() -> None:
    contract = _contract()
    recipe = load_outcome_recipe(RECIPE_PATH)
    candidate = _candidate()

    before = dict(candidate.feature_values)

    synthetic_success_probability(
        candidate,
        recipe=recipe,
        contract=contract,
    )

    assert candidate.feature_values == before


def test_outcome_sampling_is_deterministic_for_same_rng_seed() -> None:
    first_rng = np.random.default_rng(42)
    second_rng = np.random.default_rng(42)

    first = [
        sample_synthetic_outcome(0.55, rng=first_rng)
        for _ in range(100)
    ]
    second = [
        sample_synthetic_outcome(0.55, rng=second_rng)
        for _ in range(100)
    ]

    assert first == second


def test_outcome_sampling_approximately_tracks_probability() -> None:
    rng = np.random.default_rng(42)

    outcomes = [
        sample_synthetic_outcome(0.70, rng=rng)
        for _ in range(10_000)
    ]

    observed = sum(outcomes) / len(outcomes)

    assert observed == pytest.approx(0.70, abs=0.02)


@pytest.mark.parametrize("probability", [-0.01, 1.01])
def test_invalid_probability_is_rejected(probability: float) -> None:
    rng = np.random.default_rng(42)

    with pytest.raises(ValueError):
        sample_synthetic_outcome(
            probability,
            rng=rng,
        )
