# 日志与可观测规则

与前端 `18-logging-observability.md` 字段对齐。

## 结构化字段

| 字段 | 说明 |
|---|---|
| `event` | `domain.resource.action.result` |
| `traceId` | 请求链路，MDC + 响应头回传 |
| `userId` / `tenantId` | 按项目 |
| `durationMs` | 慢接口 |
| `errorCode` | 业务错误 |
| `httpStatus` / `method` / `path` | HTTP 失败分类；path 不含 query，优先路由模板 |
| `exceptionType` | 异常全限定名；需要代码定位时同时把异常对象交给 logger |
| `validation` | `field:constraint` 安全摘要，不含 rejected value |

使用 SLF4J + Logback；禁止 `System.out`。

## 平台日志底座

若项目基于 RuoYi-Vue-Plus / RuoYi-Cloud-Plus 或等价成熟后台平台：

1. 日志标准以本规则包为准；实现层优先复用平台已有 `@Log`、AOP、事件发布、登录日志、操作日志、错误日志与监控权限。
2. 业务模块禁止重复实现公共 `LogAspect`、`LogService`、登录日志、操作日志、错误日志表。
3. 平台默认字段不足时，只允许在公共日志模块做兼容扩展，例如补齐 `traceId`、`tenantId`、`userId`、`durationMs`、`errorCode`。
4. 业务代码只补充模块名、动作、资源 ID、结果摘要；不得在 Controller 手写散落式日志代替公共能力。

## 分布式追踪

1. 优先对齐 **W3C Trace Context**（`traceparent` / `tracestate`）；与网关、前端、MQ 保持一致。
2. `Filter` 或 Micrometer Tracing / OpenTelemetry 注入；缺失时生成。
3. 业务 `traceId` 写入 MDC 与响应头；出站 HTTP/MQ **必须**传递（见 `fullstack-contract.md`）。

## 异常诊断主事件

1. 每个失败请求至少有一条与响应 `traceId` 一致的结构化诊断主事件；只有 traceId、没有错误事件，不算可观测。
2. 未知 5xx：`ERROR + exception`；应用代码主动抛出的业务 4xx：`WARN + exception`；参数校验 4xx：记录字段与约束，默认不打印框架堆栈。
3. 同一异常只在最终分类边界打印一次堆栈；下层只有执行了重试、降级、补偿等独立动作时才记录自己的动作事件。
4. 高流量 4xx 先按 `errorCode + route` 聚合指标，再按明确策略限频或采样；禁止直接取消所有 4xx 日志。

## 指标与健康（RED）

| 信号 | 指标示例 |
|---|---|
| Rate | QPS、消费速率 |
| Errors | 5xx 率、业务 `errorCode` 率 |
| Duration | P95/P99 延迟 |

1. 暴露 Actuator：`health`、`info`（见 `22-operability.md`）。
2. 核心接口须接入监控；SLO 与燃尽率告警见 `32-service-reliability.md`。
3. **禁止**将高基数维度作为 metric label（如裸 `userId`、`orderId`、未归一化 `uri`），避免时序库爆炸。

## 禁止

- 密码、Token、完整证件号、完整 body。
- 生产 DEBUG 默认关闭。
