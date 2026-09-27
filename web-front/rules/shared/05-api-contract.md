# API 契约规则

API、表单、表格字段必须以契约为单一事实来源。

## 统一入口

1. 组件禁止直接调用 `axios` / `fetch`。
2. 请求必须走 `src/api` 与统一 request wrapper。
3. request wrapper 统一处理 token、错误、loading、traceId、文件下载、重试。
4. 错误须经项目 **error normalizer**（如 `normalizeError`、`toAppError`，以仓库实际导出为准）转为稳定字段 `code` / `message` / `errorCode` / `traceId`，再供页面 logger / 错误 UI 使用；禁止在业务代码直接假设 `err.code` / `err.status` / 平台原文案字段形态。既有响应壳映射见后端 `docs/fullstack-contract.md` §既有响应壳适配。
5. api 层不直接弹 Toast / Message；UI 反馈由页面或统一错误层处理。

## Schema SSOT

优先级：

```text
contracts/schema.json
  -> src/api/generated
  -> src/api/* thin wrapper
  -> views / components
```

规则：

1. 写表单字段、表格列、查询条件前，先读 `contracts/schema.json` 或 generated 类型。
2. 禁止添加 schema 中不存在的字段。
3. 禁止手写与 generated 重复或冲突的 DTO。
4. `src/api/generated` 禁止手改。
5. 契约变更后必须重新 `schema:sync` + `api:gen` + `api:check`。

## API 兼容

| 变更 | 规则 |
|---|---|
| 新增响应字段 | 向后兼容，前端不要假设旧环境一定存在 |
| 新增请求字段 | 必须有默认值或后端兼容缺省 |
| 字段删除 / 重命名 | breaking change，需废弃期和迁移说明 |
| 枚举新增 | 前端必须有 unknown fallback |
| 响应结构调整 | breaking change，需版本同步和回滚方案 |

## BFF / Adapter

1. 多端共用接口差异明显时，优先使用 BFF 或 adapter 层收敛。
2. 不在页面里写大量接口形态分支。
3. BFF 返回给前端的结构仍须进入 schema，不允许口头契约。

## Mock

1. 本地可使用 MSW / vite-plugin-mock。
2. CI 使用独立 fixture，不依赖生产数据。
3. 生产包禁止包含 mock handler 或假数据。
