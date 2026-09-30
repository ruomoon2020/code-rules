import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "validate-rules-package.py"
SPEC = importlib.util.spec_from_file_location("backend_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class ValidateRulesPackageTests(unittest.TestCase):
    def test_feature_flag_lifecycle_rejects_shortened_numbered_and_expected_clauses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "evals").mkdir()
            (root / "shared/22-operability.md").write_text(
                "1. 灰度开关须登记 Owner、默认值和到期日。\n", encoding="utf-8"
            )
            (root / "shared/32-service-reliability.md").write_text(
                "3. 功能开关（Feature Flag）须登记 Owner 与到期日。\n", encoding="utf-8"
            )
            (root / "evals/prompts.md").write_text(
                "**期望**：拒绝；环境相关和运维参数须进入配置；高风险开关须有 Owner、默认值和到期日。\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_feature_flag_lifecycle(root, errors)

        self.assertEqual(len(errors), 3)
        self.assertTrue(all("安全失败值" in error for error in errors))
        self.assertTrue(all("观察指标" in error for error in errors))
        self.assertTrue(all("回滚方式" in error for error in errors))

    def test_feature_flag_lifecycle_rejects_stale_subset_wording(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "shared"
            shared.mkdir()
            source = (rules_root / "shared/32-service-reliability.md").read_text(encoding="utf-8")
            source = source.replace(
                "功能开关、灰度和实验配置须统一遵循",
                "Owner 与过期时间只是该清单子集；功能开关、灰度和实验配置须统一遵循",
            )
            (shared / "32-service-reliability.md").write_text(source, encoding="utf-8")
            errors: list[str] = []

            validator.check_feature_flag_lifecycle(root, errors)

        self.assertTrue(any("stale feature flag subset wording" in error for error in errors))

    def test_feature_flag_lifecycle_rejects_subset_wording_in_prompts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evals").mkdir()
            (root / "evals/prompts.md").write_text(
                "**期望**：拒绝；环境相关和运维参数须登记 Owner。\n"
                "Owner、默认值和过期时间只是该清单子集。\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_feature_flag_lifecycle(root, errors)

        self.assertTrue(any("prompts.md: stale feature flag subset wording" in error for error in errors))

    def test_shared_titles_require_chinese_without_repeated_number(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "shared"
            shared.mkdir()
            (shared / "00-must-follow.md").write_text("# Must Follow\n", encoding="utf-8")
            (shared / "01-project-structure.md").write_text("# 01 项目结构规则\n", encoding="utf-8")
            (shared / "02-naming.md").write_text("# 命名规则\n", encoding="utf-8")
            errors: list[str] = []
            validator.check_shared_titles(root, errors)

        self.assertEqual(len(errors), 2)

    def test_project_local_sample_requires_testing_governance_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "examples" / "99-project-local.mdc.sample"
            sample.parent.mkdir(parents=True)
            sample.write_text("# local\n", encoding="utf-8")
            errors: list[str] = []
            validator.check_project_local_sample(root, errors)

        self.assertTrue(any("testing governance markers missing" in error for error in errors))

    def test_project_local_sample_requires_architecture_api_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "examples" / "99-project-local.mdc.sample"
            sample.parent.mkdir(parents=True)
            sample.write_text("# local\n", encoding="utf-8")
            errors: list[str] = []
            validator.check_project_local_sample(root, errors)

        self.assertTrue(any("architecture/API markers missing" in error for error in errors))

    def test_project_local_sample_requires_default_compatibility_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "examples" / "99-project-local.mdc.sample"
            sample.parent.mkdir(parents=True)
            sample.write_text(
                "- 架构档：`CRUD_LITE`\n"
                "- 对象命名：`ENTITY_REQUEST_RESPONSE`\n"
                "- API 风格：`GET_POST_COMPAT`，与 x-api-style 一致\n"
                "- 租户模型：`NONE`\n"
                "- 全局表 / 租户豁免表：`NONE`\n"
                "- 数据所有权：默认当前模块只写自己的表\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.check_project_local_sample(root, errors)

        self.assertTrue(any("default/compatibility markers missing" in error for error in errors))

    def test_project_local_sample_rejects_non_selected_profile_lists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "examples" / "99-project-local.mdc.sample"
            sample.parent.mkdir(parents=True)
            sample.write_text(
                "- 架构档：`CRUD_LITE` / `CLASSIC_LAYERED`\n"
                "- 对象命名：`ENTITY_REQUEST_RESPONSE`\n"
                "- API 风格：`GET_POST_COMPAT`，与 x-api-style 一致\n"
                "- 租户模型：`NONE`\n"
                "- 全局表 / 租户豁免表：`NONE`\n"
                "- 数据所有权：默认当前模块只写自己的表\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.check_project_local_sample(root, errors)

        self.assertTrue(any("架构档 must select exactly one" in error for error in errors))

    def test_project_local_sample_rejects_multiple_tenancy_models(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "examples" / "99-project-local.mdc.sample"
            sample.parent.mkdir(parents=True)
            sample.write_text(
                "- 架构档：`CRUD_LITE`\n"
                "- 对象命名：`ENTITY_REQUEST_RESPONSE`\n"
                "- API 风格：`GET_POST_COMPAT`，与 x-api-style 一致\n"
                "- 租户模型：`NONE` / `SHARED_COLUMN`\n"
                "- 全局表 / 租户豁免表：`NONE`\n"
                "- 数据所有权：默认当前模块只写自己的表\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.check_project_local_sample(root, errors)

        self.assertTrue(any("租户模型 must select exactly one" in error for error in errors))

    def test_testing_governance_suite_matches_smoke_index(self):
        rules_root = Path(__file__).parents[2]
        smoke = validator.read(rules_root / "evals" / "smoke-prompts.md")
        evals_readme = validator.read(rules_root / "evals" / "README.md")

        smoke_ids = validator.parse_suite_line(smoke, "## Testing Governance")
        readme_ids = validator.parse_evals_table_suite(evals_readme, "Testing Governance")

        self.assertEqual(sorted(smoke_ids), sorted(validator.TESTING_GOVERNANCE_SUITE))
        self.assertEqual(sorted(readme_ids), sorted(validator.TESTING_GOVERNANCE_SUITE))

    def test_ai_tool_safety_rejects_missing_case(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evals").mkdir()
            text = validator.read(rules_root / "evals" / "ai-tool-safety.md")
            text = text.replace("### BAT05", "### BAT99")
            (root / "evals" / "ai-tool-safety.md").write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_ai_tool_safety(root, errors)

        self.assertTrue(any("BAT01-BAT05" in error for error in errors))

    def test_scaffold_runtime_rejects_java_syntax_error(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            java = root / "examples" / "scaffold" / "java" / "common" / "web" / "ApiResult.java"
            java.write_text(java.read_text(encoding="utf-8")[:-2], encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_runtime(root, errors)

        self.assertTrue(any("scaffold Java syntax failed" in error for error in errors))

    def test_b19_topic_guard_rejects_rubric_semantic_drift(self):
        errors: list[str] = []
        # Fixture must satisfy every EVAL_TOPIC_GUARDS id; only B19 drifts.
        prompts = "\n".join(
            f"### {eval_id} — {topic}"
            for eval_id, topic in validator.EVAL_TOPIC_GUARDS.items()
        )
        rubric_lines = []
        for eval_id, topic in validator.EVAL_TOPIC_GUARDS.items():
            cell = "拒绝永久公开错误文件 URL" if eval_id == "B19" else topic
            rubric_lines.append(f"| {eval_id} | {cell} |")
        rubric = "\n".join(rubric_lines)

        validator.check_eval_topic_guards(prompts, rubric, errors)

        self.assertEqual(errors, ["B19: rubric topic must contain '高风险导入无确认'"])

    def test_cursor_rejects_bare_shared_rule_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "cursor").mkdir()
            (root / "shared").mkdir()
            (root / "shared" / "08-exception-errorcodes.md").write_text("# rule\n", encoding="utf-8")
            (root / "cursor" / "08.mdc").write_text(
                "全文：`08-exception-errorcodes.md`\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_cursor_shared_refs(root, errors)

        self.assertEqual(errors, ["08.mdc: bare shared reference 08-exception-errorcodes.md; use rules/shared/..."])

    def test_agents_rejects_missing_rules_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "codex").mkdir()
            (root / "codex" / "AGENTS.md").write_text(
                "读取 `rules/shared/missing.md`\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_agents_paths(root, errors)

        self.assertEqual(errors, ["codex/AGENTS.md: missing rules/shared/missing.md"])

    def test_scaffold_runtime_rejects_invalid_mapper_xml(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapper = root / "examples" / "scaffold" / "resources" / "mapper" / "system" / "UserMapper.xml"
            mapper.parent.mkdir(parents=True)
            mapper.write_text("<mapper>", encoding="utf-8")
            errors: list[str] = []

            validator.check_scaffold_runtime(root, errors)

        self.assertTrue(any("invalid XML" in error for error in errors))

    def test_architecture_profile_assets_cover_all_declared_profiles(self):
        rules_root = Path(__file__).parents[2]
        errors: list[str] = []

        validator.check_architecture_profile_assets(rules_root, errors)

        self.assertEqual(errors, [])

    def test_openapi_diff_assets_use_pinned_oasdiff(self):
        rules_root = Path(__file__).parents[2]
        errors: list[str] = []

        validator.check_openapi_diff_assets(rules_root, errors)

        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "rules"
            shutil.copytree(rules_root, copied)
            workflow = copied / "examples" / "ci" / "backend-ci-required.yml"
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "github.com/oasdiff/oasdiff@v1.32.1", "github.com/oasdiff/oasdiff@latest"
                ),
                encoding="utf-8",
            )
            errors = []
            validator.check_openapi_diff_assets(copied, errors)
            self.assertTrue(any("pinned oasdiff" in error for error in errors))
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "github.com/oasdiff/oasdiff@latest", "github.com/oasdiff/oasdiff@v1.32.1"
                ).replace("--fail-on WARN", "--fail-on ERR"),
                encoding="utf-8",
            )
            errors = []
            validator.check_openapi_diff_assets(copied, errors)
            self.assertTrue(any("--fail-on WARN" in error for error in errors))
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "--fail-on ERR", "--fail-on WARN"
                ).replace(
                    'git show "$base:contracts/openapi.baseline.yaml"',
                    'git show "$base:contracts/openapi.yaml"',
                ),
                encoding="utf-8",
            )
            errors = []
            validator.check_openapi_diff_assets(copied, errors)
            self.assertTrue(any("target-branch baseline guard" in error for error in errors))
            template = copied / "examples" / ".github" / "pull_request_template.md"
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "oasdiff breaking --fail-on WARN", "npx @redocly/cli diff"
                ),
                encoding="utf-8",
            )
            errors = []
            validator.check_openapi_diff_assets(copied, errors)
            self.assertTrue(any("unsupported OpenAPI diff" in error for error in errors))
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "npx @redocly/cli diff", "oasdiff breaking --fail-on WARN"
                )
                + "\nOpenAPI diff / Spectral（或说明 skip 原因）\n",
                encoding="utf-8",
            )
            errors = []
            validator.check_openapi_diff_assets(copied, errors)
            self.assertTrue(any("must not allow" in error for error in errors))

    def test_scaffold_openapi_alignment_accepts_repository_examples(self):
        rules_root = Path(__file__).parents[2]
        errors: list[str] = []

        validator.check_scaffold_openapi_alignment(rules_root, errors)

        self.assertEqual(errors, [])

    def test_scaffold_openapi_alignment_rejects_integer_path_id(self):
        rules_root = Path(__file__).parents[2]
        repository_root = rules_root.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            contracts = root / "contracts"
            contracts.mkdir()
            source = (repository_root / "contracts" / "openapi.yaml").read_text(encoding="utf-8")
            source = source.replace(
                "in: path\n      required: true\n      schema:\n        type: string",
                "in: path\n      required: true\n      schema:\n        type: integer\n        format: int64",
            )
            (contracts / "openapi.yaml").write_text(source, encoding="utf-8")
            errors: list[str] = []

            validator.check_scaffold_openapi_alignment(root, errors)

        self.assertTrue(any("path id must be string" in error for error in errors))

    def test_scaffold_openapi_alignment_allows_released_baseline_to_differ(self):
        rules_root = Path(__file__).parents[2]
        repository_root = rules_root.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            contracts = root / "contracts"
            contracts.mkdir()
            shutil.copy2(repository_root / "contracts" / "openapi.yaml", contracts / "openapi.yaml")
            (contracts / "openapi.baseline.yaml").write_text(
                "openapi: 3.0.3\ninfo: {title: released, version: 1.0.0}\npaths: {}\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_scaffold_openapi_alignment(root, errors)

        self.assertEqual(errors, [])

    def test_scaffold_openapi_alignment_rejects_method_style_drift(self):
        rules_root = Path(__file__).parents[2]
        repository_root = rules_root.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            contracts = root / "contracts"
            contracts.mkdir()
            shutil.copy2(repository_root / "contracts" / "openapi.yaml", contracts / "openapi.yaml")
            controller = root / "examples" / "scaffold" / "java" / "modules" / "system" / "api" / "UserController.java"
            text = controller.read_text(encoding="utf-8").replace(
                '@PostMapping("/{id}/update")', '@PatchMapping("/{id}")'
            )
            controller.write_text(text, encoding="utf-8")
            errors: list[str] = []

            validator.check_scaffold_openapi_alignment(root, errors)

        self.assertTrue(any("API-style/auth contract drift" in error for error in errors))

    def test_scaffold_openapi_alignment_rejects_missing_dto_validation(self):
        rules_root = Path(__file__).parents[2]
        repository_root = rules_root.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            contracts = root / "contracts"
            contracts.mkdir()
            shutil.copy2(repository_root / "contracts" / "openapi.yaml", contracts / "openapi.yaml")
            dto = root / "examples" / "scaffold" / "java" / "modules" / "system" / "api" / "dto" / "UserUpdateRequest.java"
            dto.write_text(dto.read_text(encoding="utf-8").replace("@NotNull @Email ", ""), encoding="utf-8")
            errors: list[str] = []

            validator.check_scaffold_openapi_alignment(root, errors)

        self.assertTrue(any("required email, format, and client version" in error for error in errors))

    def test_scaffold_openapi_alignment_rejects_ignored_update_result(self):
        rules_root = Path(__file__).parents[2]
        repository_root = rules_root.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            contracts = root / "contracts"
            contracts.mkdir()
            shutil.copy2(repository_root / "contracts" / "openapi.yaml", contracts / "openapi.yaml")
            service = root / "examples" / "scaffold" / "java" / "modules" / "system" / "application" / "UserService.java"
            service.write_text(
                service.read_text(encoding="utf-8").replace(
                    "int affected = userMapper.updateById(user)", "userMapper.updateById(user)"
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_scaffold_openapi_alignment(root, errors)

        self.assertTrue(any("concurrency result handling missing" in error for error in errors))

    def test_scaffold_openapi_alignment_requires_success_data_and_concurrency_behavior(self):
        rules_root = Path(__file__).parents[2]
        repository_root = rules_root.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            contracts = root / "contracts"
            contracts.mkdir()
            contract = (repository_root / "contracts" / "openapi.yaml").read_text(encoding="utf-8")
            contract = contract.replace(
                "        - type: object\n          required: [data]\n          properties:\n            data:\n              $ref: '#/components/schemas/UserDetailResponse'",
                "        - type: object\n          properties:\n            data:\n              $ref: '#/components/schemas/UserDetailResponse'",
            )
            (contracts / "openapi.yaml").write_text(contract, encoding="utf-8")
            service = root / "examples/scaffold/java/modules/system/application/UserService.java"
            service.write_text(
                service.read_text(encoding="utf-8").replace(
                    ".eq(User::getVersion, user.getVersion())", ".eq(User::getId, user.getId())", 1
                ),
                encoding="utf-8",
            )
            test_sample = root / "examples/scaffold/java/test/UserControllerIT.sample.java"
            test_sample.write_text(
                test_sample.read_text(encoding="utf-8").replace(
                    "same_version_should_allow_only_first_update", "single_update_only"
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_scaffold_openapi_alignment(root, errors)

        self.assertTrue(any("required: [data]" in error for error in errors))
        self.assertTrue(any("concurrency result handling missing" in error for error in errors))
        self.assertTrue(any("concurrency behavior tests missing" in error for error in errors))

    def test_default_scaffold_rejects_tenant_implementation(self):
        rules_root = Path(__file__).parents[2]
        repository_root = rules_root.parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples", root / "examples")
            contracts = root / "contracts"
            contracts.mkdir()
            shutil.copy2(repository_root / "contracts" / "openapi.yaml", contracts / "openapi.yaml")
            entity = root / "examples/scaffold/java/modules/system/domain/User.java"
            entity.write_text(
                entity.read_text(encoding="utf-8").replace(
                    "private Long id;", "private Long id;\n    private String tenantId;"
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_scaffold_default_tenancy(root, errors)

        self.assertTrue(any("default NONE scaffold contains tenant implementation" in error for error in errors))

    def test_data_scope_rejects_string_inferred_authorization_policy(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples", root / "examples")
            scope = root / "examples/scaffold/java/common/datascope/DataScope.java"
            scope.write_text(
                scope.read_text(encoding="utf-8").replace(
                    "DataScopePolicy policy", "String resourceType", 1
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_mysql_utc_and_query_samples(root, errors)

        self.assertTrue(any("must not infer authorization from resource strings" in error for error in errors))

    def test_scaffold_sort_rejects_last_order_by(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples", root / "examples")
            service = root / "examples/scaffold/java/modules/system/application/UserService.java"
            service.write_text(
                service.read_text(encoding="utf-8").replace(
                    "wrapper.orderBy(true, asc, column);",
                    'wrapper.last("ORDER BY created_at " + (asc ? "ASC" : "DESC"));',
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_scaffold_default_tenancy(root, errors)

        self.assertTrue(any("must use Wrapper sorting" in error for error in errors))

    def test_mysql_utc_and_query_samples_reject_session_time_and_two_sided_like(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples", root / "examples")
            migration = root / "examples/db/migration/mysql/V1__init_system_user.sql"
            migration.write_text(
                migration.read_text(encoding="utf-8").replace(
                    "DEFAULT (UTC_TIMESTAMP(3))", "DEFAULT CURRENT_TIMESTAMP(3)", 1
                ),
                encoding="utf-8",
            )
            service = root / "examples/scaffold/java/modules/system/application/UserService.java"
            service.write_text(
                service.read_text(encoding="utf-8").replace(
                    ".likeRight(User::getUsername", ".like(User::getUsername"
                ).replace(
                    "entity.setCreatedAt(now);", "// creation timestamp omitted"
                ),
                encoding="utf-8",
            )
            shared = root / "shared"
            shared.mkdir()
            shutil.copy2(rules_root / "shared/31-production-data-ops.md", shared / "31-production-data-ops.md")
            data_fix = shared / "31-production-data-ops.md"
            data_fix.write_text(
                data_fix.read_text(encoding="utf-8").replace(
                    "updated_at = :executed_at_utc", "updated_at = UTC_TIMESTAMP(3)"
                ).replace(
                    "LIMIT :batch_size;", "-- batch limit omitted"
                ).replace(
                    "WHERE 1 = 0", "WHERE status = :old_status"
                ),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_mysql_utc_and_query_samples(root, errors)

        self.assertTrue(any("CURRENT_TIMESTAMP session time zone" in error for error in errors))
        self.assertTrue(any("two-sided LIKE" in error for error in errors))
        self.assertTrue(any("portable UTC instant" in error for error in errors))
        self.assertTrue(any("preview, update, and rollback batches" in error for error in errors))
        self.assertTrue(any("must not copy all candidate rows" in error for error in errors))
        self.assertTrue(any("entity.setCreatedAt(now)" in error for error in errors))

    def test_logic_delete_rejects_timestamp_sentinel(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "examples/config"
            config.mkdir(parents=True)
            source = (rules_root / "examples/config/application-mybatis.sample.yml").read_text(encoding="utf-8")
            source = source.replace("logic-delete-field: isDeleted", "logic-delete-field: deletedAt")
            source = source.replace("logic-not-delete-value: 0", "logic-not-delete-value: \"1970-01-01 00:00:00.000\"")
            (config / "application-mybatis.sample.yml").write_text(source, encoding="utf-8")
            errors: list[str] = []

            validator.check_mysql_utc_and_query_samples(root, errors)

        self.assertTrue(any("must filter isDeleted" in error for error in errors))
        self.assertTrue(any("epoch sentinel" in error for error in errors))

    def test_data_fix_rejects_missing_live_row_predicate(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "shared"
            shared.mkdir()
            source = (rules_root / "shared/31-production-data-ops.md").read_text(encoding="utf-8")
            (shared / "31-production-data-ops.md").write_text(
                source.replace("is_deleted = 0", "status = status"),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_mysql_utc_and_query_samples(root, errors)

        self.assertTrue(
            any("is_deleted = 0 on every live sys_user read and write" in error for error in errors)
        )

    def test_data_fix_rejects_missing_version_increment(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "shared"
            shared.mkdir()
            source = (rules_root / "shared/31-production-data-ops.md").read_text(encoding="utf-8")
            (shared / "31-production-data-ops.md").write_text(
                source.replace("version = version + 1", "version = version"),
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_mysql_utc_and_query_samples(root, errors)

        self.assertTrue(
            any("must increment version on the fix and again on rollback" in error for error in errors)
        )

    def test_scaffold_exception_contract_rejects_missing_business_stack_log(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            handler = root / "examples" / "scaffold" / "java" / "common" / "exception" / "GlobalExceptionHandler.java"
            text = handler.read_text(encoding="utf-8")
            text = text.replace("log.warn(", "log.info(", 1)
            handler.write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_exception_contract(root, errors)

        self.assertTrue(any("BusinessException WARN stack log" in error for error in errors))

    def test_scaffold_exception_contract_rejects_missing_validation_handler(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            handler = root / "examples" / "scaffold" / "java" / "common" / "exception" / "GlobalExceptionHandler.java"
            text = handler.read_text(encoding="utf-8")
            text = text.replace("handleValidation", "handleInvalidRequest")
            handler.write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_exception_contract(root, errors)

        self.assertTrue(any("dedicated validation 4xx handler" in error for error in errors))

    def test_scaffold_exception_contract_requires_spring_method_validation_handler(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            handler = root / "examples" / "scaffold" / "java" / "common" / "exception" / "GlobalExceptionHandler.java"
            text = handler.read_text(encoding="utf-8")
            text = text.replace("            HandlerMethodValidationException.class,\n", "")
            handler.write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_exception_contract(root, errors)

        self.assertTrue(any("dedicated validation 4xx handler" in error for error in errors))

    def test_scaffold_exception_contract_rejects_validation_framework_stack(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            handler = root / "examples" / "scaffold" / "java" / "common" / "exception" / "GlobalExceptionHandler.java"
            text = handler.read_text(encoding="utf-8")
            text = text.replace("validationSummary(ex)\n        );", "validationSummary(ex),\n                ex\n        );")
            handler.write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_exception_contract(root, errors)

        self.assertTrue(any("without framework stack or rejected values" in error for error in errors))

    def test_scaffold_exception_contract_rejects_missing_cause_constructor(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            business = root / "examples" / "scaffold" / "java" / "common" / "exception" / "BusinessException.java"
            text = business.read_text(encoding="utf-8")
            text = text.replace("Throwable cause", "Object cause")
            business.write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_exception_contract(root, errors)

        self.assertTrue(any("BusinessException cause constructor" in error for error in errors))

    def test_scaffold_exception_contract_rejects_non_4xx_business_status(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            business = root / "examples" / "scaffold" / "java" / "common" / "exception" / "BusinessException.java"
            text = business.read_text(encoding="utf-8")
            text = text.replace("!httpStatus.is4xxClientError()", "httpStatus.is5xxServerError()")
            business.write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_exception_contract(root, errors)

        self.assertTrue(any("reject non-4xx HTTP status" in error for error in errors))

    def test_scaffold_exception_contract_rejects_blank_business_error_code(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "examples" / "scaffold", root / "examples" / "scaffold")
            business = root / "examples" / "scaffold" / "java" / "common" / "exception" / "BusinessException.java"
            text = business.read_text(encoding="utf-8")
            text = text.replace("errorCode.isBlank()", "errorCode.isEmpty()")
            business.write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_scaffold_exception_contract(root, errors)

        self.assertTrue(any("reject blank errorCode" in error for error in errors))

    def test_l0_scope_rejects_numbered_high_level_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "shared" / "00-must-follow.md").write_text(
                "1. 密码必须使用带盐慢哈希。金额禁止使用 `double` / `float`。时刻必须携带时区或明确 UTC。禁止静默改变已有语义。\n"
                "## 条件触发路由（不计入 Level 0 硬规则）\n"
                "1. 见 42-cost-governance.md\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_l0_hard_rule_scope(root, errors)

        self.assertEqual(
            errors,
            ["00-must-follow.md: non-L0 shared rule numbered as L0: 42-cost-governance.md"],
        )

    def test_l0_scope_rejects_high_level_topic_without_file_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "shared" / "00-must-follow.md").write_text(
                "1. 所有项目必须完成威胁建模。密码必须使用带盐慢哈希。金额禁止使用 `double` / `float`。时刻必须携带时区或明确 UTC。禁止静默改变已有语义。\n"
                "## 条件触发路由（不计入 Level 0 硬规则）\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_l0_hard_rule_scope(root, errors)

        self.assertEqual(
            errors,
            ["00-must-follow.md: high-level topic numbered as L0: 威胁建模"],
        )

    def test_l0_scope_requires_baselines_in_numbered_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            rules = [f"{index}. 普通规则。" for index in range(1, 27)]
            rules[0] = "1. 密码必须使用带盐慢哈希。"
            rules[1] = "2. 金额禁止使用 `double` / `float`。"
            rules[2] = "3. 时刻必须携带时区或明确 UTC。"
            (root / "shared" / "00-must-follow.md").write_text(
                "\n".join(rules)
                + "\n## 条件触发路由（不计入 Level 0 硬规则）\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_l0_hard_rule_scope(root, errors)

        self.assertEqual(
            errors,
            ["00-must-follow.md: missing numbered L0 baseline: 禁止静默改变已有语义"],
        )

    def test_l0_scope_rejects_baseline_repeated_in_conditional_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "shared" / "00-must-follow.md").write_text(
                "1. 密码必须使用带盐慢哈希。金额禁止使用 `double` / `float`。时刻必须携带时区或明确 UTC。禁止静默改变已有语义。\n"
                "## 条件触发路由（不计入 Level 0 硬规则）\n"
                "- 金额禁止 `double` / `float`。\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_l0_hard_rule_scope(root, errors)

        self.assertEqual(
            errors,
            [
                "00-must-follow.md: L0 baseline duplicated in conditional route: "
                "金额禁止 `double` / `float`"
            ],
        )

    def test_v2_regression_coverage_rejects_missing_migration_route(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root, root, dirs_exist_ok=True)
            agents = root / "codex/AGENTS.md"
            agents.write_text(
                agents.read_text(encoding="utf-8").replace(
                    "`02-naming.md`、`07-persistence-mybatis.md`、`43-business-module-extension.md`",
                    "`02-naming.md`、`07-missing.md`、`43-business-module-extension.md`",
                    1,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.check_v2_regression_coverage(root, errors)

        self.assertTrue(any("codex migration route missing" in error for error in errors))

    def test_v2_regression_coverage_rejects_generic_onboarding_contract_gate(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root, root, dirs_exist_ok=True)
            onboarding = root / "docs/onboarding-new-project.md"
            onboarding.write_text(
                onboarding.read_text(encoding="utf-8").replace(
                    "4. 固定版本 `oasdiff breaking --fail-on WARN`（契约 PR 必跑）",
                    "4. OpenAPI diff（契约 PR 必跑）",
                    1,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.check_v2_regression_coverage(root, errors)

        self.assertTrue(
            any(
                error.startswith("docs/onboarding-new-project.md: backend v2 summary missing")
                for error in errors
            )
        )
