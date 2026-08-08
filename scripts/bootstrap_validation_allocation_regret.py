"""Paired group bootstrap for validation allocation regret."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd
from numpy.typing import NDArray

INPUT_PATH = Path(
    "reports/evidence/modeling/"
    "VALIDATION_ALLOCATION_REGRET_v1.csv"
)

OUTPUT_PATH = Path(
    "reports/evidence/modeling/"
    "VALIDATION_ALLOCATION_REGRET_BOOTSTRAP_v1.json"
)

BOOTSTRAP_ITERATIONS = 10000
BOOTSTRAP_SEED = 42

FloatArray = NDArray[np.float64]


class BootstrapResult(TypedDict):
    """Typed result for one paired bootstrap comparison."""

    delta_definition: str
    observed_delta: float
    ci_95_low: float
    ci_95_high: float
    probability_first_lower_regret: float
    probability_second_lower_regret: float


def bootstrap_delta(
    first: FloatArray,
    second: FloatArray,
    *,
    rng: np.random.Generator,
) -> BootstrapResult:
    """Bootstrap paired mean-regret difference first - second."""

    if len(first) != len(second):
        raise ValueError(
            "Paired arrays harus memiliki panjang sama."
        )

    observed = float(
        np.mean(first - second)
    )

    n_groups = len(first)

    estimates = np.empty(
        BOOTSTRAP_ITERATIONS,
        dtype=float,
    )

    for iteration in range(
        BOOTSTRAP_ITERATIONS
    ):
        indices = rng.integers(
            0,
            n_groups,
            size=n_groups,
        )

        estimates[iteration] = float(
            np.mean(
                first[indices]
                - second[indices]
            )
        )

    quantiles = np.asarray(
        np.quantile(
            estimates,
            [0.025, 0.975],
        ),
        dtype=np.float64,
    )

    ci_low = float(quantiles[0])
    ci_high = float(quantiles[1])

    return {
        "delta_definition": (
            "first_model_minus_second_model"
        ),
        "observed_delta": observed,
        "ci_95_low": ci_low,
        "ci_95_high": ci_high,
        "probability_first_lower_regret": float(
            np.mean(estimates < 0)
        ),
        "probability_second_lower_regret": float(
            np.mean(estimates > 0)
        ),
    }


def original_pair_context(
    first: FloatArray,
    second: FloatArray,
) -> dict[str, float | int]:
    """Describe paired group-level comparison before bootstrapping."""

    delta = first - second

    return {
        "first_lower_regret_groups": int(
            np.sum(delta < 0)
        ),
        "equal_regret_groups": int(
            np.sum(delta == 0)
        ),
        "second_lower_regret_groups": int(
            np.sum(delta > 0)
        ),
        "mean_delta": float(
            np.mean(delta)
        ),
        "median_delta": float(
            np.median(delta)
        ),
    }


def main() -> None:
    """Run paired scenario-group bootstrap."""

    df = pd.read_csv(INPUT_PATH)

    required = {
        "scenario_group_id",
        "model",
        "regret",
        "normalized_regret",
    }

    missing = required - set(df.columns)

    if missing:
        raise RuntimeError(
            f"Missing columns: {sorted(missing)}"
        )

    if df["scenario_group_id"].nunique() != 360:
        raise RuntimeError(
            "Expected exactly 360 validation groups."
        )

    regret = df.pivot(
        index="scenario_group_id",
        columns="model",
        values="regret",
    )

    normalized = df.pivot(
        index="scenario_group_id",
        columns="model",
        values="normalized_regret",
    )

    expected_models = {
        "LR",
        "HGB_B",
        "HGB_E",
    }

    if set(regret.columns) != expected_models:
        raise RuntimeError(
            "Unexpected model set: "
            f"{list(regret.columns)}"
        )

    if regret.isna().any().any():
        raise RuntimeError(
            "Incomplete paired regret matrix."
        )

    if normalized.isna().any().any():
        raise RuntimeError(
            "Incomplete normalized-regret matrix."
        )

    rng = np.random.default_rng(
        BOOTSTRAP_SEED
    )

    pairs = [
        ("LR", "HGB_B"),
        ("LR", "HGB_E"),
        ("HGB_B", "HGB_E"),
    ]

    result: dict[str, object] = {
        "evaluation_version": "1.0.0",
        "split": "validation",
        "test_accessed": False,
        "bootstrap_unit": "scenario_group_id",
        "bootstrap_iterations": (
            BOOTSTRAP_ITERATIONS
        ),
        "bootstrap_seed": BOOTSTRAP_SEED,
        "mean_regret_comparisons": {},
        "mean_normalized_regret_comparisons": {},
    }

    regret_output = result[
        "mean_regret_comparisons"
    ]

    normalized_output = result[
        "mean_normalized_regret_comparisons"
    ]

    assert isinstance(
        regret_output,
        dict,
    )

    assert isinstance(
        normalized_output,
        dict,
    )

    print(
        "=== VALIDATION ALLOCATION "
        "REGRET BOOTSTRAP ==="
    )
    print(
        f"Groups     : {len(regret)}"
    )
    print(
        f"Iterations : {BOOTSTRAP_ITERATIONS}"
    )
    print(
        f"Seed       : {BOOTSTRAP_SEED}"
    )

    for first_name, second_name in pairs:
        key = (
            f"{first_name}_vs_{second_name}"
        )

        first_regret: FloatArray = np.asarray(
            regret[first_name].to_numpy(),
            dtype=np.float64,
        )

        second_regret: FloatArray = np.asarray(
            regret[second_name].to_numpy(),
            dtype=np.float64,
        )

        first_normalized: FloatArray = np.asarray(
            normalized[first_name].to_numpy(),
            dtype=np.float64,
        )

        second_normalized: FloatArray = np.asarray(
            normalized[second_name].to_numpy(),
            dtype=np.float64,
        )

        paired_context = (
            original_pair_context(
                first_regret,
                second_regret,
            )
        )

        regret_result = bootstrap_delta(
            first_regret,
            second_regret,
            rng=rng,
        )

        normalized_result = bootstrap_delta(
            first_normalized,
            second_normalized,
            rng=rng,
        )

        regret_output[key] = {
            "paired_group_context": (
                paired_context
            ),
            **regret_result,
        }

        normalized_output[key] = (
            normalized_result
        )

        print()
        print(
            f"--- {first_name} "
            f"vs {second_name} ---"
        )
        print(
            "Mean regret delta "
            f"({first_name}-{second_name}): "
            f"{regret_result['observed_delta']:.2f}"
        )
        print(
            "95% CI: "
            f"[{regret_result['ci_95_low']:.2f}, "
            f"{regret_result['ci_95_high']:.2f}]"
        )
        print(
            f"P({first_name} lower regret): "
            f"{regret_result['probability_first_lower_regret']:.2%}"
        )
        print(
            "Original groups: "
            f"{paired_context['first_lower_regret_groups']} "
            f"{first_name} better / "
            f"{paired_context['equal_regret_groups']} equal / "
            f"{paired_context['second_lower_regret_groups']} "
            f"{second_name} better"
        )

        print(
            "Normalized delta: "
            f"{normalized_result['observed_delta']:.6f}"
        )
        print(
            "Normalized 95% CI: "
            f"[{normalized_result['ci_95_low']:.6f}, "
            f"{normalized_result['ci_95_high']:.6f}]"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Evidence: {OUTPUT_PATH}")
    print("Test accessed: False")


if __name__ == "__main__":
    main()
