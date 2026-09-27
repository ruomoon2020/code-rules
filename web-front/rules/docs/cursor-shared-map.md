# Cursor ↔ Shared 编号对照（管理端）

> **编号不相等**：`cursor/NN` 是触发入口，`shared/NN` 是正文。维护与排障以本表为准。

| Cursor | Shared 正文 | 主题 |
|---|---|---|
| `00-project-overview.mdc` | `00-must-follow.md` | 总览 / Level 0 |
| `01-architecture.mdc` | `01-project-structure.md` | 工程结构 |
| `02-vue3-typescript.mdc` | `03-code-style.md`（兼 `02-naming`） | Vue / TS 风格 |
| `03-ui-design-system.mdc` | `16-design-tokens.md`、`04-ui-patterns.md` | 设计 Token / UI |
| `04-component-usage.mdc` | `04-ui-patterns.md`、`11-base-components-context.md` | 组件用法 |
| `05-api-state-error.mdc` | `05-api-contract.md`、`06-state-route-permission.md`、`12-schema-ssot.md` | API / 路由权限 / schema |
| `06-security-performance.mdc` | `07-security-performance.md` | 安全与性能 |
| `07-review-checklist.mdc` | `10-verification-checklist.md` | 收尾 |
| `08-quality-testing.mdc` | `08-quality-gates.md`、`15-testing.md`、`10` | 门禁与测试 |
| `09-shell-navigation.mdc` | `17-shell-navigation.md`、`06` | 壳层导航 |
| `10-base-components.mdc` | `11-base-components-context.md` | Base 组件 |
| `11-schema-ssot.mdc` | `12-schema-ssot.md` | Schema SSOT |
| `12-logging-observability.mdc` | `18-logging-observability.md` | 可观测 |
| `13-list-pagination.mdc` | `19-list-pagination.md` | 列表分页 |
| `14-upload-import-export.mdc` | `14-upload-import-export.md` | 上传导入导出 |
| `15-naming-conventions.mdc` | `02-naming.md` | 命名 |
| `16-dependency-governance.mdc` | `20-dependency-governance.md` | 依赖治理 |
| `17-error-recovery.mdc` | `21-error-recovery.md` | 错误恢复 |
| `18-business-module-extension.mdc` | `22-business-module-extension.md` | 业务扩展 |
| `19-platform-boundary.mdc` | `22`、`17`、`12` | 平台边界 |
| `20-form-detail.mdc` | `13-form-and-detail.md` | 表单详情 |
| `21-ai-generation.mdc` | `09-ai-generation.md` | AI 生成 |
| `22-i18n-locale.mdc` | `23-i18n-locale.md` | i18n |
| `23-realtime-rich-content.mdc` | `24-realtime-rich-content.md` | 实时 / 富文本 |
| `24-regulated-web-hardening.mdc` | `25-regulated-web-hardening.md` | 受监管 Web |

Codex 不读 `cursor/*.mdc`。
