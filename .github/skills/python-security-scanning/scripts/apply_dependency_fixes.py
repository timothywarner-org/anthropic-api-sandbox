"""Run pip-audit fix workflow with schema validation and safe defaults.

Default behavior is dry-run. Use --execute to apply upgrades.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from security_json_models import SchemaValidationError, validate_pip_audit_payload


def _run_command(command: list[str], timeout_seconds: int) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:
        return (127, "", f"Command not found: {command[0]} ({exc})")
    except subprocess.TimeoutExpired as exc:
        return (124, "", f"Command timed out after {timeout_seconds}s ({exc})")

    return (completed.returncode, completed.stdout, completed.stderr)


def _parse_payload(stdout: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"pip-audit did not emit valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SchemaValidationError("pip-audit JSON payload must be an object")

    return payload


def _build_command(args: argparse.Namespace) -> list[str]:
    command = [
        "pip-audit",
        "--fix",
        "--format",
        "json",
        "--desc",
        "on",
        "--aliases",
        "on",
        "--vulnerability-service",
        args.pip_audit_service,
    ]

    if not args.execute:
        command.append("--dry-run")

    if args.requirement:
        for requirement in args.requirement:
            command.extend(["-r", requirement])
    else:
        command.append(args.target)

    return command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run pip-audit --fix workflow and emit structured fix report"
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Project path when not using --requirement",
    )
    parser.add_argument(
        "--requirement",
        action="append",
        default=[],
        help="Requirements file for pip-audit (repeatable)",
    )
    parser.add_argument(
        "--pip-audit-service",
        choices=("pypi", "osv", "esms"),
        default="pypi",
        help="Vulnerability source used by pip-audit",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply fixes; default mode is dry-run",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Command timeout in seconds",
    )
    parser.add_argument(
        "--output",
        default="pip-audit-fix-report.json",
        help="Path to write fix report",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    command = _build_command(args)

    exit_code, stdout, stderr = _run_command(command, timeout_seconds=args.timeout)

    report: dict[str, Any] = {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "execute" if args.execute else "dry-run",
        "command": command,
        "exit_code": exit_code,
    }

    if stderr:
        report["stderr"] = stderr

    if stdout.strip():
        try:
            payload = _parse_payload(stdout)
            validate_pip_audit_payload(payload)
            report["status"] = "ok"
            report["pip_audit"] = payload

            fixes = payload.get("fixes", [])
            if isinstance(fixes, list):
                report["summary"] = {
                    "fix_records": len(fixes),
                    "applied_or_planned": sum(
                        1
                        for item in fixes
                        if isinstance(item, dict) and "new_version" in item
                    ),
                    "skipped": sum(
                        1
                        for item in fixes
                        if isinstance(item, dict) and "skip_reason" in item
                    ),
                }
        except SchemaValidationError as exc:
            report["status"] = "error"
            report["error"] = str(exc)
    else:
        report["status"] = "error"
        report["error"] = "pip-audit produced no JSON output"

    output_path = Path(args.output)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Fix report written to: {output_path}")
    if "summary" in report:
        print(json.dumps(report["summary"], indent=2))

    return 0 if report.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
