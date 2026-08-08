"""Quality audit for generated synthetic rescue datasets."""

import json
from pathlib import Path

import pandas as pd

from afterlife_ai.contracts.enums import (
    BusinessType,
    SeasonalityStatus,
    StorageRequirementMode,
    SurplusSource,
    UrgencyLevel,
)
from afterlife_ai.synthetic.catalog import (
    ACTION_DESTINATION_TYPES,
    MODEL_SCORED_ACTIONS,
    PRODUCT_PROFILES,
)
from afterlife_ai.synthetic.config import SyntheticDatasetConfig
from afterlife_ai.synthetic.schema_contract import ModelFeatureContract

_LOCAL_ACTIONS = {
    "LOCAL_DISCOUNT",
    "BUNDLE",
    "PROMOTIONAL_BONUS",
    "INTERNAL_REPURPOSE",
    "INTERNAL_USE",
}


def _category_counts(
    frame: pd.DataFrame,
    column: str,
) -> dict[str, int]:
    counts = frame[column].value_counts(dropna=False)

    return {
        str(key): int(value)
        for key, value in counts.items()
    }


def _numeric_summary(
    frame: pd.DataFrame,
    column: str,
) -> dict[str, float]:
    series = frame[column]

    return {
        "min": float(series.min()),
        "max": float(series.max()),
        "mean": float(series.mean()),
        "std": float(series.std(ddof=0)),
    }


def _invalid_category_count(
    frame: pd.DataFrame,
    column: str,
    allowed: set[str],
) -> int:
    return int((~frame[column].isin(allowed)).sum())


def audit_synthetic_dataset(
    *,
    candidate_path: Path,
    oracle_path: Path,
    config: SyntheticDatasetConfig,
    contract: ModelFeatureContract,
) -> dict[str, object]:
    """Audit one generated candidate/oracle dataset pair."""

    candidate = pd.read_csv(candidate_path)
    oracle = pd.read_csv(oracle_path)

    errors: list[str] = []
    warnings: list[str] = []

    row_count = len(candidate)
    oracle_row_count = len(oracle)
    scenario_group_count = int(
        candidate["scenario_group_id"].nunique()
    )

    duplicate_rows = int(candidate.duplicated().sum())
    duplicate_candidate_ids = int(
        candidate["candidate_id"].duplicated().sum()
    )
    missing_cells = int(candidate.isna().sum().sum())

    candidate_oracle_aligned = bool(
        candidate["candidate_id"].tolist()
        == oracle["candidate_id"].tolist()
    )

    forbidden_present = sorted(
        set(candidate.columns)
        & set(contract.forbidden_model_inputs)
        - {
            contract.canonical_target,
            *contract.group_split_fields,
            "business_profile_id",
            "request_id",
            "lot_id",
            "candidate_id",
            "source_type",
        }
    )

    if not (
        config.generation.candidate_rows_min
        <= row_count
        <= config.generation.candidate_rows_max
    ):
        errors.append("candidate row count berada di luar configured target")

    if scenario_group_count != config.generation.scenario_groups:
        errors.append("scenario group count tidak sesuai configuration")

    if row_count != oracle_row_count:
        errors.append("candidate dan oracle row count berbeda")

    if duplicate_rows:
        errors.append("duplicate candidate records ditemukan")

    if duplicate_candidate_ids:
        errors.append("duplicate candidate_id ditemukan")

    if missing_cells:
        errors.append("missing candidate feature values ditemukan")

    if not candidate_oracle_aligned:
        errors.append("candidate dan oracle artifacts tidak aligned")

    if forbidden_present:
        errors.append(
            "forbidden estimator inputs ditemukan pada candidate artifact"
        )

    target_values = set(
        int(value)
        for value in candidate[contract.canonical_target].unique()
    )

    if not target_values <= {0, 1}:
        errors.append("target mengandung nilai selain 0/1")

    oracle_probability = oracle[contract.latent_generator_field]

    if not oracle_probability.between(0.0, 1.0).all():
        errors.append("oracle probability berada di luar interval [0,1]")

    valid_product_categories = {
        profile.category.value
        for profile in PRODUCT_PROFILES
    }
    valid_subcategories = {
        value
        for profile in PRODUCT_PROFILES
        for value in profile.subcategories
    }
    valid_package_formats = {
        value
        for profile in PRODUCT_PROFILES
        for value in profile.package_formats
    }

    allowed_categories: dict[str, set[str]] = {
        "product_category": valid_product_categories,
        "product_subcategory": valid_subcategories,
        "action_type": {
            action.value
            for action in MODEL_SCORED_ACTIONS
        },
        "business_type": {
            value.value
            for value in BusinessType
        },
        "storage_requirement_mode": {
            value.value
            for value in StorageRequirementMode
        },
        "urgency_level": {
            value.value
            for value in UrgencyLevel
        },
        "surplus_source": {
            value.value
            for value in SurplusSource
        },
        "destination_type": set(ACTION_DESTINATION_TYPES.values()),
        "seasonality_status": {
            value.value
            for value in SeasonalityStatus
        },
        "package_format": valid_package_formats,
    }

    invalid_categories = {
        column: _invalid_category_count(
            candidate,
            column,
            allowed,
        )
        for column, allowed in allowed_categories.items()
    }

    if any(invalid_categories.values()):
        errors.append("invalid categorical values ditemukan")

    impossible_checks = {
        "planning_quantity_nonpositive": int(
            (candidate["planning_quantity"] <= 0).sum()
        ),
        "shelf_life_outside_range": int(
            (
                (candidate["remaining_shelf_life_days"] < 1)
                | (candidate["remaining_shelf_life_days"] > 365)
            ).sum()
        ),
        "safe_window_nonpositive": int(
            (candidate["remaining_safe_window_hours"] <= 0).sum()
        ),
        "commercial_window_nonpositive": int(
            (candidate["remaining_commercial_window_days"] <= 0).sum()
        ),
        "unit_cost_nonpositive": int(
            (candidate["unit_cost"] <= 0).sum()
        ),
        "normal_price_below_cost": int(
            (
                candidate["normal_selling_price"]
                < candidate["unit_cost"]
            ).sum()
        ),
        "offered_price_negative": int(
            (
                candidate["offered_or_selling_price_per_unit"]
                < 0
            ).sum()
        ),
        "offered_price_above_normal": int(
            (
                candidate["offered_or_selling_price_per_unit"]
                > candidate["normal_selling_price"]
            ).sum()
        ),
        "negative_action_cost": int(
            (
                (candidate["direct_action_cost"] < 0)
                | (candidate["logistics_cost"] < 0)
                | (candidate["handling_cost"] < 0)
            ).sum()
        ),
        "completion_nonpositive": int(
            (candidate["estimated_completion_hours"] <= 0).sum()
        ),
        "demand_nonpositive": int(
            (candidate["active_demand_quantity"] <= 0).sum()
        ),
        "capacity_nonpositive": int(
            (candidate["available_capacity"] <= 0).sum()
        ),
        "invalid_minimum_order_quantity": int(
            (
                (candidate["minimum_order_quantity"] <= 0)
                | (
                    candidate["minimum_order_quantity"]
                    > candidate["planning_quantity"]
                )
            ).sum()
        ),
        "capability_ratio_nonpositive": int(
            (candidate["capability_resource_ratio"] <= 0).sum()
        ),
        "demand_coverage_nonpositive": int(
            (candidate["demand_coverage_ratio"] <= 0).sum()
        ),
        "negative_demand_freshness": int(
            (candidate["demand_freshness_hours"] < 0).sum()
        ),
        "negative_distance": int(
            (candidate["distance_km"] < 0).sum()
        ),
        "package_volume_nonpositive": int(
            (candidate["package_volume_ml"] <= 0).sum()
        ),
        "package_weight_nonpositive": int(
            (candidate["package_weight_g"] <= 0).sum()
        ),
    }

    local_mask = candidate["action_type"].isin(_LOCAL_ACTIONS)

    impossible_checks["local_action_nonzero_distance"] = int(
        (
            local_mask
            & (candidate["distance_km"] != 0)
        ).sum()
    )
    impossible_checks["local_action_nonzero_logistics"] = int(
        (
            local_mask
            & (candidate["logistics_cost"] != 0)
        ).sum()
    )

    if any(impossible_checks.values()):
        errors.append("impossible atau inconsistent numeric values ditemukan")

    positive_count = int(
        candidate[contract.canonical_target].sum()
    )
    negative_count = row_count - positive_count
    positive_rate = positive_count / row_count
    minority_rate = min(
        positive_count,
        negative_count,
    ) / row_count

    if minority_rate < 0.20:
        warnings.append(
            "class minority berada di bawah 20%; "
            "interpretasikan ranking dan calibration dengan hati-hati"
        )

    group_sizes = candidate.groupby(
        "scenario_group_id",
        sort=True,
    ).size()

    group_distribution = {
        "group_count": int(len(group_sizes)),
        "min_candidates_per_group": int(group_sizes.min()),
        "max_candidates_per_group": int(group_sizes.max()),
        "mean_candidates_per_group": float(group_sizes.mean()),
    }

    if (
        group_distribution["min_candidates_per_group"]
        < config.generation.candidates_per_planning_lot_min
        or group_distribution["max_candidates_per_group"]
        > config.generation.candidates_per_planning_lot_max
    ):
        errors.append("candidate count per group berada di luar config")

    mean_oracle_probability = float(oracle_probability.mean())
    overall_calibration_gap = abs(
        positive_rate - mean_oracle_probability
    )

    if overall_calibration_gap > 0.03:
        warnings.append(
            "overall sampled outcome rate berbeda >3pp "
            "dari mean latent probability"
        )

    calibration_table: list[dict[str, object]] = []

    calibration_frame = pd.DataFrame(
        {
            "probability": oracle_probability,
            "outcome": candidate[contract.canonical_target],
        }
    )
    calibration_frame["bin"] = pd.cut(
        calibration_frame["probability"],
        bins=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        include_lowest=True,
    )

    grouped_calibration = calibration_frame.groupby(
        "bin",
        observed=True,
    )

    for interval, frame in grouped_calibration:
        calibration_table.append(
            {
                "probability_bin": str(interval),
                "rows": int(len(frame)),
                "mean_probability": float(frame["probability"].mean()),
                "observed_positive_rate": float(frame["outcome"].mean()),
            }
        )

    categorical_distribution = {
        column: _category_counts(candidate, column)
        for column in contract.allowed_categorical_features
    }

    numeric_distribution = {
        column: _numeric_summary(candidate, column)
        for column in contract.allowed_numeric_features
    }

    expected_coverage = dict(allowed_categories)
    expected_coverage["seasonality_status"] = {
        SeasonalityStatus.IN_SEASON.value,
        SeasonalityStatus.POST_SEASON.value,
        SeasonalityStatus.PRE_SEASON.value,
        SeasonalityStatus.NOT_APPLICABLE.value,
    }

    coverage_missing = {
        column: sorted(
            expected_coverage[column]
            - set(candidate[column].astype(str).unique())
        )
        for column in expected_coverage
    }

    coverage_missing = {
        key: value
        for key, value in coverage_missing.items()
        if value
    }

    if coverage_missing:
        warnings.append(
            "sebagian categorical catalog values tidak muncul pada dataset"
        )

    return {
        "report_version": "1.0.0",
        "status": "PASS" if not errors else "FAIL",
        "claim_boundary": (
            "Quality checks validate internal synthetic consistency only. "
            "They do not validate real-world rescue probabilities."
        ),
        "errors": errors,
        "warnings": warnings,
        "dataset_structure": {
            "candidate_rows": row_count,
            "oracle_rows": oracle_row_count,
            "columns": int(len(candidate.columns)),
            "scenario_groups": scenario_group_count,
            "missing_cells": missing_cells,
            "duplicate_rows": duplicate_rows,
            "duplicate_candidate_ids": duplicate_candidate_ids,
            "candidate_oracle_aligned": candidate_oracle_aligned,
            "forbidden_columns_present": forbidden_present,
        },
        "class_distribution": {
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_rate": positive_rate,
            "negative_rate": negative_count / row_count,
            "minority_rate": minority_rate,
        },
        "label_generation": {
            "oracle_probability_min": float(oracle_probability.min()),
            "oracle_probability_max": float(oracle_probability.max()),
            "oracle_probability_mean": mean_oracle_probability,
            "observed_positive_rate": positive_rate,
            "overall_calibration_gap": overall_calibration_gap,
            "calibration_bins": calibration_table,
        },
        "invalid_categories": invalid_categories,
        "impossible_values": impossible_checks,
        "group_distribution": group_distribution,
        "categorical_distribution": categorical_distribution,
        "numeric_distribution": numeric_distribution,
        "catalog_values_missing_from_dataset": coverage_missing,
    }


def write_dataset_quality_report(
    report: dict[str, object],
    *,
    json_path: Path,
    markdown_path: Path,
) -> None:
    """Write deterministic JSON and human-readable Markdown evidence."""

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    structure = report["dataset_structure"]
    classes = report["class_distribution"]
    labels = report["label_generation"]
    groups = report["group_distribution"]

    assert isinstance(structure, dict)
    assert isinstance(classes, dict)
    assert isinstance(labels, dict)
    assert isinstance(groups, dict)

    lines = [
        "# Synthetic Dataset Quality Report",
        "",
        f"**Status:** {report['status']}",
        "",
        "## Claim Boundary",
        "",
        str(report["claim_boundary"]),
        "",
        "## Dataset Structure",
        "",
        f"- Candidate rows: {structure['candidate_rows']}",
        f"- Oracle rows: {structure['oracle_rows']}",
        f"- Scenario groups: {structure['scenario_groups']}",
        f"- Missing cells: {structure['missing_cells']}",
        f"- Duplicate rows: {structure['duplicate_rows']}",
        f"- Duplicate candidate IDs: {structure['duplicate_candidate_ids']}",
        f"- Candidate/oracle aligned: {structure['candidate_oracle_aligned']}",
        "",
        "## Class Distribution",
        "",
        f"- Positive rows: {classes['positive_count']}",
        f"- Negative rows: {classes['negative_count']}",
        f"- Positive rate: {classes['positive_rate']:.6f}",
        f"- Minority rate: {classes['minority_rate']:.6f}",
        "",
        "## Label Generation",
        "",
        f"- Oracle probability min: {labels['oracle_probability_min']:.6f}",
        f"- Oracle probability max: {labels['oracle_probability_max']:.6f}",
        f"- Oracle probability mean: {labels['oracle_probability_mean']:.6f}",
        f"- Observed positive rate: {labels['observed_positive_rate']:.6f}",
        f"- Overall calibration gap: {labels['overall_calibration_gap']:.6f}",
        "",
        "## Group Distribution",
        "",
        f"- Group count: {groups['group_count']}",
        f"- Min candidates/group: {groups['min_candidates_per_group']}",
        f"- Max candidates/group: {groups['max_candidates_per_group']}",
        f"- Mean candidates/group: {groups['mean_candidates_per_group']:.6f}",
        "",
        "## Errors",
        "",
    ]

    errors = report["errors"]
    warnings = report["warnings"]

    assert isinstance(errors, list)
    assert isinstance(warnings, list)

    lines.extend(
        [f"- {error}" for error in errors]
        if errors
        else ["- None"]
    )

    lines.extend(
        [
            "",
            "## Warnings",
            "",
        ]
    )

    lines.extend(
        [f"- {warning}" for warning in warnings]
        if warnings
        else ["- None"]
    )

    markdown_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "audit_synthetic_dataset",
    "write_dataset_quality_report",
]
