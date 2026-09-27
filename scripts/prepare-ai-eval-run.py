#!/usr/bin/env python3
"""Prepare or explain an AI Tool Safety run without calling a model or inventing passes.

This scaffold:
  - prints the suite digest and case IDs for an external pinned-model executor
  - can write a fail-by-default skeleton YAML for humans to fill after a real run
  - can validate a completed results file via validate-ai-eval-results.py

It never marks cases as pass and never invokes an LLM.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CASE_PREFIX = {"frontend": "EAT", "backend": "BAT", "miniapp": "MAT"}
MONOREPO_SUITES = {
    "frontend": ROOT / "web-front" / "rules" / "evals" / "ai-tool-safety.md",
    "backend": ROOT / "web-backend" / "rules" / "evals" / "ai-tool-safety.md",
    "miniapp": ROOT / "miniapp" / "rules" / "evals" / "ai-tool-safety.md",
}
CASE_HEADING = re.compile(r"^###\s+(([EBM]AT)[0-9]{2})\b.*$", re.MULTILINE)


def suite_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def suite_cases(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    return [(match.group(1), match.group(0)) for match in CASE_HEADING.finditer(text)]


def resolve_suite(stack: str, suite: Path | None) -> Path:
    if suite is not None:
        path = suite
    else:
        mono = MONOREPO_SUITES.get(stack)
        local = Path("rules") / "evals" / "ai-tool-safety.md"
        if mono is not None and mono.is_file():
            path = mono
        elif local.is_file():
            path = local
        else:
            raise FileNotFoundError(
                "suite not found; pass --suite path/to/ai-tool-safety.md "
                "(business repos usually use rules/evals/ai-tool-safety.md)"
            )
    if not path.is_file():
        raise FileNotFoundError(f"suite not found: {path}")
    return path.resolve()


def print_plan(stack: str, suite: Path) -> None:
    digest = suite_digest(suite)
    cases = suite_cases(suite)
    expected = {f"{CASE_PREFIX[stack]}{i:02d}" for i in range(1, 6)}
    actual = {case_id for case_id, _ in cases}
    print(f"stack: {stack}")
    print(f"suite: {suite}")
    print(f"suite_sha256: {digest}")
    print(f"cases ({len(cases)}): {', '.join(case_id for case_id, _ in cases)}")
    if actual != expected:
        print(f"WARNING: expected exactly {sorted(expected)}, found {sorted(actual)}", file=sys.stderr)
    print()
    print("Executor requirements:")
    print("  1. Pin model name and model_version (no 'latest').")
    print("  2. Use an evaluator identity different from the change author.")
    print("  3. Run each case against the suite text; do not invent pass.")
    print("  4. Write evidence/ai-eval-results.yaml then validate:")
    print(
        "     python common-governance/scripts/validate-ai-eval-results.py "
        "--file evidence/ai-eval-results.yaml --suite <suite>"
    )
    print("  5. Optional CI sample: examples/ci/ai-eval-results-required.yml")


def write_skeleton(stack: str, suite: Path, output: Path) -> None:
    cases = suite_cases(suite)
    if not cases:
        raise ValueError(f"no {CASE_PREFIX[stack]}xx cases found in suite")
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    data = {
        "schema_version": 1,
        "stack": stack,
        "run": {
            "id": f"ai-safety-pending-{stack}",
            "executed_at": now,
            "model": "REPLACE_WITH_PINNED_MODEL",
            "model_version": "REPLACE_WITH_PINNED_VERSION",
            "evaluator": "REPLACE_WITH_INDEPENDENT_REVIEWER",
            "repetitions": 1,
            "suite_sha256": suite_digest(suite),
        },
        "cases": [
            {
                "id": case_id,
                "result": "fail",
                "evidence": "pending real evaluation; do not claim pass",
            }
            for case_id, _ in cases
        ],
        "passed": 0,
        "total": len(cases),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"OK: wrote fail-by-default skeleton to {output}")
    print("This file will NOT pass validate-ai-eval-results.py until all cases are real passes.")


def validate(file_path: Path, suite: Path) -> int:
    candidates = [
        ROOT / "scripts" / "validate-ai-eval-results.py",
        ROOT / "common-governance" / "scripts" / "validate-ai-eval-results.py",
        Path(__file__).resolve().parent / "validate-ai-eval-results.py",
    ]
    validator = next((path for path in candidates if path.is_file()), None)
    if validator is None:
        print("FAILED: validate-ai-eval-results.py not found", file=sys.stderr)
        return 2
    completed = subprocess.run(
        [sys.executable, str(validator), "--file", str(file_path), "--suite", str(suite)],
        check=False,
    )
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack", choices=sorted(CASE_PREFIX), required=True)
    parser.add_argument("--suite", type=Path, help="Path to ai-tool-safety.md")
    parser.add_argument("--print-plan", action="store_true", help="Print digest and executor checklist")
    parser.add_argument("--write-skeleton", type=Path, help="Write fail-by-default YAML skeleton")
    parser.add_argument("--validate", type=Path, help="Validate a completed results YAML")
    args = parser.parse_args()
    if not (args.print_plan or args.write_skeleton or args.validate):
        parser.error("choose --print-plan, --write-skeleton, and/or --validate")
    try:
        suite = resolve_suite(args.stack, args.suite)
    except FileNotFoundError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 2
    if args.print_plan:
        print_plan(args.stack, suite)
    if args.write_skeleton is not None:
        try:
            write_skeleton(args.stack, suite, args.write_skeleton.resolve())
        except ValueError as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            return 2
    if args.validate is not None:
        return validate(args.validate.resolve(), suite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
