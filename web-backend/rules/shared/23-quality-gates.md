# Quality Gates and CI Rules

用于把规则落到工具、CI 和 Review 阻断级别。规则缺工具时，PR / Codex 最终回复必须明确“项目未配置该门禁”，不得伪造通过。

## 规则到工具映射

| 规则域 | 工具 / 门禁 | 阻断级别 |
|---|---|---|
| 编译与单测 | `mvn verify` / `./gradlew check` | PR 必须阻断 |
| 分层架构 | ArchUnit（见 `examples/archunit`） | PR 必须阻断 |
| Java 风格 | Checkstyle / Spotless / PMD（按项目） | PR 建议阻断 |
| OpenAPI 契约 | openapi-diff / Spectral / contract test | API 变更必须阻断 |
| Flyway 迁移 | `flyway validate` + Testcontainers 或等价真实引擎的多库迁移 | DB 变更必须阻断 |
| SQL 安全 | 扫描 / Review：`${}`、排序白名单、N+1 | PR 必须阻断 |
| 依赖安全 | OWASP Dependency-Check / SCA / license check / SBOM | 高危漏洞必须阻断 |
| Secret 扫描 | gitleaks / trufflehog / CI 等价工具 | PR 必须阻断 |
| 性能回归 | 慢 SQL、关键接口基准、压测报告 | 核心接口建议阻断 |
| 测试稳定性 | flaky rate、隔离清单、重试记录 | Required 用例不得靠重试洗绿 |
| 并发与幂等 | 重复提交、并发更新、消息重放、任务多实例 | 相关写链路必须阻断 |
| 兼容与迁移 | N/N-1、事件 Schema、expand/migrate/contract | 滚动升级 / DB / 事件变更必须阻断 |
| 失败证据 | 测试报告、run/test id、原始输出；有请求上下文时含 traceId | Required 失败须可诊断且脱敏 |
| 容器与运维 | Actuator health/readiness、配置检查 | 发布分支必须阻断 |
| 审计 / 外部调用 | Review + 可选 ArchUnit | 敏感 PR 必须阻断 |
| 集成测试环境 | CI 禁止 `prod`/`pre` 数据源 profile | PR 必须阻断 |
| 生产数据操作 | Runbook + dry-run + 影响行数 + 审批记录 | 生产执行必须阻断 |

## CI 门禁分级

| 级别 | 门禁 | 说明 |
|---|---|---|
| **Required** | `mvn verify` / `./gradlew check` | 含编译、单测；ArchUnit 建议在 verify 内 |
| **Required** | OpenAPI diff / Spectral | 契约 PR 必跑；无 baseline 须在 PR 说明 skip |
| **Required** | Secret scan（gitleaks 等） | PR 必跑 |
| **Conditional** | Flyway validate + 多库迁移 | 仅 DB migration PR；MySQL + PostgreSQL 各一次 |
| **Conditional** | OWASP Dependency-Check / SCA / license | 按合规策略；高危 CVE 阻断 |
| **Optional** | SBOM、container scan、Pact、perf smoke | 平台团队或核心域按需接入 |

样板 job 标注见 `examples/ci/github-actions-backend.yml` 文件头注释；Maven/Gradle 拆分见 `backend-ci-optional.yml` / `backend-ci-optional-gradle.yml` 与 `common-governance/examples/ci/supply-chain-required.yml`；接入清单见 `examples/README.md`。

## CI 基线

1. PR 至少运行 **Required** 项；契约变更加 OpenAPI diff。
2. DB 变更必须跑 Flyway validate（**Conditional**）；多库项目至少 MySQL + PostgreSQL 各跑一次迁移。
3. 生产发布分支必须运行集成测试或 Testcontainers 等价用例。
4. 跳过门禁必须写明原因、风险、owner 与补跑计划（`docs/pull-request-template.md`）。
5. GitHub Actions 样板见 `examples/ci/github-actions-backend.yml`；**仅为参考**，须按项目裁剪；未启用的 job 不得伪造通过（见 `examples/README.md`）。
6. Required 测试失败后重跑通过时，原始失败仍须可见并进入 flaky 治理；禁止 job 内吞掉首次失败后只上报绿色。

## 安全测试分层

1. PR 必跑静态分析、依赖/凭据扫描及高风险接口鉴权、跨租户回归。
2. 存在可部署隔离环境时，高风险 API 按项目威胁模型启用 DAST 或接口模糊测试；未配置须说明适用性与补偿检查。
3. 人工渗透测试按监管要求、风险等级或大版本发布启用，不作为所有日常 PR 的统一门禁。

## Review 必看

- Controller 是否越层访问 Mapper。
- Entity 是否出现在 API body。
- SQL 是否存在注入、N+1、未分页、大事务。
- 是否新增依赖、配置、权限码、错误码、OpenAPI breaking change。
- 敏感操作是否有审计；外部调用是否有超时；大表查询是否有索引策略。
- 测试是否误连生产/预发库。
- 是否存在生产数据修复脚本；若有，是否附 runbook、dry-run、回滚和审批记录。
