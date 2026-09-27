#!/usr/bin/env python3
"""Validate machine-readable, time-boxed governance exception records."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXCEPTION_ID = re.compile(r"^EXC-[0-9]{4}-[0-9]{3,}$")
PLACEHOLDERS = {"todo", "tbd", "unknown", "example", "placeholder", "n/a"}


def _text(data: dict[str, object], field: str, errors: list[str]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or len(value.strip()) < 3 or value.strip().lower() in PLACEHOLDERS:
        errors.append(f"{field} must be meaningful")
        return None
    return value.strip()


def _date(data: dict[str, object], field: str, errors: list[str]) -> dt.date | None:
    value = data.get(field)
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        errors.append(f"{field} must be YYYY-MM-DD")
        return None


def validate_exception(data: object, as_of: dt.date) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["exception root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    exception_id = data.get("id")
    if not isinstance(exception_id, str) or not EXCEPTION_ID.fullmatch(exception_id):
        errors.append(f"id must match {EXCEPTION_ID.pattern}")
    status = data.get("status")
    if status not in {"open", "closed"}:
        errors.append("status must be open or closed")
    for field in ("rule", "reason", "scope", "owner", "risk_acceptor", "close_condition"):
        _text(data, field, errors)
    controls = data.get("compensating_controls")
    if not isinstance(controls, list) or not controls or any(
        not isinstance(item, str) or len(item.strip()) < 3 for item in controls
    ):
        errors.append("compensating_controls must be a non-empty list")
    approvals = data.get("approvals")
    if not isinstance(approvals, list) or not approvals:
        errors.append("approvals must be a non-empty list")
    else:
        for index, approval in enumerate(approvals):
            if not isinstance(approval, dict):
                errors.append(f"approvals[{index}] must be an object")
                continue
            for field in ("role", "approver", "approved_at"):
                value = approval.get(field)
                if not isinstance(value, str) or len(value.strip()) < 3:
                    errors.append(f"approvals[{index}].{field} must be meaningful")

    starts_at = _date(data, "starts_at", errors)
    expires_at = _date(data, "expires_at", errors)
    review_due = _date(data, "review_due", errors)
    if starts_at and expires_at:
        if expires_at < starts_at:
            errors.append("expires_at must not precede starts_at")
        elif (expires_at - starts_at).days > 90:
            errors.append("exception duration must not exceed 90 days")
    if starts_at and review_due and not starts_at <= review_due:
        errors.append("review_due must not precede starts_at")
    if expires_at and review_due and review_due > expires_at:
        errors.append("review_due must not be after expires_at")

    if status == "open" and expires_at and expires_at < as_of:
        errors.append("open exception is expired")
    if status == "closed":
        closed_at = _date(data, "closed_at", errors)
        _text(data, "closure_evidence", errors)
        if closed_at and starts_at and closed_at < starts_at:
            errors.append("closed_at must not precede starts_at")
    return errors


def exception_paths(root: Path) -> list[Path]:
    directory = root / "docs" / "exceptions"
    if not directory.is_dir():
        return []
    return sorted((*directory.glob("*.yaml"), *directory.glob("*.yml")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--file", type=Path, action="append", default=[])
    parser.add_argument("--as-of", type=dt.date.fromisoformat, default=dt.date.today())
    args = parser.parse_args()
    root = args.root.resolve()
    paths = [path.resolve() for path in args.file] or exception_paths(root)
    errors: list[str] = []
    seen_ids: set[str] = set()
    for path in paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"{path}: cannot read exception: {exc}")
            continue
        label = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        record_errors = validate_exception(data, args.as_of)
        errors.extend(f"{label}: {error}" for error in record_errors)
        if isinstance(data, dict) and isinstance(data.get("id"), str):
            if data["id"] in seen_ids:
                errors.append(f"{label}: duplicate exception id {data['id']}")
            seen_ids.add(data["id"])
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: governance exceptions passed ({len(paths)} records, as of {args.as_of.isoformat()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
