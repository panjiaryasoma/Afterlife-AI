"""Synthetic latent rescue-success probability and outcome sampling."""

from math import exp, log1p
from pathlib import Path
from typing import Literal, Self

import numpy as np
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from afterlife_ai.synthetic.scenarios import SyntheticScenarioCandidate
from afterlife_ai.synthetic.schema_contract import ModelFeatureContract


class ProbabilityBounds(BaseModel):
    """Bounds preventing degenerate synthetic probabilities."""

    model_config = ConfigDict(extra="forbid")

    minimum: float = Field(gt=0.0, lt=1.0)
    maximum: float = Field(gt=0.0, lt=1.0)

    @model_validator(mode="after")
    def validate_order(self) -> Self:
        if self.maximum <= self.minimum:
            raise ValueError(
                "maximum probability harus lebih besar dari minimum."
            )

        return self


class OutcomeRecipeConfig(BaseModel):
    """Versioned synthetic latent-probability recipe."""

    model_config = ConfigDict(extra="forbid")

    recipe_version: str
    claim_boundary: str
    intercept: float
    weights: dict[str, float]
    action_offsets: dict[str, float]
    nonlinear: dict[str, float]
    probability_bounds: ProbabilityBounds


def load_outcome_recipe(path: Path) -> OutcomeRecipeConfig:
    """Load one synthetic outcome recipe."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Outcome recipe harus berupa YAML mapping.")

    return OutcomeRecipeConfig.model_validate(payload)


def _numeric(
    candidate: SyntheticScenarioCandidate,
    field: str,
) -> float:
    value = candidate.feature_values[field]

    if value is None:
        return 0.0

    if not isinstance(value, (int, float)):
        raise TypeError(
            f"Feature {field!r} harus numeric, mendapat {type(value).__name__}."
        )

    return float(value)


def _categorical(
    candidate: SyntheticScenarioCandidate,
    field: str,
) -> str:
    value = candidate.feature_values[field]

    if not isinstance(value, str):
        raise TypeError(
            f"Feature {field!r} harus string, mendapat {type(value).__name__}."
        )

    return value


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + exp(-value))

    exponent = exp(value)
    return exponent / (1.0 + exponent)


def synthetic_success_probability(
    candidate: SyntheticScenarioCandidate,
    *,
    recipe: OutcomeRecipeConfig,
    contract: ModelFeatureContract,
) -> float:
    """Calculate generator-only latent synthetic rescue probability."""

    actual = set(candidate.feature_values)
    expected = set(contract.model_features)

    if actual != expected:
        raise ValueError(
            "Candidate feature set tidak sesuai model feature contract."
        )

    forbidden_overlap = actual & set(contract.forbidden_model_inputs)

    if forbidden_overlap:
        raise ValueError(
            "Outcome generator menerima forbidden model inputs: "
            f"{sorted(forbidden_overlap)}"
        )

    normal_price = max(
        _numeric(candidate, "normal_selling_price"),
        1.0,
    )
    offered_price = _numeric(
        candidate,
        "offered_or_selling_price_per_unit",
    )
    unit_cost = max(_numeric(candidate, "unit_cost"), 1.0)

    price_recovery_ratio = offered_price / normal_price

    shelf_life_days = max(
        _numeric(candidate, "remaining_shelf_life_days"),
        0.0,
    )
    shelf_life_log = log1p(shelf_life_days) / log1p(365.0)

    demand_quantity = max(
        _numeric(candidate, "active_demand_quantity"),
        0.0,
    )
    planning_quantity = max(
        _numeric(candidate, "planning_quantity"),
        1.0,
    )
    demand_fit = min(demand_quantity / planning_quantity, 2.0) / 2.0

    capability_fit = min(
        max(
            _numeric(candidate, "capability_resource_ratio"),
            0.0,
        ),
        1.5,
    ) / 1.5

    completion_hours = max(
        _numeric(candidate, "estimated_completion_hours"),
        0.0,
    )
    safe_window_hours = max(
        _numeric(candidate, "remaining_safe_window_hours"),
        1.0,
    )
    completion_pressure = min(
        completion_hours / safe_window_hours,
        3.0,
    ) / 3.0

    logistics_cost = max(
        _numeric(candidate, "logistics_cost"),
        0.0,
    )
    logistics_pressure = min(
        logistics_cost / max(unit_cost * planning_quantity, 1.0),
        2.0,
    ) / 2.0

    distance_km = max(
        _numeric(candidate, "distance_km"),
        0.0,
    )
    distance_log = log1p(distance_km) / log1p(40.0)

    urgency = _categorical(candidate, "urgency_level")
    seasonality = _categorical(candidate, "seasonality_status")
    action = _categorical(candidate, "action_type")
    storage_mode = _categorical(
        candidate,
        "storage_requirement_mode",
    )

    weights = recipe.weights

    score = recipe.intercept
    score += weights["price_recovery_ratio"] * price_recovery_ratio
    score += weights["shelf_life_log"] * shelf_life_log
    score += weights["demand_fit"] * demand_fit
    score += weights["capability_fit"] * capability_fit
    score += weights["completion_pressure"] * completion_pressure
    score += weights["logistics_pressure"] * logistics_pressure
    score += weights["distance_log"] * distance_log

    if urgency == "HIGH":
        score += weights["urgency_high"]
    elif urgency == "CRITICAL":
        score += weights["urgency_critical"]

    if seasonality == "POST_SEASON":
        score += weights["post_season"]

    score += recipe.action_offsets.get(action, 0.0)

    nonlinear = recipe.nonlinear

    if demand_fit >= 0.80 and capability_fit >= 0.65:
        score += nonlinear["strong_demand_bonus"]

    if demand_fit <= 0.30:
        score += nonlinear["weak_demand_penalty"]

    if (
        urgency in {"HIGH", "CRITICAL"}
        and completion_pressure >= 0.60
    ):
        score += nonlinear["urgent_short_window_penalty"]

    if (
        distance_km >= 20.0
        and storage_mode
        in {
            "COLD_REQUIRED_FOR_QUALITY_WINDOW",
            "SAFETY_CRITICAL_COLD_CHAIN",
        }
    ):
        score += nonlinear["long_distance_fragile_penalty"]

    probability = _sigmoid(score)

    return min(
        recipe.probability_bounds.maximum,
        max(recipe.probability_bounds.minimum, probability),
    )


def sample_synthetic_outcome(
    probability: float,
    *,
    rng: np.random.Generator,
) -> Literal[0, 1]:
    """Sample one binary synthetic outcome from latent probability."""

    if not 0.0 <= probability <= 1.0:
        raise ValueError("Probability harus berada pada interval [0, 1].")

    return 1 if float(rng.random()) < probability else 0


__all__ = [
    "OutcomeRecipeConfig",
    "load_outcome_recipe",
    "sample_synthetic_outcome",
    "synthetic_success_probability",
]
