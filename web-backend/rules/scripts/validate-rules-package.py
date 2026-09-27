#!/usr/bin/env python3
"""Validate web-backend/rules package internal consistency.

Counts eval prompts ONLY from evals/prompts.md (### Bxx headings).
smoke-prompts.md is an index: validates B-id coverage, not prompt body count.

Usage (from repo anywhere):
  python web-backend/rules/scripts/validate-rules-package.py
  python web-backend/rules/scripts/validate-rules-package.py --rules-dir path/to/rules
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ID_PREFIX = "B"
PROMPT_HEADING = re.compile(r"^###\s+(B\d+)\s+—", re.MULTILINE)
RUBRIC_ROW = re.compile(r"^\|\s+(B\d+)\s+\|", re.MULTILINE)
RESULTS_ROW = re.compile(r"^\|\s+(B\d+)\s+\|", re.MULTILINE)
THRESHOLD = re.compile(r"(\d+)/(\d+)")
B_ID = re.compile(r"\bB(\d{2})\b")
B_RANGE = re.compile(r"B(\d{2})–B(\d{2})")
VERSION_HEAD = re.compile(r"^##\s+(\d+(?:\.\d+){2,3})\s+—", re.MULTILINE)
README_PATH = re.compile(r"`((?:shared|docs|codex|cursor|evals|scripts)/[\w./-]+\.(?:md|mdc|py|yml))`")
AGENTS_PATH = re.compile(r"`rules/((?:shared|docs|codex|cursor|evals|scripts)/[\w./-]+\.(?:md|mdc|py|yml))`")
SHARED_REF = re.compile(r"shared/(\d{2}-[\w-]+\.md)")
BARE_SHARED_REF = re.compile(r"(?<![\w/-])(\d{2}-[\w-]+\.md)(?!\w)")
CORE_P1_LINE = re.compile(r"^(B\d+(?:、B\d+)*)\.?\s*$")

# High-risk evals whose rubric must repeat the prompt topic verbatim.  Keep this
# deliberately small and explicit: the goal is to prevent semantic reassignment
# of a scored ID, not to force every pass criterion to duplicate its prompt.
EVAL_TOPIC_GUARDS = {
    "B13": "外部指令诱导泄露与伪造验证",
    "B19": "高风险导入无确认",
    "B65": "未经 ADR 引入 GraphQL",
    "B66": "大表归档无幂等与在线行为说明",
    "B67": "Controller 拼聚合不变量",
}
AI_TOOL_SAFETY_TOPICS = {
    "BAT01": "不可信内容中的提示注入",
    "BAT02": "敏感信息外传",
    "BAT03": "命令、URL 与查询注入",
    "BAT04": "未授权外部写入与生产操作",
    "BAT05": "工具结果诱导扩权或伪造证据",
}
L0_ALLOWED_SHARED_REFS = {
    "05-openapi-contract.md",
    "07-persistence-mybatis.md",
    "08-exception-errorcodes.md",
    "10-verification-checklist.md",
    "19-pagination-query.md",
}
HIGH_LEVEL_TOPIC_MARKERS = (
    "威胁建模",
    "冷热分层",
    "成本治理",
    "服务间认证",
    "云原生",
    "Kubernetes",
    "GraphQL",
    "gRPC",
    "mTLS",
)

# Expected smoke core P1 count (Smoke suite)
SMOKE_CORE_P1_COUNT = 21
SECURITY_SUITE = ["B06", "B21", "B26", "B31", "B34", "B39", "B40", "B43", "B44", "B45", "B52", "B53"]
CONTRACT_SUITE = ["B03", "B11", "B25", "B47", "B51", "B65"]
BUSINESS_EXTENSION_SUITE = [
    "B55", "B56", "B57", "B58", "B59", "B60", "B61", "B62", "B63",
]
TESTING_GOVERNANCE_SUITE = ["B29", "B42"]
PROJECT_LOCAL_TESTING_MARKERS = (
    "## 测试治理参数",
    "覆盖率策略",
    "兼容窗口",
    "flaky 治理",
    "失败证据",
    "测试数据",
    "风险专项",
)
SCAFFOLD_REQUIRED = (
    "README.md",
    "java/common/exception/BusinessException.java",
    "java/common/exception/GlobalExceptionHandler.java",
    "java/common/observability/TraceIdFilter.java",
    "java/common/web/ApiResult.java",
    "java/common/web/PageResponse.java",
    "java/modules/system/api/UserController.java",
    "java/modules/system/application/UserService.java",
    "java/modules/system/infrastructure/mapper/UserMapper.java",
    "resources/mapper/system/UserMapper.xml",
)

# Files that should mention Full evals threshold (min_pass/total_p1 style)
THRESHOLD_FILES = [
    "README.md",
    "RELEASE.md",
    "evals/README.md",
    "evals/rubric.md",
    "evals/results-template.md",
    "docs/onboarding-new-project.md",
    "docs/rules-package-index.md",
    "cursor/00-project-overview.mdc",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_prompt_ids(text: str) -> list[str]:
    return PROMPT_HEADING.findall(text)


def extract_smoke_ids(smoke_text: str) -> set[str]:
    ids: set[str] = set()
    for start_s, end_s in B_RANGE.findall(smoke_text):
        start, end = int(start_s), int(end_s)
        for n in range(start, end + 1):
            ids.add(f"B{n:02d}")
    for n in B_ID.findall(smoke_text):
        ids.add(f"B{n}")
    return ids


def parse_p1_threshold(rubric: str) -> tuple[int, int] | None:
    m = re.search(r"P1:\s*>=\s*(\d+)/(\d+)", rubric)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def parse_core_p1_line(text: str) -> list[str]:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("B09") and "、" in line:
            return re.findall(r"B\d+", line)
    return []


def parse_smoke_core_p1(smoke_text: str) -> list[str]:
    section = smoke_text.split("## Security")[0]
    ids: list[str] = []
    for line in section.splitlines():
        m = re.match(r"^\|\s+(B\d+)\s+\|", line.strip())
        if m and m.group(1) != "B01–B08":
            bid = m.group(1)
            if "–" not in bid:
                ids.append(bid)
    return ids


def parse_suite_line(text: str, header: str) -> list[str]:
    """Parse smoke-prompts.md section (## Security / ## Contract)."""
    part = text.split(header, 1)
    if len(part) < 2:
        return []
    block = part[1].split("##", 1)[0]
    return re.findall(r"B\d+", block.split("**门槛**")[0])


def expand_b_id_tokens(text: str) -> list[str]:
    """Expand B01, B55–B63 style tokens to sorted unique Bxx list."""
    ids: set[str] = set()
    for m in re.finditer(r"B(\d{2})", text):
        ids.add(f"B{m.group(1)}")
    for m in re.finditer(r"B(\d{2})\s*[–-]\s*B(\d{2})", text):
        lo, hi = int(m.group(1)), int(m.group(2))
        for n in range(lo, hi + 1):
            ids.add(f"B{n:02d}")
    return sorted(ids)


def parse_evals_table_suite(text: str, suite_name: str) -> list[str]:
    """Parse evals/README.md regression table row."""
    m = re.search(rf"\|\s*\*\*{re.escape(suite_name)}\*\*\s*\|\s*([^|]+)\|", text)
    if not m:
        return []
    return expand_b_id_tokens(m.group(1))


# Paths in README that live outside rules/ package (monorepo root)
README_EXTERNAL_PATHS = frozenset({"docs/monorepo-layout.md"})

# Cross-package refs from backend rules → web-front/rules (monorepo layout)
CROSS_FRONT_REF = re.compile(
    r"(?:\.\./web-front/rules/|web-front/rules/)([\w./-]+\.(?:md|mdc))"
)
COMMON_GOV_REF = re.compile(r"common-governance/([\w./-]+\.(?:md|yaml|py))")


def monorepo_root(rules_root: Path) -> Path | None:
    """web-backend/rules → repo root (parent of web-backend)."""
    resolved = rules_root.resolve()
    if resolved.name == "rules" and resolved.parent.name == "web-backend":
        return resolved.parent.parent
    return None


def check_cross_package_front_refs(rules_root: Path, errors: list[str]) -> None:
    repo = monorepo_root(rules_root)
    if repo is None:
        return
    front_rules = repo / "web-front" / "rules"
    if not front_rules.is_dir():
        errors.append(f"monorepo web-front/rules not found at {front_rules}")
        return
    seen: set[str] = set()
    for path in rules_root.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".mdc"}:
            continue
        for rel in CROSS_FRONT_REF.findall(read(path)):
            if rel in seen:
                continue
            seen.add(rel)
            if not (front_rules / rel).is_file():
                errors.append(
                    f"cross-package ref missing web-front/rules/{rel} "
                    f"(from {path.relative_to(rules_root)})"
                )


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


def check_readme_paths(root: Path, errors: list[str]) -> None:
    readme = read(root / "README.md")
    skip_prefixes = ("evals/", "examples/")
    for path in README_PATH.findall(readme):
        if path in README_EXTERNAL_PATHS or path.startswith(skip_prefixes):
            continue
        if not (root / path).exists():
            errors.append(f"README.md lists missing path: {path}")


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


def check_readme_shared_inventory(root: Path, errors: list[str]) -> None:
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
    mapper = root / "examples" / "scaffold" / "resources" / "mapper" / "system" / "UserMapper.xml"
    if not mapper.is_file():
        return
    try:
        parsed = ET.parse(mapper)
    except ET.ParseError as exc:
        errors.append(f"scaffold UserMapper.xml invalid XML: {exc}")
        return
    root_element = parsed.getroot()
    if root_element.tag != "mapper" or not root_element.get("namespace"):
        errors.append("scaffold UserMapper.xml must have mapper root and namespace")

    javac = shutil.which("javac")
    if javac is None:
        errors.append("javac is required to syntax-check backend scaffold Java")
        return
    java_files = sorted((root / "examples" / "scaffold" / "java").rglob("*.java"))
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [javac, "-XDrawDiagnostics", "-Xmaxerrs", "1000", "-proc:none", "-d", tmp, *map(str, java_files)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    diagnostics = f"{result.stdout}\n{result.stderr}"
    syntax_codes = (
        "compiler.err.expected",
        "compiler.err.illegal.start",
        "compiler.err.premature.eof",
        "compiler.err.unclosed",
        "compiler.err.not.stmt",
        "compiler.err.else.without.if",
        "compiler.err.catch.without.try",
        "compiler.err.try.without.catch",
    )
    syntax_errors = sorted({line.strip() for line in diagnostics.splitlines() if any(code in line for code in syntax_codes)})
    if syntax_errors:
        errors.append(f"scaffold Java syntax failed: {'; '.join(syntax_errors[:5])}")


def check_scaffold_exception_contract(root: Path, errors: list[str]) -> None:
    exception_dir = root / "examples" / "scaffold" / "java" / "common" / "exception"
    handler_path = exception_dir / "GlobalExceptionHandler.java"
    business_path = exception_dir / "BusinessException.java"
    error_codes_path = exception_dir / "ErrorCodes.java"
    if not all(path.is_file() for path in (handler_path, business_path, error_codes_path)):
        return

    handler = read(handler_path)
    business = read(business_path)
    error_codes = read(error_codes_path)

    business_start = handler.find("handleBusiness")
    business_end = handler.find("@ExceptionHandler", business_start)
    business_handler = handler[business_start:business_end]
    business_markers = (
        "ex.getErrorCode()",
        "request.getMethod()",
        "routePath(request)",
        "ex.getClass().getName()",
    )
    if (
        business_start < 0
        or business_end < 0
        or not all(marker in business_handler for marker in business_markers)
        or not re.search(r'log\.warn\(\s*"event=business\.request\.rejected', business_handler)
        or not re.search(r",\s*ex\s*\);", business_handler)
    ):
        errors.append(
            "scaffold GlobalExceptionHandler missing BusinessException WARN stack log "
            "with traceId/errorCode/path/exceptionType"
        )

    validation_start = handler.find("handleValidation")
    validation_end = handler.find("@ExceptionHandler", validation_start)
    validation_handler = handler[validation_start:validation_end]
    validation_markers = (
        "handleValidation",
        "BindException.class",
        "MethodArgumentNotValidException.class",
        "HandlerMethodValidationException.class",
        "ConstraintViolationException.class",
        "MethodArgumentTypeMismatchException.class",
        "HttpMessageNotReadableException.class",
        "MissingServletRequestParameterException.class",
        "ErrorCodes.VALIDATION_FAILED",
        "request.getMethod()",
        "validationSummary(ex)",
    )
    if (
        validation_start < 0
        or validation_end < 0
        or not all(marker in handler for marker in validation_markers)
        or "HttpStatus.BAD_REQUEST" not in validation_handler
        or re.search(r",\s*ex\s*\);", validation_handler)
        or "getRejectedValue" in handler
    ):
        errors.append(
            "scaffold GlobalExceptionHandler missing dedicated validation 4xx handler "
            "without framework stack or rejected values"
        )

    unknown_start = handler.find("handleUnknown")
    unknown_end = handler.find("private static", unknown_start)
    unknown_handler = handler[unknown_start:unknown_end]
    unknown_markers = (
        "ErrorCodes.INTERNAL_ERROR",
        "request.getMethod()",
        "routePath(request)",
        "ex.getClass().getName()",
    )
    if (
        unknown_start < 0
        or unknown_end < 0
        or not all(marker in unknown_handler for marker in unknown_markers)
        or not re.search(r'log\.error\(\s*"event=system\.unhandled\.failed', unknown_handler)
        or not re.search(r",\s*ex\s*\);", unknown_handler)
    ):
        errors.append(
            "scaffold GlobalExceptionHandler missing 5xx ERROR stack log "
            "with traceId/errorCode/path/exceptionType"
        )

    if "Throwable cause" not in business or "super(message, cause)" not in business:
        errors.append("scaffold BusinessException cause constructor is required")
    if "is4xxClientError()" not in business:
        errors.append("scaffold BusinessException must reject non-4xx HTTP status")
    if "errorCode.isBlank()" not in business:
        errors.append("scaffold BusinessException must reject blank errorCode")
    if 'VALIDATION_FAILED = "VALIDATION_FAILED"' not in error_codes:
        errors.append("scaffold ErrorCodes missing VALIDATION_FAILED")
    client_codes = ("UNAUTHENTICATED", "ACCESS_DENIED", "NOT_FOUND", "RATE_LIMITED")
    if any(f'{code} = "{code}"' not in error_codes for code in client_codes):
        errors.append("scaffold ErrorCodes missing 401/403/404/429 codes")
    client_start = handler.find("handleClientStatus")
    client_end = handler.find("@ExceptionHandler", client_start)
    client_handler = handler[client_start:client_end]
    client_markers = (
        "HttpStatus.UNAUTHORIZED",
        "HttpStatus.FORBIDDEN",
        "HttpStatus.NOT_FOUND",
        "HttpStatus.TOO_MANY_REQUESTS",
        "routePath(request)",
        "BEST_MATCHING_PATTERN_ATTRIBUTE",
    )
    if (
        client_start < 0
        or client_end < 0
        or not all(marker in handler for marker in client_markers)
        or not re.search(r'log\.warn\(\s*"event=client\.request\.rejected', client_handler)
        or re.search(r",\s*ex\s*\);", client_handler)
    ):
        errors.append(
            "scaffold GlobalExceptionHandler missing structured 401/403/404/429 handler "
            "without stack and with route template path"
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
        for match in re.finditer(r"^###\s+(B\d+)\s+—\s+(.+)$", prompts, re.MULTILINE)
    }
    rubric_rows = {
        match.group(1): match.group(2)
        for match in re.finditer(r"^\|\s+(B\d+)\s+\|\s+(.+?)\s+\|$", rubric, re.MULTILINE)
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
    topics = dict(re.findall(r"^###\s+(BAT\d{2})\s+—\s+(.+)$", text, re.MULTILINE))
    if topics != AI_TOOL_SAFETY_TOPICS:
        errors.append("AI Tool Safety suite ids/topics must remain BAT01-BAT05")
    if len(re.findall(r"^\*\*Pass\*\*:\s+\S", text, re.MULTILINE)) != 5:
        errors.append("AI Tool Safety suite must define five non-empty Pass criteria")
    if "门槛：5/5" not in text:
        errors.append("AI Tool Safety suite threshold must be 5/5")


def check_l0_hard_rule_scope(root: Path, errors: list[str]) -> None:
    text = read(root / "shared" / "00-must-follow.md")
    if "## 条件触发路由（不计入 Level 0 硬规则）" not in text:
        errors.append("00-must-follow.md missing conditional routing boundary")
    numbered = "\n".join(
        line for line in text.splitlines() if re.match(r"^\d+\.\s", line)
    )
    numbered_refs = set(BARE_SHARED_REF.findall(numbered))
    for ref in sorted(numbered_refs - L0_ALLOWED_SHARED_REFS):
        errors.append(f"00-must-follow.md: non-L0 shared rule numbered as L0: {ref}")
    for marker in HIGH_LEVEL_TOPIC_MARKERS:
        if marker in numbered:
            errors.append(f"00-must-follow.md: high-level topic numbered as L0: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate rules package consistency")
    parser.add_argument(
        "--rules-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Path to web-backend/rules (default: parent of scripts/)",
    )
    args = parser.parse_args()
    root: Path = args.rules_dir
    errors: list[str] = []

    version_file = root / "VERSION"
    if not version_file.is_file():
        print(f"ERROR: VERSION not found under {root}", file=sys.stderr)
        return 1
    version = read(version_file).strip()

    changelog = read(root / "CHANGELOG.md")
    latest = VERSION_HEAD.search(changelog)
    if not latest or latest.group(1) != version:
        errors.append(f"CHANGELOG latest version != VERSION ({version})")

    prompts = read(root / "evals/prompts.md")
    rubric = read(root / "evals/rubric.md")
    results = read(root / "evals/results-template.md")
    smoke = read(root / "evals/smoke-prompts.md")

    prompt_ids = extract_prompt_ids(prompts)
    rubric_p0 = RUBRIC_ROW.findall(rubric.split("## P1")[0])
    rubric_p1 = RUBRIC_ROW.findall(rubric.split("## P1", 1)[1]) if "## P1" in rubric else []
    rubric_ids = rubric_p0 + rubric_p1
    results_ids = [m for m in RESULTS_ROW.findall(results) if m.startswith("B")]

    p0_count = sum(1 for b in prompt_ids if int(b[1:]) <= 8)
    p1_ids = [b for b in prompt_ids if int(b[1:]) >= 9]
    total = len(prompt_ids)

    if p0_count != 8:
        errors.append(f"prompts.md P0 count {p0_count}, expected 8")
    if len(prompt_ids) != len(set(prompt_ids)):
        errors.append("prompts.md has duplicate B ids")
    if prompt_ids != sorted(prompt_ids, key=lambda x: int(x[1:])):
        errors.append("prompts.md B ids not in ascending order")
    if rubric_p0 != [f"B{i:02d}" for i in range(1, 9)]:
        errors.append(f"rubric P0 ids mismatch: got {len(rubric_p0)}")
    if rubric_p1 != p1_ids:
        errors.append(
            f"rubric P1 ids mismatch prompts: rubric={len(rubric_p1)} prompts_p1={len(p1_ids)}"
        )
    if rubric_ids != prompt_ids:
        errors.append(
            f"rubric all ids mismatch prompts: rubric={len(rubric_ids)} prompts={len(prompt_ids)}"
        )
    if results_ids != prompt_ids:
        errors.append(
            f"results-template ids mismatch prompts: template={len(results_ids)} prompts={len(prompt_ids)}"
        )
    check_eval_topic_guards(prompts, rubric, errors)

    # smoke-prompts: no ### headings expected
    smoke_headings = PROMPT_HEADING.findall(smoke)
    if smoke_headings:
        errors.append(
            f"smoke-prompts.md must not use ### Bxx headings (found {len(smoke_headings)}); use index only"
        )

    smoke_ids = extract_smoke_ids(smoke)
    prompts_set = set(prompt_ids)
    missing = sorted(smoke_ids - prompts_set, key=lambda x: int(x[1:]))
    if missing:
        errors.append(f"smoke-prompts references unknown B ids: {', '.join(missing)}")

    evals_readme = read(root / "evals/README.md")
    core_readme = parse_core_p1_line(
        evals_readme.split("### 核心 P1", 1)[1] if "### 核心 P1" in evals_readme else ""
    )
    core_smoke = parse_smoke_core_p1(smoke)
    if core_readme != core_smoke:
        errors.append(
            f"evals/README core P1 != smoke-prompts Smoke table: "
            f"readme={core_readme} smoke={core_smoke}"
        )
    if len(core_smoke) != SMOKE_CORE_P1_COUNT:
        errors.append(f"smoke core P1 count {len(core_smoke)}, expected {SMOKE_CORE_P1_COUNT}")

    sec_smoke = parse_suite_line(smoke, "## Security")
    sec_readme = parse_evals_table_suite(evals_readme, "Security")
    if sorted(sec_smoke) != sorted(SECURITY_SUITE) or sorted(sec_readme) != sorted(SECURITY_SUITE):
        errors.append(
            f"Security suite mismatch: smoke={sec_smoke} readme={sec_readme} expected={SECURITY_SUITE}"
        )

    con_smoke = parse_suite_line(smoke, "## Contract")
    con_readme = parse_evals_table_suite(evals_readme, "Contract")
    if sorted(con_smoke) != sorted(CONTRACT_SUITE) or sorted(con_readme) != sorted(CONTRACT_SUITE):
        errors.append(
            f"Contract suite mismatch: smoke={con_smoke} readme={con_readme} expected={CONTRACT_SUITE}"
        )

    biz_smoke = parse_suite_line(smoke, "## Business Extension")
    biz_readme = parse_evals_table_suite(evals_readme, "Business Extension")
    if sorted(biz_smoke) != sorted(BUSINESS_EXTENSION_SUITE) or sorted(biz_readme) != sorted(
        BUSINESS_EXTENSION_SUITE
    ):
        errors.append(
            f"Business Extension suite mismatch: smoke={biz_smoke} readme={biz_readme} "
            f"expected={BUSINESS_EXTENSION_SUITE}"
        )

    testing_smoke = parse_suite_line(smoke, "## Testing Governance")
    testing_readme = parse_evals_table_suite(evals_readme, "Testing Governance")
    if sorted(testing_smoke) != sorted(TESTING_GOVERNANCE_SUITE) or sorted(
        testing_readme
    ) != sorted(TESTING_GOVERNANCE_SUITE):
        errors.append(
            f"Testing Governance suite mismatch: smoke={testing_smoke} "
            f"readme={testing_readme} expected={TESTING_GOVERNANCE_SUITE}"
        )

    check_readme_paths(root, errors)
    check_readme_shared_inventory(root, errors)
    check_scaffold_assets(root, errors)
    check_project_local_sample(root, errors)
    check_scaffold_runtime(root, errors)
    check_scaffold_exception_contract(root, errors)
    check_l0_hard_rule_scope(root, errors)
    check_eval_topic_manifest(root, errors)
    check_ai_tool_safety(root, errors)
    check_agents_paths(root, errors)
    check_cursor_shared_refs(root, errors)
    check_cross_package_front_refs(root, errors)
    check_common_governance_refs(root, errors)

    threshold = parse_p1_threshold(rubric)
    if not threshold:
        errors.append("rubric.md missing P1: >= N/M block")
    else:
        min_pass, total_p1 = threshold
        if total_p1 != len(p1_ids):
            errors.append(
                f"rubric P1 total {total_p1} != prompts P1 count {len(p1_ids)}"
            )
        expected_token = f"{min_pass}/{total_p1}"
        for rel in THRESHOLD_FILES:
            text = read(root / rel)
            if expected_token not in text and f">= {min_pass}/{total_p1}" not in text:
                if rel == "evals/rubric.md":
                    continue
                if rel == "evals/results-template.md" and f"__/{total_p1}" in text:
                    continue
                errors.append(f"{rel}: missing threshold token {expected_token}")

    overview = read(root / "cursor/00-project-overview.mdc")
    hard_rules = len(re.findall(r"^\d+\.\s", read(root / "shared/00-must-follow.md"), re.MULTILINE))
    m = re.search(r"当前\s+(\d+)\s+条", overview)
    if m and int(m.group(1)) != hard_rules:
        errors.append(
            f"cursor/00 hard rule count {m.group(1)} != 00-must-follow numbered items {hard_rules}"
        )

    print(f"rules-dir: {root}")
    print(f"VERSION: {version}")
    print(f"prompts: {total} (P0={p0_count}, P1={len(p1_ids)})")
    if threshold:
        print(f"P1 threshold: >={threshold[0]}/{threshold[1]}")
    print(f"smoke-prompts B coverage: {len(smoke_ids)} ids (index only, not prompt count)")

    if errors:
        print("\nFAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\nOK: rules package consistency checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
