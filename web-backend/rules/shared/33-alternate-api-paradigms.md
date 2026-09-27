# Alternate API Paradigms（GraphQL / gRPC / WebSocket / SSE）

本规则包默认 **REST + OpenAPI** 为对外契约（见 `05-openapi-contract.md`）。

## 默认策略

1. **禁止**在未评审的情况下引入 GraphQL、gRPC、WebSocket、SSE 作为新业务对外接口。
2. AI 不得因「实现方便」在管理后台项目中随手新增上述通信范式。

## 引入前必须

1. 编写 **ADR**（见 `30-ownership-adr.md`），说明：业务场景、为何 REST 不足、安全与运维成本。
2. 明确 Owner；与前端 / 网关 / 移动端消费方对齐。
3. 定义契约与版本策略（schema / proto / 事件格式），禁止无 schema 的随意字段。

## 若引入，须满足

| 范式 | 最低要求 |
|---|---|
| GraphQL | 查询深度/复杂度限制、鉴权 per field、禁止 N+1、生产禁用随意 introspection |
| gRPC | TLS、mTLS 或等价、超时、重试边界、错误码映射、与 REST 网关边界清晰 |
| WebSocket / SSE | 鉴权握手、心跳、断线重连、租户隔离、限流、消息体最小化 |

观测（traceId、指标、日志）与 `09-logging-observability.md` 一致；限流熔断与 `32-service-reliability.md` 一致。
