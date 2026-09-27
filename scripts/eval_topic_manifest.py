#!/usr/bin/env python3
"""Shared eval topic manifest: generate and verify prompt/rubric alignment."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

PROMPT_HEADING = re.compile(r"^###\s+([A-Z]\d+)\s+—\s+(.+)$", re.MULTILINE)
RUBRIC_ROW = re.compile(r"^\|\s+([A-Z]\d+)\s+\|\s+(.+?)\s+\|$", re.MULTILINE)
SUITE_LINE = re.compile(r"^\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


SMOKE_HEADERS = {
    "Security": "## Security",
    "Contract": "## Contract",
    "Business Extension": "## Business Extension",
    "Platform Extension": "## Platform Extension",
    "Resilience": "## Resilience",
    "Enterprise Hardening": "## Enterprise Hardening",
}

CANONICAL_SMOKE_SUITES: dict[str, list[str]] = {
    "E": ["Security", "Contract", "Business Extension", "Platform Extension"],
    "B": ["Security", "Contract", "Business Extension"],
    "M": ["Security", "Contract", "Business Extension", "Resilience", "Enterprise Hardening"],
}


def live_smoke_suites(rules_root: Path, id_prefix: str) -> dict[str, list[str]]:
    smoke_path = rules_root / "evals" / "smoke-prompts.md"
    if not smoke_path.is_file():
        return {}
    smoke = read(smoke_path)
    suites: dict[str, list[str]] = {}
    for name in CANONICAL_SMOKE_SUITES.get(id_prefix, []):
        header = SMOKE_HEADERS[name]
        ids = parse_smoke_suite_ids(smoke, header, id_prefix)
        if ids:
            suites[name] = ids
    return suites


def extract_prompt_topics(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in PROMPT_HEADING.finditer(text)}


def extract_rubric_pass(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in RUBRIC_ROW.finditer(text)}


def parse_evals_readme_suites(text: str) -> dict[str, list[str]]:
    """Parse | **Suite** | E01–E08 | rows from evals/README.md."""
    suites: dict[str, list[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("| **"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        name = parts[0].strip("*").strip()
        if name in {"套件", "级别"}:
            continue
        range_cell = parts[1]
        ids: list[str] = []
        for m in re.finditer(r"([A-Z])(\d{2})–\1(\d{2})", range_cell):
            prefix = m.group(1)
            for n in range(int(m.group(2)), int(m.group(3)) + 1):
                ids.append(f"{prefix}{n:02d}")
        for m in re.finditer(r"\b([A-Z]\d{2})\b", range_cell):
            if m.group(1) not in ids:
                ids.append(m.group(1))
        if ids:
            suites[name] = ids
    return suites


def parse_smoke_suite_ids(smoke_text: str, header: str, id_prefix: str) -> list[str]:
    section = smoke_text.split(header, 1)
    if len(section) < 2:
        return []
    body = section[1].split("##", 1)[0]
    ids: list[str] = []
    for m in re.finditer(rf"\b({id_prefix}\d{{2}})\b", body):
        token = m.group(1)
        if token not in ids:
            ids.append(token)
    for m in re.finditer(rf"{id_prefix}(\d{{2}})–{id_prefix}(\d{{2}})", body):
        start, end = int(m.group(1)), int(m.group(2))
        for n in range(start, end + 1):
            token = f"{id_prefix}{n:02d}"
            if token not in ids:
                ids.append(token)
    return ids


def build_manifest(rules_root: Path, id_prefix: str) -> dict[str, Any]:
    prompts = read(rules_root / "evals" / "prompts.md")
    rubric = read(rules_root / "evals" / "rubric.md")
    prompt_topics = extract_prompt_topics(prompts)
    rubric_pass = extract_rubric_pass(rubric)

    entries: dict[str, dict[str, str]] = {}
    for eval_id, topic in sorted(prompt_topics.items()):
        if not eval_id.startswith(id_prefix):
            continue
        entries[eval_id] = {
            "prompt_topic": topic,
            "rubric_pass": rubric_pass.get(eval_id, ""),
        }

    suites: dict[str, list[str]] = live_smoke_suites(rules_root, id_prefix)

    return {
        "version": 1,
        "id_prefix": id_prefix,
        "entries": entries,
        "suites": suites,
    }


def write_manifest(rules_root: Path, id_prefix: str) -> Path:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    data = build_manifest(rules_root, id_prefix)
    out = rules_root / "evals" / "topic-manifest.yaml"
    header = (
        "# SSOT for eval prompt titles and rubric pass conditions.\n"
        "# Regenerate: python scripts/generate-eval-topic-manifest.py --rules-dir <path>\n"
    )
    with out.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(header + yaml.dump(data, allow_unicode=True, sort_keys=False))
    return out


def load_manifest(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    text = read(path)
    if text.startswith("#"):
        text = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
    return yaml.safe_load(text)


def check_manifest(rules_root: Path, id_prefix: str, errors: list[str]) -> None:
    manifest_path = rules_root / "evals" / "topic-manifest.yaml"
    if not manifest_path.is_file():
        errors.append("evals/topic-manifest.yaml missing; run scripts/generate-eval-topic-manifest.py")
        return

    manifest = load_manifest(manifest_path)
    if manifest.get("id_prefix") != id_prefix:
        errors.append(f"topic-manifest id_prefix {manifest.get('id_prefix')!r} != {id_prefix!r}")

    prompts = read(rules_root / "evals" / "prompts.md")
    rubric = read(rules_root / "evals" / "rubric.md")
    live_prompts = extract_prompt_topics(prompts)
    live_rubric = extract_rubric_pass(rubric)
    entries: dict[str, dict[str, str]] = manifest.get("entries") or {}

    live_ids = {k for k in live_prompts if k.startswith(id_prefix)}
    manifest_ids = set(entries.keys())
    if live_ids != manifest_ids:
        missing = sorted(live_ids - manifest_ids)
        extra = sorted(manifest_ids - live_ids)
        if missing:
            errors.append(f"topic-manifest missing entries: {missing[:5]}{'...' if len(missing) > 5 else ''}")
        if extra:
            errors.append(f"topic-manifest stale entries: {extra[:5]}{'...' if len(extra) > 5 else ''}")

    for eval_id, entry in entries.items():
        expected_topic = entry.get("prompt_topic", "")
        expected_rubric = entry.get("rubric_pass", "")
        if live_prompts.get(eval_id) != expected_topic:
            errors.append(
                f"{eval_id}: prompt topic drift (manifest={expected_topic!r}, "
                f"live={live_prompts.get(eval_id)!r})"
            )
        live_pass = live_rubric.get(eval_id, "")
        if expected_rubric and live_pass != expected_rubric:
            errors.append(
                f"{eval_id}: rubric pass drift (manifest={expected_rubric!r}, live={live_pass!r})"
            )
        elif expected_rubric and expected_rubric not in live_pass:
            errors.append(f"{eval_id}: rubric missing manifest pass condition")

    # Suite IDs must match smoke-prompts.md extension sections
    live_suites = live_smoke_suites(rules_root, id_prefix)
    manifest_suites: dict[str, list[str]] = manifest.get("suites") or {}
    for name, live_ids in live_suites.items():
        manifest_ids = manifest_suites.get(name, [])
        if sorted(manifest_ids) != sorted(live_ids):
            errors.append(
                f"topic-manifest suite {name} drift: manifest={manifest_ids} live={live_ids}"
            )
    for name in manifest_suites:
        if name not in live_suites and name in CANONICAL_SMOKE_SUITES.get(id_prefix, []):
            errors.append(f"topic-manifest suite {name} missing in smoke-prompts.md")

    for suite_name, ids in manifest_suites.items():
        for eval_id in ids:
            if eval_id not in entries:
                errors.append(f"suite {suite_name}: {eval_id} not in manifest entries")
