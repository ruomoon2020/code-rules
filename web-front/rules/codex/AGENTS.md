# AGENTS.md

本仓库为企业级 Vue 3 前端项目。Codex 必须以 `rules/` 作为 AI 规则唯一入口，不得使用已废弃的 `rules.md`。

## 每次改代码前必读

1. `rules/codex/01-before-editing.md`
2. `rules/shared/00-must-follow.md`

## 实现前命中声明

改代码前，先用 3-8 行说明本轮规则路由；纯问答、只审查不修改时可不声明。

- **任务包**：命中下表哪一行。
- **将读取**：本轮实际会读的 `rules/` 文件路径。
- **不读取及原因**：例如“非成熟后台二开 / 无导入导出 / 仅改样式”。

未声明即开始写代码，视为未遵守本文件。

## 按任务包追加阅读

先判断属于下表哪一行，只读该行和被点名的细则；不要一次加载全部 `shared/`。

| 任务 | 必读规则 |
|---|---|
| 任意前端改动 | `rules/codex/01-before-editing.md`、`rules/shared/00-must-follow.md` |
| 立项 / 架构方案 / 上线评审 | `common-governance/docs/architect-engineering-checklist.md`、`common-governance/docs/definition-of-done.md`、`common-governance/docs/dod-maturity-mapping.md` |
| 需求分析 / 业务 PR / 缺陷修复 | `common-governance/docs/requirements-traceability.md`、`common-governance/docs/business-correctness-review.md` |
| 写 `src/views/**` 页面（列表 / 查询 / 表格） | `rules/shared/04-ui-patterns.md`、`rules/shared/11-base-components-context.md`、`rules/shared/12-schema-ssot.md`、`rules/shared/19-list-pagination.md`、`rules/codex/02-page-generation.md` |
| 表单 / 详情 / 弹窗 | `rules/shared/13-form-and-detail.md`、`rules/shared/12-schema-ssot.md`、`rules/codex/02-page-generation.md` |
| 成熟后台二开 / CRUD / 菜单 / 树表 / 主子表 | `rules/shared/22-business-module-extension.md`、`rules/docs/business-feature-playbook-frontend.md`、`rules/shared/06-state-route-permission.md`、`rules/shared/12-schema-ssot.md`、`rules/shared/14-upload-import-export.md`、`rules/shared/17-shell-navigation.md` |
| `src/api/**`、schema、generated | `rules/shared/05-api-contract.md`、`rules/shared/12-schema-ssot.md`、`rules/codex/04-api-and-schema.md` |
| 路由 / Store / 权限 / 菜单 | `rules/shared/06-state-route-permission.md`、`rules/shared/17-shell-navigation.md`、`rules/shared/05-api-contract.md` |
| 上传 / 导入 / 导出 | `rules/shared/14-upload-import-export.md`、`rules/shared/05-api-contract.md`、`rules/shared/18-logging-observability.md` |
| `src/components/**`、设计 Token | `rules/shared/02-naming.md`、`rules/shared/03-code-style.md`、`rules/shared/04-ui-patterns.md`、`rules/shared/16-design-tokens.md`、`rules/codex/03-component-generation.md` |
| 安全 / 性能 / 错误恢复 | `rules/shared/07-security-performance.md`、`rules/shared/21-error-recovery.md` |
| 测试 / flaky / 竞态 / 兼容 / CI / 依赖 / 发布 | `rules/shared/15-testing.md`、`rules/shared/08-quality-gates.md`、`rules/shared/20-dependency-governance.md` |
| 生产发布 / 灰度 / 回滚 | `common-governance/docs/environment-promotion.md`、`common-governance/docs/release-evidence.md` |
| 生产事故 / 安全事件 / 复盘 | `common-governance/docs/incident-response.md`、`common-governance/docs/incident-postmortem-template.md` |
| AI 生成复杂前端代码；读取网页 / Issue / 日志；调用外部工具 | `rules/shared/09-ai-generation.md` |
| i18n / 金额 / 日期 / 时区展示 | `rules/shared/23-i18n-locale.md`、`rules/shared/13-form-and-detail.md` |
| WebSocket / SSE / 富文本 / 编辑器 | `rules/shared/24-realtime-rich-content.md`、`rules/shared/07-security-performance.md` |
| 金融 / 政务 / 高敏数据 / 第三方脚本 / 嵌入页面 / 跨窗口通信 | `rules/shared/25-regulated-web-hardening.md`、`rules/shared/07-security-performance.md` |
| 架构 / 新模块 | `rules/shared/01-project-structure.md` |
| 收尾 / Review | `rules/shared/10-verification-checklist.md`、`rules/codex/05-verification.md` |

## 业务扩展触发词

出现 CRUD、业务模块、管理后台、CodeGen、菜单、按钮权限、字典、导入、导出、树表、主子表、RuoYi、Jeecg 等时，必须追加读取 `rules/shared/22-business-module-extension.md` 与 `rules/docs/business-feature-playbook-frontend.md`。

## 路径触发

- 编辑 `src/views/**`、`src/router/**`（业务域）→ 追加 `22` + playbook（成熟后台场景）。
- 编辑 `contracts/schema.json`、`src/api/generated/**` → 追加 `12-schema-ssot.md` + `05-api-contract.md`。
- 编辑 `src/components/base/**` → 追加 `11-base-components-context.md`。
- 编辑 `src/layouts/**`、全局壳层 → 追加 `17-shell-navigation.md`。
- 编辑 `src/**/*i18n*`、locale、formatter → 追加 `23-i18n-locale.md`。
- 编辑 WebSocket、SSE、富文本、编辑器相关代码 → 追加 `24-realtime-rich-content.md`。
- 编辑第三方脚本、嵌入页面、跨窗口通信、远程高风险开关，或项目声明为受监管场景 → 追加 `25-regulated-web-hardening.md`。

Codex 优先读 `rules/shared/*.md` 与 `rules/codex/*.md`。

- 不要依赖 `rules/cursor/*.mdc`（该目录仅供 Cursor）。
- 维护规则包时可读 `rules/docs/contributing-rules-package.md`；业务编码任务只按本文件明确路由读取对应文档。成熟后台新增业务页可读 `rules/docs/business-feature-playbook-frontend.md`，编码约束以 `rules/shared/22-business-module-extension.md` 为准。

## 硬规则

- 未阅读目标仓库 Base 组件源码或 `rules/shared/11-base-components-context.md` 前，不得编写或重构 `src/views/**`。
- 未阅读 `contracts/schema.json`（或 generated 类型）前，不得新增表单字段、表格列或 DTO。
- `src/views/**` 禁止使用原生 Element Plus（`el-*`、denylist 内 PascalCase 如 `<ElButton>`，以及 `element-plus` / `element-plus/*` import）。
- 禁止虚构 Base 组件 props / events / slots、schema 字段、权限码、路由名。
- 禁止在 Vue 组件内直接 `axios` / `fetch`。
- 禁止显式 `any`；未知类型用 `unknown` 并收窄。
- 禁止无说明引入新依赖；禁止为通过检查而 `as any`。新增或升级依赖时按任务路由读取 `rules/shared/20-dependency-governance.md`。
- 禁止修改公共组件 API 而不同步所有调用方。
- 禁止把 mock、密钥、调试日志、不安全 `v-html` 带入生产代码。
- 涉及文件导入导出时，禁止 schema 外字段、未授权字段或未脱敏敏感字段，并按任务路由读取 `rules/shared/14-upload-import-export.md`。
- 不得在单文件模板内堆叠 API、权限、表格、表单、弹窗全部逻辑；行数阈值按项目和 `rules/shared/03-code-style.md` 执行。

## Schema 固定指令

生成或修改 `views/` 下业务页面前：

```text
1. 读取 contracts/schema.json（或执行 pnpm schema:sync 后的最新文件）。
2. 定位当前模块对应 service 的 request/response。
3. 据此生成类型、api 调用、表单字段、表格列。
4. 禁止添加 schema 中不存在的字段；禁止手写与 generated 重复的 interface。
5. UI 仅使用项目 Base 组件；views 禁 el-*、禁 EP PascalCase（见 `00-must-follow` §7）。
```

## 完成前

运行项目中实际存在的脚本；若不存在则明确说明未配置，不得伪造通过结果：

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build
```

API 或 schema 变更后，若项目有 `pnpm api:check`，必须运行。

详细检查项见 `rules/shared/10-verification-checklist.md` 与 `rules/codex/05-verification.md`。
