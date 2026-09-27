#!/usr/bin/env python3
"""Validate least-privilege and immutable-action rules for GitHub workflows."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment failure path
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIRS = (
    ".github/workflows",
    "examples/ci",
    "examples/adoption-fixture/frontend/.github/workflows",
    "common-governance/examples/ci",
    "web-backend/rules/examples/ci",
    "web-front/rules/examples/ci",
    "miniapp/rules/examples/ci",
)
USES = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)
IMMUTABLE_ACTION = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
ALLOWED_PERMISSION_VALUES = {"none", "read", "write"}


def workflow_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for rel in WORKFLOW_DIRS:
        directory = root / rel
        if directory.is_dir():
            paths.extend(directory.glob("*.yml"))
            paths.extend(directory.glob("*.yaml"))
    return sorted(set(paths))


def _permissions(value: object, label: str, errors: list[str]) -> dict[str, str]:
    if not isinstance(value, dict):
        errors.append(f"{label}: permissions must be an object")
        return {}
    result: dict[str, str] = {}
    for key, permission in value.items():
        if not isinstance(key, str) or permission not in ALLOWED_PERMISSION_VALUES:
            errors.append(f"{label}: invalid permission {key}={permission}")
            continue
        result[key] = permission
    return result


def validate_workflow(path: Path, root: Path) -> list[str]:
    rel = path.relative_to(root)
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if re.search(r"(?m)^\s*pull_request_target\s*:", text):
        errors.append(f"{rel}: pull_request_target is forbidden in baseline workflows")
    for action in USES.findall(text):
        if action.startswith("./"):
            continue
        if not IMMUTABLE_ACTION.fullmatch(action):
            errors.append(f"{rel}: external action must use a 40-character commit SHA: {action}")

    if yaml is None:
        errors.append(f"{rel}: PyYAML is required")
        return errors
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.append(f"{rel}: invalid YAML: {exc}")
        return errors
    if not isinstance(data, dict):
        errors.append(f"{rel}: workflow root must be an object")
        return errors
    root_permissions = _permissions(data.get("permissions"), str(rel), errors)
    if root_permissions != {"contents": "read"}:
        errors.append(f"{rel}: top-level permissions must be exactly contents: read")

    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        errors.append(f"{rel}: jobs must be an object")
        return errors
    for job_name, job in jobs.items():
        if not isinstance(job, dict) or "permissions" not in job:
            continue
        permissions = _permissions(job.get("permissions"), f"{rel}:{job_name}", errors)
        for key, value in permissions.items():
            if value == "write" and key not in {"id-token", "attestations", "packages"}:
                errors.append(f"{rel}:{job_name}: write permission not allowlisted: {key}")
    return errors


def validate_all(root: Path = ROOT) -> tuple[list[str], int]:
    paths = workflow_paths(root)
    errors = [error for path in paths for error in validate_workflow(path, root)]
    return errors, len(paths)


def main() -> int:
    errors, count = validate_all()
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: workflow security passed ({count} workflows, immutable actions, least privilege)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

