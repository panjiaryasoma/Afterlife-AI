"""Assembly of synthetic candidates, oracle truth, and binary outcomes."""

from dataclasses import dataclass

import numpy as np

from afterlife_ai.synthetic.config import SyntheticDatasetConfig
from afterlife_ai.synthetic.outcome import (
    OutcomeRecipeConfig,
    sample_synthetic_outcome,
    synthetic_success_probability,
)
from afterlife_ai.synthetic.rows import (
    SyntheticCandidateRow,
    SyntheticOracleRow,
)
from afterlife_ai.synthetic.scenarios import (
    SyntheticScenarioCandidate,
    generate_scenario_candidates,
)
from afterlife_ai.synthetic.schema_contract import ModelFeatureContract

_OUTCOME_SEED_OFFSET = 1_000_003


@dataclass(frozen=True)
class SyntheticDatasetBundle:
    """One deterministic in-memory synthetic dataset."""

    candidate_rows: tuple[SyntheticCandidateRow, ...]
    oracle_rows: tuple[SyntheticOracleRow, ...]

    @property
    def row_count(self) -> int:
        return len(self.candidate_rows)

    @property
    def scenario_group_count(self) -> int:
        return len(
            {
                row.scenario_group_id
                for row in self.candidate_rows
            }
        )

    @property
    def positive_count(self) -> int:
        return sum(
            row.simulated_rescue_outcome
            for row in self.candidate_rows
        )

    @property
    def positive_rate(self) -> float:
        if not self.candidate_rows:
            return 0.0

        return self.positive_count / self.row_count


def assemble_synthetic_dataset(
    candidates: list[SyntheticScenarioCandidate],
    *,
    outcome_seed: int,
    recipe: OutcomeRecipeConfig,
    contract: ModelFeatureContract,
) -> SyntheticDatasetBundle:
    """Attach latent oracle probabilities and sampled binary outcomes."""

    rng = np.random.default_rng(outcome_seed)

    candidate_rows: list[SyntheticCandidateRow] = []
    oracle_rows: list[SyntheticOracleRow] = []

    seen_candidate_ids: set[str] = set()

    for candidate in candidates:
        if candidate.candidate_id in seen_candidate_ids:
            raise ValueError(
                "Duplicate synthetic candidate_id ditemukan: "
                f"{candidate.candidate_id}"
            )

        seen_candidate_ids.add(candidate.candidate_id)

        probability = synthetic_success_probability(
            candidate,
            recipe=recipe,
            contract=contract,
        )

        outcome = sample_synthetic_outcome(
            probability,
            rng=rng,
        )

        candidate_row = SyntheticCandidateRow(
            scenario_group_id=candidate.scenario_group_id,
            business_profile_id=candidate.business_profile_id,
            request_id=candidate.request_id,
            lot_id=candidate.lot_id,
            candidate_id=candidate.candidate_id,
            simulated_rescue_outcome=outcome,
            feature_values=dict(candidate.feature_values),
        )

        candidate_row.validate_against(contract)

        oracle_row = SyntheticOracleRow(
            scenario_group_id=candidate.scenario_group_id,
            business_profile_id=candidate.business_profile_id,
            request_id=candidate.request_id,
            lot_id=candidate.lot_id,
            candidate_id=candidate.candidate_id,
            generator_success_probability=probability,
        )

        candidate_rows.append(candidate_row)
        oracle_rows.append(oracle_row)

    bundle = SyntheticDatasetBundle(
        candidate_rows=tuple(candidate_rows),
        oracle_rows=tuple(oracle_rows),
    )

    _validate_bundle_alignment(bundle)

    return bundle


def generate_synthetic_dataset(
    *,
    config: SyntheticDatasetConfig,
    recipe: OutcomeRecipeConfig,
    contract: ModelFeatureContract,
) -> SyntheticDatasetBundle:
    """Generate the configured production synthetic dataset in memory."""

    candidates = generate_scenario_candidates(
        seed=config.randomness.primary_seed,
        scenario_groups=config.generation.scenario_groups,
        candidates_per_group_min=(
            config.generation.candidates_per_planning_lot_min
        ),
        candidates_per_group_max=(
            config.generation.candidates_per_planning_lot_max
        ),
        contract=contract,
    )

    bundle = assemble_synthetic_dataset(
        candidates,
        outcome_seed=(
            config.randomness.primary_seed
            + _OUTCOME_SEED_OFFSET
        ),
        recipe=recipe,
        contract=contract,
    )

    if bundle.scenario_group_count != config.generation.scenario_groups:
        raise RuntimeError(
            "Jumlah generated scenario groups tidak sesuai config."
        )

    if not (
        config.generation.candidate_rows_min
        <= bundle.row_count
        <= config.generation.candidate_rows_max
    ):
        raise RuntimeError(
            "Generated candidate row count berada di luar target: "
            f"{bundle.row_count} not in "
            f"[{config.generation.candidate_rows_min}, "
            f"{config.generation.candidate_rows_max}]"
        )

    return bundle


def _validate_bundle_alignment(
    bundle: SyntheticDatasetBundle,
) -> None:
    """Ensure candidate and oracle artifacts remain one-to-one aligned."""

    if len(bundle.candidate_rows) != len(bundle.oracle_rows):
        raise ValueError(
            "Candidate dan oracle row count harus identik."
        )

    candidate_ids = [
        row.candidate_id
        for row in bundle.candidate_rows
    ]
    oracle_ids = [
        row.candidate_id
        for row in bundle.oracle_rows
    ]

    if candidate_ids != oracle_ids:
        raise ValueError(
            "Candidate dan oracle rows harus memiliki alignment identik."
        )

    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError(
            "Synthetic dataset tidak boleh memiliki duplicate candidate_id."
        )


__all__ = [
    "SyntheticDatasetBundle",
    "assemble_synthetic_dataset",
    "generate_synthetic_dataset",
]
