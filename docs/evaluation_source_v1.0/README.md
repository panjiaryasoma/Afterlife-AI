# Evaluation Source Snapshot v1.0

This directory is a production-repository snapshot of the locked
pre-production evaluation source artifacts.

Original project phase:

04_EVALUATION_AND_DOMAIN_RULES

Purpose:

- preserve the authoritative EVAL-001 through EVAL-030 source specification;
- provide traceable production-test inputs;
- prevent production tests from depending on files outside the repository;
- keep source evaluation artifacts separate from executable runtime adapters.

These files are source contracts, not runtime planner implementation.

The executable evaluation package is generated/implemented separately and
must remain traceable to these artifacts.

Source artifacts:

- domain_rules_v1.0.yaml
- evaluation_matrix_v1.0.csv
- evaluation_spec_v1.0.yaml
- feature_traceability_v1.0.csv
- SOURCE_EVALUATION_SUITE_001-030.md
