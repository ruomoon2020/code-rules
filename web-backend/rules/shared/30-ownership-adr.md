# Ownership and ADR

企业后端的公共能力、跨模块契约和架构决策必须有明确负责人，避免 AI 或个人在局部任务中随意引入长期负担。

## Owner

1. 以下对象必须有 Owner：`common` 公共包、认证授权、异常与错误码、OpenAPI 契约、数据库迁移、消息/任务框架、缓存策略、第三方集成、安全配置。
2. 修改公共对象时须在 PR 描述中写明影响范围，并邀请对应 Owner Review。
3. 未找到 Owner 时，不得直接新增替代实现；先在仓库文档、历史 ADR、模块 README 或团队约定中查找，再提出补位建议。
4. 业务模块内部规则由模块 Owner 负责，跨模块复用不得绕过公共 Owner。

## ADR 触发条件

以下变更需要 ADR 或等价设计记录：

1. 新增框架、中间件、基础设施依赖或替换现有技术栈。
2. 新增跨模块公共抽象、通用 SDK、统一拦截器、AOP、Starter。
3. 对外 API breaking change、认证授权模型变化、多租户模型变化。
4. 数据库分库分表、索引重构、批量回填、跨库迁移策略。
5. 消息、任务、Outbox、分布式锁、缓存一致性方案。
6. 第三方核心集成、支付、短信、实名、风控等有外部 SLA 的能力。
7. 引入 GraphQL、gRPC、WebSocket、SSE 等非 REST 对外范式（见 `33-alternate-api-paradigms.md`）。

## ADR 最小内容

1. 背景与要解决的问题。
2. 已考虑方案与取舍，不少于两个可行选项。
3. 决策结果、影响范围、迁移计划、回滚方案。
4. Owner、Review 人、创建日期、状态：`proposed` / `accepted` / `deprecated`。
5. 与 `05-openapi-contract.md`、`07-persistence-mybatis.md`、`20-dependency-governance.md`、`28-external-integration.md` 的关系。

模板见 `docs/adr/0000-template.md`。

## 废弃与迁移

1. 废弃公共 API / 公共类须标记 `@Deprecated`，给出替代方案、迁移期限和删除版本。
2. 删除前须搜索调用方，提供迁移 PR 或清单。
3. 禁止同时保留两套长期等价能力；若短期并存，必须写清收敛计划。

## AI 生成约束

1. AI 不得在未阅读现有 Owner / ADR / README 的情况下引入新框架、新公共抽象或新全局拦截器。
2. AI 可以提出 ADR 草案，但不得把草案当作已批准结论。
3. AI 修改公共层代码时，回复必须说明影响范围、需要 Owner Review 的对象、未确认的架构假设。
