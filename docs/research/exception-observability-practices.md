# 异常可观测性实践研究：让开发人员仅凭日志定位问题

> 研究日期：2026-09-25
> 研究范围：异常日志、结构化字段、Trace/Correlation ID、4xx/5xx 分级、异常堆栈、参数校验、敏感信息与日志降噪。
> 来源口径：仅采用厂商官方文档、官方代码规约或开放标准的一手资料。本文是研究结论，不是当前规则的替代 SSOT。

## 1. 结论

目标应明确为：**每个失败请求都能用响应中的 `traceId` 在日志中找到至少一条“诊断主事件”；该事件足以判断失败分类、请求位置、代码抛出位置或校验失败字段，并能继续关联整条调用链。**

现有“5xx 打完整堆栈、4xx 按级别记录”的方向正确，但还不足以保证可定位。要达到目标，至少需要同时满足以下条件：

1. 在统一异常边界记录一条结构化诊断事件，包含 `traceId`、`errorCode`、HTTP 状态、请求方法、路径、异常类型等稳定字段。
2. 需要代码定位的异常必须把**异常对象**交给 logger，保留完整 stack trace 和 cause chain，不能只拼 `ex.getMessage()`。
3. 自定义业务异常必须支持 `cause`，跨数据库、RPC、消息等边界包装异常时不得丢失原始原因。
4. 参数校验异常必须单独映射为 4xx，并记录“哪个字段、哪条约束失败”；框架校验栈不能代替字段错误摘要。
5. 5xx 响应保持通用错误信息，堆栈只进入受控日志，不能返回客户端。
6. 同一异常只在具备处理上下文的边界记录一次，避免每层 catch 后重复打印同一堆栈。
7. 对高频、可预期的 4xx 做字段化、限频或采样；但优化前提是仍能按 `traceId` 找到诊断主事件。
8. 请求体、校验失败值、令牌、密码、连接串和个人信息不得原样写日志。

一个关键边界是：**“所有 4xx 都打印完整堆栈”并不是行业共同原则。** 业务代码主动抛出的 `BusinessException` 可以在本仓库基线中采用 `WARN + exception` 来满足抛出行定位；但 Bean Validation、404、认证失败、限流等高频客户端错误，更适合记录结构化失败原因而不是无差别打印框架堆栈。

## 2. 行业共同原则

### 2.1 上下文和异常堆栈缺一不可

阿里巴巴官方 Java 开发规约明确要求异常信息同时包含“上下文信息”和“异常堆栈”，示例将异常对象作为 logger 的异常参数；规约还要求非法参数使用 WARN、系统逻辑错误等重要异常使用 ERROR，并提醒无效和过量日志会降低问题定位效率。[Alibaba Java Coding Guidelines - Logs](https://github.com/alibaba/Alibaba-Java-Coding-Guidelines#logs)

OpenTelemetry 异常日志语义约定将 `exception.type`、`exception.message` 和 `exception.stacktrace` 定义为异常诊断属性；当日志 API 支持直接传异常实例时，建议传异常实例，而不是由应用手工拆字段。这支持“logger 接收异常对象、日志后端提取标准属性”的实现方式。[OpenTelemetry Semantic Conventions for Exceptions in Logs](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/)

因此，只有 `message`、`errorCode` 或一句业务描述不能替代异常对象。它们适合检索和分类，堆栈与 cause chain 才负责代码位置和根因定位。

### 2.2 日志应结构化，关键字段应可查询

Google Cloud 建议应用始终写结构化日志；其日志模型支持 `severity`、`message`、source location、trace、span 等专用字段，并说明异常堆栈应进入可由 Error Reporting 解析的日志字段。[Google Cloud Structured Logging](https://cloud.google.com/logging/docs/structured-logging) [Google Cloud Log Entry Data Model](https://cloud.google.com/logging/docs/log-entry-data-model)

AWS 建议统一日志模式、使用合适的日志级别，并为请求生成 correlation ID；调用下游微服务时继续传播 trace ID，使多个组件的日志能够关联。[AWS Prescriptive Guidance - Logging](https://docs.aws.amazon.com/prescriptive-guidance/latest/performance-engineering-aws/logging.html)

腾讯云 CLS 的官方能力同样建立在结构化采集、字段检索和上下文还原之上；腾讯云应用性能监控说明，日志需输出 `trace_id` 才能与链路关联。[腾讯云 CLS 采集概述](https://cloud.tencent.com/document/product/614/33494) [腾讯云 APM 日志关联常见问题](https://intl.cloud.tencent.com/zh/document/product/248/65513)

因此，异常日志不能只依赖一段自由文本。字段名应稳定，至少保证开发人员可按 `traceId`、`errorCode`、服务、路径、异常类型和版本过滤。

### 2.3 Trace ID 是检索入口，不是诊断内容本身

Google Cloud 要求待关联日志包含相同的 trace 字段，才能把同一请求的日志聚合展示；AWS 也把 correlation ID 的生成与跨服务传播列为应用日志最佳实践。[Google Cloud - Correlate Log Entries](https://cloud.google.com/logging/docs/view/correlate-logs) [AWS Prescriptive Guidance - Logging](https://docs.aws.amazon.com/prescriptive-guidance/latest/performance-engineering-aws/logging.html)

这意味着响应中返回 `traceId` 只是第一步。如果异常处理器没有产生包含相同 `traceId` 的诊断事件，前端给出的 trace ID 仍然无法帮助开发人员定位问题。

### 2.4 4xx 与 5xx 要按语义分类，不能用兜底异常统一变成 500

Spring MVC 官方文档说明，`@Valid @RequestBody` 校验失败会产生 `MethodArgumentNotValidException` 并默认映射为 `400 Bad Request`；方法级校验可能产生 `HandlerMethodValidationException`，应用应覆盖这两种异常。Spring 的默认异常解析表也把参数缺失、类型不匹配、消息不可读和这两类校验异常映射为 400。[Spring MVC Validation](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html) [Spring `@RequestBody`](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/requestbody.html) [Spring DefaultHandlerExceptionResolver](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/servlet/mvc/support/DefaultHandlerExceptionResolver.html)

Microsoft 的 ASP.NET Core 文档同样将模型校验失败作为客户端错误，使用 `ValidationProblemDetails` 表达，并把 400--499 与 500--599 分开处理。[Microsoft - Handle Errors in ASP.NET Core APIs](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api)

因此，校验异常掉进未知异常兜底并返回 500，既会污染服务端错误率，也会让日志展示框架栈而不是业务上“哪个字段不合法”。

### 2.5 日志级别表达运维影响，不应仅由“是否存在异常对象”决定

OpenTelemetry 的异常日志建议按影响分级：未被应用处理的异常使用 ERROR，预期会被应用处理的异常使用 WARN；阿里规约也建议非法参数使用 WARN、系统逻辑错误和重要异常使用 ERROR。OpenTelemetry 该 severity 章节当前仍标记为 Development，因此宜作为分级参考，而不是机械照搬。[OpenTelemetry Exception Log Severity](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/#severity) [Alibaba Java Coding Guidelines - Logs](https://github.com/alibaba/Alibaba-Java-Coding-Guidelines#logs)

这支持如下通用判断：

- 未预期且影响服务正确性的 5xx：`ERROR`，保留完整异常对象。
- 已识别并转换为明确业务响应的异常：通常 `WARN`；若它本来就是正常高频交互，可依据运营语义降为 `INFO` 或采用采样，但不得丢失必要诊断字段。
- 客户端取消等不代表系统故障的异常：可以低于 WARN。

### 2.6 客户端响应与服务端诊断必须分离

Microsoft 明确警告生产环境不能向公众展示详细异常信息，并说明完整错误信息应依赖日志；非开发环境使用统一异常处理生成安全错误载荷。[Microsoft - Handle Errors in ASP.NET Core APIs](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api)

因此，服务端记录完整堆栈与客户端只返回通用文案并不矛盾。正确做法是：客户端得到稳定的 `errorCode` 和 `traceId`，开发人员凭 `traceId` 查到受控日志中的完整诊断信息。

### 2.7 保留 cause chain，并避免重复记录同一异常

阿里官方规约在分层建议中给出 `throw new DAOException(e)` 的包装方式，并建议异常在具备处理上下文的上层记录，而不是 DAO 和上层重复打印；同一规约还要求异常上下文和堆栈同时存在。[Alibaba Java Coding Guidelines - Application Layers](https://github.com/alibaba/Alibaba-Java-Coding-Guidelines#application-layers) [Alibaba Java Coding Guidelines - Logs](https://github.com/alibaba/Alibaba-Java-Coding-Guidelines#logs)

因此，自定义异常应提供 `cause` 构造器并调用 `super(message, cause)`。底层若不能完成恢复或最终分类，应保留 cause 后上抛；统一边界负责输出一次诊断主事件。只有当某层已经完成重试、降级、补偿等独立动作时，该层才应记录自己的动作结果事件。

### 2.8 可定位性不能以泄露敏感信息为代价

AWS 要求日志只保留有用、可行动的数据，禁止直接记录访问令牌、密码、连接串、密钥、支付数据和敏感个人信息；必要数据应删除、掩码、清洗、哈希或加密。Azure Well-Architected Framework 同样要求机密和敏感数据不得出现在日志中，并推荐结构化日志以便统一查询和过滤。[AWS Logging Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/logging-monitoring-for-application-owners/logging-best-practices.html) [Azure Well-Architected - Monitoring and Threat Detection](https://learn.microsoft.com/en-us/azure/well-architected/security/monitor-threats)

异常 message 和 rejected value 也可能包含敏感数据。OpenTelemetry 对 `exception.message` 明确给出敏感信息警告。[OpenTelemetry Exception Log Attributes](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/#attributes)

### 2.9 日志必须可行动，也必须控制噪声

AWS 指出过量日志会影响性能、增加成本，甚至使真正的安全事件被淹没；建议重点记录 4xx/5xx，而生产环境谨慎启用 INFO/DEBUG。阿里规约也要求谨慎记录 INFO 和业务 WARN，避免无效日志妨碍快速定位。[AWS Logging Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/logging-monitoring-for-application-owners/logging-best-practices.html) [Alibaba Java Coding Guidelines - Logs](https://github.com/alibaba/Alibaba-Java-Coding-Guidelines#logs)

因此，“可定位”不等于“越多越好”。应通过日志分级、事件去重、按错误码限频或采样、指标聚合和短期动态调高日志级别来兼顾诊断能力与容量。

## 3. 本仓库建议

以下内容是基于上述共同原则、结合本仓库 Java/Spring 样板目标形成的实施建议，不代表每家厂商都采用完全相同的字段或级别。

### 3.1 建立“每个失败请求一条诊断主事件”的硬约束

统一异常处理器必须为进入响应转换阶段的失败生成一条诊断主事件，并满足：

- 客户端拿到的 `traceId` 与日志中的 `traceId` 完全一致。
- `event`、`errorCode`、`httpStatus`、`method`、`path`、`exception.type` 均为独立可检索字段。
- 需要代码定位的异常把异常对象作为 logger 最后的异常参数，而不是把异常 `toString()` 拼进消息。
- 下游异常经 `BusinessException` 包装时保留 cause，日志可看到 `Caused by` 链。
- 该诊断主事件只打印一次；下层只在执行了独立恢复动作时记录动作事件。

“一条”是最低数量而不是限制调用链日志只能有一条。请求访问日志、SQL 慢日志、RPC 重试日志仍可存在，但必须能通过 trace/span 关联，且不能重复打印同一异常堆栈。

### 3.2 推荐字段模型

| 类别 | 推荐字段 | 要求 |
| --- | --- | --- |
| 事件身份 | `timestamp`、`severity`、`event` | `event` 使用稳定机器名，例如 `business.request.rejected` |
| 服务身份 | `service`、`environment`、`release`/`version`、`instance` | 用于定位哪一版、哪个实例 |
| 链路 | `traceId`、`spanId`、`requestId` | `traceId` 必填；跨 HTTP/MQ 传播 |
| HTTP | `httpStatus`、`method`、`path`/`route` | 优先记录路由模板，避免动态 ID 造成高基数 |
| 错误 | `errorCode`、`exception.type`、`exception.message` | message 先做敏感信息审查；异常类型建议全限定名 |
| 代码定位 | `exception.stacktrace` 或 logger 异常参数 | 业务异常与 5xx 保留；校验错误按下节处理 |
| 业务上下文 | `tenantId`、脱敏后的 `userId`、资源 ID | 仅按白名单记录；不得记录令牌和完整 PII |
| 校验 | `validationErrors[].field`、`constraint`、安全摘要 | 默认不记录 rejected value 和完整请求体 |

`path` 应是无查询串的请求路径或路由模板。Authorization、Cookie、请求体、上传内容、密码、验证码、Token、密钥不得作为通用异常上下文自动记录。

### 3.3 推荐分级矩阵

| 场景 | HTTP | 级别 | 是否默认打印异常堆栈 | 诊断重点 |
| --- | ---: | --- | --- | --- |
| 未知异常、空指针、程序缺陷 | 500 | ERROR | 是 | 完整异常及 cause、traceId、路径、版本 |
| 数据库/RPC/MQ 等失败被包装为业务异常 | 4xx 或 5xx，按真实责任分类 | WARN 或 ERROR | 是 | 包装异常和原始 cause 都必须保留 |
| 应用代码主动抛出的 `BusinessException` | 通常 400/404/409 | WARN | **本仓库基线建议为是** | 直接定位 `throw new BusinessException(...)` 行 |
| Bean Validation / 绑定 / 类型转换失败 | 400 | WARN；高频场景可按错误码降级或采样 | 通常否 | 字段名、约束、路径；框架栈通常没有额外业务价值 |
| 认证失败、禁止访问 | 401/403 | WARN 或安全审计级别 | 通常否 | 主体、资源、策略结果；主体需脱敏 |
| 路由不存在 | 404 | INFO/WARN，视是否异常流量 | 否 | method、path、来源摘要、计数指标 |
| 限流 | 429 | WARN/INFO | 否 | 限流键摘要、策略、阈值、计数指标 |
| 客户端取消请求 | 499 或框架等价值 | DEBUG/INFO | 通常否 | 取消来源、耗时；避免误报服务错误 |

这里对 `BusinessException` 默认打印堆栈，是为了满足本仓库“开发人员直接从日志看到抛出行”的明确目标。若未来某个错误码被证明是高频正常分支，可以通过**显式错误码策略**降级或关闭堆栈，而不是全局取消所有业务异常堆栈。

### 3.4 参数校验应形成独立错误族

建议至少覆盖 Spring MVC 常见输入错误：

- `MethodArgumentNotValidException`
- `HandlerMethodValidationException`
- `ConstraintViolationException`
- `BindException`
- `TypeMismatchException`
- `HttpMessageNotReadableException`
- 缺少请求参数、请求头或请求体的相应异常

它们应转换为稳定的 4xx `errorCode`，例如 `VALIDATION_ERROR`、`MALFORMED_REQUEST`、`TYPE_MISMATCH`。日志事件应记录字段路径、约束名和安全的错误摘要；响应只返回前端需要的字段错误信息，不返回 Java 类名、内部路径或堆栈。

不建议参数校验失败默认打印完整 Spring 框架栈。此时“具体哪里错了”指请求中的哪个字段违反哪条约束，而不是校验框架内部调用到哪一行。若自定义 validator 抛出非预期异常，则它应进入 5xx 路径并打印完整堆栈。

### 3.5 `BusinessException` 必须保留原始异常

异常类型至少应支持以下语义构造方式：

- `errorCode + message`
- `errorCode + message + httpStatus`
- `errorCode + message + cause`
- `errorCode + message + httpStatus + cause`

包装底层异常时不得只复制 `cause.getMessage()`。否则即使全局处理器传入 `BusinessException`，日志也只能看到包装位置，无法还原数据库、RPC 或消息处理的原始失败位置。

同时应审查业务错误的 HTTP 归类：依赖不可用、数据库失败等系统故障不应为了复用 `BusinessException` 而伪装成 400。异常类型、HTTP 状态和日志级别必须表达真实责任方。

### 3.6 客户端安全响应

5xx 响应建议固定为：

- HTTP 500（或准确的 502/503/504）
- `errorCode=INTERNAL_ERROR`（或稳定的网关/依赖错误码）
- 通用用户文案，例如“系统繁忙”
- `traceId`

不得返回 `exception.type`、stack trace、SQL、服务器路径、内部服务地址、数据库信息或 cause message。4xx 可返回对用户有帮助的业务文案和字段错误，但同样不能携带内部堆栈。

### 3.7 日志降噪和容量保护

建议按以下顺序降噪，不能先删除诊断信息：

1. 确保同一异常只在统一边界记录一次。
2. 把 404、认证失败、参数校验等按独立事件分类，避免全都进入 `system.unhandled.failed`。
3. 对高频事件按 `errorCode + route + tenant` 聚合指标并告警。
4. 对已知高频错误码做限频或采样，同时保留计数器和至少部分完整样本。
5. 允许在限定时间、限定服务或限定 trace 上动态开启更详细日志，结束后自动恢复。

不建议直接按“所有 4xx 不记日志”降噪，因为这会重新造成响应有 traceId、日志无对应事件的问题。

## 4. 验收口径

建议后续规则、样板和测试以以下可观察证据验收：

1. **业务异常定位**：触发用户不存在或用户名重复，响应为预期 4xx；使用响应 `traceId` 能找到一条 WARN，包含 `errorCode`、method、path、异常类型，堆栈第一条业务帧指向实际 throw 行。
2. **cause 保留**：模拟数据库或远程调用失败后包装为业务异常，日志包含包装异常和 `Caused by` 原始异常；不存在仅保留 message 的断链。
3. **5xx 安全与定位**：触发未知异常，日志为 ERROR 且包含完整堆栈、cause、路径、`INTERNAL_ERROR`；响应只有通用文案、错误码和 traceId，不含类名或堆栈片段。
4. **校验归类**：请求体字段违反约束时返回 400，不计入 5xx；日志含字段名与约束，不记录密码、令牌、完整请求体和默认 rejected value。
5. **方法级校验**：分别覆盖 `MethodArgumentNotValidException` 与 `HandlerMethodValidationException`，避免只修复一种控制器签名。
6. **一次记录**：同一失败请求的相同异常堆栈只出现一次；下层若有重试日志，应是独立、可区分的动作事件。
7. **链路关联**：HTTP 下游和 MQ 场景中 traceId 可传播；日志平台能按 traceId 聚合同一请求的跨服务事件。
8. **噪声验证**：批量触发校验失败或 404 时，不产生堆栈洪峰；聚合计数仍准确，并可找到抽样或主事件。
9. **敏感信息验证**：自动测试日志输出不含 Authorization、Cookie、密码、Token、连接串和受保护字段值。

## 5. 对当前问题的直接判断

如果全局处理器只对未知异常执行 `log.error(..., ex)`，而 `BusinessException` 仅构造响应，那么它不满足本文定义的可定位目标：`traceId` 没有对应的诊断主事件，业务异常也没有抛出行。若 `BusinessException` 不支持 cause，包装数据库或远程异常后还会永久丢失原始故障位置。

推荐的收口方向是：

- 业务异常：`WARN + 结构化字段 + 异常对象`；
- 未知 5xx：`ERROR + 结构化字段 + 异常对象`；
- 参数校验：独立 4xx 处理，记录字段错误摘要，不默认输出框架堆栈；
- 所有错误响应：携带与日志一致的 `traceId`，5xx 不泄露内部细节；
- 自定义异常：支持 cause，并在最终分类边界只记录一次。

这比简单规定“4xx/5xx 都打堆栈”更接近国内外官方实践，也更直接地服务于“开发人员能从日志看清具体哪里出了问题”的目标。

## 6. 一手来源索引

- [阿里巴巴官方 Java 开发规约（英文 GitBook）](https://github.com/alibaba/Alibaba-Java-Coding-Guidelines)
- [阿里巴巴 P3C 官方仓库](https://github.com/alibaba/p3c)
- [Google Cloud Structured Logging](https://cloud.google.com/logging/docs/structured-logging)
- [Google Cloud Correlate Log Entries](https://cloud.google.com/logging/docs/view/correlate-logs)
- [AWS Prescriptive Guidance - Logging](https://docs.aws.amazon.com/prescriptive-guidance/latest/performance-engineering-aws/logging.html)
- [AWS Logging Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/logging-monitoring-for-application-owners/logging-best-practices.html)
- [Microsoft ASP.NET Core Error Handling](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api)
- [Microsoft ASP.NET Core Logging](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/)
- [Azure Well-Architected Security Monitoring](https://learn.microsoft.com/en-us/azure/well-architected/security/monitor-threats)
- [Spring MVC Validation](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html)
- [OpenTelemetry Exception Log Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/)
- [腾讯云 CLS 采集概述](https://cloud.tencent.com/document/product/614/33494)
- [腾讯云 APM 日志关联常见问题](https://intl.cloud.tencent.com/zh/document/product/248/65513)
