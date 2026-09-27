#!/usr/bin/env python3
"""Generate or verify the distributable common-governance package from root docs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "common-governance"
SOURCE_DOCS = ROOT / "docs"
TARGET_DOCS = PACKAGE / "docs"
DOCS = (
    "project-adoption-guide.md",
    "requirements-traceability.md",
    "business-correctness-review.md",
    "ai-tool-security.md",
    "release-evidence.md",
    "environment-promotion.md",
    "incident-response.md",
    "incident-postmortem-template.md",
    "definition-of-done.md",
    "architect-engineering-checklist.md",
    "rule-exception-process.md",
    "codeowners-matrix.md",
    "supply-chain-baseline.md",
    "data-classification-matrix.md",
    "slo-alerting-template.md",
    "dod-maturity-mapping.md",
    "adoption-scorecard.md",
    "compliance-evidence-log.md",
    "branch-protection.md",
    "git-pr-governance.md",
    "migration-baseline.md",
)
STATIC_PACKAGE_FILES = (
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "examples/commitlint.config.cjs.sample",
    "examples/SECURITY.md.sample",
    "examples/adr-template.md",
    "examples/ci/credential-scan-required.yml",
    "scripts/validate-package.py",
)
GENERATED_FILES = {
    "examples/pull_request_template.md": ROOT / ".github" / "pull_request_template.md",
    "docs/control-catalog.yaml": ROOT / "docs" / "control-catalog.yaml",
    "docs/exceptions/README.md": ROOT / "docs" / "exceptions" / "README.md",
    "scripts/check-project-adoption.py": ROOT / "scripts" / "check-project-adoption.py",
    "scripts/check-debt-baseline.py": ROOT / "scripts" / "check-debt-baseline.py",
    "scripts/validate-ai-eval-results.py": ROOT / "scripts" / "validate-ai-eval-results.py",
    "scripts/prepare-ai-eval-run.py": ROOT / "scripts" / "prepare-ai-eval-run.py",
    "scripts/validate-control-catalog.py": ROOT / "scripts" / "validate-control-catalog.py",
    "scripts/validate-exceptions.py": ROOT / "scripts" / "validate-exceptions.py",
    "scripts/validate-pr-governance.py": ROOT / "scripts" / "validate-pr-governance.py",
    "scripts/validate-release-evidence.py": ROOT / "scripts" / "validate-release-evidence.py",
    "scripts/validate-workflow-security.py": ROOT / "scripts" / "validate-workflow-security.py",
    "examples/release-evidence.yaml": ROOT / "examples" / "release-evidence.yaml",
    "examples/rule-exception.yaml": ROOT / "examples" / "rule-exception.yaml",
    "examples/ci/artifact-trust-required.yml": ROOT / "examples" / "ci" / "artifact-trust-required.yml",
    "examples/ci/supply-chain-required.yml": ROOT / "examples" / "ci" / "supply-chain-required.yml",
    "examples/ci/rules-adoption-required.yml": ROOT / "examples" / "ci" / "rules-adoption-required.yml",
    "examples/ci/debt-baseline-required.yml": ROOT / "examples" / "ci" / "debt-baseline-required.yml",
    "examples/ci/exceptions-required.yml": ROOT / "examples" / "ci" / "exceptions-required.yml",
    "examples/ci/ai-eval-results-required.yml": ROOT / "examples" / "ci" / "ai-eval-results-required.yml",
    "examples/ai-eval-results.yaml": ROOT / "examples" / "ai-eval-results.yaml",
    "examples/governance-adoption.yaml": ROOT / "examples" / "governance-adoption.yaml",
    "examples/governance-platform-evidence.json": ROOT / "examples" / "governance-platform-evidence.json",
    "examples/PROJECT_RULES.md.sample": ROOT / "examples" / "PROJECT_RULES.md.sample",
    "examples/contract-baseline.md.sample": ROOT / "examples" / "contract-baseline.md.sample",
    "examples/migration-baseline.json": ROOT / "examples" / "migration-baseline.json",
}


def manifest_files() -> tuple[str, ...]:
    return tuple(f"docs/{name}" for name in DOCS) + STATIC_PACKAGE_FILES + tuple(GENERATED_FILES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_manifest() -> dict[str, object]:
    version = (PACKAGE / "VERSION").read_text(encoding="utf-8").strip()
    return {
        "version": version,
        "source": "code-rules/docs",
        "files": {rel: sha256(PACKAGE / rel) for rel in manifest_files()},
    }


def write_package() -> None:
    TARGET_DOCS.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        shutil.copyfile(SOURCE_DOCS / name, TARGET_DOCS / name)
    for rel, source in GENERATED_FILES.items():
        target = PACKAGE / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    manifest = expected_manifest()
    with (PACKAGE / "MANIFEST.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def check_package() -> list[str]:
    errors: list[str] = []
    for name in DOCS:
        source = SOURCE_DOCS / name
        target = TARGET_DOCS / name
        if not source.is_file():
            errors.append(f"missing source docs/{name}")
        elif not target.is_file():
            errors.append(f"missing package docs/{name}")
        elif source.read_bytes() != target.read_bytes():
            errors.append(f"drift: docs/{name}")

    expected_docs = set(DOCS)
    actual_docs = {path.name for path in TARGET_DOCS.glob("*.md")}
    for name in sorted(actual_docs - expected_docs):
        errors.append(f"unexpected generated doc: docs/{name}")

    for rel, source in GENERATED_FILES.items():
        target = PACKAGE / rel
        if not source.is_file():
            errors.append(f"missing source {source.relative_to(ROOT)}")
        elif not target.is_file():
            errors.append(f"missing package {rel}")
        elif source.read_bytes() != target.read_bytes():
            errors.append(f"drift: {rel}")

    for rel in STATIC_PACKAGE_FILES:
        if not (PACKAGE / rel).is_file():
            errors.append(f"missing common-governance/{rel}")

    manifest_path = PACKAGE / "MANIFEST.json"
    if not manifest_path.is_file():
        errors.append("missing common-governance/MANIFEST.json")
    elif not errors:
        try:
            actual_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"common-governance/MANIFEST.json is invalid: {exc.msg}")
        else:
            if actual_manifest != expected_manifest():
                errors.append("common-governance/MANIFEST.json is stale")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Regenerate package docs and manifest")
    args = parser.parse_args()
    if args.write:
        write_package()
    errors = check_package()
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: common-governance {len(DOCS)} docs match root SSOT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
