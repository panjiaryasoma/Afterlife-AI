"""Freeze the validation-selected HGB-E model artifact."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.metrics import average_precision_score, brier_score_loss

from afterlife_ai.modeling.baselines import (
    attach_split_assignments,
    select_modeling_split,
)
from afterlife_ai.modeling.hist_gradient import (
    fit_hist_gradient_boosting,
    load_hist_gradient_config,
    predict_hist_gradient_probabilities,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

SELECTED_CONFIG_PATH = Path(
    "configs/selected_model_v1.yaml"
)
SCHEMA_PATH = Path(
    "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
)
CANDIDATE_PATH = Path(
    "data/generated/synthetic_candidates_v2.csv"
)
SPLIT_PATH = Path(
    "reports/evidence/synthetic_dataset/"
    "SPLIT_GROUPS_v2.csv"
)

ARTIFACT_PATH = Path(
    "models/HGB_E_v1.joblib"
)
MANIFEST_PATH = Path(
    "reports/evidence/modeling/"
    "SELECTED_MODEL_MANIFEST_v1.json"
)

EXPECTED_VALIDATION_PR_AUC = 0.853664
EXPECTED_VALIDATION_BRIER = 0.155145
METRIC_TOLERANCE = 0.00001


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()


def main() -> None:
    config = load_hist_gradient_config(
        SELECTED_CONFIG_PATH
    )
    contract = load_model_feature_contract(
        SCHEMA_PATH
    )

    candidates = pd.read_csv(
        CANDIDATE_PATH
    )
    assignments = pd.read_csv(
        SPLIT_PATH
    )

    modeling = attach_split_assignments(
        candidates,
        assignments,
    )

    train = select_modeling_split(
        modeling,
        "train",
    )
    validation = select_modeling_split(
        modeling,
        "validation",
    )

    if set(train["split"].astype(str)) != {"train"}:
        raise RuntimeError(
            "Artifact training frame is not train-only."
        )

    if set(validation["split"].astype(str)) != {
        "validation"
    }:
        raise RuntimeError(
            "Artifact integrity frame is not validation-only."
        )

    ARTIFACT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    MANIFEST_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    started = time.perf_counter()

    model = fit_hist_gradient_boosting(
        train,
        contract=contract,
        config=config,
    )

    training_seconds = (
        time.perf_counter() - started
    )

    joblib.dump(
        model,
        ARTIFACT_PATH,
    )

    loaded_model = joblib.load(
        ARTIFACT_PATH
    )

    validation_predictions = (
        predict_hist_gradient_probabilities(
            loaded_model,
            validation,
            contract=contract,
        )
    )

    y_true = validation_predictions[
        "simulated_rescue_outcome"
    ].astype(int)

    y_score = validation_predictions[
        "model_score"
    ].astype(float)

    validation_pr_auc = float(
        average_precision_score(
            y_true,
            y_score,
        )
    )

    validation_brier = float(
        brier_score_loss(
            y_true,
            y_score,
        )
    )

    if (
        abs(
            validation_pr_auc
            - EXPECTED_VALIDATION_PR_AUC
        )
        > METRIC_TOLERANCE
    ):
        raise RuntimeError(
            "Packaged artifact does not reproduce "
            "locked HGB-E validation PR-AUC: "
            f"{validation_pr_auc:.9f}"
        )

    if (
        abs(
            validation_brier
            - EXPECTED_VALIDATION_BRIER
        )
        > METRIC_TOLERANCE
    ):
        raise RuntimeError(
            "Packaged artifact does not reproduce "
            "locked HGB-E validation Brier: "
            f"{validation_brier:.9f}"
        )

    artifact_sha256 = sha256_file(
        ARTIFACT_PATH
    )

    manifest = {
        "manifest_version": "1.0.0",
        "status": "FROZEN_BEFORE_FINAL_TEST",
        "selected_label": "HGB_E",
        "model_family": (
            "HistGradientBoostingClassifier"
        ),
        "model_id": model.model_id,
        "configuration": config.model_dump(),
        "training": {
            "split": "train",
            "rows": int(model.training_rows),
            "scenario_groups": int(
                train[
                    "scenario_group_id"
                ].nunique()
            ),
            "duration_seconds": (
                training_seconds
            ),
        },
        "selection_validation": {
            "rows": int(len(validation)),
            "scenario_groups": int(
                validation[
                    "scenario_group_id"
                ].nunique()
            ),
            "pr_auc": validation_pr_auc,
            "brier": validation_brier,
            "expected_pr_auc": (
                EXPECTED_VALIDATION_PR_AUC
            ),
            "expected_brier": (
                EXPECTED_VALIDATION_BRIER
            ),
            "artifact_roundtrip_verified": True,
        },
        "artifact": {
            "path": ARTIFACT_PATH.as_posix(),
            "sha256": artifact_sha256,
        },
        "inputs": {
            "feature_schema": {
                "path": SCHEMA_PATH.as_posix(),
                "sha256": sha256_file(
                    SCHEMA_PATH
                ),
            },
            "synthetic_candidates": {
                "path": CANDIDATE_PATH.as_posix(),
                "sha256": sha256_file(
                    CANDIDATE_PATH
                ),
            },
            "split_manifest": {
                "path": SPLIT_PATH.as_posix(),
                "sha256": sha256_file(
                    SPLIT_PATH
                ),
            },
            "selected_model_config": {
                "path": (
                    SELECTED_CONFIG_PATH.as_posix()
                ),
                "sha256": sha256_file(
                    SELECTED_CONFIG_PATH
                ),
            },
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
        },
        "repository": {
            "packaging_commit_parent": git_head(),
        },
        "claim_boundary": (
            "Selected model was trained on the "
            "frozen synthetic benchmark. "
            "This artifact is not evidence of "
            "real-world rescue probability accuracy."
        ),
        "test_accessed": False,
    }

    MANIFEST_PATH.write_text(
        json.dumps(
            manifest,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=== SELECTED MODEL ARTIFACT ===")
    print(
        "model       : HGB-E"
    )
    print(
        f"train rows  : {model.training_rows}"
    )
    print(
        "validation  : "
        f"PR-AUC={validation_pr_auc:.6f}, "
        f"Brier={validation_brier:.6f}"
    )
    print(
        f"artifact    : {ARTIFACT_PATH}"
    )
    print(
        "sha256      : "
        f"{artifact_sha256}"
    )
    print(
        f"manifest    : {MANIFEST_PATH}"
    )
    print(
        "test accessed: False"
    )
    print()
    print("STATUS: FROZEN")


if __name__ == "__main__":
    main()
