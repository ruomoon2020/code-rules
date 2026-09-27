# AGENTS.md（Spring Boot 后端）

本仓库为企业级 Spring Boot 后端项目。Codex 必须以 `rules/` 为 AI 规则唯一入口。

## 每次改代码前必读

1. `rules/codex/01-before-editing.md`
2. `rules/shared/00-must-follow.md`

## 实现前命中声明

改代码前，先用 3-8 行说明本轮规则路由；纯问答、只审查不修改时可不声明。

- **任务包**：命中下表哪一行。
- **将读取**：本轮实际会读的 `rules/` 文件路径。
- **不读取及原因**：例如“非成熟后台二开 / 未改 SQL / 未改安全权限”。

未声明即开始写代码，视为未遵守本文件。

## 按任务包追加阅读

先判断属于下表哪一行，只读该行和被点名的细则；不要一次加载全部 `shared/`。
**Level 3 / 窄场景**（多范式 API、归档、密钥、金额时间、状态机、成本）不进主表，只在「路径触发」命中时读取。

| 任务 | 必读规则 |
|---|---|
| 任意后端改动 | `rules/codex/01-before-editing.md`、`rules/shared/00-must-follow.md` |
| 立项 / 架构方案 / 上线评审 | `common-governance/docs/architect-engineering-checklist.md`、`common-governance/docs/definition-of-done.md`、`common-governance/docs/dod-maturity-mapping.md` |
| 需求分析 / 业务 PR / 缺陷修复 | `common-governance/docs/requirements-traceability.md`、`common-governance/docs/business-correctness-review.md` |
| 写 API / Controller / DTO | `rules/shared/04-rest-api-design.md`、`rules/shared/05-openapi-contract.md`、`rules/shared/08-exception-errorcodes.md`、`rules/shared/12-dto-mapping.md`、`rules/shared/13-validation.md`、`rules/shared/19-pagination-query.md`、`rules/codex/02-api-implementation.md` |
| 写持久化 / SQL / 多库 | `rules/shared/07-persistence-mybatis.md`、`rules/shared/19-pagination-query.md`、`rules/docs/sql-dialect-matrix.md`、`rules/codex/03-domain-persistence.md` |
| 领域模型 / 聚合 / Entity 边界 | `rules/shared/11-domain-model.md`、`rules/shared/12-dto-mapping.md` |
| 成熟后台二开 / CRUD / CodeGen / 菜单 / 树表 / 主子表 | `rules/shared/43-business-module-extension.md`、`rules/docs/business-feature-playbook.md`、`rules/shared/06-security-authz.md`、`rules/shared/14-file-import-export.md`、`rules/shared/24-data-access-cache.md`、`rules/shared/25-jobs-scheduling.md`、`rules/shared/27-audit-log.md` |
| 安全 / 权限 / 隐私 / 审计 / 威胁建模 | `rules/shared/06-security-authz.md`、`rules/shared/27-audit-log.md`、`rules/shared/29-data-privacy-lifecycle.md`、`rules/shared/35-threat-modeling.md`、`rules/codex/04-security-integration.md` |
| 集成 / 异步 / Job / MQ / Webhook | `rules/shared/17-messaging-async.md`、`rules/shared/18-idempotency-concurrency.md`、`rules/shared/25-jobs-scheduling.md`、`rules/shared/28-external-integration.md`、`rules/shared/37-service-to-service-auth.md`、`rules/shared/39-event-contracts.md` |
| 平台 / 公共层 / framework / system / generator | `rules/shared/30-ownership-adr.md`、`rules/shared/43-business-module-extension.md`、`rules/docs/adr/0000-template.md` |
| 测试 / 性能 / CI / 依赖 / 配置 | `rules/shared/15-testing.md`、`rules/shared/16-performance.md`、`rules/shared/20-dependency-governance.md`、`rules/shared/21-configuration-secrets.md`、`rules/shared/23-quality-gates.md` |
| 日志 / 可观测 / 发版 / 运维 / 合规 | `rules/shared/09-logging-observability.md`、`rules/shared/22-operability.md`、`rules/shared/31-production-data-ops.md`、`rules/shared/32-service-reliability.md`、`rules/docs/release-checklist.md`、`common-governance/docs/environment-promotion.md`、`common-governance/docs/release-evidence.md` |
| flaky / 测试失败证据 / 并发幂等测试 / N/N-1 / 迁移兼容验证 | `rules/shared/15-testing.md`、`rules/shared/23-quality-gates.md` |
| 生产事故 / 安全事件 / 复盘 | `common-governance/docs/incident-response.md`、`common-governance/docs/incident-postmortem-template.md` |
| AI 生成；读取网页 / Issue / 日志；调用外部工具 | `rules/shared/26-ai-generation.md` |
| 收尾 / Review | `rules/shared/10-verification-checklist.md`、`rules/codex/05-verification.md` |

- 不要读 `rules/cursor/*.mdc`（仅供 Cursor；编号对照见 `rules/docs/cursor-shared-map.md`）。
- 新项目结构见 `rules/docs/scaffold-module-system.md`。
- 合规映射按需追加：`rules/docs/owasp-api-top10-mapping.md`、`rules/docs/compliance-cn-mapping.md`。

## 业务扩展触发词

用户需求或改动中出现以下场景时，必须追加读取 `rules/shared/43-business-module-extension.md` 与 `rules/docs/business-feature-playbook.md`：

- CRUD、业务模块、管理后台、业务表、CodeGen、代码生成、generator。
- 菜单、按钮权限、权限码、字典、导入、导出、树表、主子表。
- 租户、数据权限、部门数据、跨租户、对象级授权。
- RuoYi、RuoYi-Vue-Plus、RuoYi-Cloud-Plus、ruoyi-vue-pro、JeecgBoot、lamp-cloud。

## 路径触发

- 编辑 `**/modules/**`、`**/ruoyi-modules/**`、`**/yudao-module-*/**`、`**/db/migration/**`、`**/sql/**/*menu*.sql` → 追加读取 `43` + `docs/business-feature-playbook.md`。
- 编辑 `**/common/**`、`**/framework/**`、`**/core/**`、`**/starter/**`、`**/system/**`、`**/generator/**`、`**/gen/**` → 追加读取 `43` §公共模块例外 + `30-ownership-adr.md`。
- 编辑 `contracts/openapi.yaml` 或等价契约文件 → 追加读取 `05-openapi-contract.md` + `12-dto-mapping.md`。
- 编辑 `**/domain/**`、`**/model/**`、聚合根或 Entity 边界相关代码 → 追加读取 `11-domain-model.md`。
- 编辑 `Dockerfile`、K8s、IaC、CI、依赖或配置 → 追加读取 `20`、`21`、`23`、`38` 中对应规则。
- 编辑日志 / metric / tracing 相关代码 → 追加读取 `09-logging-observability.md`。
- 编辑全局异常处理器、业务异常、校验异常映射 → 追加读取 `08-exception-errorcodes.md`、`09-logging-observability.md`、`13-validation.md`。
- 编辑 GraphQL / gRPC / 非 REST 入口 → 追加读取 `33-alternate-api-paradigms.md` + `05-openapi-contract.md`。
- 编辑归档 Job、冷热数据迁移 → 追加读取 `34-data-archival.md` + `31-production-data-ops.md`。
- 编辑加密、密钥、KMS、签名校验 → 追加读取 `36-crypto-key-management.md` + `35-threat-modeling.md`。
- 编辑金额、汇率、账单、时区边界、状态机、字典驱动流转 → 追加读取 `40`、`41`。
- 编辑容量配额、成本标签、资源预算 → 追加读取 `42-cost-governance.md` + `16-performance.md`。

## Hard Rules（摘要）

- Controller 禁止直接调用 Mapper。
- 禁止 Entity 作为 API  body；OpenAPI 为先。
- 禁止用户输入进入 SQL `${}`；排序白名单。
- 写操作 `@Transactional` 在 Service 层。
- 多库：方言仅在 XML/databaseId/Flyway，禁止 Service 里按库写业务分支。
- 多租户 / 数据权限不得漏条件；缓存必须有 key、TTL、失效策略。
- 定时任务多实例须防重，重试须幂等。
- 敏感操作须结构化审计；禁止事务内同步外部 HTTP。
- 基于 RuoYi-Vue-Plus / RuoYi-Cloud-Plus 时，日志实现优先复用平台 `@Log`、AOP、事件、登录日志、操作日志、错误日志与监控权限；业务模块禁止重复造公共日志系统。
- 敏感接口须覆盖越权测试；核心接口 / 批处理须说明性能预算与数据量上限。
- 公共架构、依赖、跨模块契约须确认 Owner；触发条件满足时先补 ADR。
- 生产数据修复 / 手工 SQL 必须有 dry-run、影响行数、审批、回滚和审计。
- 高风险安全变更须做威胁建模；密码/Token/签名/密钥禁止弱加密与硬编码。
- 内部服务、Webhook、MQ、Job 不得只信内网；须有机器身份、签名/幂等/审计。
- 金额禁 double/float；时间须明确时区和边界；状态流转不得绕过状态机。
- API breaking / deprecated 遵守 `05`；大表禁止无条件 `%keyword%` 模糊查询。
- 对象级授权（BOLA/IDOR）与 SSRF 出站校验；可重试写操作须幂等键；metric 禁止高基数 label。
- 新增业务默认扩展业务模块，复用平台用户、权限、菜单、字典、文件、日志、任务、租户、数据权限和代码生成能力；禁止重复造公共能力。

## 完成前

```bash
mvn verify
# 或 ./gradlew check
```

详见 `rules/shared/10-verification-checklist.md`。
