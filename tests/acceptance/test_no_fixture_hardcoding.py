from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

RUNTIME_DIRS = (
    REPO_ROOT / "src",
    REPO_ROOT / "app",
    REPO_ROOT / "scripts",
)

FORBIDDEN_FIXTURE_IDENTIFIERS = (
    "LOT-HEALTHY-001",
    "LOT-PARTIAL-SURPLUS-001",
    "LOT-MONITOR-001",
    "LOT-MIXED-001",
    "LOT-EXPIRED-001",
    "LOT-REVIEW-001",
    "LOT-SALES-REVIEW-001",
    "LOT-DECLARED-001",
)


def test_runtime_path_does_not_hardcode_acceptance_fixtures() -> None:
    violations: list[str] = []

    for runtime_dir in RUNTIME_DIRS:
        if not runtime_dir.exists():
            continue

        for source_path in runtime_dir.rglob("*.py"):
            text = source_path.read_text(
                encoding="utf-8-sig"
            )

            for identifier in FORBIDDEN_FIXTURE_IDENTIFIERS:
                if identifier in text:
                    relative_path = source_path.relative_to(
                        REPO_ROOT
                    )
                    violations.append(
                        f"{relative_path}: {identifier}"
                    )

    assert violations == [], (
        "Acceptance fixture identifiers ditemukan pada runtime path:\n"
        + "\n".join(violations)
    )
