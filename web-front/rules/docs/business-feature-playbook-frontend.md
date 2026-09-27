# Business Feature Playbook（前端）

> **AI 执行 SSOT**：`shared/22-business-module-extension.md`。
> 与后端 `web-backend/rules/docs/business-feature-playbook.md`、`web-backend/rules/docs/fullstack-contract.md` §新增业务功能 对齐。

## 1. 先确认后端已就绪

1. `contracts/openapi.yaml`（或 schema）已更新并通过 diff。
2. 权限码已在后端定义（如 `crm:customer:create`）。
3. 菜单 / 路由命名与后端 `action` / `resourceType` 策略已对齐。
4. 字典 type 或 OpenAPI 枚举与后端一致。

## 2. 落地顺序

1. **契约**：`schema:sync` → `api:gen` → `api:check`；禁止手改 `src/api/generated`。
2. **类型与 API**：薄 wrapper；组件内禁止直接 `axios`/`fetch`（`05-api-contract`）。
3. **路由 / 菜单**：路由 `name` PascalCase，与 keep-alive、菜单、权限码一致（`06-state-route-permission`、`17-shell-navigation`）。
4. **页面**：列表用 `BasePage` + `useTable`（loading/empty/error/permission）；表单/详情见 `13-form-and-detail`。
5. **权限**：按钮权限指令；路由守卫；禁止仅隐藏按钮（后端必须鉴权）。
6. **字典 / 枚举**：组件展示 + unknown fallback；禁止与后端 action 码不一致的硬编码文案。
7. **导入 / 导出**：模板下载、错误明细、操作记录刷新（`14-upload-import-export`）。
8. **验证**：`pnpm lint`、`type-check`、相关单测；联调越权与分页边界。

## 3. 列表页最小完成定义

- 查询、表格、分页与 OpenAPI 字段一致。
- 无 `el-*` / `<El*>`（`00` 硬规则）。
- 删除当前页最后一条后回退页码（evals E19）。
- 搜索/翻页防竞态（`19-list-pagination`）。
- 权限码与后端菜单按钮码一致或可追踪。

## 4. CodeGen / 脚手架后的人工补齐

| 项 | 要求 |
|---|---|
| 组件 | 替换为项目 Base 组件；禁止 CodeGen 原生 EP 页直接上线 |
| 四态 | loading、empty、error（含重试）、permission |
| 权限 | 按钮码、路由 meta 与后端一致；不只隐藏 UI |
| 字典 | unknown fallback；与 OpenAPI 枚举同源 |
| 分页 | 回第一页、末条删除回退、竞态取消 |
| 导入导出 | 模板、错误明细、下载鉴权、操作记录刷新 |

## 5. 树表 / 主子表（UI）

| 类型 | 必查项 |
|---|---|
| 树表 | 父节点选择受权限与租户约束；非法父节点有明确错误态 |
| 主子表 | 提交 / 回滚与后端事务一致；子表无权限时有禁用或提示 |
| 导入导出 | 主子错误明细；异步任务 UI；完成后刷新列表与操作记录 |

## 6. 与后端 Business Extension evals 对照（联调 / 双端 PR）

| 后端 | 前端 | 主题 |
|---|---|---|
| B55 | **E32** | 不污染 layout / 全局 store |
| B56 | **E33** | 复用平台菜单 / 权限 / 字典 |
| B57 | **E34** | CodeGen 页换 Base + 四态 + 权限 |
| B58 | **E35** | 列表 / 详情 / 导出权限一致 |
| B59 | **E36** | 导出审计 UI、鉴权下载 |
| B60 | **E37** | 导入任务状态，禁止伪造成功 |
| B61 | **E38** | 树表禁选非法父节点 |
| B62 | **E39** | 主子表失败态与回滚一致 |
| B63 | **E40** | 禁止改 generator 全局 Vue 模板 |

成熟后台业务 PR 建议：后端 **B55–B63（9/9）** + 前端 **E32–E40（9/9）**。

涉及 i18n、WebSocket/SSE、富文本或编辑器 PR 时，另跑前端 **Platform Extension E41–E43（建议 3/3）**（无后端 B 对称项）。

## 7. PR 自检

- [ ] 已 `schema:sync` + `api:gen` + `api:check`；未手改 `generated`
- [ ] 路由 `name`、菜单、按钮权限码与后端一致
- [ ] 未重复实现全局菜单 / 权限 / 字典 / 登录过期逻辑
- [ ] 列表四态、分页竞态、删除末条回退已处理
- [ ] 导入 / 导出 / 下载有权限、脱敏、操作记录刷新
- [ ] 树表 / 主子表（若有）已对照 §5；建议跑 **E38–E39**（与后端 B61–B62）
- [ ] 成熟后台业务 PR 已跑 **Business Extension** E32–E40（建议 9/9）
- [ ] i18n / 实时 / 富文本 PR 已跑 **Platform Extension** E41–E43（建议 3/3）
- [ ] 已跑 `pnpm lint`、`type-check`（或项目等价命令）
- [ ] 全栈字段对齐见 `web-backend/rules/docs/fullstack-contract.md` §新增业务功能

## 8. 禁止

- 虚构 schema 字段或 Base 组件 API。
- 在 views 重复实现全局错误恢复、登录过期（用 `21-error-recovery`）。
- 导入导出绕过权限与脱敏展示。
- 后端契约未就绪时先写假字段页面。
