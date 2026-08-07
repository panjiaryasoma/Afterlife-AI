# XLSX Intake Validation Evidence

## Repository

- HEAD: b169e69f18ddb0f402e86b80bfc9b740baebe9fe
- Valid input fixture: reports/evidence/intake_validation/valid_inventory_input.xlsx
- Canonical output: reports/evidence/intake_validation/canonical_inventory_output.json
- Malformed-input test output: reports/evidence/intake_validation/malformed_input_output.txt

## Validation Coverage

- Required worksheet validation: PASS
- Required column validation: PASS
- Empty inventory rejection: PASS
- Unknown column rejection: PASS
- x_ extension column acceptance: PASS
- Exact duplicate row rejection: PASS
- Same SKU across different lots acceptance: PASS
- Invalid numeric value rejection with row and field context: PASS
- Invalid enum/category rejection with readable error: PASS

## Canonical Intake

- One valid XLSX fixture is readable: PASS
- Valid input produces canonical inventory records: PASS
- Canonical output is JSON-safe: PASS

## Acceptance Result

Input tidak valid ditolak dengan error yang jelas: PASS
