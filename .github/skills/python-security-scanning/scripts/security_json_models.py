"""Shared validators for security scanner JSON payloads.

Grounded sources:
- Bandit JSON formatter docs and source
- pip-audit JSON formatter source

See ../references/api-docs.md for canonical URLs.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


class SchemaValidationError(ValueError):
    """Raised when scanner output does not match expected shape."""


def _require_keys(obj: Mapping[str, object], keys: Sequence[str], context: str) -> None:
    missing = [key for key in keys if key not in obj]
    if missing:
        joined = ", ".join(missing)
        raise SchemaValidationError(f"Missing keys in {context}: {joined}")


def validate_bandit_payload(payload: object) -> dict[str, object]:
    """Validate the minimum Bandit JSON contract used by this skill."""
    if not isinstance(payload, dict):
        raise SchemaValidationError("Bandit payload must be a JSON object")

    _require_keys(payload, ("errors", "generated_at", "metrics", "results"), "bandit")

    errors = payload["errors"]
    results = payload["results"]

    if not isinstance(errors, list):
        raise SchemaValidationError("Bandit 'errors' must be an array")
    if not isinstance(results, list):
        raise SchemaValidationError("Bandit 'results' must be an array")

    for index, item in enumerate(results):
        if not isinstance(item, dict):
            raise SchemaValidationError(
                f"Bandit result at index {index} must be an object"
            )
        _require_keys(
            item,
            (
                "filename",
                "issue_confidence",
                "issue_severity",
                "issue_text",
                "line_number",
                "line_range",
                "more_info",
                "test_id",
                "test_name",
            ),
            f"bandit.results[{index}]",
        )

    return payload


def validate_pip_audit_payload(payload: object) -> dict[str, object]:
    """Validate the minimum pip-audit JSON contract used by this skill."""
    if not isinstance(payload, dict):
        raise SchemaValidationError("pip-audit payload must be a JSON object")

    _require_keys(payload, ("dependencies", "fixes"), "pip-audit")

    dependencies = payload["dependencies"]
    fixes = payload["fixes"]

    if not isinstance(dependencies, list):
        raise SchemaValidationError("pip-audit 'dependencies' must be an array")
    if not isinstance(fixes, list):
        raise SchemaValidationError("pip-audit 'fixes' must be an array")

    for index, dep in enumerate(dependencies):
        if not isinstance(dep, dict):
            raise SchemaValidationError(
                f"pip-audit dependency at index {index} must be an object"
            )

        if "skip_reason" in dep:
            _require_keys(dep, ("name", "skip_reason"), f"dependencies[{index}]")
            continue

        _require_keys(dep, ("name", "version", "vulns"), f"dependencies[{index}]")
        vulns = dep["vulns"]
        if not isinstance(vulns, list):
            raise SchemaValidationError(
                f"pip-audit dependencies[{index}].vulns must be an array"
            )

        for vuln_index, vuln in enumerate(vulns):
            if not isinstance(vuln, dict):
                raise SchemaValidationError(
                    "pip-audit vulnerability entry must be an object"
                )
            _require_keys(
                vuln,
                ("id", "fix_versions"),
                f"dependencies[{index}].vulns[{vuln_index}]",
            )

    for index, fix_item in enumerate(fixes):
        if not isinstance(fix_item, dict):
            raise SchemaValidationError(
                f"pip-audit fix at index {index} must be an object"
            )

        if "skip_reason" in fix_item:
            _require_keys(fix_item, ("name", "version", "skip_reason"), f"fixes[{index}]")
        else:
            _require_keys(
                fix_item,
                ("name", "old_version", "new_version"),
                f"fixes[{index}]",
            )

    return payload
