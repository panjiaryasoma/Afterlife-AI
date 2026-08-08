"""Leakage-safe deterministic baseline scoring."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Self

import pandas as pd
import yaml
from pydantic import BaseModel, ConfigDict, model_validator


class B0RulePriorityConfig(BaseModel):
    """Fixed rule-priority baseline configuration."""

    model_config = ConfigDict(extra="forbid")

    baseline_id: Literal["B0"]
    description: str
    score_semantics: Literal["ORDINAL_PRIORITY_SCORE"]
    action_priority: list[str]

    @model_validator(mode="after")
    def validate_action_priority(self) -> Self:
        if not self.action_priority:
            raise ValueError("B0 action_priority tidak boleh kosong.")

        if len(self.action_priority) != len(set(self.action_priority)):
            raise ValueError("B0 action_priority tidak boleh duplikat.")

        return self


class B1ActionPriorConfig(BaseModel):
    """Train-only action-prior baseline configuration."""

    model_config = ConfigDict(extra="forbid")

    baseline_id: Literal["B1"]
    description: str
    score_semantics: Literal["TRAIN_ACTION_SUCCESS_RATE"]
    action_column: Literal["action_type"]
    target_column: Literal["simulated_rescue_outcome"]
    unseen_action_policy: Literal["GLOBAL_TRAIN_PRIOR"]


class SplitPolicyConfig(BaseModel):
    """Baseline-development split policy."""

    model_config = ConfigDict(extra="forbid")

    fit_split: Literal["train"]
    selection_split: Literal["validation"]
    test_access_allowed: Literal[False]


class BaselineConfig(BaseModel):
    """Top-level deterministic baseline configuration."""

    model_config = ConfigDict(extra="forbid")

    config_version: Literal["1.0.0"]
    b0_rule_priority: B0RulePriorityConfig
    b1_action_prior: B1ActionPriorConfig
    split_policy: SplitPolicyConfig


@dataclass(frozen=True)
class ActionPriorModel:
    """Action-level success priors fitted from training rows only."""

    global_prior: float
    action_priors: dict[str, float]
    training_rows: int


def load_baseline_config(path: Path) -> BaselineConfig:
    """Load baseline configuration."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Baseline config harus berupa YAML mapping.")

    return BaselineConfig.model_validate(payload)


def attach_split_assignments(
    candidate: pd.DataFrame,
    assignments: pd.DataFrame,
) -> pd.DataFrame:
    """Attach one group-level split assignment to every candidate row."""

    required_candidate = {
        "scenario_group_id",
        "candidate_id",
        "action_type",
        "simulated_rescue_outcome",
    }
    required_assignment = {
        "scenario_group_id",
        "split",
    }

    missing_candidate = required_candidate - set(candidate.columns)
    missing_assignment = required_assignment - set(assignments.columns)

    if missing_candidate:
        raise ValueError(
            "Candidate dataset kehilangan columns: "
            f"{sorted(missing_candidate)}"
        )

    if missing_assignment:
        raise ValueError(
            "Split assignments kehilangan columns: "
            f"{sorted(missing_assignment)}"
        )

    if assignments["scenario_group_id"].duplicated().any():
        raise ValueError(
            "Split assignments harus unik per scenario_group_id."
        )

    merged = candidate.merge(
        assignments[["scenario_group_id", "split"]],
        on="scenario_group_id",
        how="left",
        validate="many_to_one",
    )

    if merged["split"].isna().any():
        raise ValueError(
            "Sebagian candidate tidak memiliki split assignment."
        )

    return merged


def select_modeling_split(
    frame: pd.DataFrame,
    split: Literal["train", "validation"],
) -> pd.DataFrame:
    """Return an allowed modeling split.

    Test is intentionally absent from the accepted interface.
    """

    if split not in {"train", "validation"}:
        raise ValueError(
            "Hanya train dan validation yang boleh diakses "
            "selama model development."
        )

    selected = frame.loc[frame["split"] == split].copy()

    if selected.empty:
        raise ValueError(f"Split {split!r} kosong.")

    return selected.reset_index(drop=True)


def score_rule_priority(
    frame: pd.DataFrame,
    config: B0RulePriorityConfig,
) -> pd.DataFrame:
    """Assign fixed ordinal B0 scores from deterministic action order."""

    priority = {
        action: index
        for index, action in enumerate(
            config.action_priority,
            start=1,
        )
    }

    observed_actions = set(frame["action_type"].astype(str))
    unknown_actions = observed_actions - set(priority)

    if unknown_actions:
        raise ValueError(
            "B0 menemukan action tanpa configured priority: "
            f"{sorted(unknown_actions)}"
        )

    action_count = len(priority)

    scored = frame[
        [
            "scenario_group_id",
            "candidate_id",
            "action_type",
            "simulated_rescue_outcome",
        ]
    ].copy()

    scored["baseline_id"] = config.baseline_id

    scored["baseline_score"] = scored["action_type"].map(
        lambda action: (
            action_count - priority[str(action)] + 1
        )
        / action_count
    )

    scored["score_semantics"] = config.score_semantics

    return scored


def fit_action_prior(
    train: pd.DataFrame,
    config: B1ActionPriorConfig,
) -> ActionPriorModel:
    """Fit action success priors using training rows only."""

    if "split" in train.columns:
        observed_splits = set(train["split"].astype(str))

        if observed_splits != {"train"}:
            raise ValueError(
                "B1 action prior hanya boleh di-fit pada train split."
            )

    target = config.target_column
    action = config.action_column

    target_values = set(int(value) for value in train[target].unique())

    if not target_values <= {0, 1}:
        raise ValueError("B1 target harus binary 0/1.")

    global_prior = float(train[target].mean())

    grouped = train.groupby(
        action,
        sort=True,
    )[target].mean()

    action_priors = {
        str(action_name): float(prior)
        for action_name, prior in grouped.items()
    }

    return ActionPriorModel(
        global_prior=global_prior,
        action_priors=action_priors,
        training_rows=len(train),
    )


def score_action_prior(
    frame: pd.DataFrame,
    model: ActionPriorModel,
    config: B1ActionPriorConfig,
) -> pd.DataFrame:
    """Score candidates using train-only action success priors."""

    scored = frame[
        [
            "scenario_group_id",
            "candidate_id",
            "action_type",
            "simulated_rescue_outcome",
        ]
    ].copy()

    scored["baseline_id"] = config.baseline_id

    scored["baseline_score"] = (
        scored[config.action_column]
        .map(model.action_priors)
        .fillna(model.global_prior)
        .astype(float)
    )

    scored["score_semantics"] = config.score_semantics

    return scored


__all__ = [
    "ActionPriorModel",
    "BaselineConfig",
    "attach_split_assignments",
    "fit_action_prior",
    "load_baseline_config",
    "score_action_prior",
    "score_rule_priority",
    "select_modeling_split",
]
