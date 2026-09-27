# Testing

## 单元测试

1. Service 逻辑 Mock Mapper；覆盖分支与异常。
2. Mapper 复杂 SQL：使用内嵌 DB 或 **Testcontainers**（优先于共享开发库）。
3. 覆盖率阈值由项目覆盖层定义，同时关注新增代码与 statements / branches / functions / lines；排除生成代码等内容须显式配置并说明理由。
4. 覆盖率不代表断言有效。核心计费、状态机、规则引擎等模块可按风险启用变异测试；解析、导入和协议边界可使用属性测试或模糊测试。

## 集成测试

1. Controller 契约优先使用 `@WebMvcTest` / MockMvc 切片测试；跨层流程使用 `@SpringBootTest` + MockMvc 或 `TestRestTemplate`。
2. 使用 **Testcontainers 或等价真实引擎隔离环境**，至少一种数据库与生产一致；多库项目 **每种目标库均须**跑迁移 + 核心 SQL 用例（CI matrix）。
3. 测试数据使用 **fixture / builder / `@Sql`**，禁止依赖共享环境脏数据或执行顺序。
4. **禁止**测试用例依赖 `@Order` 或隐式执行顺序（JUnit 5 默认并行友好）。
5. **禁止**集成测试连接生产或预发数据库；`application-test.yml` 仅指向容器、嵌入式依赖或等价的隔离临时环境。
6. 敏感接口须包含越权测试：未登录、无权限、跨租户、普通用户访问管理员资源（见 `06-security-authz.md`）。
7. Spring Boot 4.x / Spring Framework 6.2+ 项目可优先使用 `MockMvcTester`、`@MockitoBean` 等新测试 API；Boot 3.x 项目保持与当前 Spring Test / Mockito API 兼容。
8. 缓存、消息队列、对象存储和外部服务边界使用容器、stub 或等价临时环境；异步与跨线程用例必须显式等待和清理，不能只依赖测试事务回滚。

## 稳定性与诊断证据

1. 固定时钟、时区、随机种子、网络响应和依赖版本；测试不得依赖机器时序、共享状态或未受控公网服务。
2. flaky test 必须修复；临时隔离须记录原因、Owner、到期日和补跑计划。有限重试只能用于采集证据，不能把首次失败静默改成通过。
3. CI 失败须保留测试报告、原始输出和 run/test id；有请求上下文时同时保留 traceId，涉及容器或中间件时保留对应日志。证据须脱敏并受保留期限约束。
4. 并行执行时，数据库 schema、租户、端口、队列/topic 和业务键必须隔离。

## 并发、幂等与兼容

1. 写操作覆盖重复提交、并发更新、唯一约束冲突和乐观锁失败；可重试请求验证幂等键不会重复产生副作用。
2. 消息和任务覆盖重复投递、乱序、重放、多实例抢占、失败重试和死信恢复；断言最终业务状态与审计记录，而不只断言消息被消费。
3. API、事件和数据库变更覆盖当前版本与上一兼容版本（N/N-1，或项目声明的兼容窗口）；滚动升级期间不得要求所有实例同时切换。
4. 数据库迁移验证目标方言、可重入或明确的失败恢复策略；破坏性变更按 expand/migrate/contract 验证前滚或回滚路径。

## 契约

1. OpenAPI 与 MockMvc 响应结构一致。
2. 改 OpenAPI 须更新测试或契约测。
3. **消费者驱动契约**（推荐）：Spring Cloud Contract / Pact 等，由 `contracts/openapi.yaml` 或契约件驱动前后端/服务间测试；CI 按项目启用，未配置须在 PR 说明。
4. 敏感接口越权用例须与 `06` BOLA/IDOR 场景一致（他人 `id`、跨租户）。
5. MQ 事件、Webhook 和批量文件同样是契约；须验证版本、可空性、枚举扩展、默认值和兼容窗口，不能只验证 JSON 能反序列化。

## ArchUnit

运行 `examples/archunit` 分层规则（Controller 不依赖 Mapper 等）。

## CI 质量门禁

```bash
mvn verify
# 或 ./gradlew check
```

PR 必跑建议包含：

- 单元测试 + 集成测试（多库项目用 Testcontainers 或等价真实引擎隔离环境覆盖每种目标库）
- Checkstyle / Spotless
- ArchUnit
- OpenAPI diff / Spectral
- Flyway validate（各支持库）+ Testcontainers 或等价真实引擎隔离环境
- 变更命中的并发/幂等、N/N-1 或迁移兼容用例

脚本不存在时不得伪造「已通过」。跳过门禁须按 `23-quality-gates.md` 说明原因。

## 测试数据与隐私

1. 测试数据不得含未脱敏的生产 PII（见 `29-data-privacy-lifecycle.md`）。
2. 导出/导入相关测试使用最小 fixture 文件，禁止提交真实业务导出件。
3. 优先 synthetic fixture；若确需生产样本，须完成脱敏、审批、最小化和到期清理。
4. fixture / builder 应可版本化、可重复执行；性能测试数据须达到声明的目标数量级，并记录数据分布。
