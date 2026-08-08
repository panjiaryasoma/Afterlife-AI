"""End-to-end synthetic dataset generation pipeline."""

import json
import shutil
from pathlib import Path

from afterlife_ai.synthetic.artifacts import write_dataset_artifacts
from afterlife_ai.synthetic.config import (
    SyntheticDatasetConfig,
    load_synthetic_dataset_config,
)
from afterlife_ai.synthetic.dataset import (
    SyntheticDatasetBundle,
    generate_synthetic_dataset,
)
from afterlife_ai.synthetic.outcome import (
    OutcomeRecipeConfig,
    load_outcome_recipe,
)
from afterlife_ai.synthetic.schema_contract import (
    ModelFeatureContract,
    load_model_feature_contract,
)

DEFAULT_CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")
DEFAULT_RECIPE_PATH = Path("configs/synthetic_outcome_v1.yaml")
DEFAULT_EVIDENCE_MANIFEST_PATH = Path(
    "reports/evidence/synthetic_dataset/DATASET_MANIFEST_v2.json"
)


def _resolve_artifact_path(path_value: str) -> Path:
    """Resolve one repository-relative artifact path."""

    return Path(path_value)


def run_synthetic_dataset_pipeline(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    recipe_path: Path = DEFAULT_RECIPE_PATH,
    evidence_manifest_path: Path = DEFAULT_EVIDENCE_MANIFEST_PATH,
) -> tuple[SyntheticDatasetBundle, dict[str, object]]:
    """Generate and serialize the production synthetic dataset."""

    config: SyntheticDatasetConfig = load_synthetic_dataset_config(
        config_path
    )
    recipe: OutcomeRecipeConfig = load_outcome_recipe(recipe_path)

    schema_path = Path(config.feature_schema.path)
    contract: ModelFeatureContract = load_model_feature_contract(
        schema_path
    )

    bundle = generate_synthetic_dataset(
        config=config,
        recipe=recipe,
        contract=contract,
    )

    candidate_path = _resolve_artifact_path(
        config.artifacts.candidate_table
    )
    oracle_path = _resolve_artifact_path(
        config.artifacts.oracle_table
    )
    manifest_path = _resolve_artifact_path(
        config.artifacts.dataset_manifest
    )

    manifest = write_dataset_artifacts(
        bundle=bundle,
        config=config,
        recipe=recipe,
        contract=contract,
        candidate_path=candidate_path,
        oracle_path=oracle_path,
        manifest_path=manifest_path,
    )

    evidence_manifest_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    shutil.copyfile(
        manifest_path,
        evidence_manifest_path,
    )

    evidence_payload = json.loads(
        evidence_manifest_path.read_text(encoding="utf-8")
    )

    if evidence_payload != manifest:
        raise RuntimeError(
            "Evidence manifest berbeda dari generated dataset manifest."
        )

    return bundle, manifest


__all__ = [
    "DEFAULT_CONFIG_PATH",
    "DEFAULT_EVIDENCE_MANIFEST_PATH",
    "DEFAULT_RECIPE_PATH",
    "run_synthetic_dataset_pipeline",
]
