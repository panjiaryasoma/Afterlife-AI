"""Tests for the synthetic dataset configuration contract."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from afterlife_ai.synthetic.config import load_synthetic_dataset_config

CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")


def test_production_synthetic_config_loads() -> None:
    config = load_synthetic_dataset_config(CONFIG_PATH)

    assert config.feature_schema.version == "2.0.0"
    assert config.target.field == "simulated_rescue_outcome"
    assert (
        config.target.latent_oracle_field
        == "generator_success_probability"
    )
    assert config.randomness.primary_seed == 42
    assert config.randomness.robustness_seeds == [42, 137, 2026]
    assert config.generation.scenario_groups == 2400
    assert config.split.unit == "scenario_group_id"
    assert config.split.random_row_split_allowed is False
    assert config.split.train == pytest.approx(0.70)
    assert config.split.validation == pytest.approx(0.15)
    assert config.split.test == pytest.approx(0.15)


def test_invalid_split_total_is_rejected(tmp_path: Path) -> None:
    payload = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    payload["split"]["train"] = 0.80

    invalid_path = tmp_path / "invalid.yaml"
    invalid_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="berjumlah 1.0"):
        load_synthetic_dataset_config(invalid_path)


def test_primary_seed_must_be_in_robustness_seeds(
    tmp_path: Path,
) -> None:
    payload = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    payload["randomness"]["primary_seed"] = 99

    invalid_path = tmp_path / "invalid-seed.yaml"
    invalid_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )

    with pytest.raises(
        ValidationError,
        match="primary_seed harus termasuk",
    ):
        load_synthetic_dataset_config(invalid_path)


def test_candidate_row_range_must_be_ordered(
    tmp_path: Path,
) -> None:
    payload = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    payload["generation"]["candidate_rows_min"] = 16000

    invalid_path = tmp_path / "invalid-range.yaml"
    invalid_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )

    with pytest.raises(
        ValidationError,
        match="candidate_rows_max tidak boleh",
    ):
        load_synthetic_dataset_config(invalid_path)
