# REST API 设计规则

## 接口风格

没有另行写明时，查询用 GET，新增、修改、删除用 POST（`GET_POST_COMPAT`）。普通增删改查按这个写，不要停下来让人选择。对外开放、走标准 REST 网关，或和其他组织对接时，在 OpenAPI 顶层声明 `x-api-style: RESOURCE_REST`，并写进 `99-project-local` 或 ADR。两种写法的资源名、鉴权、错误码、幂等和契约保持一致。同一个业务模块不要无说明地混用。

| 风格 | 方法与路径 | 适用场景 |
|---|---|---|
| `RESOURCE_REST` | 查询 `GET`、创建 `POST`、全量替换 `PUT`、部分更新 `PATCH`、删除 `DELETE` | 公网开放接口、标准 REST 网关、跨组织集成 |
| `GET_POST_COMPAT` | 查询只用 `GET`；创建和状态变更使用 `POST`；更新 `/resources/{id}/update`，删除 `/resources/{id}/delete` | 企业内网网关、签名 SDK、审计或防火墙仅放行 GET/POST |

共同规则：

1. 资源名使用复数名词；路径版本前缀 `/api/v1`（按项目约定）。
2. `GET` 必须安全且无副作用，禁止用 GET 执行新增、更新、删除或审批。
3. `GET_POST_COMPAT` 的写操作必须使用明确、稳定的动作路径；禁止把所有命令塞进 `/execute`、`/doAction` 或靠 body 中的任意字符串分发。
4. `RESOURCE_REST` 中只接收部分可编辑字段的 Request DTO 禁止使用 `PUT`。
5. 批量操作可使用 `POST /users/batch-delete` 等动作端点，但须在 OpenAPI 描述资源范围、权限、幂等和部分失败语义。
6. HTTP Adapter 的方法限制不得渗入 Service 接口；两种风格应调用同一用例方法，避免复制业务实现。

## 统一响应

成功与失败结构见 `08-exception-errorcodes.md`，典型：

```json
{
  "code": 0,
  "message": "ok",
  "data": { },
  "traceId": "..."
}
```

列表分页 `data`：

```json
{
  "records": [],
  "total": 100,
  "page": 1,
  "pageSize": 20
}
```

与前端 `19-list-pagination` 对齐。

## HTTP 状态与响应头

1. 同步创建资源返回 `201 Created` + `Location`；不得一律返回 `200`。
2. 同步删除成功返回 `204 No Content`；`204` 禁止携带 JSON 响应体。需追踪时可用 `X-Trace-Id` 响应头。
3. 异步导入、导出、批处理等返回 `202 Accepted`，并给出可查询的任务资源或状态地址。
4. 契约须显式声明可能的 `400` / `401` / `403` / `404` / `409` / `429` / `5xx`；禁止 OpenAPI 只写成功响应。
5. HTTP status 表达协议结果，`errorCode` 表达业务原因；禁止所有失败都用 HTTP 200 后只看 body `code`。
6. 对外 / 开放接口优先采用 RFC 9457 `application/problem+json`；内部管理端可保留统一 `ApiResult`，但须正确使用 HTTP status 并在 OpenAPI 复用错误 schema。

## 幂等

1. 支付、下单、创建资源等**可重试写操作**须在 OpenAPI 声明 `Idempotency-Key`（HTTP Header）或等价业务幂等键，服务端去重；见 `05-openapi-contract.md`、`18-idempotency-concurrency.md`。
2. `PUT` 按资源 ID 幂等；`POST` 若无幂等键须在文档明确「不可安全重试」。`GET_POST_COMPAT` 的更新、删除、审批等命令应使用业务幂等键、版本号或结果复用保证可控重试。
3. 幂等键建议 TTL ≥ 24h，冲突时返回与原请求一致的业务结果或 `409` + 明确 `errorCode`。

## 管理端与对外 API

1. 管理后台 API 建议使用独立路径前缀（如 `/api/v1/admin/`）或独立网关，鉴权强于开放 API。
2. 禁止将仅内网使用的运维接口暴露到公网；BFF 聚合层不得绕过后端权限校验。

## 限流响应（建议）

触发限流时响应可包含（按项目统一）：`Retry-After`、`X-RateLimit-Limit`、`X-RateLimit-Remaining`；`errorCode` 与 `06-security-authz.md` 一致。

## 版本与兼容

1. 破坏性变更升版本或新路径；固定版本 `oasdiff breaking --fail-on WARN` 进 CI。
2. **字段只增不改语义**：新字段默认可选；禁止在未升版本时改变既有字段含义。
3. 废弃字段走 OpenAPI `deprecated: true`，保留至少一个版本周期；细则见 `05-openapi-contract.md`。
4. 枚举只允许扩展新值，禁止删除或静默改已有枚举含义。
5. `nullable`、`required`、类型变化均属 breaking，须版本策略与迁移说明。
6. API 版本策略（URL `/api/v1`、Header、兼容字段）项目选一种并文档化，禁止混用无说明。
7. 删除接口须有替代方案、下线时间与前端/调用方通知记录。
