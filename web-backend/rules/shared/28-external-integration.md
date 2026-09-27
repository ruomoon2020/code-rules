# External Integration Rules

调用 HTTP API、第三方 SDK、短信/支付/OSS 等外部依赖时的统一约束。

## 分层

1. **禁止**在 Controller 直接调用第三方 SDK 或 `RestClient` / `RestTemplate` / `WebClient`。
2. 外部调用封装在 `infrastructure` 或 `integration` 包；application 层只调端口接口（Port/Adapter 按项目约定）。
3. 新增同步 HTTP 调用优先使用 Spring `RestClient`；异步、流式或响应式场景使用 `WebClient`；已有 `RestTemplate` 可迁移但必须保留统一超时、拦截器、错误映射与观测配置。

## 超时与重试

1. 所有外部调用必须配置 **connect timeout** 与 **read timeout**（禁止默认值无限等待）。
2. 重试仅用于**幂等**读操作或带幂等键的写操作；非幂等 `POST` 默认不重试。
3. 重试须指数退避 + 上限次数；禁止无界重试。

## 韧性

按项目中间件选用：

- 熔断（Circuit Breaker）
- 限流（与 `06-security-authz.md` 对内接口限流区分）
- 降级：返回可理解的业务错误码，禁止把第三方堆栈直接暴露给客户端

## 可观测

1. 传递 `traceId`（HTTP Header 或 MQ 属性，与 `09` 一致）。
2. 记录外部调用：目标服务、耗时、结果码；**禁止**记录请求/响应中的密钥与完整 PII。

## 错误映射

1. 第三方错误码映射为内部 `errorCode`（见 `08-exception-errorcodes.md`）。
2. 对用户暴露统一文案；细节仅进日志（脱敏后）。

## SSRF 防护

1. **禁止**根据用户输入的 URL（Webhook 回调地址、导入文件 URL、图片链接等）直接由服务端发起请求，除非经过严格校验。
2. 出站 URL 须：仅 `https`（按策略）、域名 **白名单**、禁止内网 IP/metadata（`169.254.169.254`、`127.0.0.1`、`10.0.0.0/8` 等）、禁止重定向跳转到内网。
3. Webhook 须签名验证 + 幂等 + 审计（见 `35-threat-modeling.md`、`27-audit-log.md`）。

## 凭证

1. AK/SK、API Key 走配置中心或环境变量（见 `21-configuration-secrets.md`）。
2. 禁止硬编码在源码或提交到 Git。

## 与事务

1. **禁止**在 `@Transactional` 内同步等待外部 HTTP/MQ 完成（见 `18-idempotency-concurrency.md`）。
2. 须外部确认时：先提交本地事务，再通过 Outbox / 异步任务 / Saga 调用（见 `17-messaging-async.md`）。
