# REST API Design Rules

## 资源与动词

1. 资源名复数名词；路径版本前缀 `/api/v1`（按项目约定）。
2. 查询用 `GET`；创建 `POST`；全量更新 `PUT`；部分更新 `PATCH`；删除 `DELETE`。
3. 批量操作：`POST /users/batch-delete` 等，须在 OpenAPI 描述清楚。

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

## 幂等

1. 支付、下单、创建资源等**可重试写操作**须在 OpenAPI 声明 `Idempotency-Key`（HTTP Header）或等价业务幂等键，服务端去重；见 `05-openapi-contract.md`、`18-idempotency-concurrency.md`。
2. `PUT` 按资源 ID 幂等；`POST` 若无幂等键须在文档明确「不可安全重试」。
3. 幂等键建议 TTL ≥ 24h，冲突时返回与原请求一致的业务结果或 `409` + 明确 `errorCode`。

## 管理端与对外 API

1. 管理后台 API 建议使用独立路径前缀（如 `/api/v1/admin/`）或独立网关，鉴权强于开放 API。
2. 禁止将仅内网使用的运维接口暴露到公网；BFF 聚合层不得绕过后端权限校验。

## 限流响应（建议）

触发限流时响应可包含（按项目统一）：`Retry-After`、`X-RateLimit-Limit`、`X-RateLimit-Remaining`；`errorCode` 与 `06-security-authz.md` 一致。

## 版本与兼容

1. 破坏性变更升版本或新路径；OpenAPI diff 进 CI。
2. **字段只增不改语义**：新字段默认可选；禁止在未升版本时改变既有字段含义。
3. 废弃字段走 OpenAPI `deprecated: true`，保留至少一个版本周期；细则见 `05-openapi-contract.md`。
4. 枚举只允许扩展新值，禁止删除或静默改已有枚举含义。
5. `nullable`、`required`、类型变化均属 breaking，须版本策略与迁移说明。
6. API 版本策略（URL `/api/v1`、Header、兼容字段）项目选一种并文档化，禁止混用无说明。
7. 删除接口须有替代方案、下线时间与前端/调用方通知记录。
