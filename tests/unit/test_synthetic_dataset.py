"""Tests for in-memory synthetic dataset assembly."""

from pathlib import Path

from afterlife_ai.synthetic.config import (
    load_synthetic_dataset_config,
)
from afterlife_ai.synthetic.dataset import (
    assemble_synthetic_dataset,
    generate_synthetic_dataset,
)
from afterlife_ai.synthetic.outcome import load_outcome_recipe
from afterlife_ai.synthetic.scenarios import (
    generate_scenario_candidates,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")
SCHEMA_PATH = Path("docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml")
RECIPE_PATH = Path("configs/synthetic_outcome_v1.yaml")


def test_small_bundle_has_aligned_candidate_and_oracle_rows() -> None:
    contract = load_model_feature_contract(SCHEMA_PATH)
    recipe = load_outcome_recipe(RECIPE_PATH)

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=10,
        candidates_per_group_min=2,
        candidates_per_group_max=4,
        contract=contract,
    )

    bundle = assemble_synthetic_dataset(
        candidates,
        outcome_seed=1_000_045,
        recipe=recipe,
        contract=contract,
    )

    assert bundle.row_count == len(candidates)
    assert len(bundle.candidate_rows) == len(bundle.oracle_rows)

    for candidate_row, oracle_row in zip(
        bundle.candidate_rows,
        bundle.oracle_rows,
        strict=True,
    ):
        assert candidate_row.candidate_id == oracle_row.candidate_id
        assert (
            candidate_row.scenario_group_id
            == oracle_row.scenario_group_id
        )


def test_oracle_probability_never_enters_training_record() -> None:
    contract = load_model_feature_contract(SCHEMA_PATH)
    recipe = load_outcome_recipe(RECIPE_PATH)

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=3,
        candidates_per_group_min=2,
        candidates_per_group_max=3,
        contract=contract,
    )

    bundle = assemble_synthetic_dataset(
        candidates,
        outcome_seed=1_000_045,
        recipe=recipe,
        contract=contract,
    )

    for row in bundle.candidate_rows:
        record = row.to_training_record(contract)

        assert "generator_success_probability" not in record
        assert "estimated_rescue_success_score" not in record


def test_binary_target_is_binary() -> None:
    contract = load_model_feature_contract(SCHEMA_PATH)
    recipe = load_outcome_recipe(RECIPE_PATH)

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=50,
        candidates_per_group_min=2,
        candidates_per_group_max=8,
        contract=contract,
    )

    bundle = assemble_synthetic_dataset(
        candidates,
        outcome_seed=1_000_045,
        recipe=recipe,
        contract=contract,
    )

    targets = {
        row.simulated_rescue_outcome
        for row in bundle.candidate_rows
    }

    assert targets <= {0, 1}
    assert targets


def test_bundle_is_deterministic_for_same_inputs() -> None:
    contract = load_model_feature_contract(SCHEMA_PATH)
    recipe = load_outcome_recipe(RECIPE_PATH)

    candidates = generate_scenario_candidates(
        seed=42,
        scenario_groups=20,
        candidates_per_group_min=2,
        candidates_per_group_max=5,
        contract=contract,
    )

    first = assemble_synthetic_dataset(
        candidates,
        outcome_seed=1_000_045,
        recipe=recipe,
        contract=contract,
    )
    second = assemble_synthetic_dataset(
        candidates,
        outcome_seed=1_000_045,
        recipe=recipe,
        contract=contract,
    )

    assert first == second


def test_production_configuration_meets_dataset_size_contract() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    contract = load_model_feature_contract(SCHEMA_PATH)
    recipe = load_outcome_recipe(RECIPE_PATH)

    bundle = generate_synthetic_dataset(
        config=config,
        recipe=recipe,
        contract=contract,
    )

    assert bundle.scenario_group_count == 2400
    assert 10_000 <= bundle.row_count <= 15_000
    assert 0.0 < bundle.positive_rate < 1.0


def test_production_generation_is_deterministic() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)
    contract = load_model_feature_contract(SCHEMA_PATH)
    recipe = load_outcome_recipe(RECIPE_PATH)

    first = generate_synthetic_dataset(
        config=config,
        recipe=recipe,
        contract=contract,
    )
    second = generate_synthetic_dataset(
        config=config,
        recipe=recipe,
        contract=contract,
    )

    assert first == second
