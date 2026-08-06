from pathlib import Path

import yaml

from afterlife_ai.contracts import enums

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "contracts"
    / "FEATURE_SCHEMA_FINAL_v2.0.yaml"
)


def test_python_enums_match_schema_contract() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))

    for enum_name, expected_values in schema["enums"].items():
        enum_class = getattr(enums, enum_name)
        actual_values = [member.value for member in enum_class]

        assert actual_values == expected_values, (
            f"{enum_name} tidak sinkron dengan schema: "
            f"expected={expected_values}, actual={actual_values}"
        )


def test_all_exported_enum_names_match_schema_contract() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert enums.__all__ == list(schema["enums"])
