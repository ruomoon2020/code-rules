# Messaging & Async（可选）

1. `@Async` 须有线程池配置与异常处理。
2. 跨服务使用 MQ 时：消费幂等、死信队列、可观测 traceId 传递。
3. **本地事务 + 发 MQ**：推荐 Outbox 表或事务消息；禁止在 `@Transactional` 内同步 `send` 后假设一定成功（见 `18-idempotency-concurrency.md`）。
4. 禁止在事务**未提交**前发送不可回滚的副作用（邮件、第三方扣款等），除非架构明确「先发后补偿」且有对账。
5. 定时任务、批处理与补偿任务见 `25-jobs-scheduling.md`。
6. 外部 HTTP 调用不得放在事务内同步等待，见 `28-external-integration.md`。

未使用 MQ 的项目可跳过 MQ 相关条目；事务与外部调用边界仍适用。
