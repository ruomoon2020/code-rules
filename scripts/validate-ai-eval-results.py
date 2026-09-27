#!/usr/bin/env python3
"""Validate machine-readable AI tool safety evaluation results."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml


CASE_PREFIX = {"frontend": "EAT", "backend": "BAT", "miniapp": "MAT"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDERS = {"todo", "tbd", "unknown", "latest", "placeholder", "pinned-by-ci-input"}


def _aware_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_results(data: object, suite_path: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["result root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    stack = data.get("stack")
    if stack not in CASE_PREFIX:
        errors.append("stack must be frontend, backend, or miniapp")
        expected_ids: set[str] = set()
    else:
        expected_ids = {f"{CASE_PREFIX[stack]}{index:02d}" for index in range(1, 6)}

    run = data.get("run")
    if not isinstance(run, dict):
        errors.append("run must be an object")
        run = {}
    for field in ("id", "model", "model_version", "evaluator"):
        if (
            not isinstance(run.get(field), str)
            or len(run[field].strip()) < 3
            or run[field].strip().lower() in PLACEHOLDERS
        ):
            errors.append(f"run.{field} must be meaningful")
    if not _aware_timestamp(run.get("executed_at")):
        errors.append("run.executed_at must be an ISO-8601 timestamp with timezone")
    if not isinstance(run.get("repetitions"), int) or run["repetitions"] < 1:
        errors.append("run.repetitions must be an integer >= 1")
    digest = run.get("suite_sha256")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        errors.append("run.suite_sha256 must be a lowercase SHA-256")
    elif not suite_path.is_file():
        errors.append(f"suite file not found: {suite_path}")
    else:
        suite_bytes = suite_path.read_bytes()
        if hashlib.sha256(suite_bytes).hexdigest() != digest:
            errors.append("run.suite_sha256 does not match the evaluated suite")
        suite_ids = set(
            re.findall(r"^###\s+([EBM]AT[0-9]{2})\b", suite_bytes.decode("utf-8"), re.MULTILINE)
        )
        if suite_ids != expected_ids:
            errors.append("evaluated suite must contain exactly the expected five safety cases")

    cases = data.get("cases")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        cases = []
    actual_ids: list[str] = []
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = case.get("id")
        if isinstance(case_id, str):
            actual_ids.append(case_id)
        else:
            errors.append(f"{label}.id must be a string")
        if case.get("result") != "pass":
            errors.append(f"{label}.result must be pass")
        if not isinstance(case.get("evidence"), str) or len(case["evidence"].strip()) < 8:
            errors.append(f"{label}.evidence must be meaningful")
    if len(actual_ids) != len(set(actual_ids)):
        errors.append("case ids must be unique")
    if set(actual_ids) != expected_ids:
        errors.append(f"cases must contain exactly: {', '.join(sorted(expected_ids))}")
    if data.get("passed") != len(expected_ids) or data.get("total") != len(expected_ids):
        errors.append("passed and total must equal the complete 5/5 safety suite")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--suite", type=Path, required=True)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.file.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAILED: cannot read AI eval results: {exc}", file=sys.stderr)
        return 1
    errors = validate_results(data, args.suite.resolve())
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: {data['stack']} AI tool safety results are 5/5 and suite-bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
