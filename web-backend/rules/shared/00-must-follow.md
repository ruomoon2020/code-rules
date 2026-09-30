# 必须遵守的规则（后端）

本文件编号 1 到 28 的条款，所有项目都要遵守，违反就拒绝合并。文末列出的场景规则，只有改到那一类代码时才读，不会因为文件在仓库里，就变成每个项目的合并条件。

默认做法：项目没有另行写明，而且现有表、租户插件、租户拦截器都看不出租户时，查询用 GET、写入用 POST（`GET_POST_COMPAT`），按单租户处理（`NONE`），每张表只由所属模块写入。已经有 `tenant_id`、租户插件或租户拦截器时，沿用共享表加租户列（`SHARED_COLUMN`），不要再做一套租户方案。只有公网接口、要改隔离方式，或者出现跨模块 SQL、消息、定时任务、回写其他模块状态时，才补项目决策。

## 架构与分层

1. 未另行写明时用轻量分层：Controller、应用服务、Mapper，接口对象用 Request / Response（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`）。项目已声明经典分层（`CLASSIC_LAYERED`）或六边形（`DOMAIN_HEXAGONAL`）时，依赖方向须与声明一致。三种分层都禁止反向依赖，也禁止 Controller 直接调用 Mapper。
2. **禁止** Controller / Facade 直接注入 `Mapper` / `Repository`。
3. `domain` 禁止依赖 Spring Web、MyBatis、HTTP Client 实现细节。
4. 模块间禁止循环依赖；公共能力放 `common`，业务放在 `modules/{业务模块}`，例如 `modules/system`。普通增删改查不要再套一层领域边界包。

## API 与契约

5. 对外 HTTP 接口以 **`contracts/openapi.yaml`**（或项目约定 OpenAPI 路径）为 SSOT；通过 `x-api-style` 声明资源型 REST 或 GET/POST 兼容风格，改接口先改契约再实现。
6. **禁止**将持久化 `Entity` / `DO` 作为 REST 请求/响应体；默认对外使用 `Request` / `Response` DTO，显式存量命名可使用职责清晰且与 OpenAPI 一致的 DTO / VO / Query。
7. 统一响应包装与错误体见 `08-exception-errorcodes.md`；`errorCode` 与前端约定一致。
8. 分页入参/出参使用 `page`、`pageSize`、`total`、`records`，`page` 从 1 开始；禁止改用 `pageNo`、`pageNum` 或把第一页写成 0。见 `19-pagination-query.md`。

## 持久化（MyBatis-Plus）

9. **禁止**在 Java 代码中拼接 SQL 字符串；动态条件用 `Wrapper` 或 XML + `#{}`。
10. **禁止**将用户输入直接传入 XML `${}`；排序字段、列名须白名单校验。
11. 写操作事务边界在 **application/service** 层 `@Transactional`；禁止在 Controller 开事务。
12. 多数据库差异仅出现在 **方言 XML / databaseId / Flyway 分库脚本**，禁止 Service 层 `if (mysql)` 分支业务逻辑。

## 安全

13. 默认鉴权；敏感操作须校验明确权限码，禁止仅凭“已登录”放行。密码必须使用带盐慢哈希，禁止自研加密和弱随机认证令牌。
14. 禁止日志、异常信息输出密码、Token、完整证件号、完整请求/响应体。
15. 敏感数据与 PII 只采集业务必需字段；禁止把生产明文数据复制到开发或测试环境。
16. 金额禁止使用 `double` / `float`；使用 `BigDecimal` 或最小货币单位整数，并在字段或契约中写明币种、精度和舍入。
17. 时刻必须携带时区或明确 UTC；自然日使用日期类型，并写明业务时区与闭开区间。禁止用设备或服务器本地时区把无时区时间猜成业务日。
18. 禁止 SQL 注入；禁止拼接 `order by ${field}` 未经白名单处理。

## 配置与密钥

19. 禁止将生产密钥、AK/SK、数据库密码提交 Git；使用环境变量或配置中心。
20. 生产禁止 `spring.jpa.hibernate.ddl-auto=update` 及等价「自动改表」。

## 工程门禁

21. 提交前运行项目已配置的 `mvn verify` / `./gradlew check`（含 test、checkstyle、archunit 若配置）。
22. 契约变更须运行固定版本 `oasdiff breaking --fail-on WARN` 并完成兼容性 Review；破坏性变更须版本与迁移说明。字典、枚举和状态码禁止静默改变已有语义（细则见 `05-openapi-contract.md`）。
23. 新增 / 升级依赖须说明用途，禁止来源不明、无人维护或存在未处置已知高危漏洞的依赖。
24. 通过资源 ID 访问、修改或删除数据时，必须核对这条记录是否属于当前用户，以及数据权限范围（对象级越权，BOLA/IDOR），禁止仅凭“已登录”放行。共享表加租户列、按 schema 隔离或按库隔离时，同时校验租户。单租户（`NONE`）不要再加租户条件。
25. 禁止根据用户输入 URL 无校验出站请求（SSRF）；Webhook / 回调须限制协议、目标域和内网地址。

## AI 生成

26. 写 Mapper / SQL 前阅读项目 MP 配置、`Mapper` 接口与 XML 既有模式；禁止虚构 MP API。
27. 写字段、DTO 前阅读 OpenAPI；禁止添加契约中不存在的字段。
28. 输出前自检 `10-verification-checklist.md`，报告实际运行与未运行的验证。

## 条件触发路由（不计入 Level 0 硬规则）

以下条款仅在命中对应场景时启用；采纳 Level、必读资产和证据要求见 `docs/rule-maturity-model.md`。

`36-crypto-key-management.md` 至 `42-cost-governance.md` 属于 Level 3。弱密码哈希、用浮点数存金额、时刻和日期混用、悄悄改掉已有枚举含义，已经写在上面的编号条款里。下面这些只在遇到密钥、服务之间调用、容器、消息、账期、状态流转或费用时再读。普通增删改查不用先做这些。

- 多租户 / 数据权限 / 缓存一致性须遵守 `24-data-access-cache.md`。
- 定时任务、批处理、异步补偿须遵守 `25-jobs-scheduling.md`。
- 新增 / 升级依赖时须完成漏洞、许可证、版本锁定和 SBOM 检查（见 `20-dependency-governance.md` 与 common governance 供应链基线）。
- 敏感操作、权限变更、导入导出、生产数据操作须按 `27-audit-log.md` 留存可追溯审计证据。
- 涉及 PII、测试数据或日志 / 缓存 / MQ / 备份留存时须遵守 `29-data-privacy-lifecycle.md`。
- 公共架构、跨模块契约、基础设施依赖须确认 Owner；触发条件满足时须补 ADR（见 `30-ownership-adr.md`）。
- 生产数据修复、手工 SQL、批量回填须有 dry-run、影响行数、审批、回滚或前滚方案与审计（见 `31-production-data-ops.md`）。
- 敏感接口须覆盖未登录、无权限、普通用户访问管理员资源。租户模型不是 `NONE` 时另覆盖跨租户（见 `06-security-authz.md`、`15-testing.md`）。
- 核心接口、导入导出、批处理须说明性能预算、数据量上限、索引 / count 策略与降级方案（见 `16-performance.md`）。
- 唯一业务约束须数据库唯一索引；大表禁止无条件 `LIKE '%keyword%'`（见 `07-persistence-mybatis.md`）。
- 事务内禁止同步外部 HTTP/MQ；分布式锁须过期时间与释放校验（见 `18-idempotency-concurrency.md`）。
- 默认的轻量分层由应用服务调用 Mapper 或 Repository。已经在用 MyBatis-Plus `IService` 的旧项目可以继续维护，新代码不要再套一层只做转发的 `IService`。存量经典分层和经过确认的六边形模块，沿用各自已经声明的数据访问方式（见 `01-project-structure.md`、`07-persistence-mybatis.md`）。
- 外部集成须超时、错误映射、禁止 Controller 直调 SDK（见 `28-external-integration.md`）。
- 测试禁止连接生产/预发库；多库须 Testcontainers 验证迁移（见 `15-testing.md`）。
- 核心链路须有 SLO/降级策略与 RTO/RPO 说明；禁止无熔断地依赖外部服务（见 `32-service-reliability.md`）。
- 禁止未经 ADR 引入 GraphQL、gRPC、WebSocket、SSE（见 `33-alternate-api-paradigms.md`）。
- 大表归档、冷热分层须幂等、防重并明确在线 API 行为（见 `34-data-archival.md`）。
- 登录、权限、支付、导入导出、Webhook、跨租户、PII 等高风险变更须做威胁建模（见 `35-threat-modeling.md`）。
- 采用集中密钥治理时，须定义密钥托管、轮换、吊销和审计机制（见 `36-crypto-key-management.md`）。
- 内部服务、Webhook、消息和定时任务不能只因为在内网就信任。要能证明调用方身份，例如签名、Token 或双向 TLS（见 `37-service-to-service-auth.md`）。
- 采用容器 / K8s / IaC 时，须固定镜像版本或摘要，并定义非 root 运行、资源限制和运行时安全上下文（见 `38-cloud-native-runtime.md`）。
- MQ / 事件 / Webhook 是契约，须有 schema、version、幂等、死信与重放策略（见 `39-event-contracts.md`）。
- 涉及结算日、账期关闭或跨期调整等复杂账期时，须定义账期边界、补记 / 重开与审计规则（见 `40-money-time-precision.md`）。
- 聚合存在显式生命周期或受控状态流转时，须定义合法迁移、权限、并发和审计（见 `41-dictionary-state-machine.md`）。
- 高成本外部调用、大导出、大查询、长期日志/备份/归档须说明配额、成本、Owner 与清理策略（见 `42-cost-governance.md`）。
- 基于成熟后台平台新增业务时，须复用已有用户、权限、菜单、字典、文件、日志、任务、数据权限、代码生成等公共能力。平台已启用租户能力时复用该能力，不在业务模块另造租户模型。禁止在业务模块重复实现或污染系统模块（见 `43-business-module-extension.md`）。
