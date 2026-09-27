#!/usr/bin/env python3
"""Validate the versioned governance control catalog and its local evidence paths."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "docs" / "control-catalog.yaml"
CONTROL_ID = re.compile(r"^CR-[A-Z]+-[0-9]{3}$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
STANDARD_PREFIXES = {
    "nist-ssdf": "NIST-SSDF-v1.1-",
    "owasp-asvs": "OWASP-ASVS-v5.0.0-",
    "openssf-osps": "OpenSSF-OSPS-2026-02-19-",
    "slsa": "SLSA-v1.1-",
}
EXPECTED_VERSIONS = {
    "nist-ssdf": "1.1",
    "owasp-asvs": "5.0.0",
    "openssf-osps": "2026-02-19",
    "slsa": "1.1",
}
VERIFICATION_KINDS = {"evidence", "presence", "manual"}


def _safe_path(root: Path, value: str) -> Path | None:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def validate_catalog(data: object, root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["catalog root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(data.get("catalog_version"), str) or not SEMVER.fullmatch(data["catalog_version"]):
        errors.append("catalog_version must be semantic version x.y.z")

    standards = data.get("standards")
    if not isinstance(standards, dict):
        errors.append("standards must be an object")
        standards = {}
    for standard, version in EXPECTED_VERSIONS.items():
        entry = standards.get(standard)
        if not isinstance(entry, dict):
            errors.append(f"standards.{standard} is required")
            continue
        if str(entry.get("version")) != version:
            errors.append(f"standards.{standard}.version must be {version}")
        if not isinstance(entry.get("url"), str) or not entry["url"].startswith("https://"):
            errors.append(f"standards.{standard}.url must be an https URL")

    controls = data.get("controls")
    if not isinstance(controls, list) or not controls:
        return errors + ["controls must be a non-empty list"]

    seen_ids: set[str] = set()
    covered_standards: set[str] = set()
    covered_levels: set[int] = set()
    for index, control in enumerate(controls):
        label = f"controls[{index}]"
        if not isinstance(control, dict):
            errors.append(f"{label} must be an object")
            continue
        control_id = control.get("id")
        if not isinstance(control_id, str) or not CONTROL_ID.fullmatch(control_id):
            errors.append(f"{label}.id must match {CONTROL_ID.pattern}")
        elif control_id in seen_ids:
            errors.append(f"duplicate control id {control_id}")
        else:
            seen_ids.add(control_id)
        for field in ("title", "owner_role"):
            if not isinstance(control.get(field), str) or len(control[field].strip()) < 3:
                errors.append(f"{label}.{field} must be meaningful")
        level = control.get("level")
        if not isinstance(level, int) or level not in range(4):
            errors.append(f"{label}.level must be 0, 1, 2, or 3")
        else:
            covered_levels.add(level)

        references = control.get("standards")
        if not isinstance(references, list) or not references:
            errors.append(f"{label}.standards must be a non-empty list")
        else:
            for reference in references:
                if not isinstance(reference, str):
                    errors.append(f"{label}.standards entries must be strings")
                    continue
                matched = [name for name, prefix in STANDARD_PREFIXES.items() if reference.startswith(prefix)]
                if not matched:
                    errors.append(f"{label} has unversioned or unknown standard reference: {reference}")
                else:
                    covered_standards.update(matched)

        kind = control.get("verification_kind")
        if kind not in VERIFICATION_KINDS:
            errors.append(f"{label}.verification_kind must be one of {sorted(VERIFICATION_KINDS)}")

        for field in ("rules", "verification"):
            paths = control.get(field)
            if not isinstance(paths, list) or not paths:
                errors.append(f"{label}.{field} must be a non-empty list")
                continue
            for value in paths:
                if not isinstance(value, str):
                    errors.append(f"{label}.{field} entries must be strings")
                    continue
                path = _safe_path(root, value)
                if path is None:
                    errors.append(f"{label}.{field} path escapes package root: {value}")
                elif not path.is_file():
                    errors.append(f"{label}.{field} path not found: {value}")

        evidence = control.get("evidence")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(item, str) or len(item.strip()) < 3 for item in evidence
        ):
            errors.append(f"{label}.evidence must be a non-empty list of meaningful strings")

        if control.get("id") == "CR-AI-001":
            if control.get("level") == 0:
                errors.append("CR-AI-001 must not be Level 0; 5/5 suite is a conditional release gate")
            if control.get("gate") != "release_or_high_risk_ai_change":
                errors.append("CR-AI-001.gate must be release_or_high_risk_ai_change")
            if kind != "evidence":
                errors.append("CR-AI-001.verification_kind must be evidence")

    missing_standards = set(STANDARD_PREFIXES) - covered_standards
    if missing_standards:
        errors.append(f"controls do not cover standards: {', '.join(sorted(missing_standards))}")
    missing_levels = set(range(4)) - covered_levels
    if missing_levels:
        errors.append(f"controls do not cover maturity levels: {', '.join(map(str, sorted(missing_levels)))}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    path = args.file.resolve()
    root = path.parent.parent if path.parent.name == "docs" else ROOT
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAILED: cannot read control catalog: {exc}", file=sys.stderr)
        return 1
    errors = validate_catalog(data, root)
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: control catalog {data['catalog_version']} ({len(data['controls'])} controls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
