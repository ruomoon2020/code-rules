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


def validate_repository(root: Path) -> tuple[list[str], int, int]:
    errors = check_trailing_whitespace(root)
    errors.extend(check_release_versions(root))
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
