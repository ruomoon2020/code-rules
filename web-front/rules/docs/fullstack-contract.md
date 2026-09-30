# 全栈契约（管理端摘要）

> 本文让 `web-front/rules/` 可以独立阅读；完整 SSOT 位于 monorepo
> `web-backend/rules/docs/fullstack-contract.md`。字段、接口或发布顺序冲突时，以后端完整版与 `contracts/openapi.yaml` 为准。

## 单一来源与发布顺序

```text
contracts/openapi.yaml
  → 后端 Controller / DTO / 校验
  → 管理端 schema / src/api/generated
  → 管理端页面、权限、审计展示
```

1. 先更新 OpenAPI、枚举、`errorCode` 和兼容策略。
2. 后端兼容发布后，前端运行项目的 `schema:sync`、`api:gen`、`api:check`。
3. 再配置菜单、路由和按钮权限，完成联调；禁止手改 generated 文件或虚构字段。

## 统一字段

| 字段 | 前端职责 |
|---|---|
| `traceId` | request / logger 关联；错误页和操作记录可供排障查询 |
| `errorCode`、`message` | 统一 normalizer；`errorCode` 是稳定契约并映射 i18n，`message` 仅作允许的 fallback；禁止页面猜码、按 message 分支或拼业务句 |
| `page`、`pageSize`、`total`、`records` | 列表状态、空态与删末页回退遵守 `shared/19-list-pagination.md` |
| `sortField`、`sortOrder` | `sortOrder` 只传 `asc` / `desc`；`ascending` / `descending` 在请求前映射 |
| 权限码 | 路由、按钮和后端 `@PreAuthorize` 同源或可追溯；UI 仅作体验收敛 |
| `Idempotency-Key` | 创建、支付等可重试写操作复用同一键；不因重试生成新业务请求 |

既有响应壳（数字码 + 文案 + data）在 request wrapper / normalizer 映射到 `code` / `message` / `errorCode` / `traceId`；平台字段名写 `99-project-local`。完整说明见后端 `docs/fullstack-contract.md` §既有响应壳适配。

## 管理端新增业务页

- 复用平台菜单、权限指令、字典、壳层、文件与操作记录；约束见 `shared/22-business-module-extension.md`。
- 列表、详情、导出、批量操作和异步任务均按后端数据权限结果展示；403/业务错误须明确反馈，不能伪造成功。
- 导入导出需要模板下载、任务状态、错误明细、下载鉴权，并在完成后刷新审计记录。
- 树表 / 主子表需处理非法父节点禁选、子表错误明细和失败态；后端事务与归属校验仍是安全边界。

## i18n / 实时 / 富文本

- 用户可见文案与枚举走 i18n 或字典；金额、日期、时区用统一 formatter（`shared/23-i18n-locale.md`）。
- WebSocket / SSE：鉴权不走 URL query 长期 Token；卸载须取消订阅（`shared/24-realtime-rich-content.md`）。
- 富文本展示须 sanitizer；禁止裸 `v-html`；重型编辑器按需加载。
- 相关 PR 建议跑 evals **Platform Extension E41–E43**（3/3）；细则见 monorepo `web-backend/rules/docs/fullstack-contract.md` §管理端 Platform Extension。

## 何时读取完整版

涉及审计字段映射、OpenAPI breaking change、跨端业务扩展、租户数据权限、i18n/实时/富文本或小程序联调时，读取 monorepo `web-backend/rules/docs/fullstack-contract.md` 对应章节（含 §管理端 Platform Extension）。
