#!/usr/bin/env python3
"""Generate or verify the stable file-level rule catalog."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "rule-catalog.yaml"
STACKS = {
    "frontend": {
        "prefix": "FE",
        "shared": ROOT / "web-front" / "rules" / "shared",
        "rules_root": ROOT / "web-front" / "rules",
        "owner_role": "Frontend owner",
        "validator": "web-front/rules/scripts/validate-rules-package.py",
        "eval_prefix": "E",
    },
    "backend": {
        "prefix": "BE",
        "shared": ROOT / "web-backend" / "rules" / "shared",
        "rules_root": ROOT / "web-backend" / "rules",
        "owner_role": "Backend owner",
        "validator": "web-backend/rules/scripts/validate-rules-package.py",
        "eval_prefix": "B",
    },
    "miniapp": {
        "prefix": "MA",
        "shared": ROOT / "miniapp" / "rules" / "shared",
        "rules_root": ROOT / "miniapp" / "rules",
        "owner_role": "Miniapp owner",
        "validator": "miniapp/rules/scripts/validate-rules-package.py",
        "eval_prefix": "M",
    },
}
FILE_NAME = re.compile(r"^(?P<number>[0-9]{2})-(?P<slug>[a-z0-9-]+)\.md$")
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)
REQUIRED = re.compile(r"必须|禁止|不得|严禁|\bMUST\b", re.IGNORECASE)
RECOMMENDED = re.compile(r"建议|推荐|\bSHOULD\b", re.IGNORECASE)
EVAL_HEADING = re.compile(r"^###\s+([EBM][0-9]{2})\b", re.MULTILINE)


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _route_files(rules_root: Path) -> list[Path]:
    files: list[Path] = []
    for directory in (rules_root / "codex", rules_root / "cursor"):
        if directory.is_dir():
            files.extend(path for path in directory.rglob("*") if path.is_file())
    return sorted(files)


def _eval_blocks(rules_root: Path) -> list[tuple[str, str]]:
    prompts = rules_root / "evals" / "prompts.md"
    if not prompts.is_file():
        return []
    text = prompts.read_text(encoding="utf-8")
    matches = list(EVAL_HEADING.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[match.start():end]))
    return blocks


def build_catalog(root: Path = ROOT) -> dict[str, object]:
    rules: list[dict[str, object]] = []
    for stack, config in STACKS.items():
        shared = config["shared"]
        rules_root = config["rules_root"]
        routes = [(path, path.read_text(encoding="utf-8", errors="replace")) for path in _route_files(rules_root)]
        eval_blocks = _eval_blocks(rules_root)
        for path in sorted(shared.glob("*.md")):
            match = FILE_NAME.fullmatch(path.name)
            if not match:
                continue
            text = path.read_text(encoding="utf-8")
            heading = HEADING.search(text)
            number = match.group("number")
            # Match full filenames and bare backtick numbers (`05`) used in older
            # eval expectations so catalog linkage stays honest across stacks.
            needles = (
                path.name,
                path.stem,
                f"shared/{path.name}",
                f"`{number}`",
            )
            route_refs = sorted(
                _relative(route_path)
                for route_path, route_text in routes
                if any(needle in route_text for needle in needles[:3])
            )
            eval_refs = sorted(
                case_id for case_id, block in eval_blocks
                if any(needle in block for needle in needles)
            )
            rules.append(
                {
                    "id": f"CR-{config['prefix']}-{int(number):03d}",
                    "stack": stack,
                    "title": heading.group(1).strip() if heading else path.stem,
                    "path": _relative(path),
                    "owner_role": config["owner_role"],
                    "strength": {
                        "required_markers": len(REQUIRED.findall(text)),
                        "recommended_markers": len(RECOMMENDED.findall(text)),
                    },
                    "routing": route_refs,
                    "eval_cases": eval_refs,
                    "verification": [config["validator"]],
                }
            )
    return {
        "schema_version": 1,
        "catalog_version": "1.0.0",
        "id_scope": "stable file-level rule topics; clause-level IDs are not assigned",
        "rules": rules,
        "coverage": {
            "total": len(rules),
            "routed": sum(bool(rule["routing"]) for rule in rules),
            "with_eval_case": sum(bool(rule["eval_cases"]) for rule in rules),
        },
    }


def render(catalog: dict[str, object]) -> str:
    return yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False, width=120)


def package_catalog(catalog: dict[str, object], stack: str, rules_root: Path) -> dict[str, object]:
    prefix = _relative(rules_root) + "/"
    selected: list[dict[str, object]] = []
    for source_rule in catalog["rules"]:
        if source_rule["stack"] != stack:
            continue
        rule = dict(source_rule)
        rule["path"] = str(rule["path"]).removeprefix(prefix)
        rule["routing"] = [str(item).removeprefix(prefix) for item in rule["routing"]]
        rule["verification"] = ["scripts/validate-rules-package.py"]
        selected.append(rule)
    return {
        "schema_version": catalog["schema_version"],
        "catalog_version": catalog["catalog_version"],
        "id_scope": catalog["id_scope"],
        "stack": stack,
        "rules": selected,
        "coverage": {
            "total": len(selected),
            "routed": sum(bool(rule["routing"]) for rule in selected),
            "with_eval_case": sum(bool(rule["eval_cases"]) for rule in selected),
        },
    }


def validate_catalog(catalog: object, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        return ["rule catalog schema_version must be 1"]
    rules = catalog.get("rules")
    if not isinstance(rules, list) or not rules:
        return ["rule catalog rules must be a non-empty list"]
    ids: set[str] = set()
    paths: set[str] = set()
    for index, rule in enumerate(rules):
        label = f"rules[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{label} must be an object")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not re.fullmatch(r"CR-(?:FE|BE|MA)-[0-9]{3}", rule_id):
            errors.append(f"{label}.id is invalid")
        elif rule_id in ids:
            errors.append(f"duplicate rule id {rule_id}")
        else:
            ids.add(rule_id)
        path_value = rule.get("path")
        if not isinstance(path_value, str) or not (root / path_value).is_file():
            errors.append(f"{label}.path is missing: {path_value}")
        elif path_value in paths:
            errors.append(f"duplicate rule path {path_value}")
        else:
            paths.add(path_value)
        routing = rule.get("routing")
        if not isinstance(routing, list) or not routing:
            errors.append(f"{rule_id or label} has no Codex/Cursor routing reference")
        verification = rule.get("verification")
        if not isinstance(verification, list) or not verification or any(
            not isinstance(item, str) or not (root / item).is_file() for item in verification
        ):
            errors.append(f"{rule_id or label} has invalid verification paths")
    expected = {
        _relative(path)
        for config in STACKS.values()
        for path in config["shared"].glob("*.md")
        if FILE_NAME.fullmatch(path.name)
    }
    if paths != expected:
        errors.append(f"catalog path coverage mismatch: missing={sorted(expected - paths)}, extra={sorted(paths - expected)}")
    coverage = catalog.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("total") != len(rules):
        errors.append("coverage.total does not match rules")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    expected = build_catalog()
    errors = validate_catalog(expected)
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    artifacts = {args.output.resolve(): render(expected)}
    for stack, config in STACKS.items():
        package_output = config["rules_root"] / "RULE-CATALOG.yaml"
        artifacts[package_output] = render(package_catalog(expected, stack, config["rules_root"]))
    if args.write:
        for output, rendered in artifacts.items():
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        drifted = [str(output.relative_to(ROOT)) for output, rendered in artifacts.items() if not output.is_file() or output.read_text(encoding="utf-8") != rendered]
        if drifted:
            print(
                f"FAILED: rule catalog drift in {', '.join(drifted)}; run {Path(__file__).name} --write",
                file=sys.stderr,
            )
            return 1
    print(
        "OK: rule catalog "
        f"{expected['catalog_version']} ({expected['coverage']['total']} rules, "
        f"{expected['coverage']['routed']} routed, {expected['coverage']['with_eval_case']} with eval coverage)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
