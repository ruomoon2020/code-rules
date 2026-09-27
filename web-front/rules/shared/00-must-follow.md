# 必须遵守的规则

本文件中带编号的 34 条是所有项目在 Level 0 都成立的不变量，违反即拒 PR。场景规则按文末条件路由启用，不因文件存在就自动成为 Level 0 门禁。

## 架构与依赖

1. `apps` 可依赖 `packages`，`packages` 禁止依赖 `apps`。
2. `components/base` 禁止依赖业务 API、业务 store、业务字段。
3. `utils` 禁止依赖 Vue 组件实例、DOM、路由实例。
4. 页面私有代码就近放置；跨页面复用后再沉淀到公共目录。

## 页面与组件

5. `src/views/**` 禁止直接使用 `el-*` 标签。
6. `src/views/**` 禁止直接从 `element-plus` 及 `element-plus/*` 引入组件。
7. `src/views/**` 禁止使用 Element Plus 的 PascalCase 组件（如 `<ElButton>`、`<ElTable>`）；即使用自动导入也须改用项目 `Base*` 组件。
8. 业务页面优先使用 `Base*` 组件，不重复封装表格、弹窗、筛选、表单。
9. AI 或人工都不得虚构 `BaseTable`、`BaseForm`、`BaseDialog` 的 Props、Events、Slots。
10. destructive 操作必须有确认；异步提交按钮必须有 loading。
11. 所有页面必须处理 loading、empty、error、permission 基本状态。

## TypeScript 与代码

12. 禁止显式 `any`；未知类型使用 `unknown` 加类型守卫。
13. 禁止在业务代码中绕过类型检查。
14. 禁止超长相对路径；优先使用 project alias。
15. 禁止在单文件内堆叠 API、权限、表格、表单、弹窗全部逻辑。
16. 禁止无说明引入新依赖；禁止引入来源不明、无人维护或存在未处置高危漏洞的依赖。

## API 与数据契约

17. 组件内禁止直接 `axios` / `fetch` 调接口。
18. API 必须走 `src/api` 与统一 request wrapper。
19. 表单字段、表格列、DTO 类型必须先读 `contracts/schema.json` 或 generated 类型。
20. 禁止手写与 `src/api/generated` 冲突或重复的 interface。
21. 禁止修改 `src/api/generated`；应修改契约源后重新生成。
22. API 契约变更必须有 generated diff，字段删除、必填变化、枚举变化必须 Review。
23. 未知枚举值必须有 fallback 展示。

## 状态、权限与缓存

24. 权限判断不能只依赖前端；前端只做展示与交互收敛。
25. 敏感信息禁止明文持久化；认证材料存储策略按项目安全要求执行。

## 安全

26. 禁止裸用 `v-html`；必须使用 `SafeHtml` / `safeHtml()` 与 DOMPurify 等消毒方案。
27. 禁止提交敏感凭据和内网生产地址。
28. 生产包禁止包含 mock handler、假数据开关、调试面板。
29. 日志与埋点禁止上报密码、完整证件号、未脱敏手机号等敏感数据；生产禁止散落 `console.*`。
30. 生产 sourcemap 不得公开暴露在 CDN。

## 样式与工程门禁

31. 业务组件禁止硬编码主题色；必须使用项目设计变量。
32. 提交前必须运行项目已配置的 lint、type-check、test、build 等门禁。
33. `views` 硬门禁须同时覆盖 Element Plus import、模板 `<el-*>` 与 PascalCase denylist；CI 禁止用 `--allow-empty` 绕过扫描。
34. 未配置、未运行或失败的检查必须如实报告，禁止声称已经通过。

## 条件触发路由（不计入 Level 0 硬规则）

以下条款命中场景后即为强制要求；采纳 Level、必读资产和证据见 `docs/rule-maturity-model.md` 与 `codex/AGENTS.md`。

- 列表页须遵守标准页面骨架、分页单一数据源、筛选 / pageSize 回第一页、请求防竞态、删除末页回退和 selection 清理（见 `04-ui-patterns.md`、`19-list-pagination.md`）。
- `keepAlive` 页面须声明与路由一致的组件名（见 `17-shell-navigation.md`）。
- 登录、登出、菜单和按钮权限改动须统一权限 helper，并在登出时执行 `resetAllStores()` 或等价清理（见 `06-state-route-permission.md`）。
- 新增 / 升级依赖和修改公共组件 API 时须完成替代方案、体积、许可证、调用方兼容与回滚检查（见 `20-dependency-governance.md`）。
- 文件导入 / 导出须遵守 schema、权限、脱敏、公式注入防护、鉴权下载和审计要求（见 `14-upload-import-export.md`）。
- 全局错误、路由 chunk 失败、登录过期和白屏恢复不得散落在页面中重复实现（见 `21-error-recovery.md`）。
- Feature Flag 须有 Owner、默认值、创建原因、观察指标、回滚方式和清理日期（见 `08-quality-gates.md`、`docs/release-checklist.md`）。
- 体积、依赖检查、API check、E2E、视觉回归、a11y 和发布门禁按项目 Level 与变更范围启用（见 `08-quality-gates.md`、`15-testing.md`）。
- AI 生成复杂前端代码前须读取 Base 源码、schema 和对应场景规则；禁止因示例存在原生 Element Plus 就沿用，并须在输出前按 `10-verification-checklist.md` 自检（见 `09-ai-generation.md`）。
- 基于成熟后台平台新增业务页面时，须复用平台菜单、路由、权限、字典、壳层与 generated API（见 `22-business-module-extension.md`）。
- 金融、政务、高敏数据后台或第三方脚本、嵌入页面、跨窗口通信等高风险场景须追加 `25-regulated-web-hardening.md`。
