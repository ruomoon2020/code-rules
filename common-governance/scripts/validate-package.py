#!/usr/bin/env python3
"""Validate a distributed common-governance package without the source monorepo."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "docs/adoption-scorecard.md",
    "docs/ai-tool-security.md",
    "docs/branch-protection.md",
    "docs/business-correctness-review.md",
    "docs/codeowners-matrix.md",
    "docs/compliance-evidence-log.md",
    "docs/control-catalog.yaml",
    "docs/data-classification-matrix.md",
    "docs/definition-of-done.md",
    "docs/architect-engineering-checklist.md",
    "docs/dod-maturity-mapping.md",
    "docs/exceptions/README.md",
    "docs/git-pr-governance.md",
    "docs/migration-baseline.md",
    "docs/environment-promotion.md",
    "docs/incident-response.md",
    "docs/incident-postmortem-template.md",
    "docs/project-adoption-guide.md",
    "docs/release-evidence.md",
    "docs/requirements-traceability.md",
    "docs/rule-exception-process.md",
    "docs/slo-alerting-template.md",
    "docs/supply-chain-baseline.md",
    "examples/commitlint.config.cjs.sample",
    "examples/pull_request_template.md",
    "examples/SECURITY.md.sample",
    "examples/adr-template.md",
    "examples/release-evidence.yaml",
    "examples/rule-exception.yaml",
    "examples/ci/credential-scan-required.yml",
    "examples/ci/artifact-trust-required.yml",
    "examples/ci/rules-adoption-required.yml",
    "examples/ci/debt-baseline-required.yml",
    "examples/ci/exceptions-required.yml",
    "examples/ci/supply-chain-required.yml",
    "examples/ci/ai-eval-results-required.yml",
    "examples/governance-adoption.yaml",
    "examples/governance-platform-evidence.json",
    "examples/PROJECT_RULES.md.sample",
    "examples/contract-baseline.md.sample",
    "examples/migration-baseline.json",
    "examples/ai-eval-results.yaml",
    "scripts/check-project-adoption.py",
    "scripts/check-debt-baseline.py",
    "scripts/validate-ai-eval-results.py",
    "scripts/prepare-ai-eval-run.py",
    "scripts/validate-control-catalog.py",
    "scripts/validate-exceptions.py",
    "scripts/validate-pr-governance.py",
    "scripts/validate-release-evidence.py",
    "scripts/validate-workflow-security.py",
    "scripts/validate-package.py",
)
VERSION_HEADING = re.compile(r"^##\s+([^\s]+)", re.MULTILINE)
PROJECT_RULES_TESTING_MARKERS = (
    "## 测试治理参数",
    "覆盖率策略",
    "兼容窗口",
    "flaky 治理",
    "失败证据",
    "测试数据",
    "风险专项",
)


def safe_package_path(rel: str) -> Path | None:
    path = (ROOT / rel).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        return None
    return path


def main() -> int:
    manifest_path = ROOT / "MANIFEST.json"
    if not manifest_path.is_file():
        print("FAILED: MANIFEST.json is missing", file=sys.stderr)
        return 1
    errors: list[str] = []
    try:
        raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: invalid MANIFEST.json: {exc}", file=sys.stderr)
        return 1
    if not isinstance(raw_manifest, dict):
        print("FAILED: MANIFEST.json root must be an object", file=sys.stderr)
        return 1
    manifest = raw_manifest

    files = manifest.get("files")
    if not isinstance(files, dict):
        errors.append("manifest files must be an object")
        files = {}

    required = set(REQUIRED_FILES)
    listed = set(files)
    for rel in sorted(required - listed):
        errors.append(f"manifest missing required entry {rel}")
    for rel in sorted(listed - required):
        errors.append(f"manifest has unexpected entry {rel}")

    for rel, expected in files.items():
        path = safe_package_path(rel)
        if path is None:
            errors.append(f"manifest path escapes package root: {rel}")
            continue
        if not path.is_file():
            errors.append(f"missing {rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"checksum mismatch {rel}")
    version_path = ROOT / "VERSION"
    if not version_path.is_file():
        version = "<missing>"
        errors.append("VERSION is missing")
    else:
        version = version_path.read_text(encoding="utf-8").strip()
        if manifest.get("version") != version:
            errors.append("manifest version does not match VERSION")

    changelog_path = ROOT / "CHANGELOG.md"
    if changelog_path.is_file():
        latest = VERSION_HEADING.search(changelog_path.read_text(encoding="utf-8"))
        if not latest or latest.group(1) != version:
            errors.append("CHANGELOG latest version does not match VERSION")
    project_rules_path = ROOT / "examples" / "PROJECT_RULES.md.sample"
    if project_rules_path.is_file():
        project_rules = project_rules_path.read_text(encoding="utf-8")
        missing_markers = [
            marker for marker in PROJECT_RULES_TESTING_MARKERS if marker not in project_rules
        ]
        if missing_markers:
            errors.append(
                "PROJECT_RULES testing governance markers missing: "
                + ", ".join(missing_markers)
            )
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: common-governance {version} package consistency passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
