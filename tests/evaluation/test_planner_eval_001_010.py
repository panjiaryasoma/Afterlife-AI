import pytest

from afterlife_ai.evaluation.assertions import evaluate_case
from afterlife_ai.evaluation.loader import DEFAULT_CASES_DIR, load_planner_case
from afterlife_ai.evaluation.runner import run_planner_eval_case

CASE_IDS = [
    f"EVAL-{number:03d}"
    for number in range(1, 11)
]

CASES = [
    load_planner_case(
        DEFAULT_CASES_DIR / f"{case_id}.yaml"
    )
    for case_id in CASE_IDS
]


@pytest.mark.parametrize(
    "case",
    CASES,
    ids=lambda case: case.case_id,
)
def test_eval_001_010_run_against_locked_contract(
    case,
) -> None:
    execution = run_planner_eval_case(case)

    failures = evaluate_case(
        case,
        execution.observation,
    )

    assert failures == []
    assert execution.assertion_failures == []
    assert execution.hard_constraint_violations == []
    assert execution.passed is True


def test_eval_batch_contains_exactly_001_through_010() -> None:
    assert [
        case.case_id
        for case in CASES
    ] == CASE_IDS
