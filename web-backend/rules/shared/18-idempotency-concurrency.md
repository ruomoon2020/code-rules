# Idempotency & Concurrency

## 幂等

1. 支付、导入、批量变更须提供幂等键；重复请求返回相同业务结果或明确冲突码。
2. `PUT` 按资源 ID 幂等；`POST` 非幂等须在 OpenAPI 说明是否支持 `Idempotency-Key`。

## 乐观锁

1. 使用 `@Version` 或 MP 乐观锁字段。
2. 冲突统一返回 `CONCURRENT_MODIFICATION`（或项目约定错误码），禁止吞掉后静默覆盖。

## 数据库并发

1. 禁止「先查再插」无唯一约束的并发创建；须**数据库唯一索引** + 捕获 `DuplicateKeyException` 转业务码。
2. 批量更新考虑乐观锁或版本字段，避免丢失更新。

## 事务边界

1. `@Transactional` 仅在 application 层（见 `07`）。
2. **禁止**在事务内同步等待：
   - 外部 HTTP/RPC
   - MQ 发送且无法与 DB 同事务回滚
   - 大批量循环写（须分批提交或异步任务）
3. 本地事务 + 发 MQ / 调第三方：优先 **Outbox / 事务消息**（见 `17-messaging-async.md`）；先提交 DB，再异步投递。
4. 跨库禁止本地 `@Transactional` 假装分布式事务；须 Seata 等显式方案。

## 分布式锁

1. 仅用于**短临界区**；禁止长事务持锁。
2. 必须：过期时间、唯一 `value`（释放时校验持有者）、锁 key 粒度明确。
3. **禁止**锁全局大 key（如 `lock:all_users`）；按业务 ID 或分片 key。
4. 获取锁失败须有明确错误码或重试策略，禁止无限自旋。

## 与外部集成

事务内禁止远程调用细则见 `28-external-integration.md`。
