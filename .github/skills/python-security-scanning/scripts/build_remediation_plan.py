"""Generate a prioritized remediation plan from unified security scan JSON."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

SEVERITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "undefined": 3,
    "unknown": 4,
}


def _normalize_severity(value: str) -> str:
    return value.strip().lower() if value else "unknown"


def _load_report(path: str) -> dict[str, Any]:
    report_path = Path(path)
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Unified report must be a JSON object")
    findings = payload.get("findings")
    if not isinstance(findings, list):
        raise ValueError("Unified report must contain a findings array")
    return payload


def _format_code_finding(item: dict[str, Any]) -> str:
    location = item.get("location", {})
    file_name = location.get("file", "unknown-file")
    line = location.get("line", "?")
    return (
        f"- [{item.get('severity', 'unknown').upper()}] "
        f"{item.get('id', 'unknown-id')} at {file_name}:{line} - "
        f"{item.get('recommendation', 'No recommendation provided')}"
    )


def _format_dependency_finding(item: dict[str, Any]) -> str:
    location = item.get("location", {})
    package_name = location.get("package", "unknown-package")
    version = location.get("version", "unknown-version")

    metadata = item.get("metadata", {})
    fix_versions = metadata.get("fix_versions", []) if isinstance(metadata, dict) else []
    fix_text = ", ".join(fix_versions) if isinstance(fix_versions, list) and fix_versions else "none published"

    return (
        f"- {package_name} {version} -> {item.get('id', 'unknown-id')} "
        f"(fix versions: {fix_text})"
    )


def _sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        findings,
        key=lambda item: SEVERITY_ORDER.get(_normalize_severity(str(item.get("severity", "unknown"))), 99),
    )


def build_plan(report: dict[str, Any]) -> str:
    findings = report.get("findings", [])

    code_findings: list[dict[str, Any]] = []
    dependency_findings: list[dict[str, Any]] = []

    for item in findings:
        if not isinstance(item, dict):
            continue
        category = item.get("category")
        if category == "code":
            code_findings.append(item)
        elif category == "dependency":
            dependency_findings.append(item)

    dependency_grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in dependency_findings:
        location = item.get("location", {})
        package_name = location.get("package", "unknown-package")
        dependency_grouped[str(package_name)].append(item)

    lines: list[str] = []
    lines.append("# Security Remediation Plan")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total findings: {len(findings)}")
    lines.append(f"- Code findings: {len(code_findings)}")
    lines.append(f"- Dependency findings: {len(dependency_findings)}")
    lines.append("")

    lines.append("## Priority Actions")
    lines.append("")
    lines.append("1. Fix HIGH code findings first.")
    lines.append("2. Upgrade dependencies with known fix versions.")
    lines.append("3. Add tests to prevent regressions after each fix.")
    lines.append("")

    lines.append("## Code Findings")
    lines.append("")
    if not code_findings:
        lines.append("- No code findings detected.")
    else:
        for item in _sort_findings(code_findings):
            lines.append(_format_code_finding(item))
    lines.append("")

    lines.append("## Dependency Findings")
    lines.append("")
    if not dependency_findings:
        lines.append("- No dependency findings detected.")
    else:
        for package_name in sorted(dependency_grouped):
            package_findings = dependency_grouped[package_name]
            lines.append(f"### {package_name}")
            for item in package_findings:
                lines.append(_format_dependency_finding(item))
            lines.append("")

    lines.append("## Verification Checklist")
    lines.append("")
    lines.append("- Re-run unified scan after remediation.")
    lines.append("- Confirm findings were reduced or resolved.")
    lines.append("- Run test suite after dependency upgrades.")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build markdown remediation plan from unified security report"
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to unified JSON report from run_security_scan.py",
    )
    parser.add_argument(
        "--output",
        default="security-remediation-plan.md",
        help="Path to write remediation markdown",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    report = _load_report(args.report)
    markdown_plan = build_plan(report)

    output_path = Path(args.output)
    output_path.write_text(markdown_plan, encoding="utf-8")

    print(f"Remediation plan written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
