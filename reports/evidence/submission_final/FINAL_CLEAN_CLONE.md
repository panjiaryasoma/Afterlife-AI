# Final Fresh-Clone Reproducibility

Status: **PASS**

Audit subject commit:

`52cfb2d7563e2b359a2c0dae0137262fad6b6100`

```yaml
fresh_clone_working_tree: clean
project_python: 3.12.7
uv_sync_locked: PASS
ruff: PASS
mypy: PASS

pytest:
  passed: 372
  failed: 0
  errors: 0
  warnings: 2
  duration_seconds: 58.52

docker_clean_build: PASS
docker_start: PASS
container_health: PASS
GET_health: 200
GET_root: 200
clean_shutdown: PASS

final_fresh_clone_working_tree: clean
```
