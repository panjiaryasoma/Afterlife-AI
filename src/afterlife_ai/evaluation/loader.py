from __future__ import annotations

from pathlib import Path

import yaml

from .contracts import PlannerEvaluationCase

DEFAULT_CASES_DIR = Path(__file__).resolve().parent / "planner_cases"


def load_planner_case(path: Path) -> PlannerEvaluationCase:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PlannerEvaluationCase.model_validate(data)


def load_all_planner_cases(cases_dir: Path = DEFAULT_CASES_DIR) -> list[PlannerEvaluationCase]:
    paths = sorted(cases_dir.glob("EVAL-*.yaml"))
    return [load_planner_case(path) for path in paths]
