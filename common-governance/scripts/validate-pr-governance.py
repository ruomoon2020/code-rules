#!/usr/bin/env python3
"""Validate that a pull request body contains actionable governance evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKED = re.compile(r"(?m)^\s*-\s*\[[xX]\]\s+(.+)$")
TABLE_ROW = re.compile(r"(?m)^\|([^\n]+)\|\s*$")
PLACEHOLDER = re.compile(r"_{4,}|\b(?:TODO|TBD|待补充)\b", re.IGNORECASE)


def _heading(body: str, words: str) -> bool:
    return re.search(rf"(?im)^#{{1,6}}\s+.*(?:{words})", body) is not None


def validate_body(body: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(body, str) or len(body.strip()) < 80:
        return ["pull request body is missing or too short"]
    for label, words in {
        "change summary": r"变更摘要|change summary",
        "requirement traceability": r"需求|issue|requirement|acceptance",
        "risk": r"风险|risk",
        "rollback": r"回滚|rollback",
        "validation commands": r"已运行命令|commands? run|validation",
    }.items():
        if not _heading(body, words):
            errors.append(f"missing {label} heading")

    rows: list[list[str]] = []
    for match in TABLE_ROW.finditer(body):
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if len(cells) >= 6 and not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            rows.append(cells)
    data_rows = [
        row for row in rows
        if not re.search(r"需求|requirement", row[0], re.IGNORECASE)
        and all(cell for cell in row[:6])
    ]
    if not data_rows:
        errors.append("requirement traceability table needs at least one completed six-column row")

    checked = CHECKED.findall(body)
    risk_choices = [item for item in checked if re.match(r"(?:Low|Medium|High|Critical)\b", item)]
    if len(risk_choices) != 1:
        errors.append("exactly one risk level must be checked")
    change_types = [
        item for item in checked
        if re.search(r"API|DB|安全|依赖|任务|配置|规则包|仅文档|其他", item, re.IGNORECASE)
    ]
    if not change_types:
        errors.append("at least one change type must be checked")
    if PLACEHOLDER.search(body):
        errors.append("pull request body still contains TODO/TBD or underscore placeholders")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path)
    source.add_argument("--event", type=Path)
    args = parser.parse_args()
    try:
        if args.event:
            event = json.loads(args.event.read_text(encoding="utf-8"))
            body = event.get("pull_request", {}).get("body")
        else:
            body = args.file.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: cannot read PR governance input: {exc}", file=sys.stderr)
        return 1
    errors = validate_body(body)
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK: pull request governance evidence is complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
