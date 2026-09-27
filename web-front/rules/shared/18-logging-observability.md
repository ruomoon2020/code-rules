# 日志与可观测规则

用于生产日志、错误上报、埋点与监控上下文。具体 **logger API 以目标仓库封装为准**（如 `src/utils/logger.ts`、`@/monitor`），禁止 AI 虚构方法签名；本文件定义**字段契约**与**禁止项**。

## 基本原则

1. 生产代码禁止散落 `console.log` / `console.debug` / `console.info`；本地调试须在合并前移除或使用 dev-only 守卫。
2. 错误与关键业务事件统一走项目 logger / monitor 封装。
3. 日志须可检索、可聚合：`event` 命名稳定，同一动作不因 refactor 随意改名。
4. 日志、埋点、错误上报必须脱敏（与 `00-must-follow` §35 一致）。

## 结构化字段（推荐契约）

| 字段 | 必填 | 说明 |
|---|---|---|
| `event` | 是 | 事件名，格式 `domain.resource.action.result`，如 `system.user.list.fetch.failed` |
| `level` | 是 | `debug` \| `info` \| `warn` \| `error` |
| `module` | 建议 | 业务模块，如 `system.user` |
| `route` | 错误/关键路径建议 | 当前路由 `name` 或 path |
| `traceId` | 错误建议 | 链路追踪 ID（通常由 request wrapper 注入） |
| `requestId` | 可选 | 单次请求 ID |
| `durationMs` | 接口/慢操作建议 | 耗时毫秒 |
| `errorCode` | 错误建议 | 业务错误码 |
| `httpStatus` | HTTP 错误建议 | 如 `500` |
| `message` | 错误建议 | 人类可读摘要，不含敏感原文 |
| `release` | 生产错误建议 | 构建版本 / commit |

其他字段（`userId`、`tenantId` 等）按项目 monitor 契约扩展；不确定时读目标仓库 logger 源码。

## 合格示例（形态参考）

示例只表达字段形态；`logger.error` 签名、`route` 来源、`release` 变量名、错误字段名均以目标仓库封装为准。AI 不得照抄 `err.code` / `err.status` 等未知字段；应先使用项目的 error normalizer / request wrapper 产物。

```ts
const normalizedError = normalizeError(error)

logger.error({
  event: 'system.user.list.fetch.failed',
  level: 'error',
  module: 'system.user',
  route: route.name,
  traceId: normalizedError.traceId,
  requestId: normalizedError.requestId,
  durationMs: normalizedError.durationMs,
  errorCode: normalizedError.errorCode,
  httpStatus: normalizedError.httpStatus,
  message: normalizedError.message,
  release,
})
```

info / warn 同理，须含 `event` + `level`；debug 仅开发环境。

## 禁止写入日志的字段

- Token、密码、refreshToken、完整 Cookie
- 完整手机号、身份证号、银行卡号
- 完整请求体 / 响应体（含 PII）
- 未脱敏邮箱（按项目合规要求；默认至少掩码）

需要记录用户标识时，使用项目约定的脱敏形式（如 `138****1234`、hash id）。

## 与 request wrapper 的关系

- `traceId` / `requestId` 应在 `src/api` request wrapper 统一注入（见 `05-api-contract.md`）。
- 写错误日志前须使用项目的 error normalizer（见 `05-api-contract.md`），不要直接读取未知形态的 `err.*`。
- 页面/composable 捕获错误时，从 wrapper 或 normalizer 产物取出 trace 信息再写 logger，不要每条请求手写随机 ID。

## 错误 vs 埋点

- **错误日志**：接口失败、未捕获异常、关键流程中断。
- **埋点**：产品行为统计；仍须脱敏，事件名遵循同一 `domain.resource.action` 风格。
- 不要把调试 `console` 当作临时埋点留在生产路径。
