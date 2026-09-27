# 业务模块扩展（前端）

适用于基于 RuoYi-Vue-Plus、RuoYi-Cloud-Plus、ruoyi-vue-pro、JeecgBoot 等成熟后台管理端**新增业务页面**。本文是前端**业务二开装配层**：不替代 `01`–`21`，只规定如何复用平台壳层与契约能力。

本地摘要见 `docs/fullstack-contract.md`；完整 SSOT 与新增业务功能对齐表见 monorepo `web-backend/rules/docs/fullstack-contract.md`；步骤清单见 `docs/business-feature-playbook-frontend.md`。

## 默认原则

1. 新业务页面进入既有业务域目录（如 `src/views/{biz}/`），不污染 `layout`、`router` 全局守卫、`store` 公共模块，除非按项目 Owner 流程改平台能力。
2. 平台已有能力必须优先复用：菜单注册、路由、按钮权限、字典、壳层导航、文件上传、导入导出、操作记录、全局错误恢复。
3. 禁止在业务 views 重复实现一套菜单 API、权限 store、字典服务或登录态逻辑。
4. CodeGen / 脚手架页面只是起点；上线前须换 Base 组件、补四态、权限、字典 fallback、分页竞态与测试。
5. 后端 OpenAPI / 权限码 / 菜单未就绪时，不得先写「假字段」页面联调。

## 平台边界与命名

1. 单一业务默认只修改业务域 views、composables、配置与 API 使用层；不得修改 `layouts`、全局 router 守卫、权限 store、Base 组件、generator 模板。
2. 确需改变平台能力时，须由 Owner 审核，并在 PR 说明兼容范围、回滚方案与既有页面回归；触发摘要见 `cursor/19-platform-boundary.mdc`。
3. Base 组件、Token、request wrapper 等公共能力须标记生命周期：`experimental`、`stable` 或 `deprecated`；废弃项必须给出替代方案、迁移期限和删除版本。
4. 修改 stable 公共 API、全局交互语义或跨应用契约时，须有 ADR 或等价设计记录，并覆盖消费方兼容测试。
3. 模块名、路由名、权限码、字典 type、导入导出任务标识和后端错误码应使用同一业务前缀或存在可追溯映射；禁止前端另造一套稳定码。

## 契约与 API

1. 字段、表格列、表单、枚举以 `contracts/schema.json` 或 `src/api/generated` 为 SSOT（`12-schema-ssot`）。
2. 改接口先改契约源，再 `schema:sync` → `api:gen` → `api:check`；**禁止**手改 `src/api/generated`。
3. 组件内禁止直接 `axios` / `fetch`；API 走 `src/api` 薄 wrapper（`05-api-contract`）。

## 路由 / 菜单 / 权限

1. 路由 `name` 使用 PascalCase，与 keep-alive、`defineOptions({ name })`、菜单配置一致（`06-state-route-permission`、`17-shell-navigation`）。
2. 按钮权限码、路由 meta 权限与后端 `@PreAuthorize` / 菜单按钮码**同源或可追踪**；禁止前端自造与后端不一致的权限字符串。
3. 权限只做展示与交互收敛；**禁止**仅隐藏按钮而无后端鉴权（`00` §29–30）。
4. 列表、详情、导出、批量操作与异步任务都必须按后端租户 / 数据权限结果处理：无权限显示明确错误或空态，不以缓存数据、前端筛选或“操作成功”掩盖拒绝结果。
5. 禁止为单个业务在 views 复制全局 `permission` directive / helper 实现。

## 页面与列表

1. 列表页用 `BasePage` + `useTable`（或项目等价封装），须含 loading、empty、error（含重试）、permission（`04-ui-patterns`、`19-list-pagination`）。
2. 查询、表格、分页字段与 OpenAPI 一致；筛选或 pageSize 变化回第一页；删当前页最后一条回退页码；请求防竞态。
3. 表单 / 详情见 `13-form-and-detail`；destructive 操作须确认 + 提交 loading。
4. 字典 / 枚举展示须有 unknown fallback；禁止硬编码与后端 `action` / 枚举码不一致的文案。

## 导入 / 导出 / 操作记录

1. 模板下载、导入错误明细、导出下载须遵守 `14-upload-import-export`：权限、脱敏、鉴权 URL、审计刷新。
2. 导出 / 导入成功后须引导查看操作记录（与后端 `27` / 全栈契约审计字段对齐）。
3. 禁止在 UI 伪造导入成功或绕过二次确认。

## 树表 / 主子表（UI）

| 类型 | 前端必查 |
|---|---|
| 树表 | 父节点选择与后端租户 / 数据范围一致；跨租户父节点须报错态，不可静默挂载 |
| 主子表 | 子表编辑与主表同一提交流或明确分步；失败时 UI 状态与后端回滚一致 |
| 导入导出 | 主子关系错误明细展示；异步任务进度 / 轮询；完成后刷新列表与操作记录 |

## 异步任务与批处理 UI

1. 导入、导出、批量处理等异步任务展示稳定 `taskId`、状态、进度、失败原因和可下载错误明细；状态值以 OpenAPI / 后端字典为准。
2. 轮询必须可取消、页面卸载即停止，并处理超时、失败和权限变化；不得无限轮询或仅靠本地计时推断成功。
3. 任务完成后刷新列表、操作记录与必要字典缓存；收到失败 / 403 时保留可排障的 `errorCode`、`traceId`，不弹成功提示。

## 禁止

- 虚构 schema 字段、Base 组件 props、权限码、路由名。
- 在 views 使用原生 Element Plus（`el-*`、`<El*>`、`element-plus` import）。
- 重复实现全局登录过期、chunk 失败、白屏恢复（用 `21-error-recovery`）。
- 为单个业务改全局 router 守卫、layout、权限 store 且无 Owner / 评审。
- CodeGen 页未换 Base 组件、未补四态直接上线。
- 导入导出绕过权限、脱敏或操作记录刷新。

## 与其他规则的关系

OpenAPI / generated 见 `12`；API 调用见 `05`；路由权限见 `06`、`17`；列表见 `19`；导入导出见 `14`；收尾见 `10`；AI 行为见 `09`。前端平台边界见 `cursor/19-platform-boundary.mdc`；后端模块边界见 monorepo `web-backend/rules/shared/43-business-module-extension.md`。
