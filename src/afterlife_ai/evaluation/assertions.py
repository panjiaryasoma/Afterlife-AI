from __future__ import annotations

from math import isclose
from typing import Any

from .contracts import (
    ContractAssertion,
    ExpectedAllocation,
    PlannerEvaluationCase,
    PlannerObservation,
)


class ContractAssertionError(AssertionError):
    """Raised when an observed planner result violates an evaluation contract."""


def _numbers_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return bool(left == right)
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9)
    return bool(left == right)


def _allocation_matches(observed: ExpectedAllocation, params: dict[str, Any]) -> bool:
    if params.get("lot_id") is not None and observed.lot_id != params["lot_id"]:
        return False
    expected_sources = params.get("source_lot_ids") or []
    if expected_sources and observed.source_lot_ids != expected_sources:
        return False
    if observed.action != params.get("action"):
        return False
    if params.get("destination") is not None and observed.destination != params["destination"]:
        return False
    expected_quantity = params.get("quantity")
    if expected_quantity is not None and not _numbers_equal(observed.quantity, expected_quantity):
        return False
    return True


def evaluate_assertion(
    case: PlannerEvaluationCase,
    observation: PlannerObservation,
    assertion: ContractAssertion,
) -> str | None:
    kind = assertion.type
    p = assertion.params

    if kind == "CASE_ID_MATCHES_FILE":
        expected = p["expected_case_id"]
        if observation.case_id != expected:
            return f"case_id={observation.case_id!r}, expected {expected!r}"

    elif kind == "HAS_RULE_TRACEABILITY":
        minimum = int(p.get("minimum_rule_count", 1))
        if len(observation.rule_ids) < minimum:
            return f"rule traceability count={len(observation.rule_ids)}, expected >= {minimum}"

    elif kind == "EXPECTED_ALLOCATION":
        if not any(_allocation_matches(item, p) for item in observation.allocations):
            return f"missing expected allocation {p}"

    elif kind == "NO_AUTOMATIC_ALLOCATION":
        automatic_quantity = observation.metrics.get("automatic_allocated_quantity")
        if automatic_quantity is None:
            automatic_quantity = sum(
                float(item.quantity or 0)
                for item in observation.allocations
                if item.action != "PENDING_HUMAN_REVIEW"
            )
        if not _numbers_equal(automatic_quantity, 0):
            return f"automatic allocated quantity={automatic_quantity}, expected 0"

    elif kind == "NO_HUMAN_CONSUMPTION_ALLOCATION":
        value = observation.metrics.get("human_consumption_allocation")
        if not _numbers_equal(value, 0):
            return f"human_consumption_allocation={value}, expected 0"

    elif kind == "STATUS_EQUALS":
        field = p["field"]
        expected = p["value"]
        actual = observation.statuses.get(field)
        if actual != expected:
            return f"status {field}={actual!r}, expected {expected!r}"

    elif kind == "HUMAN_REVIEW_REQUIRED":
        if not observation.human_review_required:
            return "human review was not required"

    elif kind == "EXPECTED_METRIC":
        name = p["name"]
        expected = p.get("value")
        actual = observation.metrics.get(name)
        if not _numbers_equal(actual, expected):
            return f"metric {name}={actual!r}, expected {expected!r}"

    elif kind == "OBJECTIVE_RUN_PRESENT":
        objective = p["objective"]
        if objective not in observation.objective_runs:
            return f"objective run {objective!r} is missing"

    elif kind == "OBJECTIVE_ACTION_QUANTITY":
        objective = p["objective"]
        action = p["action"]
        expected = p["quantity"]
        run = observation.objective_runs.get(objective, {})
        actual = run.get(action) if isinstance(run, dict) else None
        if not _numbers_equal(actual, expected):
            return f"objective {objective} action {action}={actual!r}, expected {expected!r}"

    elif kind == "QUANTITY_CONSERVATION":
        lot_id = p["lot_id"]
        input_quantity = float(p["input_quantity"])
        expected_allocated = float(p["expected_allocated_quantity"])
        expected_unallocated = float(p["expected_unallocated_quantity"])
        actual_allocated = sum(
            float(item.quantity or 0) for item in observation.allocations if item.lot_id == lot_id
        )
        if not isclose(actual_allocated, expected_allocated, abs_tol=1e-9):
            return f"allocated {actual_allocated} for {lot_id}, expected {expected_allocated}"
        if not isclose(actual_allocated + expected_unallocated, input_quantity, abs_tol=1e-9):
            return (
                f"quantity mismatch for {lot_id}: allocated {actual_allocated} + "
                f"unallocated {expected_unallocated} != input {input_quantity}"
            )

    elif kind == "BATCH_ROUTING_CONSERVATION":
        expected_input = float(p["input_quantity"])
        expected_allocated = float(p["expected_allocated_quantity"])
        routed_metric = p["routed_metric"]
        expected_routed = float(p["expected_routed_quantity"])
        actual_allocated = sum(float(item.quantity or 0) for item in observation.allocations)
        actual_routed = observation.metrics.get(routed_metric)
        if not _numbers_equal(actual_allocated, expected_allocated):
            return f"batch allocated {actual_allocated}, expected {expected_allocated}"
        if not _numbers_equal(actual_routed, expected_routed):
            return f"routed metric {routed_metric}={actual_routed}, expected {expected_routed}"
        if not isinstance(actual_routed, (int, float)):
            return (
                f"routed metric {routed_metric}={actual_routed!r} "
                "is not numeric"
            )
        actual_routed_float = float(actual_routed)
        if not isclose(
            actual_allocated + actual_routed_float,
            expected_input,
            abs_tol=1e-9,
        ):
            return (
                f"batch routing mismatch: allocated {actual_allocated} + "
                f"routed {actual_routed} != input {expected_input}"
            )

    elif kind == "BATCH_QUANTITY_CONSERVATION":
        expected_input = float(p["input_quantity"])
        expected_allocated = float(p["expected_allocated_quantity"])
        actual_allocated = sum(float(item.quantity or 0) for item in observation.allocations)
        if not isclose(actual_allocated, expected_allocated, abs_tol=1e-9):
            return f"batch allocated {actual_allocated}, expected {expected_allocated}"
        if not isclose(actual_allocated, expected_input, abs_tol=1e-9):
            return f"batch allocation {actual_allocated} != input {expected_input}"

    else:  # pragma: no cover - guarded by Pydantic Literal
        return f"unsupported assertion type: {kind}"

    return None


def evaluate_case(
    case: PlannerEvaluationCase,
    observation: PlannerObservation,
) -> list[str]:
    failures: list[str] = []
    for assertion in case.assertions:
        failure = evaluate_assertion(case, observation, assertion)
        if failure:
            failures.append(f"{assertion.type}: {failure}")
    return failures


def assert_case_passes(case: PlannerEvaluationCase, observation: PlannerObservation) -> None:
    failures = evaluate_case(case, observation)
    if failures:
        details = "\n".join(f"- {item}" for item in failures)
        raise ContractAssertionError(f"{case.case_id} failed:\n{details}")
