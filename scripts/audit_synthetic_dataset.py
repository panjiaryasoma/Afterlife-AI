"""Audit production synthetic dataset quality."""

from pathlib import Path

from afterlife_ai.synthetic.config import load_synthetic_dataset_config
from afterlife_ai.synthetic.quality import (
    audit_synthetic_dataset,
    write_dataset_quality_report,
)
from afterlife_ai.synthetic.schema_contract import (
    load_model_feature_contract,
)

CONFIG_PATH = Path("configs/synthetic_dataset_v2.yaml")
JSON_REPORT_PATH = Path(
    "reports/evidence/synthetic_dataset/DATASET_QUALITY_REPORT_v2.json"
)
MARKDOWN_REPORT_PATH = Path(
    "reports/evidence/synthetic_dataset/DATASET_QUALITY_REPORT_v2.md"
)


def main() -> None:
    """Run dataset-quality audit and write evidence."""

    config = load_synthetic_dataset_config(CONFIG_PATH)
    contract = load_model_feature_contract(
        Path(config.feature_schema.path)
    )

    report = audit_synthetic_dataset(
        candidate_path=Path(config.artifacts.candidate_table),
        oracle_path=Path(config.artifacts.oracle_table),
        config=config,
        contract=contract,
    )

    write_dataset_quality_report(
        report,
        json_path=JSON_REPORT_PATH,
        markdown_path=MARKDOWN_REPORT_PATH,
    )

    print(f"Dataset quality status : {report['status']}")

    structure = report["dataset_structure"]
    classes = report["class_distribution"]
    labels = report["label_generation"]
    groups = report["group_distribution"]

    assert isinstance(structure, dict)
    assert isinstance(classes, dict)
    assert isinstance(labels, dict)
    assert isinstance(groups, dict)

    print(f"Rows                   : {structure['candidate_rows']}")
    print(f"Scenario groups        : {structure['scenario_groups']}")
    print(f"Missing cells          : {structure['missing_cells']}")
    print(f"Duplicate rows         : {structure['duplicate_rows']}")
    print(f"Positive rate          : {classes['positive_rate']:.6f}")
    print(f"Minority rate          : {classes['minority_rate']:.6f}")
    print(
        "Oracle probability mean:",
        f"{labels['oracle_probability_mean']:.6f}",
    )
    print(
        "Calibration gap        :",
        f"{labels['overall_calibration_gap']:.6f}",
    )
    print(
        "Candidates/group       :",
        f"{groups['min_candidates_per_group']}-"
        f"{groups['max_candidates_per_group']}",
    )
    warnings = report["warnings"]
    errors = report["errors"]

    assert isinstance(warnings, list)
    assert isinstance(errors, list)

    print(f"Warnings               : {len(warnings)}")
    print(f"Errors                 : {len(errors)}")

    if report["status"] != "PASS":
        raise SystemExit("Dataset quality audit FAILED.")


if __name__ == "__main__":
    main()
