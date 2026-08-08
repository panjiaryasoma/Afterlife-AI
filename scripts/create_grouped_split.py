"""Create deterministic grouped dataset split artifacts."""

from pathlib import Path

import pandas as pd

from afterlife_ai.synthetic.config import (
    load_synthetic_dataset_config,
)
from afterlife_ai.synthetic.split import (
    assign_grouped_splits,
    build_split_manifest,
    write_split_artifacts,
)

CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")

PROCESSED_ASSIGNMENT_PATH = Path(
    "data/processed/synthetic_split_manifest_v2.csv"
)
EVIDENCE_ASSIGNMENT_PATH = Path(
    "reports/evidence/synthetic_dataset/SPLIT_GROUPS_v2.csv"
)
EVIDENCE_MANIFEST_PATH = Path(
    "reports/evidence/synthetic_dataset/SPLIT_MANIFEST_v2.json"
)


def main() -> None:
    """Create and verify grouped train/validation/test assignments."""

    config = load_synthetic_dataset_config(CONFIG_PATH)
    candidate_path = Path(config.artifacts.candidate_table)

    candidate = pd.read_csv(candidate_path)

    assignments = assign_grouped_splits(
        candidate,
        config=config,
    )

    manifest = build_split_manifest(
        candidate_path=candidate_path,
        assignments=assignments,
        config=config,
    )

    write_split_artifacts(
        assignments=assignments,
        manifest=manifest,
        processed_assignment_path=PROCESSED_ASSIGNMENT_PATH,
        evidence_assignment_path=EVIDENCE_ASSIGNMENT_PATH,
        evidence_manifest_path=EVIDENCE_MANIFEST_PATH,
    )

    print("Grouped split complete")
    print(
        f"Total groups   : {manifest['total_group_count']}"
    )

    splits = manifest["splits"]
    assert isinstance(splits, dict)

    for split_name in ("train", "validation", "test"):
        summary = splits[split_name]
        assert isinstance(summary, dict)

        print(
            f"{split_name:<10}: "
            f"{summary['group_count']} groups, "
            f"{summary['row_count']} rows"
        )

    print(
        f"Group leakage : {manifest['group_leakage_count']}"
    )
    print(
        f"Test policy   : {manifest['test_split_policy']}"
    )


if __name__ == "__main__":
    main()
