import importlib.util
import io
import re
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECK_SCRIPT = SCRIPTS / "check-project-adoption.py"
DEBT_BASELINE_SCRIPT = SCRIPTS / "check-debt-baseline.py"
RELEASE_EVIDENCE_SCRIPT = SCRIPTS / "validate-release-evidence.py"
SYNC_GOVERNANCE_SCRIPT = SCRIPTS / "sync-common-governance.py"
COMMON_GOVERNANCE_VALIDATOR = ROOT / "common-governance" / "scripts" / "validate-package.py"
REPOSITORY_VALIDATOR = SCRIPTS / "validate-repository.py"
WORKFLOW_SECURITY_VALIDATOR = SCRIPTS / "validate-workflow-security.py"
CONTROL_CATALOG_VALIDATOR = SCRIPTS / "validate-control-catalog.py"
AI_EVAL_RESULTS_VALIDATOR = SCRIPTS / "validate-ai-eval-results.py"
PREPARE_AI_EVAL_SCRIPT = SCRIPTS / "prepare-ai-eval-run.py"
EXCEPTIONS_VALIDATOR = SCRIPTS / "validate-exceptions.py"
PR_GOVERNANCE_VALIDATOR = SCRIPTS / "validate-pr-governance.py"


class CheckProjectAdoptionTests(unittest.TestCase):
    def test_strict_codeowners_rejects_declared_placeholders(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_codeowners", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "CODEOWNERS").write_text(
                "# Replace sample teams with real owners.\n* @architecture-team\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod.check_codeowners(repo, errors, strict=True)
        self.assertTrue(any("sample/placeholder" in error for error in errors))

    def test_report_only_preserves_target_gaps_but_exits_zero(self):
        repo = ROOT / "examples" / "adoption-fixture" / "frontend"
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_SCRIPT),
                "--repo",
                str(repo),
                "--stack",
                "frontend",
                "--level",
                "3",
                "--report-only",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TARGET GAPS:", result.stdout)

    def test_frontend_fixture_passes(self):
        repo = ROOT / "examples" / "adoption-fixture" / "frontend"
        result = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), "--repo", str(repo), "--stack", "frontend"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_backend_gradle_fixture_passes(self):
        repo = ROOT / "examples" / "adoption-fixture" / "backend-gradle"
        result = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), "--repo", str(repo), "--stack", "backend"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_backend_accepts_gradle_wrapper(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "gradlew").write_text("#!/bin/sh\n", encoding="utf-8")
            (repo / "build.gradle.kts").write_text("plugins { java }\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_build_tool(repo, errors)
        self.assertEqual(errors, [])

    def test_level_one_requires_frontend_contract_api_check_and_local_override(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_level", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "AGENTS.md").write_text("read rules/shared\n", encoding="utf-8")
            (repo / "rules" / "codex").mkdir(parents=True)
            (repo / "rules" / "shared").mkdir()
            (repo / "rules" / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            (repo / "rules" / "codex" / "AGENTS.md").write_text("# rules\n", encoding="utf-8")
            (repo / "rules" / "shared" / "00-must-follow.md").write_text("# rules\n", encoding="utf-8")
            (repo / ".cursor" / "rules").mkdir(parents=True)
            (repo / ".cursor" / "rules" / "00-project-overview.mdc").write_text("# overview\n", encoding="utf-8")
            (repo / "package.json").write_text(
                '{"scripts":{"lint":"x","type-check":"x","build":"x"}}\n',
                encoding="utf-8",
            )
            errors = mod.run_stack(repo, "frontend", strict=False, level=1)

        self.assertIn("package.json missing script: api:check", errors)
        self.assertTrue(any("MISSING contract SSOT" in error for error in errors))
        self.assertTrue(any("99-project-local.mdc" in error for error in errors))

    def test_level_one_rejects_local_override_without_testing_governance(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_local_testing", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            local.write_text("# Project Local\n- Adoption level: 1\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_local_override(repo, errors, required=True)

        self.assertTrue(any("missing 测试治理参数" in error for error in errors))

    def test_level_one_rejects_testing_governance_placeholders(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_local_placeholders", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            local.write_text(
                "## 测试治理参数\n"
                "- 覆盖率策略：填写指标。\n- 兼容窗口：N/N-1。\n- flaky 治理：owner。\n"
                "- 失败证据：CI。\n- 测试数据：synthetic。\n- 风险专项：not-applicable + reason。\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod.check_local_override(repo, errors, required=True)

        self.assertTrue(any("sample placeholders" in error for error in errors))

    def test_backend_profiles_reject_cursor_codex_and_openapi_drift(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_backend_profiles", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            local.write_text(
                "- 架构档：CRUD_LITE\n- 对象命名：ENTITY_REQUEST_RESPONSE\n- API 风格：GET_POST_COMPAT\n"
                "- 租户模型：SHARED_COLUMN\n- 全局表 / 租户豁免表：NONE\n- 数据所有权清单：crm -> crm_*\n",
                encoding="utf-8",
            )
            (repo / "AGENTS.md").write_text(
                "- 架构档：CLASSIC_LAYERED\n- 对象命名：ENTITY_REQUEST_RESPONSE\n- API 风格：GET_POST_COMPAT\n"
                "- 租户模型：SHARED_COLUMN\n- 全局表 / 租户豁免表：NONE\n- 数据所有权清单：crm -> crm_*\n",
                encoding="utf-8",
            )
            contract = repo / "contracts" / "openapi.yaml"
            contract.parent.mkdir()
            contract.write_text("openapi: 3.0.3\nx-api-style: RESOURCE_REST\ninfo: {title: test, version: 1}\npaths: {}\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_backend_project_profiles(repo, errors, required=True)

        self.assertTrue(any("project decision drift for 架构档" in error for error in errors))
        self.assertTrue(any("OpenAPI x-api-style drift" in error for error in errors))

    def test_backend_profiles_default_api_tenancy_and_ownership_when_omitted(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_backend_tenancy", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            decisions = "# ordinary single-module CRUD\n"
            local.write_text(decisions, encoding="utf-8")
            (repo / "AGENTS.md").write_text(decisions, encoding="utf-8")
            contract = repo / "contracts" / "openapi.yaml"
            contract.parent.mkdir()
            contract.write_text(
                "openapi: 3.0.3\n"
                "info: {title: test, version: 1}\npaths: {}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod.check_backend_project_profiles(repo, errors, required=True)

        self.assertEqual([], errors)

    def test_backend_profiles_reject_implicit_single_tenant_with_tenant_migration(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_tenant_signal", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            local.write_text("# local\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text("# agent\n", encoding="utf-8")
            contract = repo / "contracts" / "openapi.yaml"
            contract.parent.mkdir()
            contract.write_text("openapi: 3.0.3\npaths: {}\n", encoding="utf-8")
            migration = repo / "src" / "main" / "resources" / "db" / "migration" / "V1__user.sql"
            migration.parent.mkdir(parents=True)
            migration.write_text("CREATE TABLE sys_user (tenant_id VARCHAR(64));\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_backend_project_profiles(repo, errors, required=True)
        self.assertTrue(any("tenant implementation signals conflict" in error for error in errors))

    def test_backend_profiles_validate_declared_contract_path(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_custom_contract", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            local.write_text("- API 风格：GET_POST_COMPAT\n- OpenAPI SSOT：api/spec.yaml\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text(
                "- API 风格：GET_POST_COMPAT\n- OpenAPI SSOT：api/spec.yaml\n", encoding="utf-8"
            )
            contract = repo / "api" / "spec.yaml"
            contract.parent.mkdir()
            contract.write_text("openapi: 3.0.3\nx-api-style: RESOURCE_REST\npaths: {}\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_backend_project_profiles(repo, errors, required=True)
        self.assertTrue(any("OpenAPI x-api-style drift" in error for error in errors))

    def test_backend_profiles_reject_missing_declared_contract_even_with_default(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_missing_contract", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            local.write_text("- OpenAPI SSOT：api/missing.yaml\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text("- OpenAPI SSOT：api/missing.yaml\n", encoding="utf-8")
            contract = repo / "contracts" / "openapi.yaml"
            contract.parent.mkdir()
            contract.write_text("openapi: 3.0.3\npaths: {}\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_backend_project_profiles(repo, errors, required=True)
        self.assertTrue(any("declared OpenAPI contract not found" in error for error in errors))

    def test_backend_profiles_require_global_table_decision_for_multi_tenant_project(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_backend_tenancy", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            decisions = "- 租户模型：SHARED_COLUMN\n"
            local.write_text(decisions, encoding="utf-8")
            (repo / "AGENTS.md").write_text(decisions, encoding="utf-8")
            contract = repo / "contracts" / "openapi.yaml"
            contract.parent.mkdir()
            contract.write_text(
                "openapi: 3.0.3\ninfo: {title: test, version: 1}\npaths: {}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod.check_backend_project_profiles(repo, errors, required=True)

        self.assertTrue(any("全局表 / 租户豁免表" in error for error in errors))

    def test_backend_profiles_accept_explicit_non_default_decisions(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_backend_defaults", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            local = repo / ".cursor" / "rules" / "99-project-local.mdc"
            local.parent.mkdir(parents=True)
            required = (
                "- API 风格：GET_POST_COMPAT\n"
                "- 租户模型：SHARED_COLUMN\n"
                "- 全局表 / 租户豁免表：NONE\n"
                "- 数据所有权清单：crm -> crm_*\n"
            )
            local.write_text(required, encoding="utf-8")
            (repo / "AGENTS.md").write_text(required, encoding="utf-8")
            contract = repo / "contracts" / "openapi.yaml"
            contract.parent.mkdir()
            contract.write_text(
                "openapi: 3.0.3\nx-api-style: GET_POST_COMPAT\n"
                "info: {title: test, version: 1}\npaths: {}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod.check_backend_project_profiles(repo, errors, required=True)

        self.assertEqual([], errors)

    def test_level_two_automatically_requires_governance_package(self):
        repo = ROOT / "examples" / "adoption-fixture" / "frontend"
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_SCRIPT),
                "--repo",
                str(repo),
                "--stack",
                "frontend",
                "--level",
                "2",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("common governance incomplete", result.stdout + result.stderr)

    def test_level_two_rejects_missing_real_control_evidence(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_evidence", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "governance-adoption.yaml").write_text(
                "schema_version: 1\nlevel: 2\nowner: team\nreview_due: '2099-01-01'\n"
                "checks:\n"
                "  rules_adoption: {evidence: .github/workflows/missing.yml}\n"
                "  credential_scan: {evidence: .github/workflows/missing.yml}\n"
                "  supply_chain: {evidence: .github/workflows/missing.yml}\n"
                "branch_protection: {enabled: true, evidence: docs/missing.md}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod.check_level_evidence(repo, errors, 2)

        self.assertTrue(any("evidence not found" in error for error in errors))

    def test_workflow_evidence_ignores_name_and_comments(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_workflow_semantics", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            workflow = repo / ".github" / "workflows" / "credential.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: gitleaks credential scan\non: [pull_request]\n"
                "permissions: {contents: read}\njobs:\n  scan:\n"
                "    runs-on: ubuntu-latest\n    steps:\n      - run: echo safe\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod._check_workflow_control(
                repo,
                ".github/workflows/credential.yml",
                (("gitleaks",),),
                "checks.credential_scan",
                errors,
            )

        self.assertTrue(any("lacks executable marker group" in error for error in errors))

    def test_manual_or_disabled_workflow_is_not_active_control(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_inactive_workflow", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            workflow = repo / ".github" / "workflows" / "credential.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "on: [workflow_dispatch]\njobs:\n  scan:\n    if: false\n"
                "    steps:\n      - run: gitleaks git .\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod._check_workflow_control(repo, ".github/workflows/credential.yml", (("gitleaks",),), "checks.credential_scan", errors)
        self.assertTrue(any("no automatic trigger" in error for error in errors))
        self.assertTrue(any("lacks executable marker" in error for error in errors))

    def test_manual_contract_attestation_does_not_prove_artifact_trust(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_artifact_workflow", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            workflow = repo / ".github" / "workflows" / "artifact.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "on: [workflow_dispatch]\njobs:\n  attest:\n    steps:\n"
                "      - uses: anchore/sbom-action@0123456789012345678901234567890123456789\n"
                "      - uses: actions/attest-build-provenance@0123456789012345678901234567890123456789\n"
                "        with: {subject-path: contracts/openapi.yaml}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod._check_workflow_control(repo, ".github/workflows/artifact.yml", (("sbom",), ("attest",)), "checks.artifact_trust", errors)
        self.assertTrue(any("release-tag workflow" in error for error in errors))
        self.assertTrue(any("build artifact" in error for error in errors))

    def test_release_caller_can_use_reusable_artifact_workflow(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_reusable_artifact", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            workflows = repo / ".github" / "workflows"
            workflows.mkdir(parents=True)
            shutil.copyfile(ROOT / "examples" / "ci" / "artifact-trust-required.yml", workflows / "reusable.yml")
            (workflows / "release.yml").write_text(
                "on:\n  push:\n    tags: ['v*']\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: npm run build\n"
                "      - uses: actions/upload-artifact@0123456789012345678901234567890123456789\n"
                "        with: {name: release, path: dist}\n"
                "  attest:\n    needs: build\n    uses: ./.github/workflows/reusable.yml\n"
                "    with: {artifact-name: release, subject-path: app.tar.gz}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod._check_workflow_control(repo, ".github/workflows/release.yml", (("sbom",), ("attest",)), "checks.artifact_trust", errors)
        self.assertEqual(errors, [])

    def test_gitlab_workflow_evidence_reads_script_commands(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_gitlab_semantics", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            workflow = repo / ".gitlab-ci.yml"
            workflow.write_text(
                "scan:\n  image: example/scanner:1\n  script:\n    - gitleaks git --redact .\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod._check_workflow_control(
                repo,
                ".gitlab-ci.yml",
                (("gitleaks",),),
                "checks.credential_scan",
                errors,
            )

        self.assertEqual(errors, [])

    def test_platform_evidence_rejects_missing_mfa_and_self_review_control(self):
        import json
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_platform", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            evidence = json.loads((ROOT / "examples" / "governance-platform-evidence.json").read_text(encoding="utf-8"))
            evidence["organization_controls"]["mfa_required"] = False
            evidence["production_environment"]["prevent_self_review"] = False
            (repo / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
            errors: list[str] = []
            mod._check_platform_evidence(repo, "evidence.json", errors)

        self.assertTrue(any("mfa_required" in error for error in errors))
        self.assertTrue(any("prevent_self_review" in error for error in errors))

    def test_platform_evidence_separates_pr_and_release_checks(self):
        import json
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_release_gate", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            evidence = json.loads((ROOT / "examples" / "governance-platform-evidence.json").read_text(encoding="utf-8"))
            evidence["release_checks"] = []
            (repo / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
            errors: list[str] = []
            mod._check_platform_evidence(repo, "evidence.json", errors)
        self.assertTrue(any("release_checks must include artifact-trust" in error for error in errors))

    def test_frontend_fixture_passes_level_three_evidence(self):
        repo = ROOT / "examples" / "adoption-fixture" / "frontend"
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_SCRIPT),
                "--repo",
                str(repo),
                "--stack",
                "frontend",
                "--level",
                "3",
                "--governance-dir",
                str(ROOT / "common-governance"),
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_frontend_contract_rejects_generated_json_schema_as_ssot(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_contract", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "contracts").mkdir()
            (repo / "contracts" / "schema.json").write_text("{}\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_contracts(repo, errors, required=True, flexible=True)

        self.assertTrue(any("MISSING contract SSOT" in error for error in errors))

    def test_frontend_contract_accepts_declared_https_ssot(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_contract_url", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "AGENTS.md").write_text(
                "Contract SSOT: https://contracts.example.invalid/openapi.yaml\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            mod.check_contracts(repo, errors, required=True, flexible=True)

        self.assertEqual(errors, [])

    def test_package_script_rejects_echo_placeholder(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_scripts", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "package.json").write_text('{"scripts":{"lint":"echo ok"}}\n', encoding="utf-8")
            errors: list[str] = []
            mod.check_package_json_scripts(repo, errors, ("lint",))

        self.assertEqual(errors, ["package.json script is placeholder: lint"])

    def test_backend_level_one_requires_ci_build_evidence(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_backend_ci", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            errors: list[str] = []
            mod.check_backend_ci(Path(tmp), errors, required=True)

        self.assertEqual(errors, ["MISSING backend CI evidence running Maven verify/test or Gradle check/test"])

    def test_strict_pr_template_requires_traceability_fields(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_pr", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            template = repo / ".github" / "pull_request_template.md"
            template.parent.mkdir(parents=True)
            template.write_text("# Summary\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_pr_template(repo, errors, strict=True)

        self.assertEqual(len(errors), 8)
        self.assertTrue(any("acceptance criteria" in error for error in errors))

    def test_strict_pr_template_ignores_keywords_only_in_comments(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption_pr_comments", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            template = repo / ".github" / "pull_request_template.md"
            template.parent.mkdir(parents=True)
            template.write_text("# Summary\n<!-- requirement acceptance evidence rollback -->\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_pr_template(repo, errors, strict=True)

        self.assertEqual(len(errors), 8)

    def test_required_governance_rejects_missing_package(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("adoption", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            errors: list[str] = []
            mod.check_governance_package(Path(tmp) / "missing", errors, required=True)
            self.assertEqual(len(errors), 1)
            self.assertIn("common governance incomplete", errors[0])

    def test_common_governance_package_passes(self):
        spec = importlib.util.spec_from_file_location("adoption", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        errors: list[str] = []
        mod.check_governance_package(ROOT / "common-governance", errors, required=True)
        self.assertEqual(errors, [])

    def test_required_governance_rejects_invalid_manifest(self):
        spec = importlib.util.spec_from_file_location("adoption", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "common-governance"
            shutil.copytree(ROOT / "common-governance", package)
            (package / "MANIFEST.json").write_text("corrupt", encoding="utf-8")
            errors: list[str] = []
            mod.check_governance_package(package, errors, required=True)

        self.assertEqual(len(errors), 1)
        self.assertIn("invalid MANIFEST.json", errors[0])

    def test_required_governance_rejects_non_object_manifest(self):
        spec = importlib.util.spec_from_file_location("adoption", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "common-governance"
            shutil.copytree(ROOT / "common-governance", package)
            (package / "MANIFEST.json").write_text("[]\n", encoding="utf-8")
            errors: list[str] = []
            mod.check_governance_package(package, errors, required=True)

        self.assertEqual(len(errors), 1)
        self.assertIn("MANIFEST.json root must be an object", errors[0])

    def test_required_governance_rejects_checksum_drift(self):
        spec = importlib.util.spec_from_file_location("adoption", CHECK_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "common-governance"
            shutil.copytree(ROOT / "common-governance", package)
            with (package / "README.md").open("a", encoding="utf-8") as stream:
                stream.write("\ndrift\n")
            errors: list[str] = []
            mod.check_governance_package(package, errors, required=True)

        self.assertEqual(len(errors), 1)
        self.assertIn("checksum mismatch README.md", errors[0])

    def test_common_governance_ssot_is_in_sync(self):
        result = subprocess.run(
            [sys.executable, str(SYNC_GOVERNANCE_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn(b"\r\n", (ROOT / "common-governance" / "MANIFEST.json").read_bytes())
        self.assertEqual(
            (ROOT / "scripts" / "check-project-adoption.py").read_bytes(),
            (ROOT / "common-governance" / "scripts" / "check-project-adoption.py").read_bytes(),
        )

    def test_common_governance_package_consistency(self):
        result = subprocess.run(
            [sys.executable, str(COMMON_GOVERNANCE_VALIDATOR)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_common_governance_validator_rejects_adr_template_contract_drift(self):
        import tempfile

        spec = importlib.util.spec_from_file_location(
            "common_governance_validator_adr", COMMON_GOVERNANCE_VALIDATOR
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "common-governance"
            shutil.copytree(ROOT / "common-governance", package)
            template = package / "examples" / "adr-template.md"
            template.write_text(
                template.read_text(encoding="utf-8")
                .replace("- Status: proposed", "- Status: Proposed")
                .replace("### Option B", "### Alternative"),
                encoding="utf-8",
            )
            mod.ROOT = package
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                result = mod.main()

        self.assertEqual(result, 1)
        self.assertIn("ADR template minimum contract missing", output.getvalue())
        self.assertIn("lowercase governed enum", output.getvalue())

    def test_distributed_validator_rejects_checksum_drift(self):
        import tempfile

        spec = importlib.util.spec_from_file_location(
            "common_governance_validator", COMMON_GOVERNANCE_VALIDATOR
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "common-governance"
            shutil.copytree(ROOT / "common-governance", package)
            with (package / "README.md").open("a", encoding="utf-8") as stream:
                stream.write("\ndrift\n")
            mod.ROOT = package
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                result = mod.main()

        self.assertEqual(result, 1)
        self.assertIn("checksum mismatch README.md", output.getvalue())

    def test_distributed_validator_rejects_missing_testing_governance_markers(self):
        import hashlib
        import json
        import tempfile

        spec = importlib.util.spec_from_file_location(
            "common_governance_testing_markers", COMMON_GOVERNANCE_VALIDATOR
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "common-governance"
            shutil.copytree(ROOT / "common-governance", package)
            project_rules = package / "examples" / "PROJECT_RULES.md.sample"
            project_rules.write_text("# Project Rules Overlay\n", encoding="utf-8")
            manifest_path = package / "MANIFEST.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"]["examples/PROJECT_RULES.md.sample"] = hashlib.sha256(
                project_rules.read_bytes()
            ).hexdigest()
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            mod.ROOT = package
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                result = mod.main()

        self.assertEqual(result, 1)
        self.assertIn("PROJECT_RULES testing governance markers missing", output.getvalue())

    def test_distributed_package_runs_level_two_adoption_check(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "frontend"
            shutil.copytree(ROOT / "examples" / "adoption-fixture" / "frontend", repo)
            package = repo / "common-governance"
            shutil.copytree(ROOT / "common-governance", package)
            result = subprocess.run(
                [
                    sys.executable,
                    str(package / "scripts" / "check-project-adoption.py"),
                    "--repo",
                    str(repo),
                    "--stack",
                    "frontend",
                    "--level",
                    "2",
                ],
                capture_output=True,
                text=True,
                cwd=repo,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_credential_scan_workflow_is_pinned_and_read_only(self):
        import yaml

        workflow_path = (
            ROOT / "common-governance" / "examples" / "ci" / "credential-scan-required.yml"
        )
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow = yaml.safe_load(workflow_text)

        self.assertEqual(workflow["permissions"], {"contents": "read"})
        steps = workflow["jobs"]["scan"]["steps"]
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["fetch-depth"], 0)
        self.assertEqual(workflow["env"]["GITLEAKS_VERSION"], "8.30.0")
        install = next(step for step in steps if step.get("name") == "Install pinned scanner")
        self.assertIn("sha256sum --check", install["run"])
        canary = next(step for step in steps if step.get("name") == "Verify scanner behavior")
        self.assertIn("must-detect.txt", canary["run"])
        self.assertIn('if [ "${status}" -ne 1 ]', canary["run"])
        scanner = next(step for step in steps if step.get("name") == "Scan repository history")
        self.assertEqual(scanner["run"], "gitleaks git --redact --verbose .")

    def test_supply_chain_workflow_rejects_ambiguous_node_lockfiles(self):
        import yaml

        source = ROOT / "examples" / "ci" / "supply-chain-required.yml"
        distributed = (
            ROOT / "common-governance" / "examples" / "ci" / "supply-chain-required.yml"
        )
        self.assertEqual(source.read_bytes(), distributed.read_bytes())
        workflow = yaml.safe_load(source.read_text(encoding="utf-8"))
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        steps = workflow["jobs"]["node-dependency-policy"]["steps"]
        lockfile = next(step for step in steps if step.get("name") == "Validate Node lockfile")
        self.assertIn('"${#locks[@]}" -ne 1', lockfile["run"])
        self.assertIn("does not silently approximate Yarn audits", lockfile["run"])
        licenses = next(step for step in steps if step.get("name") == "Check production licenses")
        self.assertIn("license-checker@25.0.1", licenses["run"])
        maven = workflow["jobs"]["maven-dependency-check"]["steps"][-1]
        self.assertIn("dependency-check-maven:12.2.2:check", maven["run"])

    def test_governance_workflow_runs_strict_fixture_command(self):
        workflow = (ROOT / ".github" / "workflows" / "validate-rules-packages.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("--stack frontend --level 2", workflow)
        self.assertRegex(
            workflow,
            re.compile(r"cp -R common-governance .*adoption-fixture/frontend/common-governance"),
        )
        self.assertIn("python scripts/validate-repository.py", workflow)
        self.assertIn("actionlint/cmd/actionlint@v1.7.12", workflow)

    def test_workflow_security_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(WORKFLOW_SECURITY_VALIDATOR)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_workflow_security_rejects_floating_action_and_write_all(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("workflow_security", WORKFLOW_SECURITY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / ".github" / "workflows" / "unsafe.yml"
            path.parent.mkdir(parents=True)
            path.write_text(
                "name: unsafe\non: [push]\npermissions:\n  contents: write\n"
                "jobs:\n  test:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - uses: actions/checkout@v4\n",
                encoding="utf-8",
            )
            errors = mod.validate_workflow(path, root)

        self.assertTrue(any("40-character commit SHA" in error for error in errors))
        self.assertTrue(any("top-level permissions" in error for error in errors))

    def test_control_catalog_passes(self):
        result = subprocess.run(
            [sys.executable, str(CONTROL_CATALOG_VALIDATOR)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_control_catalog_rejects_unversioned_reference_and_missing_path(self):
        spec = importlib.util.spec_from_file_location("control_catalog", CONTROL_CATALOG_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        import yaml

        data = yaml.safe_load((ROOT / "docs" / "control-catalog.yaml").read_text(encoding="utf-8"))
        data["controls"][0]["standards"] = ["NIST-SSDF-PO.1.1"]
        data["controls"][0]["verification"] = ["scripts/missing.py"]
        errors = mod.validate_catalog(data, ROOT)

        self.assertTrue(any("unversioned or unknown" in error for error in errors))
        self.assertTrue(any("path not found" in error for error in errors))

    def test_control_catalog_rejects_ai_control_as_level_zero(self):
        spec = importlib.util.spec_from_file_location("control_catalog", CONTROL_CATALOG_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        import yaml

        data = yaml.safe_load((ROOT / "docs" / "control-catalog.yaml").read_text(encoding="utf-8"))
        ai = next(item for item in data["controls"] if item["id"] == "CR-AI-001")
        ai["level"] = 0
        ai["gate"] = "always"
        errors = mod.validate_catalog(data, ROOT)

        self.assertTrue(any("CR-AI-001 must not be Level 0" in error for error in errors))
        self.assertTrue(any("CR-AI-001.gate must be" in error for error in errors))

    def test_ai_eval_results_are_suite_bound(self):
        result = subprocess.run(
            [
                sys.executable,
                str(AI_EVAL_RESULTS_VALIDATOR),
                "--file",
                "examples/ai-eval-results.yaml",
                "--suite",
                "web-front/rules/evals/ai-tool-safety.md",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_prepare_ai_eval_run_prints_plan_and_writes_fail_skeleton(self):
        import tempfile

        plan = subprocess.run(
            [
                sys.executable,
                str(PREPARE_AI_EVAL_SCRIPT),
                "--stack",
                "frontend",
                "--print-plan",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(plan.returncode, 0, plan.stdout + plan.stderr)
        self.assertIn("suite_sha256:", plan.stdout)
        self.assertIn("EAT01", plan.stdout)
        self.assertIn("do not invent pass", plan.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            skeleton = Path(tmp) / "ai-eval-results.yaml"
            written = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_AI_EVAL_SCRIPT),
                    "--stack",
                    "frontend",
                    "--write-skeleton",
                    str(skeleton),
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(written.returncode, 0, written.stdout + written.stderr)
            self.assertTrue(skeleton.is_file())
            text = skeleton.read_text(encoding="utf-8")
            self.assertIn("result: fail", text)
            self.assertNotIn("result: pass", text)
            failing = subprocess.run(
                [
                    sys.executable,
                    str(AI_EVAL_RESULTS_VALIDATOR),
                    "--file",
                    str(skeleton),
                    "--suite",
                    "web-front/rules/evals/ai-tool-safety.md",
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(failing.returncode, 1)

    def test_ai_eval_results_reject_failed_case_and_suite_drift(self):
        spec = importlib.util.spec_from_file_location("ai_eval_results", AI_EVAL_RESULTS_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        import tempfile
        import yaml

        data = yaml.safe_load((ROOT / "examples" / "ai-eval-results.yaml").read_text(encoding="utf-8"))
        data["cases"][0]["result"] = "fail"
        with tempfile.TemporaryDirectory() as tmp:
            suite = Path(tmp) / "suite.md"
            suite.write_text("changed suite\n", encoding="utf-8")
            errors = mod.validate_results(data, suite)

        self.assertTrue(any("result must be pass" in error for error in errors))
        self.assertTrue(any("does not match" in error for error in errors))

    def test_ai_eval_results_reject_placeholder_model_metadata(self):
        spec = importlib.util.spec_from_file_location("ai_eval_metadata", AI_EVAL_RESULTS_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        import yaml

        data = yaml.safe_load((ROOT / "examples" / "ai-eval-results.yaml").read_text(encoding="utf-8"))
        data["run"]["model_version"] = "latest"
        errors = mod.validate_results(data, ROOT / "web-front" / "rules" / "evals" / "ai-tool-safety.md")

        self.assertTrue(any("run.model_version must be meaningful" in error for error in errors))

    def test_repository_hygiene_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(REPOSITORY_VALIDATOR)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_hygiene_validator_rejects_broken_artifacts(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("repository_validator", REPOSITORY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "broken.md").write_text(
                "[missing](missing.md)\ntrailing space \n", encoding="utf-8"
            )
            (root / "broken.yml").write_text("items: [\n", encoding="utf-8")
            errors, links, yaml_files = mod.validate_repository(root)

        self.assertEqual(links, 1)
        self.assertEqual(yaml_files, 1)
        self.assertTrue(any("trailing whitespace" in error for error in errors))
        self.assertTrue(any("missing local link" in error for error in errors))
        self.assertTrue(any("invalid YAML" in error for error in errors))

    def test_repository_hygiene_validator_rejects_ambiguous_root_contract_ssot(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("repository_ssot", REPOSITORY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("OpenAPI / schema 作为 SSOT\n", encoding="utf-8")
            errors = mod.check_root_openapi_ssot(root)

        self.assertTrue(any("peer OpenAPI SSOT" in error for error in errors))

    def test_repository_hygiene_validator_rejects_stale_contract_gate_wording(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("repository_contract_gate", REPOSITORY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            branch = root / "docs/branch-protection.md"
            template = root / ".github/pull_request_template.md"
            readme = root / "README.md"
            branch.parent.mkdir(parents=True)
            template.parent.mkdir(parents=True)
            branch.write_text("契约门禁：OpenAPI diff / Spectral\n", encoding="utf-8")
            template.write_text("OpenAPI diff / Spectral\n", encoding="utf-8")
            readme.write_text("接入 OpenAPI diff\n", encoding="utf-8")
            errors = mod.check_root_contract_gate_wording(root)

        self.assertTrue(any("contract gate wording missing" in error for error in errors))
        self.assertTrue(any("generic OpenAPI diff / Spectral" in error for error in errors))
        self.assertTrue(any(error.startswith("README.md:") for error in errors))

    def test_repository_hygiene_validator_requires_aligned_four_part_versions(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("repository_versions", REPOSITORY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in mod.VERSION_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("1.0.0.0\n", encoding="utf-8")
            self.assertEqual(mod.check_release_versions(root), [])

            (root / "miniapp" / "rules" / "VERSION").write_text(
                "1.0.0\n", encoding="utf-8"
            )
            errors = mod.check_release_versions(root)

        self.assertTrue(any("invalid four-part release version" in error for error in errors))
        self.assertTrue(any("release versions are not aligned" in error for error in errors))

    def test_repository_hygiene_validator_enforces_chinese_unnumbered_shared_titles(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("repository_titles", REPOSITORY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared = root / "web-backend" / "rules" / "shared"
            shared.mkdir(parents=True)
            (shared / "00-must-follow.md").write_text("# Must Follow Rules\n", encoding="utf-8")
            (shared / "01-project-structure.md").write_text("# 01 项目结构规则\n", encoding="utf-8")
            (shared / "02-naming.md").write_text("# 命名规则（Java）\n", encoding="utf-8")

            errors = mod.check_shared_rule_titles(root)

        self.assertEqual(len(errors), 2)
        self.assertTrue(any("Chinese display title" in error for error in errors))
        self.assertTrue(any("must not repeat" in error for error in errors))

    def test_repository_hygiene_validator_rejects_bare_or_missing_checklist_rule_refs(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("repository_refs", REPOSITORY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checklist = root / "docs" / "architect-engineering-checklist.md"
            checklist.parent.mkdir(parents=True)
            checklist.write_text(
                "`07`\n`web-front/rules/shared/07-security-performance.md`\n",
                encoding="utf-8",
            )
            errors = mod.check_architecture_checklist_rule_references(root)

        self.assertTrue(any("bare rule reference" in error for error in errors))
        self.assertTrue(any("missing rule reference" in error for error in errors))

    def test_repository_hygiene_validator_enforces_chinese_agent_document_titles(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("repository_agent_titles", REPOSITORY_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / "web-backend" / "rules" / "codex"
            codex.mkdir(parents=True)
            (root / "AGENTS.md").write_text("# Repository Instructions\n", encoding="utf-8")
            (codex / "01-before-editing.md").write_text("# 01 Before Editing\n", encoding="utf-8")
            errors = mod.check_agent_document_titles(root)

        self.assertEqual(len(errors), 3)
        self.assertTrue(any("Chinese explanatory title" in error for error in errors))
        self.assertTrue(any("must not repeat" in error for error in errors))


class ReleaseEvidenceTests(unittest.TestCase):
    def test_release_evidence_sample_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                str(RELEASE_EVIDENCE_SCRIPT),
                "--file",
                str(ROOT / "examples" / "release-evidence.yaml"),
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_release_evidence_rejects_placeholders_and_untested_rollback(self):
        spec = importlib.util.spec_from_file_location("release_evidence", RELEASE_EVIDENCE_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        invalid = {
            "schema_version": 2,
            "release": {
                "id": "TODO",
                "version": "1.0.0",
                "environment": "production",
                "owner": "team",
                "change_ref": "PR-1",
                "commit_sha": "not-a-sha",
                "artifact_digest": "sha256:bad",
                "approved_at": "2026-08-14T10:00:00+08:00",
                "rules_versions": {"common-governance": "2.0.0"},
            },
            "requirements": [{"id": "REQ-1", "acceptance_evidence": "TBD"}],
            "risk": {"level": "high", "summary": "change", "rollout_evidence": "N/A"},
            "rollback": {"tested": False, "command_or_runbook": "TODO", "owner": "team"},
            "observability": {
                "dashboards": ["dashboard"],
                "alerts": ["alert"],
                "observation_window_minutes": 60,
            },
            "gates": {name: "passed" for name in mod.GATE_NAMES},
            "exceptions": [],
        }
        errors = mod.validate_release_evidence(invalid)

        self.assertTrue(any("release.id" in error for error in errors))
        self.assertTrue(any("acceptance_evidence" in error for error in errors))
        self.assertIn("rollback.tested must be true", errors)
        self.assertTrue(any("risk.rollout_evidence" in error for error in errors))
        self.assertTrue(any("commit_sha" in error for error in errors))
        self.assertTrue(any("artifact_digest" in error for error in errors))

    def test_release_evidence_rejects_unmatched_exception(self):
        spec = importlib.util.spec_from_file_location("release_exception", RELEASE_EVIDENCE_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        import yaml

        data = yaml.safe_load((ROOT / "examples" / "release-evidence.yaml").read_text(encoding="utf-8"))
        data["gates"]["security"] = "exception"
        errors = mod.validate_release_evidence(data)

        self.assertTrue(any("exception gates lack approved exception records" in error for error in errors))

    def test_release_evidence_binds_digest_to_artifact_bytes(self):
        import hashlib
        import tempfile
        import yaml

        spec = importlib.util.spec_from_file_location("release_artifact", RELEASE_EVIDENCE_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        data = yaml.safe_load((ROOT / "examples" / "release-evidence.yaml").read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "artifact.bin"
            artifact.write_bytes(b"trusted artifact\n")
            data["release"]["artifact_digest"] = f"sha256:{hashlib.sha256(artifact.read_bytes()).hexdigest()}"
            self.assertEqual(mod.validate_release_evidence(data, artifact), [])
            artifact.write_bytes(b"tampered\n")
            errors = mod.validate_release_evidence(data, artifact)

        self.assertIn("release.artifact_digest does not match --artifact bytes", errors)


class GovernanceEvidenceTests(unittest.TestCase):
    def test_closed_exception_sample_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                str(EXCEPTIONS_VALIDATOR),
                "--file",
                "examples/rule-exception.yaml",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_open_expired_exception_fails(self):
        spec = importlib.util.spec_from_file_location("exceptions", EXCEPTIONS_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        import datetime as dt
        import yaml

        data = yaml.safe_load((ROOT / "examples" / "rule-exception.yaml").read_text(encoding="utf-8"))
        data["status"] = "open"
        data.pop("closed_at")
        data.pop("closure_evidence")
        errors = mod.validate_exception(data, dt.date(2026, 9, 15))
        self.assertIn("open exception is expired", errors)

    def test_exception_longer_than_ninety_days_fails(self):
        spec = importlib.util.spec_from_file_location("exceptions_duration", EXCEPTIONS_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        import datetime as dt
        import yaml

        data = yaml.safe_load((ROOT / "examples" / "rule-exception.yaml").read_text(encoding="utf-8"))
        data["expires_at"] = "2026-12-31"
        errors = mod.validate_exception(data, dt.date(2026, 9, 15))
        self.assertIn("exception duration must not exceed 90 days", errors)

    def test_pr_governance_rejects_blank_template(self):
        spec = importlib.util.spec_from_file_location("pr_governance", PR_GOVERNANCE_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        body = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        errors = mod.validate_body(body)
        self.assertTrue(any("completed six-column row" in error for error in errors))
        self.assertTrue(any("risk level" in error for error in errors))

    def test_pr_governance_accepts_completed_body(self):
        spec = importlib.util.spec_from_file_location("pr_governance_valid", PR_GOVERNANCE_VALIDATOR)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        body = """## 变更摘要
补齐治理门禁并提供可审计证据。

## 需求 / Issue 与验收证据
| 需求 / Issue | 验收条件 | 影响面 | 实现 / 契约 | 验证证据 | 状态 |
|---|---|---|---|---|---|
| GOV-1 | 提交时校验完整证据 | CI | validator | unit test | Pass |

## 变更类型
- [x] 规则包 `rules/**` 变更

## 风险
- [x] Low（低风险）

## 回滚方案
回退该治理提交并重新运行校验。

## 已运行命令
python -m unittest discover -s scripts/tests -v
"""
        self.assertEqual(mod.validate_body(body), [])


class DebtBaselineTests(unittest.TestCase):
    def test_regex_count_passes_at_baseline_and_fails_on_growth(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            source = root / "src" / "page.vue"
            source.write_text("legacy-component\n", encoding="utf-8")
            config = root / "baseline.json"
            config.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "baseline_commit": "0123456789abcdef0123456789abcdef01234567",
                        "captured_at": "2026-09-15T12:00:00+08:00",
                        "owner": "test-owner",
                        "scan_command": "python scripts/check-debt-baseline.py --config baseline.json",
                        "metrics": [
                            {
                                "name": "legacy",
                                "kind": "regex-count",
                                "root": ".",
                                "globs": ["src/**/*.vue"],
                                "pattern": "legacy-component",
                                "maximum": 1,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            passing = subprocess.run(
                [sys.executable, str(DEBT_BASELINE_SCRIPT), "--config", str(config)],
                capture_output=True,
                text=True,
            )
            source.write_text("legacy-component\nlegacy-component\n", encoding="utf-8")
            failing = subprocess.run(
                [sys.executable, str(DEBT_BASELINE_SCRIPT), "--config", str(config)],
                capture_output=True,
                text=True,
            )

        self.assertEqual(passing.returncode, 0, passing.stdout + passing.stderr)
        self.assertEqual(failing.returncode, 1)
        self.assertIn("delta=+1", failing.stdout)

    def test_debt_baseline_rejects_empty_scan_by_default(self):
        import tempfile

        spec = importlib.util.spec_from_file_location("debt_empty_scan", DEBT_BASELINE_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            config = root / "baseline.json"
            metric = {"name": "legacy", "kind": "regex-count", "root": ".", "globs": ["src/**/*.vue"], "pattern": "legacy", "maximum": 2}
            with self.assertRaisesRegex(ValueError, "scan matched 0 files"):
                mod.regex_count(metric, config)
            metric["minimum_files"] = 0
            metric["allow_empty_reason"] = "project has no Vue files"
            self.assertEqual(mod.regex_count(metric, config)[0]["files_scanned"], 0)

    def test_path_allowlist_reports_added_and_removed_paths(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "legacy").mkdir()
            (root / "legacy" / "new.txt").write_text("new\n", encoding="utf-8")
            config = root / "baseline.json"
            config.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "baseline_commit": "0123456789abcdef0123456789abcdef01234567",
                        "captured_at": "2026-09-15T12:00:00+08:00",
                        "owner": "test-owner",
                        "scan_command": "python scripts/check-debt-baseline.py --config baseline.json",
                        "metrics": [
                            {
                                "name": "paths",
                                "kind": "path-allowlist",
                                "root": ".",
                                "globs": ["legacy/**"],
                                "allowed": ["legacy/old.txt"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(DEBT_BASELINE_SCRIPT),
                    "--config",
                    str(config),
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["metrics"][0]["added"], ["legacy/new.txt"])
        self.assertEqual(payload["metrics"][0]["removed"], ["legacy/old.txt"])


class EvalTopicManifestTests(unittest.TestCase):
    def test_suite_drift_detection_logic(self):
        sys.path.insert(0, str(SCRIPTS))
        import eval_topic_manifest as etm

        rules_root = ROOT / "web-front" / "rules"
        live = etm.live_smoke_suites(rules_root, "E")
        self.assertIn("Security", live)
        tampered = dict(live)
        tampered["Security"] = ["E99"]
        errors: list[str] = []
        for name, live_ids in live.items():
            if sorted(tampered.get(name, [])) != sorted(live_ids):
                errors.append(name)
        self.assertIn("Security", errors)

    def test_frontend_manifest_suites_in_sync(self):
        sys.path.insert(0, str(SCRIPTS))
        import eval_topic_manifest as etm

        rules_root = ROOT / "web-front" / "rules"
        manifest = etm.load_manifest(rules_root / "evals" / "topic-manifest.yaml")
        live = etm.live_smoke_suites(rules_root, "E")
        for name, live_ids in live.items():
            self.assertEqual(
                sorted((manifest.get("suites") or {}).get(name, [])),
                sorted(live_ids),
                name,
            )

    def test_generated_manifests_use_lf(self):
        for rel in (
            "web-front/rules/evals/topic-manifest.yaml",
            "web-backend/rules/evals/topic-manifest.yaml",
            "miniapp/rules/evals/topic-manifest.yaml",
        ):
            self.assertNotIn(b"\r\n", (ROOT / rel).read_bytes(), rel)
