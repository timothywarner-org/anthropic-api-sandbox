"""Run Python security scans and emit a unified, normalized report.

This script runs:
- Bandit for static code issue detection
- pip-audit for dependency vulnerability detection

Then it validates each raw payload shape and emits one merged JSON report.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from security_json_models import (
    SchemaValidationError,
    validate_bandit_payload,
    validate_pip_audit_payload,
)


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


def _parse_json_output(stdout: str, tool_name: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"{tool_name} did not emit valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SchemaValidationError(f"{tool_name} JSON payload must be an object")

    return payload


def _bandit_findings(bandit_payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for item in bandit_payload["results"]:
        severity = str(item.get("issue_severity", "UNDEFINED")).lower()
        confidence = str(item.get("issue_confidence", "UNDEFINED")).lower()
        issue_text = str(item.get("issue_text", "")).strip()
        more_info = str(item.get("more_info", "")).strip()

        recommendation = (
            f"Review test {item.get('test_id')} and replace insecure pattern. "
            f"Use guidance at {more_info}"
        ).strip()

        findings.append(
            {
                "source": "bandit",
                "category": "code",
                "id": str(item.get("test_id", "unknown")),
                "severity": severity,
                "confidence": confidence,
                "summary": issue_text,
                "recommendation": recommendation,
                "location": {
                    "file": str(item.get("filename", "")),
                    "line": int(item.get("line_number", 0)),
                },
                "metadata": {
                    "test_name": item.get("test_name"),
                    "line_range": item.get("line_range"),
                    "cwe": item.get("issue_cwe"),
                    "more_info": more_info,
                },
            }
        )

    return findings


def _pip_audit_findings(pip_payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    dependencies = pip_payload.get("dependencies", [])
    if not isinstance(dependencies, list):
        return findings

    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue
        if "vulns" not in dependency:
            continue

        package_name = str(dependency.get("name", ""))
        package_version = str(dependency.get("version", ""))
        vulns = dependency.get("vulns", [])
        if not isinstance(vulns, list):
            continue

        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue

            fix_versions_obj = vuln.get("fix_versions", [])
            fix_versions = (
                [str(version) for version in fix_versions_obj]
                if isinstance(fix_versions_obj, list)
                else []
            )

            if fix_versions:
                recommendation = (
                    f"Upgrade {package_name} from {package_version} to one of: "
                    f"{', '.join(fix_versions)}"
                )
            else:
                recommendation = (
                    f"No fixed version published for {package_name} yet. "
                    "Mitigate via compensating controls and monitor advisories."
                )

            findings.append(
                {
                    "source": "pip-audit",
                    "category": "dependency",
                    "id": str(vuln.get("id", "unknown")),
                    "severity": "unknown",
                    "summary": str(vuln.get("description", "Dependency vulnerability detected")),
                    "recommendation": recommendation,
                    "location": {
                        "package": package_name,
                        "version": package_version,
                    },
                    "metadata": {
                        "aliases": vuln.get("aliases", []),
                        "fix_versions": fix_versions,
                    },
                }
            )

    return findings


def _build_pip_audit_command(
    target: str,
    requirements: list[str],
    vulnerability_service: str,
) -> list[str]:
    command = [
        "pip-audit",
        "--format",
        "json",
        "--desc",
        "on",
        "--aliases",
        "on",
        "--vulnerability-service",
        vulnerability_service,
    ]

    if requirements:
        for requirement in requirements:
            command.extend(["-r", requirement])
        return command

    command.append(target)
    return command


def run_scan(args: argparse.Namespace) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    bandit_command = ["bandit", "-r", args.target, "-f", "json", "-q"]
    pip_command = _build_pip_audit_command(
        target=args.target,
        requirements=args.requirement,
        vulnerability_service=args.pip_audit_service,
    )

    bandit_info: dict[str, Any] = {
        "command": bandit_command,
        "exit_code": -1,
        "status": "skipped",
    }
    pip_info: dict[str, Any] = {
        "command": pip_command,
        "exit_code": -1,
        "status": "skipped",
    }

    if not args.skip_bandit:
        bandit_exit_code, bandit_stdout, bandit_stderr = _run_command(
            bandit_command,
            timeout_seconds=args.timeout,
        )
        bandit_info["exit_code"] = bandit_exit_code
        if bandit_stderr:
            bandit_info["stderr"] = bandit_stderr

        if bandit_stdout.strip():
            try:
                bandit_payload = _parse_json_output(bandit_stdout, "Bandit")
                validate_bandit_payload(bandit_payload)
                findings.extend(_bandit_findings(bandit_payload))
                bandit_info["status"] = "ok"
            except SchemaValidationError as exc:
                bandit_info["status"] = "error"
                bandit_info["error"] = str(exc)
        else:
            bandit_info["status"] = "error"
            bandit_info["error"] = "Bandit produced no JSON output"

    if not args.skip_pip_audit:
        pip_exit_code, pip_stdout, pip_stderr = _run_command(
            pip_command,
            timeout_seconds=args.timeout,
        )
        pip_info["exit_code"] = pip_exit_code
        if pip_stderr:
            pip_info["stderr"] = pip_stderr

        if pip_stdout.strip():
            try:
                pip_payload = _parse_json_output(pip_stdout, "pip-audit")
                validate_pip_audit_payload(pip_payload)
                findings.extend(_pip_audit_findings(pip_payload))
                pip_info["status"] = "ok"
            except SchemaValidationError as exc:
                pip_info["status"] = "error"
                pip_info["error"] = str(exc)
        else:
            pip_info["status"] = "error"
            pip_info["error"] = "pip-audit produced no JSON output"

    code_findings = sum(1 for item in findings if item["category"] == "code")
    dependency_findings = sum(1 for item in findings if item["category"] == "dependency")

    report = {
        "unified_scan_schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target": args.target,
        "summary": {
            "total_findings": len(findings),
            "code_findings": code_findings,
            "dependency_findings": dependency_findings,
        },
        "tools": {
            "bandit": bandit_info,
            "pip_audit": pip_info,
        },
        "findings": findings,
    }

    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run Bandit and pip-audit, validate JSON payloads, and emit a unified "
            "security report."
        )
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Directory or project path to scan (default: current directory)",
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
        "--skip-bandit",
        action="store_true",
        help="Skip Bandit code scan",
    )
    parser.add_argument(
        "--skip-pip-audit",
        action="store_true",
        help="Skip pip-audit dependency scan",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-command timeout in seconds",
    )
    parser.add_argument(
        "--output",
        default="security-scan-report.json",
        help="Path to write unified JSON report",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Return exit code 1 when findings are present",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    report = run_scan(args)
    output_path = Path(args.output)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2))
    print(f"Unified security report written to: {output_path}")

    if args.fail_on_findings and report["summary"]["total_findings"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
