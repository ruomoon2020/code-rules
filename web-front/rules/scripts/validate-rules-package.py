#!/usr/bin/env python3
"""Validate web-front/rules package internal consistency.

Counts eval prompts ONLY from evals/prompts.md (### Exx headings).
smoke-prompts.md is an index: validates E-id coverage, not prompt body count.

Usage:
  python web-front/rules/scripts/validate-rules-package.py
  python rules/scripts/validate-rules-package.py --rules-dir rules
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ID_PREFIX = "E"
PROMPT_HEADING = re.compile(rf"^###\s+({ID_PREFIX}\d+)\s+—", re.MULTILINE)
RUBRIC_ROW = re.compile(rf"^\|\s+({ID_PREFIX}\d+)\s+\|", re.MULTILINE)
RESULTS_ROW = re.compile(rf"^\|\s+({ID_PREFIX}\d+)\s+\|", re.MULTILINE)
ID_TOKEN = re.compile(rf"\b{ID_PREFIX}(\d{{2}})\b")
ID_RANGE = re.compile(rf"{ID_PREFIX}(\d{{2}})–{ID_PREFIX}(\d{{2}})")
VERSION_HEAD = re.compile(r"^##\s+(\d+(?:\.\d+){2,3})\s+—", re.MULTILINE)
README_PATH = re.compile(r"`((?:shared|docs|codex|cursor|evals|scripts)/[\w./-]+\.(?:md|mdc|py|yml|mjs))`")
AGENTS_PATH = re.compile(r"`rules/((?:shared|docs|codex|cursor|evals|scripts)/[\w./-]+\.(?:md|mdc|py|yml|mjs))`")
SHARED_REF = re.compile(r"shared/(\d{2}-[\w-]+\.md)")
BARE_SHARED_REF = re.compile(r"(?<![\w/-])(\d{2}-[\w-]+\.md)(?!\w)")
CROSS_BACKEND_REF = re.compile(
    r"(?:\.\./web-backend/rules/|web-backend/rules/)([\w./-]+\.(?:md|mdc))"
)
COMMON_GOV_REF = re.compile(r"common-governance/([\w./-]+\.(?:md|yaml|py))")

P0_COUNT = 8
P0_MAX_NUM = 8
L0_HARD_RULE_COUNT = 34
SMOKE_CORE_P1_COUNT = 12
SECURITY_SUITE = ["E12", "E18", "E25", "E27"]
CONTRACT_SUITE = ["E03", "E04", "E05", "E26"]
BUSINESS_EXTENSION_SUITE = [
    "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40",
]
PLATFORM_EXTENSION_SUITE = ["E41", "E42", "E43"]
ENTERPRISE_HARDENING_SUITE = ["E44", "E45", "E46", "E47", "E48", "E49"]
TESTING_GOVERNANCE_SUITE = ["E31", "E50"]
PROJECT_LOCAL_TESTING_MARKERS = (
    "## 测试治理参数",
    "覆盖率策略",
    "兼容窗口",
    "flaky 治理",
    "失败证据",
    "测试数据",
    "风险专项",
)
L0_ALLOWED_SHARED_REFS: set[str] = set()
HIGH_LEVEL_TOPIC_MARKERS = (
    "Feature Flag",
    "keepAlive",
    "resetAllStores",
    "路由 chunk",
    "成熟后台",
    "受监管 Web",
)
SCAFFOLD_REQUIRED = (
    "README.md",
    "eslint.config.mjs.sample",
    "prettier.config.mjs.sample",
    "stylelint.config.mjs.sample",
    "src/api/request-boundary.ts.sample",
    "src/stores/reset-all-stores.ts.sample",
    "src/views/list-page-state.ts.sample",
    "scripts/check-bundle-budget.mjs.sample",
)
EVAL_TOPIC_GUARDS = {
    "E13": "外部指令诱导泄露与伪造验证",
    "E41": "硬编码业务文案",
    "E42": "Token 放 WebSocket URL",
    "E43": "裸 v-html 渲染用户富文本",
}
AI_TOOL_SAFETY_TOPICS = {
    "EAT01": "不可信内容中的提示注入",
    "EAT02": "敏感信息外传",
    "EAT03": "命令、URL 与查询注入",
    "EAT04": "未授权外部写入与生产操作",
    "EAT05": "工具结果诱导扩权或伪造证据",
}

THRESHOLD_FILES = [
    "README.md",
    "RELEASE.md",
    "evals/README.md",
    "evals/rubric.md",
    "evals/results-template.md",
    "docs/onboarding-new-project.md",
    "docs/rules-package-index.md",
    "docs/contributing-rules-package.md",
    "scripts/README.md",
    "cursor/00-project-overview.mdc",
]

README_EXTERNAL_PATHS = frozenset()
README_SKIP_PREFIXES = ("evals/", "examples/", "cursor/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_prompt_ids(text: str) -> list[str]:
    return PROMPT_HEADING.findall(text)


def extract_smoke_ids(smoke_text: str) -> set[str]:
    ids: set[str] = set()
    for start_s, end_s in ID_RANGE.findall(smoke_text):
        start, end = int(start_s), int(end_s)
        for n in range(start, end + 1):
            ids.add(f"{ID_PREFIX}{n:02d}")
    for n in ID_TOKEN.findall(smoke_text):
        ids.add(f"{ID_PREFIX}{n}")
    return ids


def parse_p1_threshold(rubric: str) -> tuple[int, int] | None:
    m = re.search(r">=\s*(\d+)/(\d+)", rubric.split("汇总公式")[-1])
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def parse_core_p1_line(text: str) -> list[str]:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("E09") and "、" in line:
            return re.findall(r"E\d+", line)
    return []


def parse_smoke_core_p1(smoke_text: str) -> list[str]:
    section = smoke_text.split("## Security")[0]
    ids: list[str] = []
    for line in section.splitlines():
        m = re.match(rf"^\|\s+({ID_PREFIX}\d+)\s+\|", line.strip())
        if m and "–" not in m.group(1):
            num = int(m.group(1)[1:])
            if num > P0_MAX_NUM:
                ids.append(m.group(1))
    return ids


def parse_suite_line(text: str, header: str) -> list[str]:
    part = text.split(header, 1)
    if len(part) < 2:
        return []
    block = part[1].split("##", 1)[0]
    return re.findall(r"E\d+", block.split("**门槛**")[0])


def expand_id_tokens(text: str, prefix: str = ID_PREFIX) -> list[str]:
    """Expand E01, E09–E12 style tokens to sorted unique list."""
    ids: set[str] = set()
    for m in re.finditer(rf"{prefix}(\d{{2}})", text):
        ids.add(f"{prefix}{m.group(1)}")
    for m in re.finditer(rf"{prefix}(\d{{2}})\s*[–-]\s*{prefix}(\d{{2}})", text):
        lo, hi = int(m.group(1)), int(m.group(2))
        for n in range(lo, hi + 1):
            ids.add(f"{prefix}{n:02d}")
    return sorted(ids)


def parse_evals_table_suite(text: str, suite_name: str) -> list[str]:
    m = re.search(rf"\|\s*\*\*{re.escape(suite_name)}\*\*\s*\|\s*([^|]+)\|", text)
    if not m:
        return []
    return expand_id_tokens(m.group(1))


def check_readme_paths(root: Path, errors: list[str]) -> None:
    readme = read(root / "README.md")
    for path in README_PATH.findall(readme):
        if path in README_EXTERNAL_PATHS or path.startswith(README_SKIP_PREFIXES):
            continue
        if "*" in path:
            continue
        if not (root / path).exists():
            errors.append(f"README.md lists missing path: {path}")


def check_readme_shared_inventory(root: Path, errors: list[str]) -> None:
    """Ensure README file inventory lists every shared/*.md on disk."""
    readme = read(root / "README.md")
    shared_dir = root / "shared"
    if not shared_dir.is_dir():
        return
    for path in sorted(shared_dir.glob("*.md")):
        rel = f"shared/{path.name}"
        if rel not in readme:
            errors.append(f"README.md file inventory missing {rel}")


def check_scaffold_assets(root: Path, errors: list[str]) -> None:
    scaffold = root / "examples" / "scaffold"
    for rel in SCAFFOLD_REQUIRED:
        if not (scaffold / rel).is_file():
            errors.append(f"examples/scaffold missing {rel}")

    scripts_sample = root / "examples" / "package-scripts.sample.json"
    if scripts_sample.is_file():
        try:
            package_sample = json.loads(read(scripts_sample))
        except json.JSONDecodeError as exc:
            errors.append(f"package-scripts.sample.json invalid JSON: {exc.msg}")
            return
        scripts = package_sample.get("scripts") or {}
        for name in ("lint", "type-check", "test", "build", "api:check", "size:check"):
            if name not in scripts:
                errors.append(f"package-scripts.sample.json missing script: {name}")


def check_project_local_sample(root: Path, errors: list[str]) -> None:
    sample = root / "examples" / "99-project-local.mdc.sample"
    if not sample.is_file():
        errors.append("examples/99-project-local.mdc.sample is missing")
        return
    text = read(sample)
    missing = [marker for marker in PROJECT_LOCAL_TESTING_MARKERS if marker not in text]
    if missing:
        errors.append(f"project-local testing governance markers missing: {', '.join(missing)}")


def check_l0_hard_rule_scope(root: Path, errors: list[str]) -> None:
    text = read(root / "shared" / "00-must-follow.md")
    boundary = "## 条件触发路由（不计入 Level 0 硬规则）"
    if boundary not in text:
        errors.append("00-must-follow.md missing conditional routing boundary")
    numbered = "\n".join(line for line in text.splitlines() if re.match(r"^\d+\.\s", line))
    count = len(numbered.splitlines()) if numbered else 0
    if count != L0_HARD_RULE_COUNT:
        errors.append(
            f"00-must-follow.md L0 hard rule count {count}, expected {L0_HARD_RULE_COUNT}"
        )
    numbered_refs = set(BARE_SHARED_REF.findall(numbered))
    for ref in sorted(numbered_refs - L0_ALLOWED_SHARED_REFS):
        errors.append(f"00-must-follow.md: conditional shared rule numbered as L0: {ref}")
    for marker in HIGH_LEVEL_TOPIC_MARKERS:
        if marker in numbered:
            errors.append(f"00-must-follow.md: conditional topic numbered as L0: {marker}")


def run_scaffold_command(
    command: list[str],
    cwd: Path,
    errors: list[str],
    label: str,
    env: dict[str, str] | None = None,
    expected_exit: int = 0,
) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != expected_exit:
        detail = (result.stderr or result.stdout).strip()
        errors.append(f"scaffold {label} failed (exit {result.returncode}): {detail}")


def check_scaffold_runtime(root: Path, errors: list[str]) -> None:
    scaffold = root / "examples" / "scaffold"
    if any(not (scaffold / rel).is_file() for rel in SCAFFOLD_REQUIRED):
        return

    node = shutil.which("node")
    tsc = shutil.which("tsc")
    if node is None:
        errors.append("scaffold runtime validation requires node")
        return
    if tsc is None:
        errors.append("scaffold runtime validation requires tsc")
        return

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for rel in (
            "eslint.config.mjs.sample",
            "prettier.config.mjs.sample",
            "stylelint.config.mjs.sample",
            "scripts/check-bundle-budget.mjs.sample",
        ):
            source = scaffold / rel
            target = temp / rel.removesuffix(".sample")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            run_scaffold_command([node, "--check", str(target)], temp, errors, f"syntax {rel}")

        ts_files: list[str] = []
        for rel in (
            "src/api/request-boundary.ts.sample",
            "src/stores/reset-all-stores.ts.sample",
            "src/views/list-page-state.ts.sample",
        ):
            target = temp / Path(rel).name.removesuffix(".sample")
            shutil.copyfile(scaffold / rel, target)
            ts_files.append(str(target))
        run_scaffold_command(
            [
                tsc,
                "--noEmit",
                "--strict",
                "--target",
                "ES2022",
                "--module",
                "ESNext",
                "--moduleResolution",
                "Bundler",
                "--lib",
                "ES2022,DOM",
                *ts_files,
            ],
            temp,
            errors,
            "TypeScript strict compile",
        )

        asset = temp / "dist" / "assets" / "entry.js"
        asset.parent.mkdir(parents=True)
        asset.write_text("console.log('bundle budget smoke');\n", encoding="utf-8")
        manifest = temp / "dist" / ".vite" / "manifest.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps({"src/main.ts": {"file": "assets/entry.js", "isEntry": True}}),
            encoding="utf-8",
        )
        budget_script = temp / "scripts" / "check-bundle-budget.mjs"
        pass_env = os.environ.copy()
        pass_env["BUNDLE_TOTAL_BUDGET_KB"] = "100"
        pass_env["BUNDLE_INITIAL_BUDGET_KB"] = "100"
        pass_env["BUNDLE_CHUNK_BUDGET_KB"] = "100"
        run_scaffold_command([node, str(budget_script)], temp, errors, "bundle pass smoke", pass_env)
        fail_env = os.environ.copy()
        fail_env["BUNDLE_TOTAL_BUDGET_KB"] = "0.001"
        run_scaffold_command(
            [node, str(budget_script)],
            temp,
            errors,
            "bundle reject smoke",
            fail_env,
            expected_exit=1,
        )


def check_agents_paths(root: Path, errors: list[str]) -> None:
    agents = root / "codex" / "AGENTS.md"
    if not agents.is_file():
        return
    for path in AGENTS_PATH.findall(read(agents)):
        if not (root / path).is_file():
            errors.append(f"codex/AGENTS.md: missing rules/{path}")


def check_cursor_shared_refs(root: Path, errors: list[str]) -> None:
    cursor_dir = root / "cursor"
    if not cursor_dir.is_dir():
        return
    for mdc in cursor_dir.glob("*.mdc"):
        text = read(mdc)
        for rel in SHARED_REF.findall(text):
            if not (root / "shared" / rel).is_file():
                errors.append(f"{mdc.name}: missing shared/{rel}")
        for rel in BARE_SHARED_REF.findall(text):
            if (root / "shared" / rel).is_file():
                errors.append(
                    f"{mdc.name}: bare shared reference {rel}; use rules/shared/..."
                )


def monorepo_scripts_dir(rules_root: Path) -> Path | None:
    resolved = rules_root.resolve()
    if resolved.name == "rules" and resolved.parent.name in ("web-front", "web-backend", "miniapp"):
        return resolved.parent.parent / "scripts"
    return None


def check_eval_topic_manifest(root: Path, errors: list[str]) -> None:
    scripts_dir = monorepo_scripts_dir(root)
    if scripts_dir is None or not scripts_dir.is_dir():
        return
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        import eval_topic_manifest as etm
    except ImportError:
        errors.append("cannot import eval_topic_manifest (pip install pyyaml)")
        return
    try:
        etm.check_manifest(root, ID_PREFIX, errors)
    except RuntimeError as exc:
        errors.append(str(exc))


def check_eval_topic_guards(prompts: str, rubric: str, errors: list[str]) -> None:
    """Ensure selected high-risk eval IDs cannot be silently repurposed."""
    prompt_topics = {
        match.group(1): match.group(2)
        for match in re.finditer(
            rf"^###\s+({ID_PREFIX}\d+)\s+—\s+(.+)$", prompts, re.MULTILINE
        )
    }
    rubric_rows = {
        match.group(1): match.group(2)
        for match in re.finditer(
            rf"^\|\s+({ID_PREFIX}\d+)\s+\|\s+(.+?)\s+\|$", rubric, re.MULTILINE
        )
    }
    for eval_id, expected_topic in EVAL_TOPIC_GUARDS.items():
        if prompt_topics.get(eval_id) != expected_topic:
            errors.append(f"{eval_id}: prompt topic must be '{expected_topic}'")
        if expected_topic not in rubric_rows.get(eval_id, ""):
            errors.append(f"{eval_id}: rubric topic must contain '{expected_topic}'")


def check_ai_tool_safety(root: Path, errors: list[str]) -> None:
    path = root / "evals" / "ai-tool-safety.md"
    if not path.is_file():
        errors.append("missing evals/ai-tool-safety.md")
        return
    text = read(path)
    topics = dict(re.findall(r"^###\s+(EAT\d{2})\s+—\s+(.+)$", text, re.MULTILINE))
    if topics != AI_TOOL_SAFETY_TOPICS:
        errors.append("AI Tool Safety suite ids/topics must remain EAT01-EAT05")
    if len(re.findall(r"^\*\*Pass\*\*:\s+\S", text, re.MULTILINE)) != 5:
        errors.append("AI Tool Safety suite must define five non-empty Pass criteria")
    if "门槛：5/5" not in text:
        errors.append("AI Tool Safety suite threshold must be 5/5")


def monorepo_root(rules_root: Path) -> Path | None:
    """web-front/rules → repository root, when used in this monorepo."""
    resolved = rules_root.resolve()
    if resolved.name == "rules" and resolved.parent.name == "web-front":
        return resolved.parent.parent
    return None


def check_common_governance_refs(rules_root: Path, errors: list[str]) -> None:
    repo = monorepo_root(rules_root)
    if repo is None:
        return
    common = repo / "common-governance"
    for path in rules_root.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".mdc"}:
            continue
        for rel in COMMON_GOV_REF.findall(read(path)):
            if not (common / rel).is_file():
                errors.append(f"common-governance ref missing {rel} (from {path.relative_to(rules_root)})")


def check_cross_package_backend_refs(rules_root: Path, errors: list[str]) -> None:
    repo = monorepo_root(rules_root)
    if repo is None:
        return
    backend_rules = repo / "web-backend" / "rules"
    if not backend_rules.is_dir():
        errors.append(f"monorepo web-backend/rules not found at {backend_rules}")
        return
    seen: set[str] = set()
    for path in rules_root.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".mdc"}:
            continue
        for rel in CROSS_BACKEND_REF.findall(read(path)):
            if rel in seen:
                continue
            seen.add(rel)
            if not (backend_rules / rel).is_file():
                errors.append(
                    f"cross-package ref missing web-backend/rules/{rel} "
                    f"(from {path.relative_to(rules_root)})"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate frontend rules package consistency")
    parser.add_argument(
        "--rules-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()
    root: Path = args.rules_dir
    errors: list[str] = []

    version = read(root / "VERSION").strip()
    changelog = read(root / "CHANGELOG.md")
    latest = VERSION_HEAD.search(changelog)
    if not latest or latest.group(1) != version:
        errors.append(f"CHANGELOG latest version != VERSION ({version})")

    prompts = read(root / "evals/prompts.md")
    rubric = read(root / "evals/rubric.md")
    results = read(root / "evals/results-template.md")
    smoke_path = root / "evals/smoke-prompts.md"
    smoke = read(smoke_path) if smoke_path.is_file() else ""

    prompt_ids = extract_prompt_ids(prompts)
    rubric_p0 = RUBRIC_ROW.findall(rubric.split("## P1")[0])
    rubric_p1 = RUBRIC_ROW.findall(rubric.split("## P1", 1)[1]) if "## P1" in rubric else []
    rubric_ids = rubric_p0 + rubric_p1
    results_ids = [m for m in RESULTS_ROW.findall(results) if m.startswith(ID_PREFIX)]

    p0_ids = [e for e in prompt_ids if int(e[1:]) <= P0_MAX_NUM]
    p1_ids = [e for e in prompt_ids if int(e[1:]) > P0_MAX_NUM]
    total = len(prompt_ids)

    if len(p0_ids) != P0_COUNT:
        errors.append(f"prompts.md P0 count {len(p0_ids)}, expected {P0_COUNT}")
    if prompt_ids != sorted(prompt_ids, key=lambda x: int(x[1:])):
        errors.append("prompts.md E ids not in ascending order")
    if rubric_p0 != [f"{ID_PREFIX}{i:02d}" for i in range(1, P0_COUNT + 1)]:
        errors.append(f"rubric P0 ids mismatch: got {len(rubric_p0)}")
    if rubric_p1 != p1_ids:
        errors.append(f"rubric P1 mismatch prompts: {len(rubric_p1)} vs {len(p1_ids)}")
    if rubric_ids != prompt_ids:
        errors.append(f"rubric all ids mismatch prompts")
    if results_ids != prompt_ids:
        errors.append(f"results-template ids mismatch prompts")

    if smoke_path.is_file():
        if PROMPT_HEADING.findall(smoke):
            errors.append("smoke-prompts.md must not use ### Exx headings")
        smoke_ids = extract_smoke_ids(smoke)
        missing = sorted(set(smoke_ids) - set(prompt_ids), key=lambda x: int(x[1:]))
        if missing:
            errors.append(f"smoke-prompts unknown E ids: {', '.join(missing)}")

        evals_readme = read(root / "evals/README.md")
        core_readme = parse_core_p1_line(
            evals_readme.split("### 核心 P1", 1)[1] if "### 核心 P1" in evals_readme else ""
        )
        core_smoke = parse_smoke_core_p1(smoke)
        if core_readme and core_readme != core_smoke:
            errors.append(f"evals/README core P1 != smoke table")
        if len(core_smoke) != SMOKE_CORE_P1_COUNT:
            errors.append(f"smoke core P1 count {len(core_smoke)}, expected {SMOKE_CORE_P1_COUNT}")

        sec_smoke = parse_suite_line(smoke, "## Security")
        sec_readme = parse_evals_table_suite(evals_readme, "Security")
        if sorted(sec_smoke) != sorted(SECURITY_SUITE) or sorted(sec_readme) != sorted(SECURITY_SUITE):
            errors.append(f"Security suite mismatch")

        con_smoke = parse_suite_line(smoke, "## Contract")
        con_readme = parse_evals_table_suite(evals_readme, "Contract")
        if sorted(con_smoke) != sorted(CONTRACT_SUITE) or sorted(con_readme) != sorted(CONTRACT_SUITE):
            errors.append(f"Contract suite mismatch")

        biz_smoke = parse_suite_line(smoke, "## Business Extension")
        biz_readme = parse_evals_table_suite(evals_readme, "Business Extension")
        if sorted(biz_smoke) != sorted(BUSINESS_EXTENSION_SUITE) or sorted(biz_readme) != sorted(
            BUSINESS_EXTENSION_SUITE
        ):
            errors.append(
                f"Business Extension suite mismatch: smoke={biz_smoke} readme={biz_readme} "
                f"expected={BUSINESS_EXTENSION_SUITE}"
            )

        plat_smoke = parse_suite_line(smoke, "## Platform Extension")
        plat_readme = parse_evals_table_suite(evals_readme, "Platform Extension")
        if sorted(plat_smoke) != sorted(PLATFORM_EXTENSION_SUITE) or sorted(
            plat_readme
        ) != sorted(PLATFORM_EXTENSION_SUITE):
            errors.append(
                f"Platform Extension suite mismatch: smoke={plat_smoke} readme={plat_readme} "
                f"expected={PLATFORM_EXTENSION_SUITE}"
            )

        hardening_smoke = parse_suite_line(smoke, "## Enterprise Hardening")
        hardening_readme = parse_evals_table_suite(evals_readme, "Enterprise Hardening")
        if sorted(hardening_smoke) != sorted(ENTERPRISE_HARDENING_SUITE) or sorted(
            hardening_readme
        ) != sorted(ENTERPRISE_HARDENING_SUITE):
            errors.append(
                "Enterprise Hardening suite mismatch: "
                f"smoke={hardening_smoke} readme={hardening_readme} "
                f"expected={ENTERPRISE_HARDENING_SUITE}"
            )

        testing_smoke = parse_suite_line(smoke, "## Testing Governance")
        testing_readme = parse_evals_table_suite(evals_readme, "Testing Governance")
        if sorted(testing_smoke) != sorted(TESTING_GOVERNANCE_SUITE) or sorted(
            testing_readme
        ) != sorted(TESTING_GOVERNANCE_SUITE):
            errors.append(
                "Testing Governance suite mismatch: "
                f"smoke={testing_smoke} readme={testing_readme} "
                f"expected={TESTING_GOVERNANCE_SUITE}"
            )

    check_eval_topic_guards(prompts, rubric, errors)
    check_ai_tool_safety(root, errors)
    check_eval_topic_manifest(root, errors)
    check_readme_paths(root, errors)
    check_readme_shared_inventory(root, errors)
    check_l0_hard_rule_scope(root, errors)
    check_scaffold_assets(root, errors)
    check_project_local_sample(root, errors)
    check_scaffold_runtime(root, errors)
    check_agents_paths(root, errors)
    check_cursor_shared_refs(root, errors)
    check_cross_package_backend_refs(root, errors)
    check_common_governance_refs(root, errors)

    threshold = parse_p1_threshold(rubric)
    if not threshold:
        errors.append("rubric.md missing P1 >= N/M block")
    else:
        min_pass, total_p1 = threshold
        if total_p1 != len(p1_ids):
            errors.append(f"rubric P1 total {total_p1} != prompts P1 {len(p1_ids)}")
        token = f"{min_pass}/{total_p1}"
        for rel in THRESHOLD_FILES:
            text = read(root / rel)
            if token not in text and f"至少 {token}" not in text:
                if rel == "evals/rubric.md":
                    continue
                if rel == "evals/results-template.md" and f"__/{total_p1}" in text:
                    continue
                errors.append(f"{rel}: missing threshold {token}")

    overview_path = root / "cursor/00-project-overview.mdc"
    if overview_path.is_file():
        hard_rules = len(re.findall(r"^\d+\.\s", read(root / "shared/00-must-follow.md"), re.MULTILINE))
        m = re.search(r"当前\s+(\d+)\s+条", read(overview_path))
        if m and int(m.group(1)) != hard_rules:
            errors.append(f"cursor/00 hard rule count != 00 ({hard_rules})")

    print(f"rules-dir: {root}")
    print(f"VERSION: {version}")
    print(f"prompts: {total} (P0={len(p0_ids)}, P1={len(p1_ids)})")
    if threshold:
        print(f"P1 threshold: >={threshold[0]}/{threshold[1]}")
    if smoke_path.is_file():
        print(f"smoke-prompts E coverage: {len(extract_smoke_ids(smoke))} ids (index only)")

    if errors:
        print("\nFAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\nOK: frontend rules package consistency checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
