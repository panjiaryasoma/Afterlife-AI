import json
from pathlib import Path

import pytest

from afterlife_ai.pipeline.runtime_config import (
    load_runtime_config,
)
from afterlife_ai.pipeline.scoring import _load_provider
from afterlife_ai.scoring.model_provider import (
    ModelIntegrityError,
    load_frozen_model_identity,
    verify_frozen_model_integrity,
)

ARTIFACT_PATH = Path("models/HGB_E_v1.joblib")
SCHEMA_PATH = Path(
    "docs/contracts/FEATURE_SCHEMA_FINAL_v2.0.yaml"
)
MANIFEST_PATH = Path(
    "reports/evidence/modeling/SELECTED_MODEL_MANIFEST_v1.json"
)


def _manifest_payload() -> dict:
    payload = json.loads(
        MANIFEST_PATH.read_text(
            encoding="utf-8",
        )
    )
    assert isinstance(payload, dict)
    return payload


def test_frozen_model_bundle_matches_selected_manifest() -> None:
    verify_frozen_model_integrity(
        artifact_path=ARTIFACT_PATH,
        schema_path=SCHEMA_PATH,
        manifest_path=MANIFEST_PATH,
    )


def test_integrity_verification_rejects_tampered_artifact(
    tmp_path: Path,
) -> None:
    artifact_copy = tmp_path / "HGB_E_v1.joblib"
    artifact_copy.write_bytes(
        ARTIFACT_PATH.read_bytes() + b"tampered"
    )

    manifest = _manifest_payload()
    manifest["artifact"]["path"] = str(
        artifact_copy
    )

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    with pytest.raises(
        ModelIntegrityError,
        match="Model artifact SHA-256",
    ):
        verify_frozen_model_integrity(
            artifact_path=artifact_copy,
            schema_path=SCHEMA_PATH,
            manifest_path=manifest_path,
        )


def test_integrity_verification_rejects_tampered_feature_schema(
    tmp_path: Path,
) -> None:
    schema_copy = tmp_path / "FEATURE_SCHEMA_FINAL_v2.0.yaml"
    schema_copy.write_bytes(
        SCHEMA_PATH.read_bytes() + b"\n# tampered\n"
    )

    manifest = _manifest_payload()
    manifest["inputs"]["feature_schema"]["path"] = str(
        schema_copy
    )

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    with pytest.raises(
        ModelIntegrityError,
        match="Feature schema SHA-256",
    ):
        verify_frozen_model_integrity(
            artifact_path=ARTIFACT_PATH,
            schema_path=schema_copy,
            manifest_path=manifest_path,
        )


def test_pipeline_does_not_downgrade_integrity_failure_to_fallback(
    tmp_path: Path,
) -> None:
    artifact_copy = tmp_path / "HGB_E_v1.joblib"
    artifact_copy.write_bytes(
        ARTIFACT_PATH.read_bytes() + b"tampered"
    )

    manifest = _manifest_payload()
    manifest["artifact"]["path"] = str(
        artifact_copy
    )

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    config = load_runtime_config(
        Path("configs/runtime_v1.yaml")
    )
    model_config = config.model.model_copy(
        update={
            "artifact_path": artifact_copy,
            "manifest_path": manifest_path,
        }
    )
    config = config.model_copy(
        update={"model": model_config}
    )

    with pytest.raises(
        ModelIntegrityError,
        match="Model artifact SHA-256",
    ):
        _load_provider(config)


def test_frozen_model_identity_matches_selected_manifest() -> None:
    model_version, model_sha256 = (
        load_frozen_model_identity(
            MANIFEST_PATH
        )
    )

    assert model_version == "HGB_E_v1"
    assert model_sha256 == (
        "a318a2550d97ea0861b85fd7af5f9b2"
        "be0291eb29f57b07a00b32ab5ea5295d9"
    )
