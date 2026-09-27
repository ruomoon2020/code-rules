# 规则包索引（前端）

| 场景 | 首选规则 |
|---|---|
| 页面 / 列表 | `shared/04-ui-patterns.md`、`shared/19-list-pagination.md`、`cursor/13-list-pagination.mdc` |
| 表单 / 详情 | `shared/13-form-and-detail.md`、`cursor/20-form-detail.mdc`、`shared/12-schema-ssot.md` |
| 路由 / 权限 / 壳层 | `shared/06-state-route-permission.md`、`shared/17-shell-navigation.md`、`cursor/09-shell-navigation.mdc` |
| API / schema | `shared/05-api-contract.md`、`shared/12-schema-ssot.md`、`cursor/11-schema-ssot.mdc` |
| 导入导出 | `shared/14-upload-import-export.md`、`cursor/14-upload-import-export.mdc` |
| 安全 / 性能 / a11y | `shared/07-security-performance.md`、`cursor/06-security-performance.mdc` |
| 错误恢复 | `shared/21-error-recovery.md`、`cursor/17-error-recovery.mdc` |
| 成熟后台业务扩展 | `shared/22-business-module-extension.md`、`cursor/18-business-module-extension.mdc`、`docs/business-feature-playbook-frontend.md` |
| 平台边界 | `cursor/19-platform-boundary.mdc`、`shared/22` §平台边界 |
| i18n / 金额 / 时区 | `shared/23-i18n-locale.md`、`cursor/22-i18n-locale.mdc` |
| WebSocket / 富文本 | `shared/24-realtime-rich-content.md`、`cursor/23-realtime-rich-content.mdc` |
| 受监管 Web 加固 | `shared/25-regulated-web-hardening.md`、`cursor/24-regulated-web-hardening.mdc` |
| 全栈 Platform Extension | `docs/fullstack-contract.md`；完整版 `web-backend/rules/docs/fullstack-contract.md` §管理端 Platform Extension |
| 测试 / CI / 发布 | `shared/15-testing.md`、`shared/08-quality-gates.md`、`cursor/08-quality-testing.mdc` |
| 业务发布 / 回滚 | `docs/release-checklist.md` |
| AI 生成 / 外部内容 / 工具调用 | `shared/09-ai-generation.md`、`cursor/21-ai-generation.mdc` |
| 验证 | `shared/10-verification-checklist.md`、`cursor/07-review-checklist.mdc` |
| 企业治理（DoD / 豁免 / Owner） | `docs/enterprise-governance.md` → monorepo `docs/` |

Codex 从 `codex/AGENTS.md` 路由；Cursor 从 `cursor/00-project-overview.mdc` 和路径 glob 触发。

**跨包编号**：各端 `shared/` 编号不等义；全栈任务按文件名路由，见 monorepo `web-backend/rules/docs/fullstack-contract.md` §跨包编号说明。

发版 evals 门槛：P0 8/8；P1 ≥39/42（E01–E50）；测试治理 E31/E50 建议 **2/2**；AI Tool Safety EAT01–EAT05 **5/5**。
