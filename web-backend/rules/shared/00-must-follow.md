# Must Follow Rules（后端）

本文件中带编号的 27 条是所有项目在 Level 0 都成立的不变量，违反即拒 PR。高阶能力按文末条件路由启用，不因文件存在就自动成为 Level 0 门禁。

## 架构与分层

1. 依赖方向：`api(Controller)` → `application(Service)` → `domain` → `infrastructure(Mapper)`；禁止反向与跨层短路。
2. **禁止** Controller / Facade 直接注入 `Mapper` / `Repository`。
3. `domain` 禁止依赖 Spring Web、MyBatis、HTTP Client 实现细节。
4. 模块间禁止循环依赖；公共能力放 `common`，业务按 `modules/{bounded-context}` 划分。

## API 与契约

5. 对外 REST 以 **`contracts/openapi.yaml`**（或项目约定 OpenAPI 路径）为 SSOT；改接口先改契约再实现。
6. **禁止**将持久化 `Entity` 作为 REST 请求/响应体；对外仅 `Request` / `Response` DTO。
7. 统一响应包装与错误体见 `08-exception-errorcodes.md`；`errorCode` 与前端约定一致。
8. 分页入参/出参须与 OpenAPI 一致（`page`、`pageSize`、`total`、`records`），见 `19-pagination-query.md`。

## 持久化（MyBatis-Plus）

9. 简单 CRUD 使用 MP `BaseMapper` + `IService`；复杂 SQL 使用 XML，见 `07-persistence-mybatis.md`。
10. **禁止**在 Java 代码中拼接 SQL 字符串；动态条件用 `Wrapper` 或 XML + `#{}`。
11. **禁止**将用户输入直接传入 XML `${}`；排序字段、列名须白名单校验。
12. 写操作事务边界在 **application/service** 层 `@Transactional`；禁止在 Controller 开事务。
13. 多数据库差异仅出现在 **方言 XML / databaseId / Flyway 分库脚本**，禁止 Service 层 `if (mysql)` 分支业务逻辑。

## 安全

14. 默认鉴权；敏感操作须校验明确权限码，禁止仅凭“已登录”放行。
15. 禁止日志、异常信息输出密码、Token、完整证件号、完整请求/响应体。
16. 敏感数据与 PII 只采集业务必需字段；禁止把生产明文数据复制到开发或测试环境。
17. 禁止 SQL 注入；禁止拼接 `order by ${field}` 未经白名单处理。

## 配置与密钥

18. 禁止将生产密钥、AK/SK、数据库密码提交 Git；使用环境变量或配置中心。
19. 生产禁止 `spring.jpa.hibernate.ddl-auto=update` 及等价「自动改表」。

## 工程门禁

20. 提交前运行项目已配置的 `mvn verify` / `./gradlew check`（含 test、checkstyle、archunit 若配置）。
21. 契约变更须 OpenAPI diff / 兼容性 Review；破坏性变更须版本与迁移说明（细则见 `05-openapi-contract.md`）。
22. 新增 / 升级依赖须说明用途，禁止来源不明、无人维护或存在未处置已知高危漏洞的依赖。
23. 通过资源 ID 访问、修改或删除数据时，必须校验对象归属、租户和数据范围（BOLA/IDOR），禁止仅凭“已登录”放行。
24. 禁止根据用户输入 URL 无校验出站请求（SSRF）；Webhook / 回调须限制协议、目标域和内网地址。

## AI 生成

25. 写 Mapper / SQL 前阅读项目 MP 配置、`Mapper` 接口与 XML 既有模式；禁止虚构 MP API。
26. 写字段、DTO 前阅读 OpenAPI；禁止添加契约中不存在的字段。
27. 输出前自检 `10-verification-checklist.md`，报告实际运行与未运行的验证。

## 条件触发路由（不计入 Level 0 硬规则）

以下条款仅在命中对应场景时启用；采纳 Level、必读资产和证据要求见 `docs/rule-maturity-model.md`。

- 多租户 / 数据权限 / 缓存一致性须遵守 `24-data-access-cache.md`。
- 定时任务、批处理、异步补偿须遵守 `25-jobs-scheduling.md`。
- 新增 / 升级依赖时须完成漏洞、许可证、版本锁定和 SBOM 检查（见 `20-dependency-governance.md` 与 common governance 供应链基线）。
- 敏感操作、权限变更、导入导出、生产数据操作须按 `27-audit-log.md` 留存可追溯审计证据。
- 涉及 PII、测试数据或日志 / 缓存 / MQ / 备份留存时须遵守 `29-data-privacy-lifecycle.md`。
- 公共架构、跨模块契约、基础设施依赖须确认 Owner；触发条件满足时须补 ADR（见 `30-ownership-adr.md`）。
- 生产数据修复、手工 SQL、批量回填须有 dry-run、影响行数、审批、回滚或前滚方案与审计（见 `31-production-data-ops.md`）。
- 敏感接口须覆盖未登录、无权限、跨租户、普通用户访问管理员资源等越权测试（见 `06-security-authz.md`、`15-testing.md`）。
- 核心接口、导入导出、批处理须说明性能预算、数据量上限、索引 / count 策略与降级方案（见 `16-performance.md`）。
- 唯一业务约束须数据库唯一索引；大表禁止无条件 `LIKE '%keyword%'`（见 `07-persistence-mybatis.md`）。
- 事务内禁止同步外部 HTTP/MQ；分布式锁须过期时间与释放校验（见 `18-idempotency-concurrency.md`）。
- 外部集成须超时、错误映射、禁止 Controller 直调 SDK（见 `28-external-integration.md`）。
- 测试禁止连接生产/预发库；多库须 Testcontainers 验证迁移（见 `15-testing.md`）。
- 核心链路须有 SLO/降级策略与 RTO/RPO 说明；禁止无熔断地依赖外部服务（见 `32-service-reliability.md`）。
- 禁止未经 ADR 引入 GraphQL、gRPC、WebSocket、SSE（见 `33-alternate-api-paradigms.md`）。
- 大表归档、冷热分层须幂等、防重并明确在线 API 行为（见 `34-data-archival.md`）。
- 登录、权限、支付、导入导出、Webhook、跨租户、PII 等高风险变更须做威胁建模（见 `35-threat-modeling.md`）。
- 禁止自研加密、弱密码哈希、硬编码 secret、弱随机 Token；密钥须可轮换可吊销（见 `36-crypto-key-management.md`）。
- 内部服务、Webhook、MQ、Job 不得只信内网；须有机器身份、签名/Token/mTLS 或等价认证（见 `37-service-to-service-auth.md`）。
- 容器 / K8s / IaC 禁止 latest、root、硬编码密钥、无资源限制的生产配置（见 `38-cloud-native-runtime.md`）。
- MQ / 事件 / Webhook 是契约，须有 schema、version、幂等、死信与重放策略（见 `39-event-contracts.md`）。
- 金额禁止 `double` / `float`；时间须明确时区、格式、边界与账期语义（见 `40-money-time-precision.md`）。
- 字典、枚举、状态码、状态流转禁止静默改语义或绕过状态机（见 `41-dictionary-state-machine.md`）。
- 高成本外部调用、大导出、大查询、长期日志/备份/归档须说明配额、成本、Owner 与清理策略（见 `42-cost-governance.md`）。
- 基于成熟后台平台新增业务时，须复用已有用户、权限、菜单、字典、文件、日志、任务、租户、数据权限、代码生成等公共能力；禁止在业务模块重复实现或污染系统模块（见 `43-business-module-extension.md`）。
