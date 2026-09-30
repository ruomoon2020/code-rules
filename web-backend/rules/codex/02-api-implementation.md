# API 实现流程

新接口推荐顺序：

```text
1. 更新 contracts/openapi.yaml
2. 定义 Request / Response DTO（或生成）
3. Controller：@Valid、鉴权、调用 Service
4. Application Service：@Transactional、业务逻辑、DTO 映射
5. Mapper / XML：数据访问
6. MockMvc / 集成测试
7. openapi-diff + archunit
```

分页列表须用 MP `Page` + `19-pagination-query` 白名单排序。

错误响应的 `traceId` 必须能关联一条诊断主事件；业务异常、未知 5xx 与参数校验的分级和堆栈策略见 `08-exception-errorcodes.md`、`09-logging-observability.md`、`13-validation.md`。

可重试写操作须在 OpenAPI 声明 `Idempotency-Key` 并在 Service 去重（见 `04`、`18`）。按资源 ID 的接口须做对象级归属校验（见 `06` BOLA/IDOR）。

非 REST 范式（GraphQL/gRPC/WebSocket/SSE）默认禁止，见 `33-alternate-api-paradigms.md`。
