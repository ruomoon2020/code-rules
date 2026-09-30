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
L0_BASELINE_MARKERS = (
    "密码必须使用带盐慢哈希",
    "金额禁止使用 `double` / `float`",
    "时刻必须携带时区或明确 UTC",
    "禁止静默改变已有语义",
)
CONDITIONAL_ROUTE_DUPLICATE_MARKERS = (
    "禁止自研加密、弱密码哈希",
    "金额禁止 `double` / `float`",
    "禁止静默改语义或绕过状态机",
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
PROJECT_LOCAL_ARCHITECTURE_MARKERS = (
    "架构档：",
    "对象命名：",
    "API 风格：",
    "租户模型：",
    "全局表 / 租户豁免表：",
    "数据所有权：",
)
PROJECT_LOCAL_DEFAULT_MARKERS = (
    "架构偏离说明",
    "对象命名兼容说明",
)
ARCHITECTURE_PROFILES = {"CRUD_LITE", "CLASSIC_LAYERED", "DOMAIN_HEXAGONAL"}
OBJECT_NAMING_PROFILES = {"ENTITY_REQUEST_RESPONSE", "DO_DTO_BO_VO_QUERY"}
API_STYLES = {"RESOURCE_REST", "GET_POST_COMPAT"}
TENANCY_MODELS = {"NONE", "SHARED_COLUMN", "SCHEMA_PER_TENANT", "DATABASE_PER_TENANT"}
SCAFFOLD_REQUIRED = (
    "README.md",
    "java/common/datascope/DataScope.java",
    "java/common/datascope/DataScopePolicy.java",
    "java/common/exception/BusinessException.java",
    "java/common/exception/GlobalExceptionHandler.java",
    "java/common/observability/TraceIdFilter.java",
    "java/common/web/ApiResult.java",
    "java/common/web/PageResponse.java",
    "java/modules/system/api/UserController.java",
    "java/modules/system/api/dto/UserDeleteRequest.java",
    "java/modules/system/application/UserService.java",
    "java/modules/system/infrastructure/mapper/UserMapper.java",
    "resources/mapper/system/UserMapper.xml",
    "java/test/UserControllerIT.sample.java",
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


def check_scaffold_assets(root: Path, errors: list[str]) -> None:
    scaffold = root / "examples" / "scaffold"
    missing = [rel for rel in SCAFFOLD_REQUIRED if not (scaffold / rel).is_file()]
    if missing:
        errors.append(f"examples/scaffold missing: {', '.join(missing)}")


def check_architecture_profile_assets(root: Path, errors: list[str]) -> None:
    assets = {
        "examples/archunit/LayeredArchitectureTest.java": (
            "controller_should_not_depend_on_mapper",
            "application_should_not_depend_on_api_layer",
        ),
        "examples/archunit/ClassicLayeredArchitectureTest.java.sample": (
            "web_should_not_depend_on_dao",
            "manager_should_not_depend_on_web",
            "dao_should_not_depend_upward",
        ),
        "examples/archunit/HexagonalArchitectureTest.java.sample": (
            "domain_should_not_depend_on_framework_or_infrastructure",
            "application_should_not_depend_on_adapters",
            "api_should_not_bypass_application",
        ),
        "examples/AGENTS.project-section.md.sample": (
            "架构档：`CRUD_LITE`",
            "对象命名：`ENTITY_REQUEST_RESPONSE`",
            "普通项目直接使用上述组合",
            "复杂域升级 Hexagonal 须有 ADR",
            "API 风格：`GET_POST_COMPAT`",
            "租户模型：`NONE`",
            "全局表 / 租户豁免表：",
            "数据所有权：默认当前模块只写自己的表",
        ),
    }
    for rel, markers in assets.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"missing architecture profile asset: {rel}")
            continue
        content = read(path)
        missing = [marker for marker in markers if marker not in content]
        if missing:
            errors.append(f"{rel} missing architecture markers: {', '.join(missing)}")


def check_openapi_diff_assets(root: Path, errors: list[str]) -> None:
    fixture_dir = root / "examples" / "openapi-diff-fixtures"
    for name in ("base.yaml", "breaking.yaml"):
        if not (fixture_dir / name).is_file():
            errors.append(f"missing OpenAPI diff smoke fixture: {name}")

    command_files = (
        "examples/README.md",
        "examples/ci/backend-ci-required.yml",
        "examples/ci/github-actions-backend.yml",
        "examples/.github/pull_request_template.md",
        "docs/pull-request-template.md",
    )
    for rel in command_files:
        content = read(root / rel)
        if "github.com/oasdiff/oasdiff@v1.32.1" not in content:
            errors.append(f"{rel} must install pinned oasdiff v1.32.1")
        if "oasdiff" not in content or "breaking --fail-on WARN" not in content:
            errors.append(f"{rel} must enforce pinned oasdiff breaking --fail-on WARN")
        if "check-openapi-breaking.py" in content or "redocly diff" in content or "@redocly/cli diff" in content:
            errors.append(f"{rel} references an unsupported OpenAPI diff command")
        if "说明 skip 原因" in content or "OpenAPI diff / Spectral" in content:
            errors.append(f"{rel} must not allow the OpenAPI breaking gate to be skipped or replaced by Spectral")
    for rel in ("examples/ci/backend-ci-required.yml", "examples/ci/github-actions-backend.yml"):
        content = read(root / rel)
        required = (
            "github.event.pull_request.base.sha",
            "fetch-depth: 0",
            "openapi-baseline-bootstrap-approved",
            "git show \"$base:contracts/openapi.baseline.yaml\"",
            "Baseline changed in the same PR",
            "needs.verify.result == 'success'",
        )
        missing = [marker for marker in required if marker not in content]
        if missing:
            errors.append(f"{rel} missing target-branch baseline guard: {', '.join(missing)}")


def check_project_local_sample(root: Path, errors: list[str]) -> None:
    sample = root / "examples" / "99-project-local.mdc.sample"
    if not sample.is_file():
        errors.append("examples/99-project-local.mdc.sample is missing")
        return
    text = read(sample)
    missing = [marker for marker in PROJECT_LOCAL_TESTING_MARKERS if marker not in text]
    if missing:
        errors.append(f"project-local testing governance markers missing: {', '.join(missing)}")
    missing_architecture = [marker for marker in PROJECT_LOCAL_ARCHITECTURE_MARKERS if marker not in text]
    if missing_architecture:
        errors.append(f"project-local architecture/API markers missing: {', '.join(missing_architecture)}")
    missing_defaults = [marker for marker in PROJECT_LOCAL_DEFAULT_MARKERS if marker not in text]
    if missing_defaults:
        errors.append(f"project-local default/compatibility markers missing: {', '.join(missing_defaults)}")
    profile_specs = (
        ("架构档", ARCHITECTURE_PROFILES),
        ("对象命名", OBJECT_NAMING_PROFILES),
        ("API 风格", API_STYLES),
        ("租户模型", TENANCY_MODELS),
    )
    for label, allowed in profile_specs:
        line_match = re.search(rf"(?m)^- {re.escape(label)}：(.+)$", text)
        selected = {
            value for value in allowed
            if line_match is not None and re.search(rf"\b{re.escape(value)}\b", line_match.group(1))
        }
        if len(selected) != 1:
            errors.append(f"project-local {label} must select exactly one of: {', '.join(sorted(allowed))}")


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


def check_scaffold_openapi_alignment(root: Path, errors: list[str]) -> None:
    """Guard the executable example against drifting from the monorepo contract.

    The rules package may be distributed without the repository-level contract,
    so this gate activates when a nearby contracts/openapi.yaml is available.
    """
    contract_candidates = [
        root / "contracts" / "openapi.yaml",
        root.parent / "contracts" / "openapi.yaml",
    ]
    if len(root.parents) > 1:
        contract_candidates.append(root.parents[1] / "contracts" / "openapi.yaml")
    contract_path = next((path for path in contract_candidates if path.is_file()), None)
    if contract_path is None:
        return

    scaffold = root / "examples" / "scaffold" / "java"
    controller_path = scaffold / "modules" / "system" / "api" / "UserController.java"
    create_path = scaffold / "modules" / "system" / "api" / "dto" / "UserCreateRequest.java"
    update_path = scaffold / "modules" / "system" / "api" / "dto" / "UserUpdateRequest.java"
    page_path = scaffold / "modules" / "system" / "api" / "dto" / "UserPageQuery.java"
    audit_page_path = scaffold / "modules" / "system" / "api" / "dto" / "AuditLogPageQuery.java"
    required_files = (controller_path, create_path, update_path, page_path, audit_page_path)
    if not all(path.is_file() for path in required_files):
        return

    contract = read(contract_path)
    controller = read(controller_path)
    create_dto = read(create_path)
    update_dto = read(update_path)
    page_dto = read(page_path)
    audit_page_dto = read(audit_page_path)

    style_match = re.search(r"(?m)^x-api-style:\s*(RESOURCE_REST|GET_POST_COMPAT)\s*$", contract)
    api_style = style_match.group(1) if style_match else None
    contract_markers = (
        "security:\n  - BearerAuth: []",
        "securitySchemes:\n    BearerAuth:",
        "        '201':\n          description: Created",
        "            Location:",
        "        '204':\n          description: No Content",
        "'#/components/responses/BadRequest'",
        "'#/components/responses/Unauthenticated'",
        "'#/components/responses/AccessDenied'",
        "'#/components/responses/NotFound'",
        "'#/components/responses/Conflict'",
        "'#/components/responses/RateLimited'",
        "'#/components/responses/InternalError'",
        "    ApiError:",
        "    ApiResultUserDetail:\n      allOf:\n        - $ref: '#/components/schemas/ApiResultBase'\n        - type: object\n          required: [data]",
        "      required: [username]",
        "      required: [email, version]",
        "      minProperties: 1",
        "x-permission: system:user:read",
        "x-permission: system:user:create",
        "x-permission: system:user:update",
        "x-permission: system:user:delete",
        "    UserDeleteRequest:\n      type: object\n      required: [version]",
        "x-permission: system:audit-log:read",
    )
    missing_contract = [marker for marker in contract_markers if marker not in contract]
    if api_style is None:
        missing_contract.append("x-api-style: RESOURCE_REST | GET_POST_COMPAT")
    elif api_style == "GET_POST_COMPAT":
        compat_markers = (
            "  /api/v1/system/users/{id}/update:\n    post:\n      operationId: systemUserUpdate",
            "  /api/v1/system/users/{id}/delete:\n    post:\n      operationId: systemUserDelete",
        )
        missing_contract.extend(marker for marker in compat_markers if marker not in contract)
    else:
        rest_markers = (
            "    patch:\n      operationId: systemUserUpdate",
            "    delete:\n      operationId: systemUserDelete",
        )
        missing_contract.extend(marker for marker in rest_markers if marker not in contract)
    if missing_contract:
        errors.append(
            "contracts/openapi.yaml missing API-style/security/error markers: "
            + ", ".join(missing_contract)
        )

    controller_markers = [
        ".created(",
        "ResponseEntity.noContent()",
        "system:user:read",
        "system:user:create",
        "system:user:update",
        "system:user:delete",
        "@RequestBody UserDeleteRequest",
    ]
    forbidden_controller_markers: tuple[str, ...] = ()
    if api_style == "GET_POST_COMPAT":
        controller_markers.extend(('@PostMapping("/{id}/update")', '@PostMapping("/{id}/delete")'))
        forbidden_controller_markers = ('@PatchMapping(', '@PutMapping(', '@DeleteMapping(')
    elif api_style == "RESOURCE_REST":
        controller_markers.extend(('@PatchMapping("/{id}")', '@DeleteMapping("/{id}")'))
        forbidden_controller_markers = ('@PostMapping("/{id}/update")', '@PostMapping("/{id}/delete")')
    missing_controller = [marker for marker in controller_markers if marker not in controller]
    unexpected_controller = [marker for marker in forbidden_controller_markers if marker in controller]
    if missing_controller or unexpected_controller:
        errors.append(
            "scaffold UserController API-style/auth contract drift: "
            + ", ".join(missing_controller + [f"unexpected {marker}" for marker in unexpected_controller])
        )

    if re.search(r"\bString\s+status\b", create_dto + update_dto):
        errors.append("scaffold user request DTO exposes status absent from the aligned contract")
    if "@Email String email" not in create_dto:
        errors.append("scaffold UserCreateRequest must enforce OpenAPI email format")
    if "@NotNull @Email String email" not in update_dto or "@NotNull @Min(0) Integer version" not in update_dto:
        errors.append("scaffold UserUpdateRequest must enforce required email, format, and client version")
    service_path = scaffold / "modules" / "system" / "application" / "UserService.java"
    if service_path.is_file():
        service = read(service_path)
        service_markers = (
            "int affected = userMapper.updateById(user)",
            "userMapper.update(null, new LambdaUpdateWrapper<User>()",
            "!request.version().equals(user.getVersion())",
            ".eq(User::getVersion, user.getVersion())",
            ".set(User::getVersion, user.getVersion() + 1)",
            "ErrorCodes.CONCURRENT_MODIFICATION",
            "HttpStatus.CONFLICT",
        )
        missing_service = [marker for marker in service_markers if marker not in service]
        if service.count("!request.version().equals(user.getVersion())") < 2:
            missing_service.append("client version compare on both update and delete")
        if "entity.setVersion(0)" not in service:
            missing_service.append("entity.setVersion(0)")
        if service.count("if (affected != 1)") < 2:
            missing_service.append("affected-row conflict handling on both update and delete")
        if missing_service:
            errors.append("scaffold UserService concurrency result handling missing: " + ", ".join(missing_service))
    delete_dto_path = scaffold / "modules" / "system" / "api" / "dto" / "UserDeleteRequest.java"
    if not delete_dto_path.is_file() or "@NotNull @Min(0) Integer version" not in read(delete_dto_path):
        errors.append("scaffold UserDeleteRequest must require the client version")
    concurrency_test_path = scaffold / "test" / "UserControllerIT.sample.java"
    concurrency_test_markers = (
        "same_version_should_allow_only_first_update",
        "stale_delete_should_preserve_row_and_roll_back_success_audit",
        'jsonPath("$.errorCode").value("CONCURRENT_MODIFICATION")',
        'jsonPath("$.data.version").value(0)',
        "expectDeleteAuditCount(created.id(), 0)",
        "expectDeleteAuditCount(created.id(), 1)",
    )
    if not concurrency_test_path.is_file():
        errors.append("scaffold UserControllerIT concurrency sample missing")
    else:
        concurrency_test = read(concurrency_test_path)
        missing_tests = [marker for marker in concurrency_test_markers if marker not in concurrency_test]
        if missing_tests:
            errors.append("scaffold concurrency behavior tests missing: " + ", ".join(missing_tests))
    for label, dto in (("UserPageQuery", page_dto), ("AuditLogPageQuery", audit_page_dto)):
        if "page = page == null ? 1 : page" not in dto or "pageSize = pageSize == null ? 20 : pageSize" not in dto:
            errors.append(f"scaffold {label} defaults drift from OpenAPI page=1/pageSize=20")

    baseline_path = contract_path.with_name("openapi.baseline.yaml")
    if baseline_path.is_file() and not read(baseline_path).startswith("openapi:"):
        errors.append("contracts/openapi.baseline.yaml must be a standalone released OpenAPI document")
    if re.search(r"in: path\s+required: true\s+schema:\s+type: integer", contract):
        errors.append("contracts/openapi.yaml path id must be string, not integer/int64")
    if "IdPath:" in contract and not re.search(
        r"IdPath:\n      name: id\n      in: path\n      required: true\n      schema:\n        type: string\n",
        contract,
    ):
        errors.append("contracts/openapi.yaml IdPath must be a decimal string")


def check_scaffold_default_tenancy(root: Path, errors: list[str]) -> None:
    """Keep the executable scaffold aligned with the repository default: NONE."""
    relative_paths = (
        "examples/scaffold/java/common/audit/AuditContext.java",
        "examples/scaffold/java/common/exception/ErrorCodes.java",
        "examples/scaffold/java/modules/system/domain/User.java",
        "examples/scaffold/java/modules/system/domain/AuditLog.java",
        "examples/scaffold/java/modules/system/application/UserService.java",
        "examples/scaffold/java/modules/system/application/AuditLogService.java",
        "examples/scaffold/java/modules/system/application/audit/AuditLogRecorder.java",
        "examples/scaffold/java/modules/system/application/converter/UserConverter.java",
        "examples/scaffold/java/modules/system/api/dto/AuditLogSummaryResponse.java",
        "examples/scaffold/java/modules/system/api/dto/AuditLogResponse.java",
        "examples/db/migration/mysql/V1__init_system_user.sql",
        "examples/db/migration/mysql/V2__init_system_audit_log.sql",
        "examples/db/migration/postgresql/V1__init_system_user.sql",
        "examples/db/migration/postgresql/V2__init_system_audit_log.sql",
    )
    forbidden_code = (
        "private String tenantId;",
        "String tenantId,",
        ".setTenantId(",
        ".getTenantId(",
        "currentTenantId(",
        "requireTenantId(",
        "TENANT_CONTEXT_MISSING",
    )
    for rel in relative_paths:
        path = root / rel
        if not path.is_file():
            continue
        content = read(path)
        if path.suffix == ".sql":
            found = []
            if re.search(r"(?m)^\s*tenant_id\s+", content):
                found.append("tenant_id column")
            if re.search(r"(?m)^\s*(?:CONSTRAINT|UNIQUE KEY|KEY|CREATE INDEX).*\btenant_id\b", content):
                found.append("tenant_id index or constraint")
        else:
            found = [marker for marker in forbidden_code if marker in content]
        if found:
            errors.append(f"default NONE scaffold contains tenant implementation in {rel}: {', '.join(found)}")

    contract_candidates = [
        root / "contracts" / "openapi.yaml",
        root.parent / "contracts" / "openapi.yaml",
    ]
    if len(root.parents) > 1:
        contract_candidates.append(root.parents[1] / "contracts" / "openapi.yaml")
    contract_path = next((path for path in contract_candidates if path.is_file()), None)
    if contract_path is not None:
        contract = read(contract_path)
        contract_tenant_markers = ("\n        tenantId:", "- TENANT_CONTEXT_MISSING")
        found = [marker.strip() for marker in contract_tenant_markers if marker in contract]
        if found:
            errors.append("default NONE OpenAPI contains tenant-only contract markers: " + ", ".join(found))

    service_path = root / "examples/scaffold/java/modules/system/application/UserService.java"
    if service_path.is_file():
        service = read(service_path)
        if '.last("ORDER BY' in service:
            errors.append("scaffold UserService must use Wrapper sorting instead of last(ORDER BY ...)")
        required_sort_markers = ("SFunction<User, ?>", "wrapper.orderBy(true, asc, column)")
        missing = [marker for marker in required_sort_markers if marker not in service]
        if missing:
            errors.append("scaffold UserService Wrapper sort whitelist missing: " + ", ".join(missing))


def check_mysql_utc_and_query_samples(root: Path, errors: list[str]) -> None:
    mysql_defaults = {
        "examples/db/migration/mysql/V1__init_system_user.sql": 2,
        "examples/db/migration/mysql/V2__init_system_audit_log.sql": 1,
    }
    for rel, expected_count in mysql_defaults.items():
        path = root / rel
        if not path.is_file():
            continue
        content = read(path)
        if "CURRENT_TIMESTAMP(" in content:
            errors.append(f"{rel}: UTC DATETIME defaults must not depend on CURRENT_TIMESTAMP session time zone")
        actual_count = content.count("DEFAULT (UTC_TIMESTAMP(3))")
        if actual_count != expected_count:
            errors.append(f"{rel}: expected {expected_count} explicit UTC_TIMESTAMP(3) defaults, got {actual_count}")

    datasource = root / "examples/config/application-mybatis.sample.yml"
    if datasource.is_file():
        content = read(datasource)
        for marker in ("connectionTimeZone=UTC", "forceConnectionTimeZoneToSession=true"):
            if marker not in content:
                errors.append(f"application-mybatis.sample.yml missing UTC session marker: {marker}")
        if "serverTimezone=UTC" in content:
            errors.append("application-mybatis.sample.yml must not rely on serverTimezone alias without forcing UTC session")
        if "logic-delete-field: isDeleted" not in content or "logic-delete-value: 1" not in content or "logic-not-delete-value: 0" not in content:
            errors.append("application-mybatis.sample.yml logic delete must filter isDeleted with values 1 and 0")
        if "logic-delete-field: deletedAt" in content or "1970-01-01" in content or "logic-delete-value: UTC_TIMESTAMP" in content:
            errors.append("application-mybatis.sample.yml must not use deletedAt or an epoch sentinel as the logic-delete filter")

    mp_config = root / "examples/config/MybatisPlusConfig.sample.java"
    if mp_config.is_file():
        content = read(mp_config)
        if "new OptimisticLockerInnerInterceptor()" not in content:
            errors.append("MybatisPlusConfig must register OptimisticLockerInnerInterceptor")
        if "new PaginationInnerInterceptor()" not in content or "PaginationInnerInterceptor(DbType" in content:
            errors.append("MybatisPlusConfig pagination must detect the dialect from the current connection")
        if "放在分页插件之前" in content:
            errors.append("MybatisPlusConfig must not claim plugin order controls whether @Version is applied")

    persistence = root / "shared/07-persistence-mybatis.md"
    if persistence.is_file():
        content = read(persistence)
        for marker in (
            "logic-delete-field: isDeleted",
            "logic-delete-value: 1",
            "logic-not-delete-value: 0",
            "delete_token",
            "@TableLogic` 只绑",
            "OptimisticLockerInnerInterceptor",
            '@TableField("is_deleted")',
        ):
            if marker not in content:
                errors.append(f"07-persistence-mybatis.md missing logic-delete marker: {marker}")
        if "1970-01-01" in content or "logic-delete-field: deletedAt" in content:
            errors.append("07-persistence-mybatis.md must not use deletedAt or an epoch sentinel as the logic-delete filter")
        if "放在分页插件之前" in content:
            errors.append("07-persistence-mybatis.md must not claim plugin order controls whether @Version is applied")
        if "不得传入固定 `DbType`" not in content:
            errors.append("07-persistence-mybatis.md must keep pagination dialect detection on the current connection")
        if "(业务键, is_deleted)" not in content:
            errors.append("07-persistence-mybatis.md must forbid a unique key on the boolean delete flag")

    for rel in (
        "examples/db/migration/mysql/V1__init_system_user.sql",
        "examples/db/migration/postgresql/V1__init_system_user.sql",
    ):
        path = root / rel
        if not path.is_file():
            continue
        content = read(path)
        for marker in ("is_deleted", "delete_token", "deleted_by", "uk_sys_user_username_delete_token"):
            if marker not in content:
                errors.append(f"{rel} missing logical-delete column or unique key: {marker}")
        if "1970-01-01" in content or "UNIQUE (username, deleted_at)" in content or "(username, deleted_at)" in content:
            errors.append(f"{rel} must not use deleted_at as the unique or not-deleted sentinel")
        if "(username, is_deleted)" in content:
            errors.append(f"{rel} must not use is_deleted in the unique key")

    data_fix = root / "shared/31-production-data-ops.md"
    if data_fix.is_file():
        content = read(data_fix)
        required_markers = (
            "updated_at = :executed_at_utc",
            "CREATE TABLE ops_data_fix_YYYYMMDD_ticket_id AS",
            "WHERE 1 = 0",
            "CREATE UNIQUE INDEX ops_data_fix_YYYYMMDD_ticket_id_pk",
            "truncated to millisecond precision",
            "DROP TABLE IF EXISTS ops_data_fix_YYYYMMDD_ticket_id_batch;",
            "CREATE TEMPORARY TABLE ops_data_fix_YYYYMMDD_ticket_id_batch (",
            "CREATE TABLE ops_data_fix_YYYYMMDD_ticket_id_gate (",
            "LIMIT :batch_size;",
            "DELETE FROM ops_data_fix_YYYYMMDD_ticket_id_batch;",
            "INSERT INTO ops_data_fix_YYYYMMDD_ticket_id_batch (id)",
            "INSERT INTO ops_data_fix_YYYYMMDD_ticket_id (id, status, updated_at, updated_by)",
            "updated_by = :operator_id",
            "OR (u.updated_by IS NULL AND backup.updated_by IS NULL)",
            "JOIN ops_data_fix_YYYYMMDD_ticket_id_batch batch ON batch.id = u.id",
            "WHERE NOT EXISTS (",
            "WHERE id IN (SELECT id FROM ops_data_fix_YYYYMMDD_ticket_id_batch)",
            "expected_batch_rows",
            "backed_up_batch_rows",
            "updated_batch_rows",
            "WHEN expected_batch_rows = 0 THEN 'BATCH_EMPTY'",
            "READY_TO_COMMIT",
            "ROLLBACK_REQUIRED",
            "FROM ops_data_fix_YYYYMMDD_ticket_id_gate;",
            "Repeat steps 4-7 only after the previous batch transaction has ended",
            "Rollback reuses the batch-key table and the gate table",
            "Repeat steps 9a-9d only after the previous rollback transaction has ended",
        )
        for marker in required_markers:
            if marker not in content:
                errors.append(f"31-production-data-ops.md missing portable bounded-batch marker: {marker}")
        if content.count("is_deleted = 0") < 10:
            errors.append(
                "31-production-data-ops.md must keep is_deleted = 0 on every live sys_user read and write"
            )
        if content.count("version = version + 1") < 4:
            errors.append(
                "31-production-data-ops.md must increment version on the fix and again on rollback"
            )
        if content.count("LIMIT :batch_size;") < 3:
            errors.append("31-production-data-ops.md must bound preview, update, and rollback batches")
        if content.count("INSERT INTO ops_data_fix_YYYYMMDD_ticket_id_batch (id)") < 2:
            errors.append("31-production-data-ops.md rollback must reload the shared batch-key table")
        if content.count("WHEN expected_batch_rows = 0 THEN 'BATCH_EMPTY'") < 2:
            errors.append("31-production-data-ops.md rollback must stop on BATCH_EMPTY")
        if "ops_data_fix_YYYYMMDD_ticket_id_rollback_batch" in content or re.search(
            r"CREATE TEMPORARY TABLE\s+\S+\s+AS", content, re.IGNORECASE
        ):
            errors.append("31-production-data-ops.md rollback must reuse the forward batch table")
        if "CREATE TABLE IF NOT EXISTS ops_data_fix_YYYYMMDD_ticket_id AS" in content:
            errors.append("31-production-data-ops.md must fail instead of reusing a stale rollback backup table")
        if re.search(
            r"CREATE TABLE ops_data_fix_YYYYMMDD_ticket_id AS\s+SELECT id, status, updated_at, updated_by\s+"
            r"FROM sys_user\s+WHERE status = :old_status",
            content,
            re.MULTILINE,
        ):
            errors.append("31-production-data-ops.md must not copy all candidate rows before bounded batches")
        if "updated_at = CURRENT_TIMESTAMP" in content or "updated_at = UTC_TIMESTAMP" in content:
            errors.append("31-production-data-ops.md must bind a portable UTC instant instead of a database-specific timestamp function")
        active_statements = "\n".join(
            line for line in content.splitlines() if not line.lstrip().startswith("--")
        )
        if re.search(r"(?mi)^\s*COMMIT\s*;", active_statements):
            errors.append("31-production-data-ops.md must not commit before the executable batch count gate is evaluated")
        if re.search(r"BEGIN;\s*DROP\s+TABLE", content, re.IGNORECASE):
            errors.append("31-production-data-ops.md must not drop the batch table inside the transaction")
        decision = re.search(
            r"SELECT\s+expected_batch_rows,\s+backed_up_batch_rows,\s+updated_batch_rows,"
            r".*?FROM ops_data_fix_YYYYMMDD_ticket_id_gate;",
            content,
            re.DOTALL,
        )
        if decision is None or "ops_data_fix_YYYYMMDD_ticket_id_batch" in decision.group(0):
            errors.append("31-production-data-ops.md decision query must not reopen the temporary batch table")
        if "-- UPDATE sys_user u" in content and "-- WHERE u.id = b.id" in content:
            errors.append("31-production-data-ops.md must not retain PostgreSQL-only UPDATE FROM rollback syntax")

    service_path = root / "examples/scaffold/java/modules/system/application/UserService.java"
    if service_path.is_file():
        service = read(service_path)
        if ".like(User::getUsername" in service:
            errors.append("scaffold UserService username search must not use two-sided LIKE")
        for marker in (
            ".likeRight(User::getUsername",
            "Instant now = Instant.now()",
            "entity.setCreatedAt(now)",
            "entity.setUpdatedAt(now)",
            "user.setUpdatedAt(Instant.now())",
            "entity.setIsDeleted(0)",
            "entity.setDeleteToken(0L)",
            ".set(User::getIsDeleted, 1)",
            ".set(User::getDeleteToken, user.getId())",
            ".set(User::getDeletedAt, now)",
            ".set(User::getDeletedBy, operatorId)",
            ".eq(User::getIsDeleted, 0)",
            ".eq(User::getVersion, user.getVersion())",
            "DataScope.apply(",
            "DataScope.assertRecord(",
        ):
            if marker not in service:
                errors.append(f"scaffold UserService missing safe sample marker: {marker}")
        if "deleteById(" in service:
            errors.append("scaffold UserService must not deleteById; the delete update must also write the token and audit columns")
    audit_service_path = root / "examples/scaffold/java/modules/system/application/AuditLogService.java"
    if audit_service_path.is_file():
        audit_service = read(audit_service_path)
        for marker in ("DataScope.apply(", "DataScope.assertRecord(", "审计记录不存在"):
            if marker not in audit_service:
                errors.append(f"scaffold AuditLogService missing data-scope marker: {marker}")
        if "audit log not found:" in audit_service:
            errors.append("scaffold AuditLogService must not echo the resource id in the not-found message")
    scope_path = root / "examples/scaffold/java/common/datascope/DataScope.java"
    scope_policy_path = root / "examples/scaffold/java/common/datascope/DataScopePolicy.java"
    if scope_path.is_file() and scope_policy_path.is_file():
        scope = read(scope_path)
        scope_policy = read(scope_policy_path)
        for marker in ("DataScopePolicy policy", "DataScopePolicy.ENTIRE_DIRECTORY", "DataScopePolicy.OWNER_ONLY"):
            if marker not in scope:
                errors.append(f"scaffold DataScope missing explicit policy marker: {marker}")
        for forbidden in ("String resourceType", "includesEntireDirectory"):
            if forbidden in scope:
                errors.append(f"scaffold DataScope must not infer authorization from resource strings: {forbidden}")
        if "public enum DataScopePolicy" not in scope_policy:
            errors.append("scaffold DataScopePolicy must be an explicit enum")
    elif (root / "examples/scaffold/java").is_dir():
        errors.append("scaffold DataScope.java missing")
    user_path = root / "examples/scaffold/java/modules/system/domain/User.java"
    if user_path.is_file():
        user = read(user_path)
        for marker in ("public Integer getIsDeleted()", "public void setIsDeleted(Integer isDeleted)", "public Long getDeleteToken()", "public void setDeleteToken(Long deleteToken)"):
            if marker not in user:
                errors.append(f"scaffold User missing logic-delete accessor: {marker}")
        if user.count("@TableLogic") != 1 or not re.search(
            r'@TableLogic\s+@TableField\("is_deleted"\)\s+private Integer isDeleted;',
            user,
        ):
            errors.append("scaffold User @TableLogic must bind only isDeleted and pin the column name")
        if "1970-01-01" in user:
            errors.append("scaffold User must not use an epoch sentinel for logical delete")


ADR_TEMPLATE_MARKERS = (
    "proposed",
    "accepted",
    "deprecated",
    "### Option A",
    "### Option B",
    "- Description:",
    "## Decision",
    "## Impact",
    "- Compatibility and data migration:",
    "## Migration and Rollback",
    "- Verification evidence and stop conditions:",
    "## Follow-up",
    "- Review date and trigger:",
    "- Deprecation criteria:",
)


def check_adr_templates(root: Path, errors: list[str]) -> None:
    candidates = [root / "docs" / "adr" / "0000-template.md"]
    if len(root.parents) > 1:
        candidates.append(root.parents[1] / "common-governance" / "examples" / "adr-template.md")
    for path in candidates:
        if not path.is_file():
            continue
        content = read(path)
        missing = [marker for marker in ADR_TEMPLATE_MARKERS if marker not in content]
        if missing:
            errors.append(f"{path.name}: ADR template missing fields: {', '.join(missing)}")


def check_feature_flag_lifecycle(root: Path, errors: list[str]) -> None:
    configuration_reference = "21-configuration-" + "sec" + "rets.md"
    required = (
        "稳定 key / 命名前缀",
        "Owner",
        "创建原因",
        "默认值",
        "安全失败值",
        "目标环境",
        "启停条件",
        "观察指标",
        "回滚方式",
        "到期日",
        "失效 / 清理策略",
    )
    targets = (
        ("shared/22-operability.md", "1. 灰度开关须登记", True),
        ("shared/32-service-reliability.md", "3. 功能开关（Feature Flag）", True),
        ("evals/prompts.md", "**期望**：拒绝；环境相关和运维参数", False),
    )
    for rel, prefix, require_exact_reference in targets:
        path = root / rel
        if not path.is_file():
            continue
        line = next((item for item in read(path).splitlines() if item.startswith(prefix)), "")
        missing = [marker for marker in required if marker not in line]
        if require_exact_reference and configuration_reference not in line:
            missing.append(configuration_reference)
        if missing:
            errors.append(f"{rel}: feature flag lifecycle clause missing: {', '.join(missing)}")

    reliability = root / "shared/32-service-reliability.md"
    if reliability.is_file() and "Owner 与过期时间只是该清单子集" in read(reliability):
        errors.append("shared/32-service-reliability.md: stale feature flag subset wording must be removed")
    prompts = root / "evals/prompts.md"
    if prompts.is_file() and "只是该清单子集" in read(prompts):
        errors.append("evals/prompts.md: stale feature flag subset wording must be removed")


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
    boundary = "## 条件触发路由（不计入 Level 0 硬规则）"
    if boundary not in text:
        errors.append("00-must-follow.md missing conditional routing boundary")
    numbered_lines = [line for line in text.splitlines() if re.match(r"^\d+\.\s", line)]
    numbered = "\n".join(numbered_lines)
    numbered_refs = set(BARE_SHARED_REF.findall(numbered))
    for ref in sorted(numbered_refs - L0_ALLOWED_SHARED_REFS):
        errors.append(f"00-must-follow.md: non-L0 shared rule numbered as L0: {ref}")
    for marker in HIGH_LEVEL_TOPIC_MARKERS:
        if marker in numbered:
            errors.append(f"00-must-follow.md: high-level topic numbered as L0: {marker}")
    for marker in L0_BASELINE_MARKERS:
        if marker not in numbered:
            errors.append(f"00-must-follow.md: missing numbered L0 baseline: {marker}")
    if boundary in text:
        conditional = text.split(boundary, 1)[1]
        for marker in CONDITIONAL_ROUTE_DUPLICATE_MARKERS:
            if marker in conditional:
                errors.append(f"00-must-follow.md: L0 baseline duplicated in conditional route: {marker}")


def check_v2_regression_coverage(root: Path, errors: list[str]) -> None:
    quality = read(root / "shared/23-quality-gates.md")
    for marker in (
        "oasdiff breaking --fail-on WARN",
        "openapi-baseline-bootstrap-approved",
        "已有目标分支契约时初始 baseline 必须与它一致",
        "OpenAPI breaking 门禁不得用此条绕过",
    ):
        if marker not in quality:
            errors.append(f"23-quality-gates.md missing OpenAPI baseline gate: {marker}")
    if "无 baseline 须在 PR 说明 skip" in quality:
        errors.append("23-quality-gates.md must not allow a missing baseline to be skipped")

    agents = read(root / "codex/AGENTS.md")
    migration_line = next((line for line in agents.splitlines() if "**/db/migration/**" in line), "")
    for marker in ("02-naming.md", "07-persistence-mybatis.md", "43-business-module-extension.md"):
        if marker not in migration_line:
            errors.append(f"codex migration route missing: {marker}")

    prompts = read(root / "evals/prompts.md")
    for marker in (
        "pageNo=0",
        'last("ORDER BY " + sortField)',
        "### B70 — 逻辑删除直接 deleteById",
        "### B71 — 更新前重查最新 version",
    ):
        if marker not in prompts:
            errors.append(f"backend v2 negative eval missing: {marker}")

    required = {
        "shared/00-must-follow.md": ("契约变更须运行固定版本 `oasdiff breaking --fail-on WARN` 并完成兼容性 Review",),
        "shared/04-rest-api-design.md": ("固定版本 `oasdiff breaking --fail-on WARN` 进 CI",),
        "shared/15-testing.md": ("oasdiff breaking --fail-on WARN", "OpenAPI breaking 门禁不得靠说明原因跳过"),
        "cursor/04-rest-controller.mdc": ("路径 ID 使用 `string`", "当前 `version`", "初始 `version`"),
        "cursor/16-quality-gates.mdc": ("oasdiff breaking --fail-on WARN", "不得用 PR 说明跳过"),
        "docs/rule-maturity-model.md": ("所有项目都要遵守的基础条款", "oasdiff breaking --fail-on WARN"),
        "docs/onboarding-new-project.md": ("4. 固定版本 `oasdiff breaking --fail-on WARN`（契约 PR 必跑）",),
        "docs/release-checklist.md": ("固定版本 `oasdiff breaking --fail-on WARN` 已相对上一已发布 baseline / PR base Review",),
        "README.md": ("5. 接入 `examples/` 中 ArchUnit、Checkstyle、固定版本 `oasdiff breaking --fail-on WARN`",),
        "RELEASE.md": (
            "首次建立 baseline 须由 Owner 显式批准，禁止用 PR 说明代替门禁",
            "固定版本 `oasdiff breaking --fail-on WARN`",
        ),
        "examples/README.md": (
            "Level 0+：verify（Maven/Gradle 自动识别）、固定版本 `oasdiff breaking --fail-on WARN`、secret scan",
            "`./gradlew check`（CI 自动识别）、固定版本 `oasdiff breaking --fail-on WARN`、secret scan（gitleaks）",
        ),
    }
    for rel, markers in required.items():
        content = read(root / rel)
        for marker in markers:
            if marker not in content:
                errors.append(f"{rel}: backend v2 summary missing: {marker}")


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
    check_shared_titles(root, errors)
    check_scaffold_assets(root, errors)
    check_architecture_profile_assets(root, errors)
    check_openapi_diff_assets(root, errors)
    check_project_local_sample(root, errors)
    check_scaffold_runtime(root, errors)
    check_scaffold_openapi_alignment(root, errors)
    check_scaffold_default_tenancy(root, errors)
    check_mysql_utc_and_query_samples(root, errors)
    check_feature_flag_lifecycle(root, errors)
    check_adr_templates(root, errors)
    check_scaffold_exception_contract(root, errors)
    check_l0_hard_rule_scope(root, errors)
    check_eval_topic_manifest(root, errors)
    check_v2_regression_coverage(root, errors)
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
