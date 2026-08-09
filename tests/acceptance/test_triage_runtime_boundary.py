import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TRIAGE_SOURCE_DIR = REPO_ROOT / "src" / "afterlife_ai" / "triage"

FORBIDDEN_IMPORT_PREFIXES = (
    "afterlife_ai.planner",
    "afterlife_ai.scoring",
    "afterlife_ai.optimization",
    "afterlife_ai.models",
    "sklearn",
    "joblib",
    "ortools",
)


def test_triage_runtime_does_not_import_ml_or_optimizer_modules() -> None:
    imported_modules: set[str] = set()

    for source_path in TRIAGE_SOURCE_DIR.glob("*.py"):
        tree = ast.parse(
            source_path.read_bytes(),
            filename=str(source_path),
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(
                    alias.name for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None:
                    imported_modules.add(node.module)

    forbidden_imports = {
        module_name
        for module_name in imported_modules
        if module_name.startswith(FORBIDDEN_IMPORT_PREFIXES)
    }

    assert forbidden_imports == set()
