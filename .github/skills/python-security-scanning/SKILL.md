---
name: python-security-scanning
description: "Python security scanning, detection, and remediation workflow using Bandit and pip-audit with schema-validated JSON outputs. Use when user asks for Python SAST scans, dependency vulnerability scans, security findings triage, remediation plans, or automated pip package fixes. Keywords: python security scan, bandit, pip-audit, vulnerability detection, remediation, fix vulnerabilities, secure dependencies, static analysis, supply chain security."
---

# Python Security Scanning

## Purpose

Use this skill to run and interpret **Python security scans** with machine-readable outputs that are validated against the scanner output contracts.

This skill covers:

- **Detection** via Bandit (code-level issues) and pip-audit (dependency vulnerabilities)
- **Triage** into a normalized findings report
- **Remediation** planning and optional dependency fix execution

## Assets

- `scripts/run_security_scan.py`
  - Runs Bandit and pip-audit
  - Validates raw JSON payloads
  - Emits a unified report
- `scripts/build_remediation_plan.py`
  - Converts the unified report into an actionable markdown plan
- `scripts/apply_dependency_fixes.py`
  - Runs `pip-audit --fix` with safe defaults and report output
- `scripts/security_json_models.py`
  - Shared validators for Bandit and pip-audit payloads
- `references/api-docs.md`
  - Source links and schema mapping notes
- `references/schemas/*.schema.json`
  - JSON schema contracts for raw and unified reports

## How To Run

From repository root:

```powershell
uv run python .github/skills/python-security-scanning/scripts/run_security_scan.py --target . --output security-scan-report.json
uv run python .github/skills/python-security-scanning/scripts/build_remediation_plan.py --report security-scan-report.json --output security-remediation-plan.md
```

Dependency fix dry run:

```powershell
uv run python .github/skills/python-security-scanning/scripts/apply_dependency_fixes.py --output pip-audit-fix-report.json
```

Apply dependency fixes (writes changes):

```powershell
uv run python .github/skills/python-security-scanning/scripts/apply_dependency_fixes.py --execute --output pip-audit-fix-report.json
```

## Installation Prerequisites

The scripts call external scanner CLIs.

```powershell
uv tool install bandit
uv tool install pip-audit
```

If you prefer project-local tooling:

```powershell
uv add --dev bandit pip-audit
```

## Expected Outputs

- Unified scan report JSON (`unified_scan_schema_version: 1.0.0`)
- Remediation plan markdown with prioritized actions
- Optional pip-audit fix report JSON

## Guardrails

- `apply_dependency_fixes.py` defaults to dry-run mode unless `--execute` is set.
- Bandit and pip-audit exit codes that indicate findings are treated as expected scan outcomes.
- Invalid scanner JSON is treated as a parsing failure and surfaced in the report.
