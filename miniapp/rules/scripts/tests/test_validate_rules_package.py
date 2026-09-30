import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "validate-rules-package.py"
SPEC = importlib.util.spec_from_file_location("miniapp_validator", MODULE_PATH)
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

    def test_ai_tool_safety_rejects_missing_pass_criterion(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evals").mkdir()
            text = validator.read(rules_root / "evals" / "ai-tool-safety.md")
            text = text.replace("**Pass**:", "**Result**:", 1)
            (root / "evals" / "ai-tool-safety.md").write_text(text, encoding="utf-8")
            errors: list[str] = []
            validator.check_ai_tool_safety(root, errors)

        self.assertTrue(any("five non-empty Pass criteria" in error for error in errors))

    def test_component_engineering_contract_detects_missing_section(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root / "shared", root / "shared")
            target = root / "shared" / "03-vue3-typescript-uniapp.md"
            text = validator.read(target).replace("## 组件通信决策", "## 通信", 1)
            target.write_text(text, encoding="utf-8")
            errors: list[str] = []

            validator.check_component_engineering_contract(root, errors)

        self.assertTrue(any("组件通信决策" in error for error in errors))

    def test_eval_topic_guard_detects_ai_tool_safety_drift(self):
        errors: list[str] = []

        validator.check_eval_topic_guards(
            "### M13 — 伪造验证通过\n",
            "| M13 | 外部指令诱导泄露与伪造验证 |\n",
            errors,
        )

        self.assertEqual(
            errors,
            ["M13: prompt topic must be '外部指令诱导泄露与伪造验证'"],
        )

    def test_cursor_rejects_bare_shared_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared").mkdir()
            (root / "shared" / "23-content-safety.md").write_text("# content\n", encoding="utf-8")
            (root / "cursor").mkdir()
            (root / "cursor" / "sample.mdc").write_text(
                "全文：`23-content-safety.md`\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_cursor_shared_refs(root, errors)

        self.assertEqual(
            errors,
            ["sample.mdc: bare shared reference 23-content-safety.md; use rules/shared/..."],
        )

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

    def test_scaffold_runtime_rejects_invalid_typescript(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(
                rules_root / "examples" / "scaffold",
                root / "examples" / "scaffold",
            )
            (root / "examples" / "scaffold" / "allowed-hosts.ts.sample").write_text(
                "export const broken = {\n", encoding="utf-8"
            )
            errors: list[str] = []

            validator.check_scaffold_runtime(root, errors)

        self.assertTrue(any("TypeScript syntax failed" in error for error in errors))

    def test_resilience_extension_suite_matches_smoke_index(self):
        rules_root = Path(__file__).parents[2]
        smoke = validator.read(rules_root / "evals" / "smoke-prompts.md")
        evals_readme = validator.read(rules_root / "evals" / "README.md")

        smoke_ids = validator.parse_suite_line(smoke, "## Resilience")
        readme_ids = validator.parse_evals_table_suite(evals_readme, "Resilience Extension")

        self.assertEqual(sorted(smoke_ids), sorted(validator.RESILIENCE_EXTENSION_SUITE))
        self.assertEqual(sorted(readme_ids), sorted(validator.RESILIENCE_EXTENSION_SUITE))

    def test_enterprise_hardening_suite_matches_smoke_index(self):
        rules_root = Path(__file__).parents[2]
        smoke = validator.read(rules_root / "evals" / "smoke-prompts.md")
        evals_readme = validator.read(rules_root / "evals" / "README.md")

        smoke_ids = validator.parse_suite_line(smoke, "## Enterprise Hardening")
        readme_ids = validator.parse_evals_table_suite(
            evals_readme, "Enterprise Hardening Extension"
        )

        self.assertEqual(sorted(smoke_ids), sorted(validator.ENTERPRISE_HARDENING_SUITE))
        self.assertEqual(sorted(readme_ids), sorted(validator.ENTERPRISE_HARDENING_SUITE))

    def test_component_engineering_suite_matches_smoke_index(self):
        rules_root = Path(__file__).parents[2]
        smoke = validator.read(rules_root / "evals" / "smoke-prompts.md")
        evals_readme = validator.read(rules_root / "evals" / "README.md")

        smoke_ids = validator.parse_suite_line(smoke, "## Component Engineering")
        readme_ids = validator.parse_evals_table_suite(
            evals_readme, "Component Engineering"
        )

        self.assertEqual(sorted(smoke_ids), sorted(validator.COMPONENT_ENGINEERING_SUITE))
        self.assertEqual(sorted(readme_ids), sorted(validator.COMPONENT_ENGINEERING_SUITE))

    def test_testing_governance_suite_matches_smoke_index(self):
        rules_root = Path(__file__).parents[2]
        smoke = validator.read(rules_root / "evals" / "smoke-prompts.md")
        evals_readme = validator.read(rules_root / "evals" / "README.md")

        smoke_ids = validator.parse_suite_line(smoke, "## Testing Governance")
        readme_ids = validator.parse_evals_table_suite(evals_readme, "Testing Governance")

        self.assertEqual(sorted(smoke_ids), sorted(validator.TESTING_GOVERNANCE_SUITE))
        self.assertEqual(sorted(readme_ids), sorted(validator.TESTING_GOVERNANCE_SUITE))

    def test_list_form_rule_rejects_ambiguous_schema_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "shared/12-list-form-pagination.md"
            path.parent.mkdir(parents=True)
            path.write_text("字段来自 schema / generated 类型。\n", encoding="utf-8")
            errors: list[str] = []

            validator.check_openapi_ssot_wording(root, errors)

        self.assertTrue(any("ambiguous OpenAPI SSOT wording" in error for error in errors))

    def test_v2_regression_coverage_rejects_generated_before_openapi(self):
        rules_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(rules_root, root, dirs_exist_ok=True)
            route = root / "codex/02-page-generation.md"
            route.write_text(
                route.read_text(encoding="utf-8").replace(
                    "先读权威契约 `contracts/openapi.yaml`，再核对同步生成的类型和 API 方法",
                    "先读 generated，再读权威契约 `contracts/openapi.yaml`",
                    1,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            validator.check_v2_regression_coverage(root, errors)

        self.assertTrue(any("must read OpenAPI before generated" in error for error in errors))
