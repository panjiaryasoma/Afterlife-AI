"""Generate the reproducible Afterlife AI synthetic dataset."""

from afterlife_ai.synthetic.pipeline import (
    DEFAULT_EVIDENCE_MANIFEST_PATH,
    run_synthetic_dataset_pipeline,
)


def main() -> None:
    """Run production synthetic dataset generation."""

    bundle, manifest = run_synthetic_dataset_pipeline()

    candidate_artifact = manifest["candidate_artifact"]
    oracle_artifact = manifest["oracle_artifact"]

    assert isinstance(candidate_artifact, dict)
    assert isinstance(oracle_artifact, dict)

    print("Synthetic dataset generation complete")
    print(f"Scenario groups : {bundle.scenario_group_count}")
    print(f"Candidate rows  : {bundle.row_count}")
    print(f"Positive rows   : {bundle.positive_count}")
    print(f"Positive rate   : {bundle.positive_rate:.4f}")
    print(
        "Candidate SHA256:",
        candidate_artifact["sha256"],
    )
    print(
        "Oracle SHA256   :",
        oracle_artifact["sha256"],
    )
    print(
        "Evidence manifest:",
        DEFAULT_EVIDENCE_MANIFEST_PATH,
    )


if __name__ == "__main__":
    main()
