# AGENTS.md（Spring Boot 后端）

本仓库为企业级 Spring Boot 后端项目。Codex 必须以 `rules/` 为 AI 规则唯一入口。

## 每次改代码前必读

1. `rules/codex/01-before-editing.md`
2. `rules/shared/00-must-follow.md`
3. 业务仓根 `AGENTS.md` 里已经写明的架构、对象命名、API、租户，或「数据所有权」声明（若有）

## 改代码前先说明

改代码前，先用 3-8 行说明本轮规则路由；纯问答、只审查不修改时可不声明。

- **这次改动**：对应下表哪一行。
- **将读取**：本轮实际会读的 `rules/` 文件路径。
- **不读取及原因**：例如“非成熟后台二开 / 未改 SQL / 未改安全权限”。

未声明即开始写代码，视为未遵守本文件。

## 按改动类型追加阅读

先判断属于下表哪一行，只读该行和被点名的细则；不要一次加载全部 `shared/`。
少见改动不进主表，只在改到对应文件时再读：GraphQL 等其他接口、归档、密钥生命周期、复杂账期、明确的状态流转、费用。

| 任务 | 必读规则 |
|---|---|
| 任意后端改动 | `rules/codex/01-before-editing.md`、`rules/shared/00-must-follow.md` |
| 立项 / 架构方案 / 上线评审 | `common-governance/docs/architect-engineering-checklist.md`、`common-governance/docs/definition-of-done.md`、`common-governance/docs/dod-maturity-mapping.md` |
| 需求分析 / 业务 PR / 缺陷修复 | `common-governance/docs/requirements-traceability.md`、`common-governance/docs/business-correctness-review.md` |
| 写 API / Controller / DTO | `rules/shared/01-project-structure.md`、`rules/shared/02-naming.md`、`rules/shared/04-rest-api-design.md`、`rules/shared/05-openapi-contract.md`、`rules/shared/08-exception-errorcodes.md`、`rules/shared/12-dto-mapping.md`、`rules/shared/13-validation.md`、`rules/shared/19-pagination-query.md`、`rules/codex/02-api-implementation.md` |
| 写持久化 / SQL / 多库 | `rules/shared/01-project-structure.md`、`rules/shared/07-persistence-mybatis.md`、`rules/shared/19-pagination-query.md`、`rules/docs/sql-dialect-matrix.md`、`rules/codex/03-domain-persistence.md` |
| 全文检索 / 搜索引擎 / 复杂查询 | `rules/shared/19-pagination-query.md`、`rules/shared/20-dependency-governance.md`、`rules/shared/42-cost-governance.md`、`rules/shared/30-ownership-adr.md` |
| 领域模型 / 聚合 / Entity 边界 | `rules/shared/11-domain-model.md`、`rules/shared/12-dto-mapping.md` |
| 成熟后台二开 / CRUD / CodeGen / 菜单 / 树表 / 主子表 | `rules/shared/43-business-module-extension.md`、`rules/docs/business-feature-playbook.md`、`rules/shared/06-security-authz.md`、`rules/shared/14-file-import-export.md`、`rules/shared/24-data-access-cache.md`、`rules/shared/25-jobs-scheduling.md`、`rules/shared/27-audit-log.md` |
| 安全 / 权限 / 隐私 / 审计 / 威胁建模 | `rules/shared/06-security-authz.md`、`rules/shared/27-audit-log.md`、`rules/shared/29-data-privacy-lifecycle.md`、`rules/shared/35-threat-modeling.md`、`rules/codex/04-security-integration.md` |
| 集成 / 异步 / Job / MQ / Webhook | `rules/shared/01-project-structure.md`、`rules/shared/17-messaging-async.md`、`rules/shared/18-idempotency-concurrency.md`、`rules/shared/25-jobs-scheduling.md`、`rules/shared/28-external-integration.md`、`rules/shared/32-service-reliability.md`、`rules/shared/37-service-to-service-auth.md`、`rules/shared/39-event-contracts.md` |
| 平台 / 公共层 / framework / system / generator | `rules/shared/30-ownership-adr.md`、`rules/shared/43-business-module-extension.md`、`rules/docs/adr/0000-template.md` |
| 测试 / 性能 / CI / 依赖 / 配置 | `rules/shared/15-testing.md`、`rules/shared/16-performance.md`、`rules/shared/20-dependency-governance.md`、`rules/shared/21-configuration-secrets.md`、`rules/shared/23-quality-gates.md` |
| 日志 / 可观测 / 发版 / 运维 / 合规 | `rules/shared/09-logging-observability.md`、`rules/shared/22-operability.md`、`rules/shared/31-production-data-ops.md`、`rules/shared/32-service-reliability.md`、`rules/docs/release-checklist.md`、`common-governance/docs/environment-promotion.md`、`common-governance/docs/release-evidence.md` |
| flaky / 测试失败证据 / 并发幂等测试 / N/N-1 / 迁移兼容验证 | `rules/shared/15-testing.md`、`rules/shared/23-quality-gates.md` |
| 生产事故 / 安全事件 / 复盘 | `common-governance/docs/incident-response.md`、`common-governance/docs/incident-postmortem-template.md` |
| AI 生成；读取网页 / Issue / 日志；调用外部工具 | `rules/shared/26-ai-generation.md` |
| 收尾 / 审查 | `rules/shared/10-verification-checklist.md`、`rules/codex/05-verification.md` |

- 不要读 `rules/cursor/*.mdc`（仅供 Cursor；编号对照见 `rules/docs/cursor-shared-map.md`）。
- 没有另行写明时，用轻量分层和 Request / Response（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`），查询用 GET、写入用 POST（`GET_POST_COMPAT`），SQL 只访问本模块的表。普通增删改查不要停下来填决策表。看不出租户时按单租户处理（`NONE`）。表上已有 `tenant_id`，或平台已有租户插件、拦截器时，沿用共享表加租户列（`SHARED_COLUMN`）。公网接口再声明资源型 REST（`RESOURCE_REST`）。要改隔离方式，或出现跨模块写入时，才停下补租户或表归属决策。项目已写明经典分层（`CLASSIC_LAYERED`）时保持原样。改用六边形（`DOMAIN_HEXAGONAL`）时要有复杂度说明和 ADR。
- 新项目结构见 `rules/docs/scaffold-module-system.md`。
- 合规映射按需追加：`rules/docs/owasp-api-top10-mapping.md`、`rules/docs/compliance-cn-mapping.md`。

## 业务扩展触发词

用户需求或改动中出现以下场景时，必须追加读取 `rules/shared/43-business-module-extension.md` 与 `rules/docs/business-feature-playbook.md`：

- CRUD、业务模块、管理后台、业务表、CodeGen、代码生成、generator。
- 菜单、按钮权限、权限码、字典、导入、导出、树表、主子表。
- 租户、数据权限、部门数据、跨租户、对象级授权。
- RuoYi、RuoYi-Vue-Plus、RuoYi-Cloud-Plus、ruoyi-vue-pro、JeecgBoot、lamp-cloud。

## 路径触发

- 编辑 `**/modules/**`、`**/ruoyi-modules/**`、`**/yudao-module-*/**`、`**/sql/**/*menu*.sql` → 追加读取 `43` + `docs/business-feature-playbook.md`。
- 编辑 `**/db/migration/**` → 追加读取 `02-naming.md`、`07-persistence-mybatis.md`、`43-business-module-extension.md` + `docs/business-feature-playbook.md`；逻辑删除、删除唯一标记、索引命名和 UTC 时间默认值以这些规则为准。
- 编辑 `**/common/**`、`**/framework/**`、`**/core/**`、`**/starter/**`、`**/system/**`、`**/generator/**`、`**/gen/**` → 追加读取 `43` §公共模块例外 + `30-ownership-adr.md`。
- 编辑 `contracts/openapi.yaml` 或等价契约文件 → 追加读取 `05-openapi-contract.md` + `12-dto-mapping.md`。
- 编辑 `**/domain/**`、`**/model/**`、聚合根或 Entity 边界相关代码 → 追加读取 `11-domain-model.md`。
- 编辑 `Dockerfile`、K8s、IaC、CI、依赖或配置 → 追加读取 `20`、`21`、`23`、`38` 中对应规则。
- 编辑日志 / metric / tracing 相关代码 → 追加读取 `09-logging-observability.md`。
- 编辑全局异常处理器、业务异常、校验异常映射 → 追加读取 `08-exception-errorcodes.md`、`09-logging-observability.md`、`13-validation.md`。
- 编辑 GraphQL / gRPC / 非 REST 入口 → 追加读取 `33-alternate-api-paradigms.md` + `05-openapi-contract.md`。
- 编辑归档 Job、冷热数据迁移 → 追加读取 `34-data-archival.md` + `31-production-data-ops.md`。
- 编辑加密、密钥、KMS、签名校验 → 追加读取 `36-crypto-key-management.md` + `35-threat-modeling.md`。
- 编辑结算日、账期关闭、跨期调整 → 追加读取 `40-money-time-precision.md`。
- 编辑显式状态迁移、审批流转、字典驱动流转 → 追加读取 `41-dictionary-state-machine.md`。
- 编辑容量配额、成本标签、资源预算 → 追加读取 `42-cost-governance.md` + `16-performance.md`。

## 必须遵守

下面只列 `00-must-follow.md` 里所有项目都要遵守的条款。缓存、定时任务、审计、威胁建模、服务账号、消息契约、账期、状态机，以及在若依一类后台上扩展业务，遇到相应改动再读。文件在仓库里，不代表做普通增删改查时也要做这些。

- 没有写明，而且看不出租户时：轻量分层，Request / Response，查询 GET、写入 POST，单租户，SQL 只访问本模块的表（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`、`GET_POST_COMPAT`、`NONE`）。已有 `tenant_id`、租户插件或拦截器时，沿用共享表加租户列（`SHARED_COLUMN`）。
- Controller 禁止直接调用 Mapper。`domain` 禁止依赖 Spring Web、MyBatis、HTTP Client。
- 禁止 Entity 作为 API body；OpenAPI 为先。分页使用 `page`、`pageSize`、`total`、`records`，`page` 从 1 开始。
- 禁止用户输入进入 SQL `${}`；排序字段走白名单。
- 写操作 `@Transactional` 在 Service 层。多库方言仅在 XML、databaseId、Flyway。
- 默认鉴权并校验权限码。密码使用带盐慢哈希。日志禁止密码、Token、完整证件号和完整请求体。
- 按资源 ID 访问时，要核对这条记录是否属于当前用户，以及数据权限范围。单租户（`NONE`）不要再加租户条件。
- 禁止根据用户输入 URL 无校验出站。Webhook 限制协议、目标域和内网地址。
- 金额禁止 `double` / `float`。时刻带时区或明确 UTC；自然日用日期类型，禁止用本地时区猜业务日。
- 禁止生产密钥进 Git，禁止生产环境自动改表。既有枚举语义不得静默修改。
- 新依赖须说明用途。契约变更先做兼容性 Review。错误码用「领域_原因」，例如 `USER_NOT_FOUND`（`DOMAIN_REASON`）。

## 完成前

```bash
mvn verify
# 或 ./gradlew check
```

详见 `rules/shared/10-verification-checklist.md`。
