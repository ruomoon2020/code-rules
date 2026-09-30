#!/usr/bin/env python3
"""Validate miniapp/rules package internal consistency.

Counts eval prompts ONLY from evals/prompts.md (### Mxx headings).
smoke-prompts.md is an index: validates M-id coverage, not prompt body count.

Usage:
  python miniapp/rules/scripts/validate-rules-package.py
  python rules/scripts/validate-rules-package.py --rules-dir rules
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ID_PREFIX = "M"
PROMPT_HEADING = re.compile(rf"^###\s+({ID_PREFIX}\d+)\s+—", re.MULTILINE)
RUBRIC_ROW = re.compile(rf"^\|\s+({ID_PREFIX}\d+)\s+\|", re.MULTILINE)
RESULTS_ROW = re.compile(rf"^\|\s+({ID_PREFIX}\d+)\s+\|", re.MULTILINE)
ID_TOKEN = re.compile(rf"\b{ID_PREFIX}(\d{{2}})\b")
ID_RANGE = re.compile(rf"{ID_PREFIX}(\d{{2}})–{ID_PREFIX}(\d{{2}})")
VERSION_HEAD = re.compile(r"^##\s+(\d+(?:\.\d+){2,3})\s+—", re.MULTILINE)
README_PATH = re.compile(r"`((?:shared|docs|codex|cursor|evals|scripts)/[\w./-]+\.(?:md|mdc|py|yml|mjs))`")
SHARED_REF = re.compile(r"shared/(\d{2}-[\w-]+\.md)")
BARE_SHARED_REF = re.compile(r"(?<![\w/-])(\d{2}-[\w-]+\.md)(?!\w)")
EVAL_TOPIC_GUARDS = {"M13": "外部指令诱导泄露与伪造验证"}
AI_TOOL_SAFETY_TOPICS = {
    "MAT01": "不可信内容中的提示注入",
    "MAT02": "敏感信息外传",
    "MAT03": "命令、URL 与查询注入",
    "MAT04": "未授权外部写入与生产操作",
    "MAT05": "工具结果诱导扩权或伪造证据",
}
COMPONENT_ENGINEERING_MARKERS = {
    "shared/02-naming.md": ("## CSS 与主题变量命名", "BEM"),
    "shared/03-vue3-typescript-uniapp.md": (
        "## 组件通信决策",
        "Props / Emits",
        "v-model",
        "Provide / Inject",
        "Pinia",
        "EventBus",
    ),
    "shared/04-page-ui-lifecycle.md": (
        "## Vue 3 组件生命周期",
        "onMounted",
        "onUnmounted",
        "onLoad",
        "onShow",
        "onHide",
        "onUnload",
    ),
    "shared/10-performance-package-size.md": (
        "P50/P95",
        "shallowRef",
        "v-show",
        "分包入口",
    ),
    "shared/16-testing-quality-gates.md": (
        "## 组件测试规范",
        "Vitest + Vue Test Utils",
        "快照测试",
        "E2E",
    ),
    "shared/24-design-system-mobile.md": (
        "## 样式架构",
        "## 主题管理",
        "## BEM 与状态",
        "## 组件文档",
    ),
}
COMMON_GOV_REF = re.compile(r"common-governance/([\w./-]+\.(?:md|yaml|py))")

P0_COUNT = 8
P0_MAX_NUM = 8
SMOKE_CORE_P1_COUNT = 10
SECURITY_SUITE = [
    "M06", "M07", "M12", "M18", "M30", "M31", "M32", "M33", "M34",
]
CONTRACT_SUITE = ["M03", "M05", "M08", "M15", "M51"]
BUSINESS_EXTENSION_SUITE = [
    "M21", "M22", "M23", "M24", "M25", "M26", "M27", "M28", "M29",
]
SECURITY_EXTENSION_SUITE = ["M30", "M31", "M32", "M33", "M34"]
RESILIENCE_EXTENSION_SUITE = ["M35", "M36", "M37", "M38"]
ENTERPRISE_HARDENING_SUITE = ["M39", "M40", "M41", "M42", "M43", "M44"]
COMPONENT_ENGINEERING_SUITE = ["M45", "M46", "M47", "M48", "M49", "M50"]
MEDIA_EXTENSION_SUITE = ["M51"]
TESTING_GOVERNANCE_SUITE = ["M49", "M52"]
PROJECT_LOCAL_TESTING_MARKERS = (
    "## 测试治理参数",
    "覆盖率策略",
    "兼容窗口",
    "flaky 治理",
    "失败证据",
    "测试数据",
    "风险专项",
)
TOTAL_PROMPTS = 52
SHARED_MAX_NUM = 26
SCAFFOLD_REQUIRED = (
    "README.md",
    "allowed-hosts.ts.sample",
    "app-bootstrap.ts.sample",
    "app-error-handler.ts.sample",
    "App.vue.sample",
    "auth-login.service.ts.sample",
    "open-webview.ts.sample",
    "request.ts.sample",
    "webview-allowlist.ts.sample",
)

THRESHOLD_FILES = [
    "README.md",
    "RELEASE.md",
    "evals/README.md",
    "evals/rubric.md",
    "evals/results-template.md",
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
        if line.startswith("M09") and "、" in line:
            return re.findall(r"M\d+", line)
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
    return re.findall(r"M\d+", block.split("**门槛**")[0])


def parse_evals_table_suite(text: str, suite_name: str) -> list[str]:
    m = re.search(rf"\|\s*\*\*{re.escape(suite_name)}\*\*\s*\|\s*([^|]+)\|", text)
    if not m:
        return []
    raw = m.group(1)
    ids: set[str] = set()
    for n in re.findall(rf"{ID_PREFIX}(\d{{2}})", raw):
        ids.add(f"{ID_PREFIX}{n}")
    for m2 in re.finditer(rf"{ID_PREFIX}(\d{{2}})\s*[–-]\s*{ID_PREFIX}(\d{{2}})", raw):
        lo, hi = int(m2.group(1)), int(m2.group(2))
        for n in range(lo, hi + 1):
            ids.add(f"{ID_PREFIX}{n:02d}")
    return sorted(ids)


def check_readme_paths(root: Path, errors: list[str]) -> None:
    readme = read(root / "README.md")
    for path in README_PATH.findall(readme):
        if path in README_EXTERNAL_PATHS or path.startswith(README_SKIP_PREFIXES):
            continue
        if "*" in path:
            continue
        if not (root / path).exists():
            errors.append(f"README.md lists missing path: {path}")


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


def check_readme_shared_inventory(root: Path, errors: list[str]) -> None:
    readme = read(root / "README.md")
    shared_dir = root / "shared"
    if not shared_dir.is_dir():
        return
    for path in sorted(shared_dir.glob("*.md")):
        rel = f"shared/{path.name}"
        if rel not in readme:
            errors.append(f"README.md file inventory missing {rel}")


def check_shared_titles(root: Path, errors: list[str]) -> None:
    for path in sorted((root / "shared").glob("*.md")):
        lines = read(path).splitlines()
        title = lines[0].strip() if lines else ""
        if not title.startswith("# "):
            errors.append(f"{path.name}: must start with an H1 title")
            continue
        if re.match(r"^#\s+\d{2}(?:\s|$)", title):
            errors.append(f"{path.name}: H1 must not repeat the filename number")
        if not re.search(r"[\u4e00-\u9fff]", title):
            errors.append(f"{path.name}: H1 must use a Chinese display title")


def check_openapi_ssot_wording(root: Path, errors: list[str]) -> None:
    path = root / "shared/12-list-form-pagination.md"
    if not path.is_file():
        return
    ambiguous = [phrase for phrase in ("OpenAPI / schema", "schema / generated") if phrase in read(path)]
    if ambiguous:
        errors.append("shared/12-list-form-pagination.md: ambiguous OpenAPI SSOT wording: " + ", ".join(ambiguous))


def check_scaffold_assets(root: Path, errors: list[str]) -> None:
    scaffold = root / "examples" / "scaffold"
    missing = [rel for rel in SCAFFOLD_REQUIRED if not (scaffold / rel).is_file()]
    if missing:
        errors.append(f"examples/scaffold missing: {', '.join(missing)}")


def check_project_local_sample(root: Path, errors: list[str]) -> None:
    sample = root / "examples" / "99-project-local.mdc.sample"
    if not sample.is_file():
        errors.append("examples/99-project-local.mdc.sample is missing")
        return
    text = read(sample)
    missing = [marker for marker in PROJECT_LOCAL_TESTING_MARKERS if marker not in text]
    if missing:
        errors.append(f"project-local testing governance markers missing: {', '.join(missing)}")


def check_scaffold_runtime(root: Path, errors: list[str]) -> None:
    scaffold = root / "examples" / "scaffold"
    if any(not (scaffold / rel).is_file() for rel in SCAFFOLD_REQUIRED):
        return
    tsc = shutil.which("tsc")
    if tsc is None:
        errors.append("scaffold runtime validation requires tsc")
        return
    sources: list[str] = []
    for rel in SCAFFOLD_REQUIRED:
        if not rel.endswith((".ts.sample", ".vue.sample")):
            continue
        text = read(scaffold / rel)
        if rel.endswith(".vue.sample"):
            match = re.search(r"<script\s+setup\s+lang=\"ts\">(.*?)</script>", text, re.DOTALL)
            if not match:
                errors.append(f"scaffold {rel} missing <script setup lang=\"ts\">")
                continue
            text = match.group(1)
        sources.append("// @ts-nocheck\n" + text)
    if errors:
        return
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        paths: list[str] = []
        for index, source in enumerate(sources):
            path = temp / f"sample-{index}.ts"
            path.write_text(source, encoding="utf-8")
            paths.append(str(path))
        result = subprocess.run(
            [
                tsc,
                "--noEmit",
                "--pretty",
                "false",
                "--target",
                "ES2022",
                "--module",
                "ESNext",
                *paths,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        errors.append(f"scaffold TypeScript syntax failed: {detail}")


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
    topics = dict(re.findall(r"^###\s+(MAT\d{2})\s+—\s+(.+)$", text, re.MULTILINE))
    if topics != AI_TOOL_SAFETY_TOPICS:
        errors.append("AI Tool Safety suite ids/topics must remain MAT01-MAT05")
    if len(re.findall(r"^\*\*Pass\*\*:\s+\S", text, re.MULTILINE)) != 5:
        errors.append("AI Tool Safety suite must define five non-empty Pass criteria")
    if "门槛：5/5" not in text:
        errors.append("AI Tool Safety suite threshold must be 5/5")


def check_component_engineering_contract(root: Path, errors: list[str]) -> None:
    """Keep component/style/lifecycle/test guidance from silently regressing."""
    for rel, markers in COMPONENT_ENGINEERING_MARKERS.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"component engineering contract missing file: {rel}")
            continue
        content = read(path)
        missing = [marker for marker in markers if marker not in content]
        if missing:
            errors.append(
                f"{rel}: component engineering markers missing: {', '.join(missing)}"
            )


def monorepo_root(rules_root: Path) -> Path | None:
    resolved = rules_root.resolve()
    if resolved.name == "rules" and resolved.parent.name == "miniapp":
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


def check_shared_numbered_files(root: Path, errors: list[str]) -> None:
    shared_dir = root / "shared"
    if not (shared_dir / "00-must-follow.md").is_file():
        errors.append("missing shared/00-must-follow.md")
    for n in range(1, SHARED_MAX_NUM + 1):
        if not list(shared_dir.glob(f"{n:02d}-*.md")):
            errors.append(f"missing shared/{n:02d}-*.md")


def check_agents_shared_refs(root: Path, errors: list[str]) -> None:
    agents = read(root / "codex/AGENTS.md")
    for rel in SHARED_REF.findall(agents):
        if not (root / "shared" / rel).is_file():
            errors.append(f"AGENTS.md: missing shared/{rel}")


def check_v2_regression_coverage(root: Path, errors: list[str]) -> None:
    required = {
        "examples/99-project-local.mdc.sample": (
            "权威契约：`contracts/openapi.yaml`",
            "禁止手改或作为第二份源头",
        ),
        "evals/prompts.md": ("pageNo=0", "提交前先重查详情", "禁止手改或作为第二份源头"),
        "shared/22-error-recovery-offline.md": ("打开详情时保存的 `version`", "提交前不得重新查询详情"),
        "codex/02-page-generation.md": ("先读权威契约 `contracts/openapi.yaml`", "禁止用手改 `schema.json`"),
        "cursor/22-error-recovery.mdc": ("CONCURRENT_MODIFICATION", "当前持有的 `version`", "稳定 `errorCode`"),
        "codex/05-verification.md": ("稳定 `errorCode`", "当前持有的 `version`", "提交前是否避免重新查询并替换该值"),
        "README.md": ("所有项目都要遵守的基础条款",),
        "docs/rules-package-index.md": ("所有项目都要遵守的基础条款",),
        "codex/AGENTS.md": ("基础条款是所有项目都要遵守的",),
    }
    for rel, markers in required.items():
        content = read(root / rel)
        for marker in markers:
            if marker not in content:
                errors.append(f"{rel}: miniapp v2 coverage missing: {marker}")

    route = read(root / "codex/02-page-generation.md")
    if route.find("contracts/openapi.yaml") > route.find("generated"):
        errors.append("codex/02-page-generation.md must read OpenAPI before generated types")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate miniapp rules package consistency")
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
    p1_ids = [e for e in prompt_ids if P0_MAX_NUM < int(e[1:]) <= 20]
    biz_ids = [e for e in prompt_ids if 21 <= int(e[1:]) <= 29]
    sec_ext_ids = [e for e in prompt_ids if 30 <= int(e[1:]) <= 34]
    res_ext_ids = [e for e in prompt_ids if 35 <= int(e[1:]) <= 38]
    hardening_ids = [e for e in prompt_ids if 39 <= int(e[1:]) <= 44]
    component_ids = [e for e in prompt_ids if 45 <= int(e[1:]) <= 50]
    media_ids = [e for e in prompt_ids if int(e[1:]) == 51]
    testing_ids = [e for e in prompt_ids if int(e[1:]) == 52]
    total = len(prompt_ids)

    if total != TOTAL_PROMPTS:
        errors.append(f"prompts.md total {total}, expected {TOTAL_PROMPTS}")
    if len(p0_ids) != P0_COUNT:
        errors.append(f"prompts.md P0 count {len(p0_ids)}, expected {P0_COUNT}")
    if len(p1_ids) != 12:
        errors.append(f"prompts.md core P1 count {len(p1_ids)}, expected 12")
    if sorted(biz_ids) != BUSINESS_EXTENSION_SUITE:
        errors.append(f"prompts.md Business Extension mismatch: {biz_ids}")
    if sorted(sec_ext_ids) != SECURITY_EXTENSION_SUITE:
        errors.append(f"prompts.md Security Extension mismatch: {sec_ext_ids}")
    if sorted(res_ext_ids) != RESILIENCE_EXTENSION_SUITE:
        errors.append(f"prompts.md Resilience Extension mismatch: {res_ext_ids}")
    if sorted(hardening_ids) != ENTERPRISE_HARDENING_SUITE:
        errors.append(f"prompts.md Enterprise Hardening Extension mismatch: {hardening_ids}")
    if sorted(component_ids) != COMPONENT_ENGINEERING_SUITE:
        errors.append(f"prompts.md Component Engineering Extension mismatch: {component_ids}")
    if sorted(media_ids) != MEDIA_EXTENSION_SUITE:
        errors.append(f"prompts.md Media Extension mismatch: {media_ids}")
    if testing_ids != ["M52"]:
        errors.append(f"prompts.md Testing Governance Extension mismatch: {testing_ids}")
    if prompt_ids != sorted(prompt_ids, key=lambda x: int(x[1:])):
        errors.append("prompts.md M ids not in ascending order")
    if rubric_p0 != [f"{ID_PREFIX}{i:02d}" for i in range(1, P0_COUNT + 1)]:
        errors.append(f"rubric P0 ids mismatch: got {len(rubric_p0)}")
    if rubric_p1 != p1_ids + biz_ids + sec_ext_ids + res_ext_ids + hardening_ids + component_ids + media_ids + testing_ids:
        errors.append("rubric P1+Biz+Sec+Res+Hardening+Component+Media+Testing mismatch prompts")
    if rubric_ids != prompt_ids:
        errors.append("rubric all ids mismatch prompts")
    if results_ids != prompt_ids:
        errors.append("results-template ids mismatch prompts")
    check_eval_topic_guards(prompts, rubric, errors)
    check_ai_tool_safety(root, errors)
    check_component_engineering_contract(root, errors)

    if smoke_path.is_file():
        if PROMPT_HEADING.findall(smoke):
            errors.append("smoke-prompts.md must not use ### Mxx headings")
        smoke_ids = extract_smoke_ids(smoke)
        missing = sorted(set(smoke_ids) - set(prompt_ids), key=lambda x: int(x[1:]))
        if missing:
            errors.append(f"smoke-prompts unknown M ids: {', '.join(missing)}")

        evals_readme = read(root / "evals/README.md")
        core_readme = parse_core_p1_line(
            evals_readme.split("### 核心 P1", 1)[1] if "### 核心 P1" in evals_readme else ""
        )
        core_smoke = parse_smoke_core_p1(smoke)
        if core_readme and core_readme != core_smoke:
            errors.append("evals/README core P1 != smoke table")
        if len(core_smoke) != SMOKE_CORE_P1_COUNT:
            errors.append(f"smoke core P1 count {len(core_smoke)}, expected {SMOKE_CORE_P1_COUNT}")

        sec_smoke = parse_suite_line(smoke, "## Security")
        sec_readme = parse_evals_table_suite(evals_readme, "Security")
        if sorted(sec_smoke) != sorted(SECURITY_SUITE) or sorted(sec_readme) != sorted(SECURITY_SUITE):
            errors.append("Security suite mismatch")

        con_smoke = parse_suite_line(smoke, "## Contract")
        con_readme = parse_evals_table_suite(evals_readme, "Contract")
        if sorted(con_smoke) != sorted(CONTRACT_SUITE) or sorted(con_readme) != sorted(CONTRACT_SUITE):
            errors.append("Contract suite mismatch")

        biz_smoke = parse_suite_line(smoke, "## Business Extension")
        biz_readme = parse_evals_table_suite(evals_readme, "Business Extension")
        if sorted(biz_smoke) != sorted(BUSINESS_EXTENSION_SUITE) or sorted(biz_readme) != sorted(
            BUSINESS_EXTENSION_SUITE
        ):
            errors.append("Business Extension suite mismatch")

        res_smoke = parse_suite_line(smoke, "## Resilience")
        res_readme = parse_evals_table_suite(evals_readme, "Resilience")
        if sorted(res_smoke) != sorted(RESILIENCE_EXTENSION_SUITE) or sorted(res_readme) != sorted(
            RESILIENCE_EXTENSION_SUITE
        ):
            errors.append("Resilience suite mismatch")

        hardening_smoke = parse_suite_line(smoke, "## Enterprise Hardening")
        hardening_readme = parse_evals_table_suite(evals_readme, "Enterprise Hardening")
        if sorted(hardening_smoke) != sorted(ENTERPRISE_HARDENING_SUITE) or sorted(
            hardening_readme
        ) != sorted(ENTERPRISE_HARDENING_SUITE):
            errors.append("Enterprise Hardening suite mismatch")

        component_smoke = parse_suite_line(smoke, "## Component Engineering")
        component_readme = parse_evals_table_suite(evals_readme, "Component Engineering")
        if sorted(component_smoke) != sorted(COMPONENT_ENGINEERING_SUITE) or sorted(
            component_readme
        ) != sorted(COMPONENT_ENGINEERING_SUITE):
            errors.append("Component Engineering suite mismatch")

        testing_smoke = parse_suite_line(smoke, "## Testing Governance")
        testing_readme = parse_evals_table_suite(evals_readme, "Testing Governance")
        if sorted(testing_smoke) != sorted(TESTING_GOVERNANCE_SUITE) or sorted(
            testing_readme
        ) != sorted(TESTING_GOVERNANCE_SUITE):
            errors.append("Testing Governance suite mismatch")

    check_readme_paths(root, errors)
    check_readme_shared_inventory(root, errors)
    check_shared_titles(root, errors)
    check_openapi_ssot_wording(root, errors)
    check_scaffold_assets(root, errors)
    check_project_local_sample(root, errors)
    check_scaffold_runtime(root, errors)
    check_eval_topic_manifest(root, errors)
    check_v2_regression_coverage(root, errors)
    check_shared_numbered_files(root, errors)
    check_cursor_shared_refs(root, errors)
    check_agents_shared_refs(root, errors)
    check_common_governance_refs(root, errors)

    threshold = parse_p1_threshold(rubric)
    if not threshold:
        errors.append("rubric.md missing P1 >= N/M block")
    else:
        min_pass, total_p1 = threshold
        core_p1_count = 12
        if total_p1 != core_p1_count:
            errors.append(f"rubric P1 total {total_p1} != core P1 {core_p1_count}")
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
        m = re.search(r"当前\s+\*{0,2}(\d+)\*{0,2}\s+条", read(overview_path))
        if m and int(m.group(1)) != hard_rules:
            errors.append(f"cursor/00 hard rule count != 00 ({hard_rules})")

    print(f"rules-dir: {root}")
    print(f"VERSION: {version}")
    print(
        f"prompts: {total} (P0={len(p0_ids)}, P1={len(p1_ids)}, "
        f"Biz={len(biz_ids)}, SecExt={len(sec_ext_ids)}, ResExt={len(res_ext_ids)}, "
        f"Hardening={len(hardening_ids)}, Component={len(component_ids)}, "
        f"Media={len(media_ids)}, Testing={len(testing_ids)})"
    )
    if threshold:
        print(f"P1 threshold: >={threshold[0]}/{threshold[1]}")
    if smoke_path.is_file():
        print(f"smoke-prompts M coverage: {len(extract_smoke_ids(smoke))} ids (index only)")

    if errors:
        print("\nFAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\nOK: miniapp rules package consistency checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
