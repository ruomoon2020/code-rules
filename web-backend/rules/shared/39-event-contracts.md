# Event and Message Contracts

消息、事件、Outbox、Webhook 也是契约，须像 REST/OpenAPI 一样治理版本、兼容和观测。

## 契约内容

1. 每个 Topic / Queue / Event 必须定义：eventName、version、producer、consumer、schema、Owner、保留时间。
2. 消息 schema 放在项目约定目录（如 `contracts/events/`），禁止无 schema 的随意 Map。
3. 字段命名、枚举、时间、金额规则与 REST DTO 一致。
4. 消息体最小化；禁止塞完整 PII、密码、Token、无必要的大对象。

## 兼容策略

1. 事件字段只增不改语义；新增字段默认可选。
2. 删除字段、改类型、改枚举语义、改 eventName 均视为 breaking change，须版本与迁移。
3. producer 升级前须确认 consumer 兼容窗口；必要时双写新旧事件。
4. 死信消息、重放消息必须使用同一幂等规则，避免重复副作用。

## Outbox 与重放

1. Outbox 表须记录 eventId、eventName、version、aggregateId、status、retryCount、lastError。
2. 重放须有 runbook、范围、审批、幂等校验和审计。
3. 消息消费失败须进入死信或可恢复状态，禁止只打印日志后丢弃。

## AI 生成约束

1. AI 新增 MQ / 事件 / Webhook 时，必须同时给出 schema、版本、幂等、死信、重放策略。
2. AI 不得建议“先发 JSON，字段后面再对齐”。
