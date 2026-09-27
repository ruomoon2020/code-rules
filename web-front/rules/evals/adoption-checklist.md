# Rules Adoption Checklist

业务仓库落地规则包时勾选。

## 规则包文件（复制到业务仓）

- [ ] 整包 `rules/` 可访问（推荐 submodule 或子目录）
- [ ] 根目录 `AGENTS.md` ← `rules/codex/AGENTS.md`
- [ ] `.cursor/rules/*.mdc` ← `rules/cursor/`
- [ ] `rules/shared/` 路径可被 AI 解析

## AI 规则落地项

- [x] AGENTS.md（规则包 `codex/AGENTS.md`）
- [x] `.cursor/rules/00-project-overview.mdc`
- [x] `.cursor/rules/01-architecture.mdc`
- [x] `.cursor/rules/02-vue3-typescript.mdc` + `shared/03-code-style.md`
- [x] `.cursor/rules/03-ui-design-system.mdc` + `shared/16-design-tokens.md`
- [x] `.cursor/rules/04-component-usage.mdc`
- [x] `.cursor/rules/05-api-state-error.mdc` + `shared/05-api-contract.md`
- [x] `.cursor/rules/06-security-performance.mdc` + `shared/07-security-performance.md`
- [x] `.cursor/rules/07-review-checklist.mdc` + `shared/10-verification-checklist.md`
- [x] `.cursor/rules/08-quality-testing.mdc` + `shared/08-quality-gates.md`、`shared/15-testing.md`
- [x] `.cursor/rules/09-shell-navigation.mdc` + `shared/17-shell-navigation.md`
- [x] `.cursor/rules/10-base-components.mdc` + `shared/11-base-components-context.md`
- [x] `.cursor/rules/11-schema-ssot.mdc` + `shared/12-schema-ssot.md`
- [x] `.cursor/rules/12-logging-observability.mdc` + `shared/18-logging-observability.md`
- [x] `.cursor/rules/13-list-pagination.mdc` + `shared/19-list-pagination.md`
- [x] `.cursor/rules/14-upload-import-export.mdc` + `shared/14-upload-import-export.md`
- [x] 命名 → `15-naming-conventions.mdc`（触发）+ `shared/02-naming.md`（SSOT）
- [x] 依赖治理 → `16-dependency-governance.mdc` + `shared/20-dependency-governance.md`
- [x] 错误恢复 → `17-error-recovery.mdc` + `shared/21-error-recovery.md`
- [x] 成熟后台业务扩展 → `18-business-module-extension.mdc` + `shared/22-business-module-extension.md`
- [x] 平台边界 → `19-platform-boundary.mdc`
- [x] 表单 / 详情 → `20-form-detail.mdc` + `shared/13-form-and-detail.md`
- [x] AI 生成 → `21-ai-generation.mdc` + `shared/09-ai-generation.md`
- [x] i18n / 区域格式 → `22-i18n-locale.mdc` + `shared/23-i18n-locale.md`
- [x] 实时 / 富文本 → `23-realtime-rich-content.mdc` + `shared/24-realtime-rich-content.md`
- [x] 受监管 Web 条件加固 → `24-regulated-web-hardening.mdc` + `shared/25-regulated-web-hardening.md`

## 硬门禁（业务项目侧，非 rules 包内）

- [ ] ESLint `views` 禁 `element-plus` 及 `element-plus/*` import（`eslint-views-ban-el.mjs`）
- [ ] CI 扫描 `views` 模板 `<el-*>`（`ci-scan-views-el-tags.mjs`，**勿**加 `--allow-empty`）
- [ ] 已跑 `node rules/examples/run-ci-scan-fixtures.mjs`（规则包发版 / 升级后）
- [ ] `@typescript-eslint/no-explicit-any`
- [ ] `contracts/schema.json` + `api:check`
- [ ] CI：`lint` / `type-check` / `build`
- [ ] `resetAllStores()` 登出实现

## 成熟后台业务扩展（若适用）

- [ ] 已阅读 `shared/22-business-module-extension.md` 与 `docs/business-feature-playbook-frontend.md`；全栈联调见 monorepo `web-backend/rules/docs/fullstack-contract.md` §新增业务功能
- [ ] 后端 playbook 与 OpenAPI 已就绪后再开前端页面（权限码、菜单、字典）
- [ ] 新增业务路由/菜单 PR 已对照后端权限码与 `action` 枚举

## 评测

- [ ] 日常 **Smoke**（`evals/smoke-prompts.md`）；发版 **Full** E01–E50
- [ ] AI 读取外部内容或调用工具时，`evals/ai-tool-safety.md` EAT01–EAT05 **5/5**
- [ ] P0 **8/8**；P1 **至少 39/42**（Full）；Smoke 核心 P1 **≥10/12**
- [ ] 成熟后台新增业务页时，跑 **Business Extension** E32–E40（建议 9/9）
- [ ] i18n / 实时 / 富文本相关 PR 时，跑 **Platform Extension** E41–E43（建议 3/3）
- [ ] 金融 / 政务 / 高敏 Web 相关 PR 时，跑 **Enterprise Hardening** E44–E49（建议 6/6）
- [ ] 已跑 `python rules/scripts/validate-rules-package.py`（嵌入 rules/ 时）

## 企业治理（monorepo）

- [ ] 已阅读 `docs/enterprise-governance.md`；复制 monorepo `docs/definition-of-done.md` 等到业务仓（若仅 submodule 本规则包）
- [ ] 已运行 `scripts/check-project-adoption.py --stack frontend`（`--strict` 推荐）
- [ ] CODEOWNERS 按 `docs/codeowners-matrix.md` 配置
- [ ] 新 PII 字段对照 `docs/data-classification-matrix.md`
