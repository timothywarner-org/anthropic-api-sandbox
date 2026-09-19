# API Grounding Notes

This skill is grounded on the official scanner docs and source implementations for output contracts.

## Sources

1. Bandit JSON formatter docs

- [Bandit JSON formatter docs](https://bandit.readthedocs.io/en/latest/formatters/json.html)
- Contract highlights:
  - Top-level keys: `errors`, `generated_at`, `metrics`, `results`
  - Result-level keys include `filename`, `line_number`, `issue_severity`, `issue_confidence`, `issue_text`, `test_id`, `test_name`, `more_info`
  - `issue_cwe` is available in modern versions (added in 1.7.3)

1. Bandit JSON formatter source

- [Bandit JSON formatter source](https://raw.githubusercontent.com/PyCQA/bandit/main/bandit/formatters/json.py)
- Ground truth details:
  - `errors` entries are objects with `filename` and `reason`
  - `more_info` is added from Bandit docs URL resolution
  - `generated_at` uses UTC format `%Y-%m-%dT%H:%M:%SZ`

1. pip-audit JSON formatter source

- [pip-audit JSON formatter source](https://raw.githubusercontent.com/pypa/pip-audit/main/pip_audit/_format/json.py)
- Ground truth details:
  - Top-level object has keys `dependencies` and `fixes`
  - Resolved dependency shape: `{name, version, vulns}`
  - Skipped dependency shape: `{name, skip_reason}`
  - Vulnerability shape: `{id, fix_versions}` with optional `aliases`, optional `description`
  - Fix shape is either resolved `{name, old_version, new_version}` or skipped `{name, version, skip_reason}`

1. pip-audit user-facing examples

- [pip-audit examples](https://github.com/pypa/pip-audit#examples)
- Used for compatibility checks with real CLI JSON examples.

## Why source-plus-docs?

Bandit publishes explicit formatter docs, while pip-audit's exact JSON contract is clearest in source and examples. Using both avoids schema drift and ensures the validation code maps to what the CLI actually emits.

## Internal Contracts in This Skill

- `references/schemas/bandit-json.schema.json`: Raw Bandit payload contract
- `references/schemas/pip-audit-json.schema.json`: Raw pip-audit payload contract
- `references/schemas/unified-security-report.schema.json`: Normalized aggregate report produced by `run_security_scan.py`
