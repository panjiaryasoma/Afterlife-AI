# Final UI / API Smoke

Status: PASS

Audit subject commit:

`52cfb2d7563e2b359a2c0dae0137262fad6b6100`

## Primary routes

- `GET /health` -> 200
- `GET /` -> 200
- `POST /api/analyze` -> PASS

## Decision contexts

```json
{
  "MAXIMIZE_RECOVERY_VALUE": {
    "http_status": 200,
    "solver_status": "OPTIMAL",
    "deterministic_execution": true,
    "model_execution_performed": true,
    "human_final_approval_status": "PENDING",
    "execution_performed": false
  },
  "MINIMIZE_WASTE": {
    "http_status": 200,
    "solver_status": "OPTIMAL",
    "deterministic_execution": true,
    "model_execution_performed": true,
    "human_final_approval_status": "PENDING",
    "execution_performed": false
  },
  "BALANCED": {
    "http_status": 200,
    "solver_status": "OPTIMAL",
    "deterministic_execution": true,
    "model_execution_performed": true,
    "human_final_approval_status": "PENDING",
    "execution_performed": false
  }
}
```

## Invalid request

`BALANCED` without `minimum_expected_rescue_ratio` -> HTTP 422

Expected validation behavior: PASS.

## Governance

```yaml
human_final_approval_status: PENDING
execution_performed: false
```
