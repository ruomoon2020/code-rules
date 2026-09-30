import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "validate-rules-package.py"
SPEC = importlib.util.spec_from_file_location("frontend_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class ValidateRulesPackageTests(unittest.TestCase):
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

    def test_frontend_checks_missing_backend_cross_package_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            front_rules = repo / "web-front" / "rules"
            front_rules.mkdir(parents=True)
            (front_rules / "README.md").write_text(
                "见 `web-backend/rules/docs/missing.md`\n", encoding="utf-8"
            )
            backend_rules = repo / "web-backend" / "rules"
            backend_rules.mkdir(parents=True)
            errors: list[str] = []

            validator.check_cross_package_backend_refs(front_rules, errors)

        self.assertEqual(
            errors,
            ["cross-package ref missing web-backend/rules/docs/missing.md (from README.md)"],
        )

    def test_agents_rejects_missing_rules_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "codex").mkdir()
            (root / "codex" / "AGENTS.md").write_text(
                "读取 `rules/docs/missing.md`\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_agents_paths(root, errors)

        self.assertEqual(errors, ["codex/AGENTS.md: missing rules/docs/missing.md"])

    def test_eval_topic_guard_detects_prompt_drift(self):
        prompts = "### E41 — 错误主题\n"
        rubric = "| E41 | 硬编码业务文案 |\n"
        errors: list[str] = []

        validator.check_eval_topic_guards(prompts, rubric, errors)

        self.assertTrue(any("E41: prompt topic must be" in error for error in errors))

    def test_eval_topic_guard_detects_rubric_drift(self):
        prompts = "### E42 — Token 放 WebSocket URL\n"
        rubric = "| E42 | 拒绝把 token 放进 query |\n"
        errors: list[str] = []

        validator.check_eval_topic_guards(prompts, rubric, errors)

        self.assertTrue(any("E42: rubric topic must contain" in error for error in errors))

    def test_ai_tool_safety_rejects_lower_threshold(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evals").mkdir()
            text = validator.read(rules_root / "evals" / "ai-tool-safety.md")
            (root / "evals" / "ai-tool-safety.md").write_text(text.replace("门槛：5/5", "门槛：4/5"), encoding="utf-8")
            errors: list[str] = []
            validator.check_ai_tool_safety(root, errors)

        self.assertIn("AI Tool Safety suite threshold must be 5/5", errors)

    def test_common_governance_ref_rejects_missing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            rules = repo / "web-front" / "rules"
            rules.mkdir(parents=True)
            (rules / "README.md").write_text("`common-governance/docs/missing.md`\n", encoding="utf-8")
            (repo / "common-governance").mkdir()
            errors: list[str] = []
            validator.check_common_governance_refs(rules, errors)

        self.assertTrue(any("common-governance ref missing docs/missing.md" in error for error in errors))

    def test_cursor_rejects_bare_shared_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "shared" / "23-i18n-locale.md").write_text("# i18n\n", encoding="utf-8")
            (root / "cursor").mkdir()
            (root / "cursor" / "sample.mdc").write_text(
                "全文：`23-i18n-locale.md`\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_cursor_shared_refs(root, errors)

        self.assertEqual(
            errors,
            ["sample.mdc: bare shared reference 23-i18n-locale.md; use rules/shared/..."],
        )

    def test_platform_extension_suite_matches_smoke_index(self):
        rules_root = Path(__file__).parents[2]
        smoke = validator.read(rules_root / "evals" / "smoke-prompts.md")
        evals_readme = validator.read(rules_root / "evals" / "README.md")

        smoke_ids = validator.parse_suite_line(smoke, "## Platform Extension")
        readme_ids = validator.parse_evals_table_suite(evals_readme, "Platform Extension")

        self.assertEqual(sorted(smoke_ids), sorted(validator.PLATFORM_EXTENSION_SUITE))
        self.assertEqual(sorted(readme_ids), sorted(validator.PLATFORM_EXTENSION_SUITE))

    def test_testing_governance_suite_matches_smoke_index(self):
        rules_root = Path(__file__).parents[2]
        smoke = validator.read(rules_root / "evals" / "smoke-prompts.md")
        evals_readme = validator.read(rules_root / "evals" / "README.md")

        smoke_ids = validator.parse_suite_line(smoke, "## Testing Governance")
        readme_ids = validator.parse_evals_table_suite(evals_readme, "Testing Governance")

        self.assertEqual(sorted(smoke_ids), sorted(validator.TESTING_GOVERNANCE_SUITE))
        self.assertEqual(sorted(readme_ids), sorted(validator.TESTING_GOVERNANCE_SUITE))

    def test_readme_must_list_all_shared_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "shared" / "00-must-follow.md").write_text("# x\n", encoding="utf-8")
            (root / "shared" / "99-missing-from-readme.md").write_text("# y\n", encoding="utf-8")
            (root / "README.md").write_text(
                "| `shared/00-must-follow.md` | hard |\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_readme_shared_inventory(root, errors)

        self.assertEqual(
            errors,
            ["README.md file inventory missing shared/99-missing-from-readme.md"],
        )

    def test_entry_docs_reject_ambiguous_openapi_schema_wording(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "codex").mkdir(parents=True)
            (root / "shared").mkdir()
            (root / "docs").mkdir()
            for rel in (
                "README.md",
                "codex/AGENTS.md",
                "codex/01-before-editing.md",
                "codex/04-api-and-schema.md",
                "shared/12-schema-ssot.md",
                "shared/13-form-and-detail.md",
                "shared/14-upload-import-export.md",
                "docs/onboarding-new-project.md",
                "examples/.github/pull_request_template.md",
            ):
                source = rules_root / rel
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            readme = root / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\nOpenAPI / schema\n", encoding="utf-8")
            errors: list[str] = []

            validator.check_openapi_ssot_wording(root, errors)

        self.assertTrue(any("ambiguous OpenAPI SSOT wording" in error for error in errors))

    def test_topic_manifest_matches_live_evals(self):
        rules_root = Path(__file__).parents[2]
        repo_scripts = rules_root.parent.parent / "scripts"
        sys.path.insert(0, str(repo_scripts))
        import eval_topic_manifest as etm

        errors: list[str] = []
        etm.check_manifest(rules_root, "E", errors)
        self.assertEqual(errors, [])

    def test_scaffold_check_rejects_missing_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "examples" / "scaffold").mkdir(parents=True)
            errors: list[str] = []

            validator.check_scaffold_assets(root, errors)

        self.assertTrue(any("examples/scaffold missing" in error for error in errors))

    def test_scaffold_runtime_rejects_invalid_javascript(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(
                rules_root / "examples" / "scaffold",
                root / "examples" / "scaffold",
            )
            (root / "examples" / "scaffold" / "prettier.config.mjs.sample").write_text(
                "export default {\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_scaffold_runtime(root, errors)

        self.assertTrue(any("syntax prettier.config.mjs.sample" in error for error in errors))

    def test_l0_scope_rejects_conditional_topic_as_numbered_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            numbered = "\n".join(f"{index}. 基础规则" for index in range(1, 34))
            (root / "shared" / "00-must-follow.md").write_text(
                numbered
                + "\n34. Feature Flag 必须始终启用。\n"
                + "## 条件触发路由（不计入 Level 0 硬规则）\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_l0_hard_rule_scope(root, errors)

        self.assertEqual(
            errors,
            ["00-must-follow.md: conditional topic numbered as L0: Feature Flag"],
        )

    def test_l0_scope_rejects_wrong_hard_rule_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "shared" / "00-must-follow.md").write_text(
                "1. 基础规则\n## 条件触发路由（不计入 Level 0 硬规则）\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            validator.check_l0_hard_rule_scope(root, errors)

        self.assertEqual(
            errors,
            ["00-must-follow.md L0 hard rule count 1, expected 34"],
        )

    def test_v2_regression_coverage_rejects_missing_iframe_allowlist(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root, root, dirs_exist_ok=True)
            summary = root / "cursor/09-shell-navigation.mdc"
            summary.write_text(
                summary.read_text(encoding="utf-8").replace(
                    "iframe 只加载项目登记的 HTTPS 来源", "iframe 可加载任意来源", 1
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.check_v2_regression_coverage(root, errors)

        self.assertTrue(any("iframe 只加载项目登记的 HTTPS 来源" in error for error in errors))
