#!/usr/bin/env python3
"""Fail when configured legacy debt grows beyond an approved baseline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read baseline config: {exc}") from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("baseline config version must be 1")
    commit = data.get("baseline_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError("baseline_commit must be a 40-character git SHA")
    captured_at = data.get("captured_at")
    if not isinstance(captured_at, str) or not re.search(r"[Zz]|[+-]\d{2}:\d{2}$", captured_at):
        raise ValueError("captured_at must be an ISO-8601 timestamp with timezone")
    owner = data.get("owner")
    if not isinstance(owner, str) or len(owner.strip()) < 2:
        raise ValueError("owner must be a non-empty string")
    scan_command = data.get("scan_command")
    if not isinstance(scan_command, str) or len(scan_command.strip()) < 3:
        raise ValueError("scan_command must be a non-empty string")
    if not isinstance(data.get("metrics"), list) or not data["metrics"]:
        raise ValueError("baseline config metrics must be a non-empty list")
    return data


def resolve_root(config_path: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("metric root must be a non-empty string")
    root = (config_path.parent / value).resolve()
    if not root.is_dir():
        raise ValueError(f"metric root is not a directory: {value}")
    return root


def collect_files(root: Path, globs: object) -> list[Path]:
    if not isinstance(globs, list) or not globs or not all(isinstance(item, str) for item in globs):
        raise ValueError("metric globs must be a non-empty string list")
    files: set[Path] = set()
    for pattern in globs:
        for path in root.glob(pattern):
            if path.is_file():
                files.add(path.resolve())
    return sorted(files)


def require_scan_coverage(metric: dict[str, Any], files: list[Path]) -> None:
    minimum = metric.get("minimum_files", 1)
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
        raise ValueError("minimum_files must be a non-negative integer")
    if minimum == 0:
        reason = metric.get("allow_empty_reason")
        if not isinstance(reason, str) or len(reason.strip()) < 8:
            raise ValueError("minimum_files=0 requires allow_empty_reason")
    if len(files) < minimum:
        raise ValueError(f"scan matched {len(files)} files; expected at least {minimum}; check root and globs")


def regex_count(metric: dict[str, Any], config_path: Path) -> tuple[dict[str, Any], bool]:
    root = resolve_root(config_path, metric.get("root", "."))
    files = collect_files(root, metric.get("globs"))
    require_scan_coverage(metric, files)
    pattern_value = metric.get("pattern")
    maximum = metric.get("maximum")
    if not isinstance(pattern_value, str) or not pattern_value:
        raise ValueError("regex-count pattern must be a non-empty string")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 0:
        raise ValueError("regex-count maximum must be a non-negative integer")
    try:
        pattern = re.compile(pattern_value, re.MULTILINE)
    except re.error as exc:
        raise ValueError(f"invalid regex-count pattern: {exc}") from exc
    current = 0
    for path in files:
        current += len(pattern.findall(path.read_text(encoding="utf-8", errors="replace")))
    result = {
        "name": metric.get("name"),
        "kind": "regex-count",
        "baseline": maximum,
        "current": current,
        "delta": current - maximum,
        "files_scanned": len(files),
    }
    return result, current <= maximum


def path_allowlist(metric: dict[str, Any], config_path: Path) -> tuple[dict[str, Any], bool]:
    root = resolve_root(config_path, metric.get("root", "."))
    files = collect_files(root, metric.get("globs"))
    require_scan_coverage(metric, files)
    allowed_value = metric.get("allowed")
    if not isinstance(allowed_value, list) or not all(isinstance(item, str) for item in allowed_value):
        raise ValueError("path-allowlist allowed must be a string list")
    allowed = {Path(item).as_posix().lstrip("./") for item in allowed_value}
    current = {path.relative_to(root).as_posix() for path in files}
    added = sorted(current - allowed)
    removed = sorted(allowed - current)
    result = {
        "name": metric.get("name"),
        "kind": "path-allowlist",
        "baseline": len(allowed),
        "current": len(current),
        "delta": len(current) - len(allowed),
        "added": added,
        "removed": removed,
        "files_scanned": len(files),
    }
    return result, not added


def evaluate(config_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    data = load_config(config_path)
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    names: set[str] = set()
    handlers = {"regex-count": regex_count, "path-allowlist": path_allowlist}
    for index, raw_metric in enumerate(data["metrics"], start=1):
        if not isinstance(raw_metric, dict):
            errors.append(f"metric {index}: must be an object")
            continue
        name = raw_metric.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"metric {index}: name must be a non-empty string")
            continue
        if name in names:
            errors.append(f"metric {name}: duplicate name")
            continue
        names.add(name)
        handler = handlers.get(raw_metric.get("kind"))
        if handler is None:
            errors.append(f"metric {name}: unsupported kind {raw_metric.get('kind')!r}")
            continue
        try:
            result, passed = handler(raw_metric, config_path)
        except (OSError, ValueError) as exc:
            errors.append(f"metric {name}: {exc}")
            continue
        results.append(result)
        if not passed:
            errors.append(f"metric {name}: debt baseline exceeded")
    return results, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True, help="Path to migration baseline JSON")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    config_path = args.config.resolve()
    try:
        results, errors = evaluate(config_path)
    except ValueError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps({"passed": not errors, "metrics": results, "errors": errors}, ensure_ascii=False))
    else:
        for result in results:
            line = (
                f"{result['name']}: baseline={result['baseline']} current={result['current']} "
                f"delta={result['delta']:+d}"
            )
            if result["kind"] == "path-allowlist":
                line += f" added={result['added']} removed={result['removed']}"
            print(line)
        if errors:
            print("FAILED:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
    if errors:
        return 1
    if args.format == "text":
        print("OK: debt baseline did not grow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
