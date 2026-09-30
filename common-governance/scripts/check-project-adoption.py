#!/usr/bin/env python3
"""Check business project adoption of code-rules packages.

Usage:
  python scripts/check-project-adoption.py --repo ./my-frontend --stack frontend
  python common-governance/scripts/check-project-adoption.py --repo . --stack backend --strict --require-governance

Exit 0 if all required checks pass; 1 otherwise.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment failure path
    yaml = None

REQUIRED_FRONTEND_SCRIPTS = ("lint", "type-check", "build")
REQUIRED_MINIAPP_SCRIPTS = ("lint", "type-check", "build:mp-weixin")
REQUIRED_FRONTEND_LEVEL1_SCRIPTS = ("api:check",)
REQUIRED_MINIAPP_LEVEL1_SCRIPTS = ("api:check", "size:check")
GOVERNANCE_REQUIRED_FILES = (
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
    "examples/ci/ai-eval-results-required.yml",
    "examples/ci/supply-chain-required.yml",
    "examples/governance-adoption.yaml",
    "examples/governance-platform-evidence.json",
    "examples/PROJECT_RULES.md.sample",
    "examples/contract-baseline.md.sample",
    "examples/migration-baseline.json",
    "examples/ai-eval-results.yaml",
    "scripts/check-debt-baseline.py",
    "scripts/check-project-adoption.py",
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
EVIDENCE_URL = re.compile(r"https://[^\s]+$", re.IGNORECASE)
CONTRACT_DECLARATION = re.compile(
    r"(?:contract\s+path|contract\s+ssot|openapi\s+ssot|契约\s*(?:路径|ssot))\s*[:：]\s*`?([^`\s]+)",
    re.IGNORECASE,
)
PLACEHOLDER_SCRIPT = re.compile(r"^(?:echo\b|printf\b|true$|exit\s+0$)", re.IGNORECASE)


def check_exists(repo: Path, rel: str, errors: list[str], label: str) -> bool:
    path = repo / rel
    if not path.exists():
        errors.append(f"MISSING {label}: {rel}")
        return False
    return True


def check_agents(repo: Path, errors: list[str]) -> None:
    agents = repo / "AGENTS.md"
    if not agents.is_file():
        errors.append("MISSING AGENTS.md at repository root")
        return
    text = agents.read_text(encoding="utf-8")
    if "rules/" not in text and "rules/shared" not in text:
        errors.append("AGENTS.md should reference rules/ paths")


def check_cursor_rules(repo: Path, errors: list[str]) -> None:
    cursor_dir = repo / ".cursor" / "rules"
    if not cursor_dir.is_dir():
        errors.append("MISSING .cursor/rules/ directory")
        return
    mdc_files = list(cursor_dir.glob("*.mdc"))
    if not mdc_files:
        errors.append("MISSING .cursor/rules/*.mdc (copy from rules/cursor/)")
    overview = cursor_dir / "00-project-overview.mdc"
    if not overview.is_file():
        errors.append("MISSING .cursor/rules/00-project-overview.mdc")


def check_rules_package(repo: Path, errors: list[str]) -> None:
    rules = repo / "rules"
    if not rules.is_dir():
        errors.append("MISSING rules/ directory (submodule or copy)")
        return
    version = rules / "VERSION"
    if not version.is_file():
        errors.append("MISSING rules/VERSION")
    agents = rules / "codex" / "AGENTS.md"
    if not agents.is_file():
        errors.append("MISSING rules/codex/AGENTS.md")
    shared = rules / "shared" / "00-must-follow.md"
    if not shared.is_file():
        errors.append("MISSING rules/shared/00-must-follow.md")


def _declared_contracts(repo: Path) -> list[Path]:
    declarations: list[Path] = []
    candidates = [repo / "AGENTS.md", repo / ".cursor" / "rules" / "99-project-local.mdc"]
    for source in candidates:
        if not source.is_file():
            continue
        for match in CONTRACT_DECLARATION.finditer(source.read_text(encoding="utf-8")):
            value = match.group(1).strip()
            if value.startswith(("http://", "https://")):
                continue
            declared = Path(value)
            declarations.append(declared if declared.is_absolute() else repo / declared)
    return declarations


def _has_external_contract_declaration(repo: Path) -> bool:
    for source in (repo / "AGENTS.md", repo / ".cursor" / "rules" / "99-project-local.mdc"):
        if not source.is_file():
            continue
        for match in CONTRACT_DECLARATION.finditer(source.read_text(encoding="utf-8")):
            if match.group(1).startswith("https://"):
                return True
    return False


def check_contracts(repo: Path, errors: list[str], required: bool, flexible: bool = False) -> None:
    candidates = [
        repo / "contracts" / "openapi.yaml",
        repo / "contracts" / "openapi.yml",
        repo.parent / "contracts" / "openapi.yaml",
        repo.parent / "contracts" / "openapi.yml",
    ]
    if flexible:
        candidates.extend(
            [
                *_declared_contracts(repo),
            ]
        )
    if any(p.is_file() for p in candidates):
        return
    if flexible and _has_external_contract_declaration(repo):
        return
    if required:
        expected = "contracts/openapi.yaml|openapi.yml or declared OpenAPI Contract path"
        errors.append(f"MISSING contract SSOT ({expected})")


def check_codeowners(repo: Path, errors: list[str], strict: bool) -> None:
    paths = [repo / "CODEOWNERS", repo / ".github" / "CODEOWNERS"]
    existing = next((path for path in paths if path.is_file()), None)
    if existing is None:
        msg = "MISSING CODEOWNERS (see docs/codeowners-matrix.md)"
        if strict:
            errors.append(msg)
        else:
            print(f"WARN: {msg}")
        return
    if not strict:
        return
    text = existing.read_text(encoding="utf-8")
    if re.search(r"(?:请替换|replace\s+(?:sample|placeholder)|example\s+codeowners)", text, re.IGNORECASE):
        errors.append(f"CODEOWNERS still declares sample/placeholder owners: {existing.relative_to(repo)}")
    owner_tokens = re.findall(r"(?m)^(?!\s*#).*?(?<!\S)(@[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?)", text)
    if not owner_tokens:
        errors.append(f"CODEOWNERS has no owner assignment: {existing.relative_to(repo)}")


def check_pr_template(repo: Path, errors: list[str], strict: bool) -> None:
    paths = [
        repo / ".github" / "pull_request_template.md",
        repo / ".github" / "PULL_REQUEST_TEMPLATE.md",
        repo / "docs" / "pull-request-template.md",
    ]
    existing = next((path for path in paths if path.is_file()), None)
    if existing is None:
        msg = "MISSING PR template (copy from rules/docs/pull-request-template.md)"
        if strict:
            errors.append(msg)
        else:
            print(f"WARN: {msg}")
        return
    if not strict:
        return
    text = existing.read_text(encoding="utf-8")
    heading_patterns = {
        "requirement / issue heading": r"^#{1,6}\s+.*(?:需求|issue|requirements?)",
        "risk / rollback heading": r"^#{1,6}\s+.*(?:风险|risk|回滚|rollback)",
    }
    for label, pattern in heading_patterns.items():
        if not re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            errors.append(f"PR template missing {label}: {existing.relative_to(repo)}")
    table_lines = [line for line in text.splitlines() if line.lstrip().startswith("|")]
    table_text = "\n".join(table_lines)
    for label, pattern in {
        "requirement / issue table column": r"需求|issue|requirements?",
        "acceptance criteria table column": r"验收|acceptance",
        "impact table column": r"影响|impact",
        "implementation / contract table column": r"实现|契约|implementation|contract",
        "validation evidence table column": r"验证|证据|validation|evidence",
        "status table column": r"状态|status",
    }.items():
        if not re.search(pattern, table_text, re.IGNORECASE):
            errors.append(f"PR template missing {label}: {existing.relative_to(repo)}")


def check_package_json_scripts(repo: Path, errors: list[str], required: tuple[str, ...]) -> None:
    pkg = repo / "package.json"
    if not pkg.is_file():
        errors.append("MISSING package.json")
        return
    data = json.loads(pkg.read_text(encoding="utf-8"))
    scripts = data.get("scripts") or {}
    for name in required:
        if name not in scripts:
            errors.append(f"package.json missing script: {name}")
            continue
        command = scripts.get(name)
        if not isinstance(command, str) or not command.strip() or PLACEHOLDER_SCRIPT.match(command.strip()):
            errors.append(f"package.json script is placeholder: {name}")


def _is_gradle_project(repo: Path) -> bool:
    has_wrapper = (repo / "gradlew").is_file()
    has_build = (repo / "build.gradle").is_file() or (repo / "build.gradle.kts").is_file()
    return has_wrapper and has_build


def _is_maven_project(repo: Path) -> bool:
    return (repo / "pom.xml").is_file()


def check_build_tool(repo: Path, errors: list[str]) -> None:
    if _is_maven_project(repo):
        text = (repo / "pom.xml").read_text(encoding="utf-8")
        if "maven-surefire-plugin" not in text and "spring-boot" not in text:
            print("WARN: pom.xml may lack standard test/build plugins")
        return
    if _is_gradle_project(repo):
        return
    errors.append(
        "MISSING backend build file: pom.xml or Gradle wrapper (gradlew + build.gradle*)"
    )


def _ci_text(repo: Path) -> str:
    candidates = list((repo / ".github" / "workflows").glob("*.yml"))
    candidates.extend((repo / ".github" / "workflows").glob("*.yaml"))
    candidates.extend(
        path for path in (repo / ".gitlab-ci.yml", repo / "Jenkinsfile", repo / "azure-pipelines.yml")
        if path.is_file()
    )
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in candidates)


def check_backend_ci(repo: Path, errors: list[str], required: bool) -> None:
    if not required:
        return
    text = _ci_text(repo)
    if not re.search(r"(?:mvnw?|\.\/mvnw)\s+[^\n]*(?:verify|test)|gradlew(?:\.bat)?\s+[^\n]*(?:check|test)", text, re.IGNORECASE):
        errors.append("MISSING backend CI evidence running Maven verify/test or Gradle check/test")


def check_local_override(repo: Path, errors: list[str], required: bool) -> None:
    local = repo / ".cursor" / "rules" / "99-project-local.mdc"
    if not local.is_file():
        message = "MISSING .cursor/rules/99-project-local.mdc (project paths and adoption Level)"
        if required:
            errors.append(message)
        else:
            print(f"WARN: {message}")
        return
    if not required:
        return

    text = local.read_text(encoding="utf-8", errors="replace")
    headings = ("## 测试治理参数", "## Testing Governance")
    matched_heading = next((heading for heading in headings if heading in text), None)
    start = text.find(matched_heading) if matched_heading else -1
    if start < 0:
        errors.append(
            "99-project-local.mdc missing 测试治理参数 "
            "(coverage/compatibility/flaky/evidence/test-data/risk-specific declarations)"
        )
        return
    section = text[start:]
    next_heading = section.find("\n## ", len(matched_heading))
    if next_heading >= 0:
        section = section[:next_heading]
    marker_groups = (
        ("覆盖率策略", "Coverage policy"),
        ("兼容窗口", "Compatibility window"),
        ("flaky 治理", "Flaky governance"),
        ("失败证据", "Failure evidence"),
        ("测试数据", "Test data"),
        ("风险专项", "Risk-specific testing"),
    )
    missing = ["/".join(group) for group in marker_groups if not any(marker in section for marker in group)]
    if missing:
        errors.append(f"99-project-local.mdc testing governance missing: {', '.join(missing)}")
    placeholders = (
        "按项目填写",
        "填写指标",
        "填写 API",
        "填写登记",
        "填写测试",
        "填写 synthetic",
        "填写属性",
        "TODO",
        "TBD",
        "<",
    )
    if any(token in section for token in placeholders):
        errors.append(
            "99-project-local.mdc testing governance still contains sample placeholders; "
            "replace them with project facts or not-applicable + reason"
        )


def _decision_value(text: str, label: str, allowed: set[str]) -> str | None:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*`?([A-Z_]+)`?\s*$", text)
    if match is None or match.group(1) not in allowed:
        return None
    return match.group(1)


def check_backend_project_profiles(repo: Path, errors: list[str], required: bool) -> None:
    if not required:
        return
    local_path = repo / ".cursor" / "rules" / "99-project-local.mdc"
    agents_path = repo / "AGENTS.md"
    if not local_path.is_file() or not agents_path.is_file():
        return

    all_declared = _declared_contracts(repo)
    declared = [path for path in all_declared if path.is_file()]
    for missing in all_declared:
        if not missing.is_file():
            errors.append(f"declared OpenAPI contract not found: {missing}")
    defaults = [
        repo / "contracts" / "openapi.yaml",
        repo / "contracts" / "openapi.yml",
        repo.parent / "contracts" / "openapi.yaml",
        repo.parent / "contracts" / "openapi.yml",
    ]
    contract_path = next(iter(declared), None) or next((path for path in defaults if path.is_file()), None)
    if contract_path is None:
        errors.append("backend project profiles need a local OpenAPI contract for x-api-style validation")
        return
    if len({path.resolve() for path in declared}) > 1:
        errors.append("AGENTS.md and 99-project-local.mdc declare different OpenAPI contract paths")

    local = local_path.read_text(encoding="utf-8", errors="replace")
    agents = agents_path.read_text(encoding="utf-8", errors="replace")
    specs = (
        ("架构档", {"CRUD_LITE", "CLASSIC_LAYERED", "DOMAIN_HEXAGONAL"}, "CRUD_LITE"),
        ("对象命名", {"ENTITY_REQUEST_RESPONSE", "DO_DTO_BO_VO_QUERY"}, "ENTITY_REQUEST_RESPONSE"),
        ("API 风格", {"RESOURCE_REST", "GET_POST_COMPAT"}, "GET_POST_COMPAT"),
        ("租户模型", {"NONE", "SHARED_COLUMN", "SCHEMA_PER_TENANT", "DATABASE_PER_TENANT"}, "NONE"),
    )
    decisions: dict[str, str] = {}
    for label, allowed, default in specs:
        local_value = _decision_value(local, label, allowed)
        agents_value = _decision_value(agents, label, allowed)
        local_declared = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]", local) is not None
        agents_declared = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]", agents) is not None
        if local_value is None and not local_declared:
            local_value = default
        if agents_value is None and not agents_declared:
            agents_value = default
        if local_value is None:
            errors.append(
                f"99-project-local.mdc has invalid {label}"
                if local_declared else f"99-project-local.mdc must select one valid {label}"
            )
            continue
        if agents_value is None:
            errors.append(
                f"AGENTS.md has invalid {label} for Codex"
                if agents_declared else f"AGENTS.md must select one valid {label} for Codex"
            )
            continue
        if local_value != agents_value:
            errors.append(f"project decision drift for {label}: Cursor={local_value}, Codex={agents_value}")
            continue
        decisions[label] = local_value

    tenant_signals: list[str] = []
    for folder in (repo / "src" / "main", repo / "db" / "migration"):
        if not folder.is_dir():
            continue
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".java", ".kt", ".sql", ".xml"}:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"\btenant_id\b|\bTenantLineInnerInterceptor\b|\bTenantLineHandler\b", content):
                tenant_signals.append(path.relative_to(repo).as_posix())
                if len(tenant_signals) >= 3:
                    break
        if len(tenant_signals) >= 3:
            break
    if tenant_signals and decisions.get("租户模型") == "NONE":
        errors.append(
            "tenant implementation signals conflict with 租户模型 NONE: "
            + ", ".join(tenant_signals)
            + "; declare the actual tenant model in both project rule files"
        )

    if decisions.get("租户模型") != "NONE":
        label = "全局表 / 租户豁免表"
        if re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*\S.+$", local) is None:
            errors.append(f"99-project-local.mdc must declare {label} for multi-tenant projects")
        if re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*\S.+$", agents) is None:
            errors.append(f"AGENTS.md must declare {label} for multi-tenant projects")

    contract = _load_yaml(contract_path, errors)
    contract_style = contract.get("x-api-style", "GET_POST_COMPAT") if contract else None
    selected_style = decisions.get("API 风格")
    if selected_style and contract_style != selected_style:
        errors.append(
            f"OpenAPI x-api-style drift: project={selected_style}, contract={contract_style or 'missing'}"
        )


def _load_yaml(path: Path, errors: list[str]) -> dict[str, object]:
    if yaml is None:
        errors.append("PyYAML is required to validate governance-adoption.yaml")
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"INVALID governance-adoption.yaml: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append("governance-adoption.yaml root must be an object")
        return {}
    return data


def _check_local_evidence(
    repo: Path,
    ref: object,
    markers: tuple[str, ...],
    label: str,
    errors: list[str],
    allow_url: bool = False,
) -> None:
    if not isinstance(ref, str) or not ref.strip():
        errors.append(f"governance adoption {label}.evidence must be a path or HTTPS URL")
        return
    ref = ref.strip()
    if EVIDENCE_URL.fullmatch(ref):
        if allow_url:
            return
        errors.append(f"governance adoption {label}.evidence must be a repository path")
        return
    path = (repo / ref).resolve()
    try:
        path.relative_to(repo.resolve())
    except ValueError:
        errors.append(f"governance adoption {label}.evidence escapes repository: {ref}")
        return
    if not path.is_file():
        errors.append(f"governance adoption {label}.evidence not found: {ref}")
        return
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    if markers and not any(marker.lower() in text for marker in markers):
        errors.append(f"governance adoption {label}.evidence lacks expected control marker")


def _repository_evidence_path(repo: Path, ref: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(ref, str) or not ref.strip() or EVIDENCE_URL.fullmatch(ref.strip()):
        errors.append(f"governance adoption {label}.evidence must be a repository path")
        return None
    path = (repo / ref.strip()).resolve()
    try:
        path.relative_to(repo.resolve())
    except ValueError:
        errors.append(f"governance adoption {label}.evidence escapes repository: {ref}")
        return None
    if not path.is_file():
        errors.append(f"governance adoption {label}.evidence not found: {ref}")
        return None
    return path


def _workflow_control_text(path: Path, label: str, errors: list[str]) -> str:
    if path.name == "Jenkinsfile":
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        text = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
        commands = [
            match.group(2)
            for match in re.finditer(
                r"\b(?:sh|bat|powershell|pwsh)\s*(?:\(\s*)?(?:script\s*:\s*)?(['\"])(.*?)\1",
                text,
                flags=re.DOTALL | re.IGNORECASE,
            )
        ]
        if not commands:
            errors.append(f"governance adoption {label}.evidence has no executable Jenkins steps")
        return "\n".join(commands).lower()
    if path.name == ".gitlab-ci.yml":
        if yaml is None:
            errors.append("PyYAML is required to validate workflow evidence")
            return ""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            errors.append(f"governance adoption {label}.evidence must be a workflow object")
            return ""
        commands = [str(command).lower() for job in data.values() if isinstance(job, dict)
                    for command in (job.get("script") if isinstance(job.get("script"), list) else [job.get("script")])
                    if isinstance(command, str)]
        if not commands:
            errors.append(f"governance adoption {label}.evidence has no executable workflow steps")
        return "\n".join(commands)
    if yaml is None:
        errors.append("PyYAML is required to validate workflow evidence")
        return ""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"governance adoption {label}.evidence invalid YAML: {exc}")
        return ""
    if not isinstance(data, dict):
        errors.append(f"governance adoption {label}.evidence must be a workflow object")
        return ""
    commands: list[str] = []
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        errors.append(f"governance adoption {label}.evidence has no jobs")
        return ""
    for job in jobs.values():
        if not isinstance(job, dict) or str(job.get("if", "")).strip().lower() == "false":
            continue
        steps = job.get("steps")
        for step in steps if isinstance(steps, list) else []:
            if not isinstance(step, dict) or str(step.get("if", "")).strip().lower() == "false":
                continue
            for key in ("uses", "run"):
                command = step.get(key)
                if isinstance(command, str):
                    commands.append(command.lower())
        reusable = job.get("uses")
        if isinstance(reusable, str):
            commands.append(reusable.lower())
    if not commands:
        errors.append(f"governance adoption {label}.evidence has no executable workflow steps")
    return "\n".join(commands)


def _github_workflow_events(path: Path) -> tuple[set[str], dict[str, object]]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return set(), {}
    if not isinstance(data, dict):
        return set(), {}
    trigger = data.get("on", data.get(True))  # PyYAML treats YAML 1.1 `on` as boolean.
    if isinstance(trigger, str):
        return {trigger}, data
    if isinstance(trigger, list):
        return {item for item in trigger if isinstance(item, str)}, data
    if isinstance(trigger, dict):
        return {str(item) for item in trigger}, data
    return set(), data


def _github_workflow_steps(data: dict[str, object]) -> list[dict[str, object]]:
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        return []
    return [step for job in jobs.values() if isinstance(job, dict) and isinstance(job.get("steps"), list)
            for step in job["steps"] if isinstance(step, dict)]


def _called_local_workflows(repo: Path, data: dict[str, object]) -> list[Path]:
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        return []
    paths: list[Path] = []
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        uses = job.get("uses")
        if isinstance(uses, str) and uses.startswith("./.github/workflows/"):
            candidate = (repo / uses[2:]).resolve()
            if candidate.is_file() and candidate.is_relative_to(repo.resolve()):
                paths.append(candidate)
    return paths


def _check_workflow_activation(repo: Path, path: Path, label: str, errors: list[str]) -> None:
    if path.parent.name != "workflows":
        return  # Other CI providers need their own live execution evidence.
    events, data = _github_workflow_events(path)
    if label.endswith("artifact_trust"):
        push = data.get("on", data.get(True))
        tag_push = isinstance(push, dict) and isinstance(push.get("push"), dict) and bool(push["push"].get("tags"))
        if not tag_push:
            errors.append(f"governance adoption {label}.evidence must be an active release-tag workflow; point to the caller when using reusable workflows")
        steps = _github_workflow_steps(data)
        called = _called_local_workflows(repo, data)
        for target in called:
            called_events, called_data = _github_workflow_events(target)
            if "workflow_call" not in called_events:
                errors.append(f"governance adoption {label}.evidence calls a workflow without workflow_call: {target.name}")
            steps.extend(_github_workflow_steps(called_data))
        if called and not any("upload-artifact@" in str(step.get("uses", "")) for step in _github_workflow_steps(data)):
            errors.append(f"governance adoption {label}.evidence caller must upload the build artifact")
        if not any("attest-build-provenance@" in str(step.get("uses", "")) for step in steps):
            errors.append(f"governance adoption {label}.evidence must attest build provenance")
        if not any("sbom" in str(step.get("uses", "")).lower() for step in steps):
            errors.append(f"governance adoption {label}.evidence must generate an SBOM")
        subjects = [str(step.get("with", {}).get("subject-path", "")) for step in steps
                    if isinstance(step.get("with"), dict) and "attest-build-provenance@" in str(step.get("uses", ""))]
        if not subjects or any(not value or value.startswith("contracts/") for value in subjects):
            errors.append(f"governance adoption {label}.evidence must attest a build artifact, not a contract file")
    elif not events.intersection({"pull_request", "push", "merge_group", "schedule"}):
        errors.append(f"governance adoption {label}.evidence has no automatic trigger")


def _check_workflow_control(
    repo: Path,
    ref: object,
    marker_groups: tuple[tuple[str, ...], ...],
    label: str,
    errors: list[str],
) -> None:
    path = _repository_evidence_path(repo, ref, label, errors)
    if path is None:
        return
    allowed = path.parent.name == "workflows" or path.name in {
        ".gitlab-ci.yml",
        "Jenkinsfile",
        "azure-pipelines.yml",
    }
    if not allowed:
        errors.append(f"governance adoption {label}.evidence must be a CI workflow")
        return
    commands = _workflow_control_text(path, label, errors)
    if path.parent.name == "workflows" and yaml is not None:
        _check_workflow_activation(repo, path, label, errors)
        if label.endswith("artifact_trust"):
            _, data = _github_workflow_events(path)
            for target in _called_local_workflows(repo, data):
                commands += "\n" + _workflow_control_text(target, label, errors)
    for alternatives in marker_groups:
        if not any(marker.lower() in commands for marker in alternatives):
            errors.append(
                f"governance adoption {label}.evidence lacks executable marker group: "
                f"{' | '.join(alternatives)}"
            )


def _check_platform_evidence(repo: Path, ref: object, errors: list[str]) -> None:
    path = _repository_evidence_path(repo, ref, "branch_protection", errors)
    if path is None:
        return
    if path.suffix.lower() != ".json":
        errors.append("governance adoption branch_protection.evidence must be JSON")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"governance platform evidence invalid JSON: {exc}")
        return
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        errors.append("governance platform evidence schema_version must be 1")
        return
    for key in ("provider", "repository", "branch"):
        value = data.get(key)
        if not isinstance(value, str) or value.strip().lower() in {"", "todo", "tbd"}:
            errors.append(f"governance platform evidence {key} must be meaningful")
    captured_at = data.get("captured_at")
    try:
        captured = dt.datetime.fromisoformat(str(captured_at).replace("Z", "+00:00"))
        if captured.utcoffset() is None:
            raise ValueError
        age = dt.datetime.now(dt.timezone.utc) - captured.astimezone(dt.timezone.utc)
        if age < dt.timedelta(0) or age > dt.timedelta(days=90):
            errors.append("governance platform evidence captured_at must be within the last 90 days")
    except ValueError:
        errors.append("governance platform evidence captured_at must be timezone-aware ISO-8601")

    required_checks = data.get("required_checks")
    expected_checks = {"rules-adoption", "credential-scan", "supply-chain"}
    check_names = {item for item in required_checks if isinstance(item, str)} if isinstance(required_checks, list) else set()
    if not expected_checks.issubset(check_names):
        errors.append(f"governance platform evidence required_checks must include {sorted(expected_checks)}")
    release_checks = data.get("release_checks")
    if not isinstance(release_checks, list) or "artifact-trust" not in release_checks:
        errors.append("governance platform evidence release_checks must include artifact-trust")
    expected_values = {
        "required_approvals": lambda value: isinstance(value, int) and not isinstance(value, bool) and value >= 1,
        "require_code_owner_reviews": lambda value: value is True,
        "dismiss_stale_reviews": lambda value: value is True,
        "require_non_author_approval": lambda value: value is True,
        "allow_force_pushes": lambda value: value is False,
        "allow_deletions": lambda value: value is False,
    }
    branch = data.get("branch_protection")
    if not isinstance(branch, dict):
        errors.append("governance platform evidence branch_protection must be an object")
    else:
        for key, predicate in expected_values.items():
            if not predicate(branch.get(key)):
                errors.append(f"governance platform evidence branch_protection.{key} is not compliant")
    organization = data.get("organization_controls")
    if not isinstance(organization, dict):
        errors.append("governance platform evidence organization_controls must be an object")
    else:
        if organization.get("mfa_required") is not True:
            errors.append("governance platform evidence organization_controls.mfa_required must be true")
        if organization.get("default_repository_permission") not in {"none", "read"}:
            errors.append("governance platform evidence default_repository_permission must be none or read")
        if organization.get("actions_default_permission") != "read":
            errors.append("governance platform evidence actions_default_permission must be read")
    production = data.get("production_environment")
    if not isinstance(production, dict):
        errors.append("governance platform evidence production_environment must be an object")
    else:
        reviewers = production.get("required_reviewers")
        if not isinstance(reviewers, int) or isinstance(reviewers, bool) or reviewers < 1:
            errors.append("governance platform evidence production_environment.required_reviewers must be >= 1")
        if production.get("prevent_self_review") is not True:
            errors.append("governance platform evidence production_environment.prevent_self_review must be true")


def check_level_evidence(repo: Path, errors: list[str], level: int) -> None:
    if level < 2:
        return
    evidence_path = repo / "governance-adoption.yaml"
    if not evidence_path.is_file():
        errors.append("MISSING governance-adoption.yaml (control declarations for Level 2+)")
        return
    data = _load_yaml(evidence_path, errors)
    if not data:
        return
    if data.get("schema_version") != 1:
        errors.append("governance-adoption.yaml schema_version must be 1")
    declared_level = data.get("level")
    if not isinstance(declared_level, int) or isinstance(declared_level, bool) or declared_level < level:
        errors.append(f"governance-adoption.yaml level must be >= requested Level {level}")
    owner = data.get("owner")
    if not isinstance(owner, str) or owner.strip().lower() in {"", "todo", "tbd"}:
        errors.append("governance-adoption.yaml owner must be meaningful")
    review_due = data.get("review_due")
    try:
        due = dt.date.fromisoformat(str(review_due))
        if due < dt.date.today():
            errors.append("governance-adoption.yaml review_due is expired")
    except ValueError:
        errors.append("governance-adoption.yaml review_due must be YYYY-MM-DD")

    checks = data.get("checks")
    if not isinstance(checks, dict):
        errors.append("governance-adoption.yaml checks must be an object")
        checks = {}
    control_markers = {
        "rules_adoption": (("check-project-adoption.py",), ("--level 2", "--level 3")),
        "credential_scan": (("gitleaks",),),
        "supply_chain": (
            ("dependency-check", "npm audit", "pnpm audit"),
            ("license-checker", "license"),
        ),
        "artifact_trust": (("sbom",), ("attest", "cosign")),
    }
    for name, markers in control_markers.items():
        control = checks.get(name)
        if not isinstance(control, dict):
            errors.append(f"governance-adoption.yaml checks.{name} must be an object")
            continue
        _check_workflow_control(repo, control.get("evidence"), markers, f"checks.{name}", errors)

    branch = data.get("branch_protection")
    if not isinstance(branch, dict) or branch.get("enabled") is not True:
        errors.append("governance-adoption.yaml branch_protection.enabled must be true")
    else:
        _check_platform_evidence(repo, branch.get("evidence"), errors)

    if level < 3:
        return
    level3 = data.get("level3")
    if not isinstance(level3, dict):
        errors.append("governance-adoption.yaml level3 must be an object")
        return
    _check_local_evidence(repo, level3.get("scorecard"), ("owner", "evidence", "status"), "level3.scorecard", errors)
    items = level3.get("evidence")
    if not isinstance(items, list) or len(items) < 3:
        errors.append("governance-adoption.yaml level3.evidence must contain at least three controls")
        return
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"governance-adoption.yaml level3.evidence[{index}] must be an object")
            continue
        for field in ("area", "owner"):
            value = item.get(field)
            if not isinstance(value, str) or value.strip().lower() in {"", "todo", "tbd"}:
                errors.append(f"governance-adoption.yaml level3.evidence[{index}].{field} must be meaningful")
        if item.get("status") != "complete":
            errors.append(f"governance-adoption.yaml level3.evidence[{index}].status must be complete")
        _check_local_evidence(
            repo,
            item.get("evidence"),
            (),
            f"level3.evidence[{index}]",
            errors,
            allow_url=True,
        )
        review_due = item.get("review_due")
        try:
            due = dt.date.fromisoformat(str(review_due))
            if due < dt.date.today():
                errors.append(f"governance-adoption.yaml level3.evidence[{index}].review_due is expired")
        except ValueError:
            errors.append(f"governance-adoption.yaml level3.evidence[{index}].review_due must be YYYY-MM-DD")


def check_governance_package(path: Path, errors: list[str], required: bool) -> None:
    findings: list[str] = []
    required_files = GOVERNANCE_REQUIRED_FILES + ("MANIFEST.json",)
    missing = [rel for rel in required_files if not (path / rel).is_file()]
    findings.extend(f"missing {rel}" for rel in missing)

    manifest_path = path / "MANIFEST.json"
    manifest: dict[str, object] = {}
    if manifest_path.is_file():
        try:
            raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"invalid MANIFEST.json: {exc}")
        else:
            if isinstance(raw_manifest, dict):
                manifest = raw_manifest
            else:
                findings.append("MANIFEST.json root must be an object")

    files = manifest.get("files") if manifest else None
    if manifest and not isinstance(files, dict):
        findings.append("MANIFEST.json files must be an object")
    elif isinstance(files, dict):
        expected_entries = set(GOVERNANCE_REQUIRED_FILES)
        listed_entries = set(files)
        for rel in sorted(expected_entries - listed_entries):
            findings.append(f"manifest missing {rel}")
        for rel in sorted(listed_entries - expected_entries):
            findings.append(f"manifest unexpected {rel}")
        for rel, expected_hash in files.items():
            candidate = (path / rel).resolve()
            try:
                candidate.relative_to(path.resolve())
            except ValueError:
                findings.append(f"manifest path escapes package: {rel}")
                continue
            if not candidate.is_file():
                continue
            actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                findings.append(f"checksum mismatch {rel}")

    version_path = path / "VERSION"
    if manifest and version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip()
        if manifest.get("version") != version:
            findings.append("manifest version does not match VERSION")
        changelog_path = path / "CHANGELOG.md"
        if changelog_path.is_file():
            latest = VERSION_HEADING.search(changelog_path.read_text(encoding="utf-8"))
            if not latest or latest.group(1) != version:
                findings.append("CHANGELOG latest version does not match VERSION")

    if not findings:
        return
    message = f"common governance incomplete at {path}: {', '.join(findings)}"
    if required:
        errors.append(message)
    else:
        print(f"WARN: {message}")


def run_stack(repo: Path, stack: str, strict: bool, level: int = 0) -> list[str]:
    errors: list[str] = []
    effective_strict = strict or level >= 2
    check_agents(repo, errors)
    check_rules_package(repo, errors)
    check_cursor_rules(repo, errors)

    if stack == "backend":
        check_build_tool(repo, errors)
        check_contracts(repo, errors, required=True, flexible=True)
        check_backend_ci(repo, errors, required=level >= 1)
        check_backend_project_profiles(repo, errors, required=level >= 1)
    elif stack == "frontend":
        check_package_json_scripts(repo, errors, REQUIRED_FRONTEND_SCRIPTS)
        if level >= 1:
            check_package_json_scripts(repo, errors, REQUIRED_FRONTEND_LEVEL1_SCRIPTS)
        check_contracts(repo, errors, required=level >= 1, flexible=True)
    elif stack == "miniapp":
        check_package_json_scripts(repo, errors, REQUIRED_MINIAPP_SCRIPTS)
        if level >= 1:
            check_package_json_scripts(repo, errors, REQUIRED_MINIAPP_LEVEL1_SCRIPTS)
        check_contracts(repo, errors, required=True)
    else:
        errors.append(f"Unknown stack: {stack}")

    check_codeowners(repo, errors, effective_strict)
    check_pr_template(repo, errors, effective_strict)
    check_local_override(repo, errors, required=level >= 1)
    check_level_evidence(repo, errors, level)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."), help="Business repository root")
    parser.add_argument(
        "--stack",
        default="frontend",
        help="Comma-separated: backend, frontend, miniapp",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat CODEOWNERS / PR template as required",
    )
    parser.add_argument(
        "--level",
        type=int,
        choices=range(0, 4),
        default=0,
        help="Adoption maturity Level 0-3; higher levels enable stricter evidence checks",
    )
    parser.add_argument(
        "--require-governance",
        action="store_true",
        help="Require a complete common-governance package (also implied when --level >= 2)",
    )
    parser.add_argument(
        "--governance-dir",
        type=Path,
        help="Governance package path, relative paths resolve under --repo (default: common-governance)",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Report target maturity gaps without returning a failing exit code",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not repo.is_dir():
        print(f"Not a directory: {repo}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for stack in [s.strip() for s in args.stack.split(",") if s.strip()]:
        print(f"=== Checking {stack} Level {args.level} @ {repo} ===")
        all_errors.extend(run_stack(repo, stack, args.strict, args.level))

    require_governance = args.require_governance or args.level >= 2
    if require_governance or args.governance_dir:
        governance_dir = args.governance_dir or Path("common-governance")
        if not governance_dir.is_absolute():
            governance_dir = repo / governance_dir
        governance_dir = governance_dir.resolve()
        check_governance_package(governance_dir, all_errors, require_governance)

    if all_errors:
        print("\nTARGET GAPS:" if args.report_only else "\nFAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 0 if args.report_only else 1

    if args.level >= 2:
        print("\nOK: adoption files and declared controls passed structural checks")
        print("Platform settings, Required check status, and workflow execution require live verification.")
    else:
        print("\nOK: project adoption checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
