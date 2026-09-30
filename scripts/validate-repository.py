#!/usr/bin/env python3
"""Validate repository-level documentation and configuration hygiene."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".mdc", ".py", ".yml", ".yaml", ".json", ".cjs", ".mjs", ".ts"}
LINK_SUFFIXES = {".md", ".mdc"}
SKIP_PARTS = {".git", ".history", ".pytest_cache", "node_modules", "__pycache__"}
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
RELEASE_VERSION = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
VERSION_FILES = (
    "VERSION",
    "common-governance/VERSION",
    "web-front/rules/VERSION",
    "web-backend/rules/VERSION",
    "miniapp/rules/VERSION",
)
SHARED_RULE_DIRECTORIES = (
    "web-front/rules/shared",
    "web-backend/rules/shared",
    "miniapp/rules/shared",
)
CODEX_DOCUMENT_DIRECTORIES = (
    "web-front/rules/codex",
    "web-backend/rules/codex",
    "miniapp/rules/codex",
)
CJK_CHARACTER = re.compile(r"[\u4e00-\u9fff]")
NUMBERED_H1 = re.compile(r"^#\s+\d{2}(?:\s|\b)")
CHECKLIST_RULE_PATH = re.compile(
    r"`((?:web-front|web-backend|miniapp)/rules/(?:shared|docs)/[^`]+\.md)`"
)
BARE_RULE_REFERENCE = re.compile(
    r"`(?:shared/)?(?!99-project-local(?:\.md)?`)\d{2}(?:-[a-z0-9-]+)?(?:\.md)?`"
)


def repository_files(root: Path, suffixes: set[str]):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        yield path


def check_trailing_whitespace(root: Path) -> list[str]:
    errors: list[str] = []
    for path in repository_files(root, TEXT_SUFFIXES):
        relative = path.relative_to(root)
        if relative.parts[:2] == ("docs", "archive"):
            continue
        text = path.read_text(encoding="utf-8-sig")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                errors.append(f"trailing whitespace: {relative.as_posix()}:{line_number}")
    return errors


def check_local_links(root: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    checked = 0
    for path in repository_files(root, LINK_SUFFIXES):
        text = path.read_text(encoding="utf-8-sig")
        for match in LINK_PATTERN.finditer(text):
            raw = match.group(1).strip()
            if not raw or raw.startswith(("#", "http://", "https://", "mailto:", "app://")):
                continue
            target = unquote(raw.split("#", 1)[0].strip("<>"))
            if not target:
                continue
            checked += 1
            candidate = (path.parent / target).resolve()
            if not candidate.exists():
                line = text.count("\n", 0, match.start()) + 1
                relative = path.relative_to(root).as_posix()
                errors.append(f"missing local link: {relative}:{line} -> {raw}")
    return errors, checked


def check_yaml(root: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    checked = 0
    for path in repository_files(root, {".yml", ".yaml"}):
        checked += 1
        try:
            with path.open("r", encoding="utf-8-sig") as stream:
                list(yaml.safe_load_all(stream))
        except (OSError, yaml.YAMLError) as exc:
            relative = path.relative_to(root).as_posix()
            errors.append(f"invalid YAML: {relative}: {exc}")
    return errors, checked


def check_release_versions(root: Path) -> list[str]:
    errors: list[str] = []
    versions: dict[str, str] = {}
    for relative in VERSION_FILES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing release version file: {relative}")
            continue
        version = path.read_text(encoding="utf-8-sig").strip()
        versions[relative] = version
        if not RELEASE_VERSION.fullmatch(version):
            errors.append(f"invalid four-part release version: {relative} ({version})")
    if versions and len(set(versions.values())) > 1:
        details = ", ".join(f"{path}={version}" for path, version in versions.items())
        errors.append(f"release versions are not aligned: {details}")
    return errors


def check_shared_rule_titles(root: Path) -> list[str]:
    """Keep shared-rule display titles Chinese while filenames remain stable English IDs."""
    errors: list[str] = []
    for relative_dir in SHARED_RULE_DIRECTORIES:
        shared_dir = root / relative_dir
        if not shared_dir.is_dir():
            continue
        for path in sorted(shared_dir.glob("*.md")):
            relative = path.relative_to(root).as_posix()
            lines = path.read_text(encoding="utf-8-sig").splitlines()
            title = lines[0].strip() if lines else ""
            if not title.startswith("# "):
                errors.append(f"shared rule must start with an H1 title: {relative}")
                continue
            if NUMBERED_H1.match(title):
                errors.append(f"shared rule H1 must not repeat the filename number: {relative}")
            if not CJK_CHARACTER.search(title):
                errors.append(f"shared rule H1 must use a Chinese display title: {relative}")
    return errors


def check_architecture_checklist_rule_references(root: Path) -> list[str]:
    """Keep cross-stack checklist references explicit and resolvable."""
    path = root / "docs" / "architect-engineering-checklist.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8-sig")
    errors: list[str] = []
    for match in BARE_RULE_REFERENCE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        errors.append(
            f"bare rule reference in architecture checklist: "
            f"docs/architect-engineering-checklist.md:{line} -> {match.group(0)}"
        )
    for match in CHECKLIST_RULE_PATH.finditer(text):
        reference = match.group(1)
        if not (root / reference).is_file():
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                f"missing rule reference in architecture checklist: "
                f"docs/architect-engineering-checklist.md:{line} -> {reference}"
            )
    return errors


def check_agent_document_titles(root: Path) -> list[str]:
    """Require Chinese explanatory titles while keeping filenames as stable IDs."""
    errors: list[str] = []
    root_agents = root / "AGENTS.md"
    candidates = [root_agents] if root_agents.is_file() else []
    for relative_dir in CODEX_DOCUMENT_DIRECTORIES:
        codex_dir = root / relative_dir
        if codex_dir.is_dir():
            candidates.extend(path for path in sorted(codex_dir.glob("*.md")) if path.name != "AGENTS.md")
    for path in candidates:
        relative = path.relative_to(root).as_posix()
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        title = lines[0].strip() if lines else ""
        if not title.startswith("# "):
            errors.append(f"agent document must start with an H1 title: {relative}")
            continue
        if NUMBERED_H1.match(title):
            errors.append(f"agent document H1 must not repeat the filename number: {relative}")
        if not CJK_CHARACTER.search(title):
            errors.append(f"agent document H1 must use a Chinese explanatory title: {relative}")
    return errors


def check_root_openapi_ssot(root: Path) -> list[str]:
    path = root / "README.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8-sig")
    ambiguous = [phrase for phrase in ("OpenAPI / schema", "schema / OpenAPI", "按 schema SSOT") if phrase in text]
    return ["README.md presents generated schema as a peer OpenAPI SSOT: " + ", ".join(ambiguous)] if ambiguous else []


def check_root_contract_gate_wording(root: Path) -> list[str]:
    errors: list[str] = []
    required = {
        "docs/branch-protection.md": (
            "oasdiff breaking --fail-on WARN",
            "首次 baseline 须有 Owner 标签",
            "禁止用 PR 说明跳过",
        ),
        ".github/pull_request_template.md": (
            "oasdiff breaking --fail-on WARN",
            "openapi-baseline-bootstrap-approved",
        ),
        "docs/project-adoption-guide.md": ("oasdiff breaking --fail-on WARN",),
        "docs/adoption-scorecard.md": ("oasdiff breaking --fail-on WARN",),
        "docs/definition-of-done.md": ("oasdiff breaking --fail-on WARN",),
        "README.md": (
            "ArchUnit、Checkstyle、固定版本 `oasdiff breaking --fail-on WARN`、CI 样板",
            "| 全栈契约 | 固定版本 `oasdiff breaking --fail-on WARN` + 前端 api:gen / api:check |",
            "后端接入 ArchUnit、Checkstyle、固定版本 `oasdiff breaking --fail-on WARN`、Flyway validate",
        ),
    }
    for rel, markers in required.items():
        path = root / rel
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8-sig")
        for marker in markers:
            if marker not in content:
                errors.append(f"{rel}: contract gate wording missing: {marker}")
        if "OpenAPI diff / Spectral" in content:
            errors.append(f"{rel}: contract gate must not use generic OpenAPI diff / Spectral wording")
    return errors


def validate_repository(root: Path) -> tuple[list[str], int, int]:
    errors = check_trailing_whitespace(root)
    errors.extend(check_release_versions(root))
    errors.extend(check_shared_rule_titles(root))
    errors.extend(check_agent_document_titles(root))
    errors.extend(check_architecture_checklist_rule_references(root))
    errors.extend(check_root_openapi_ssot(root))
    errors.extend(check_root_contract_gate_wording(root))
    link_errors, links = check_local_links(root)
    yaml_errors, yaml_files = check_yaml(root)
    errors.extend(link_errors)
    errors.extend(yaml_errors)
    return errors, links, yaml_files


def main() -> int:
    errors, links, yaml_files = validate_repository(ROOT)
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: repository hygiene passed ({links} local links, {yaml_files} YAML files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
