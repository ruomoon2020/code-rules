# 新建 Spring Boot 项目落地指南

> 维护者与架构 onboarding；AI 日常读 `README.md`、`codex/AGENTS.md`。

## 0. 选择成熟度目标

按 `docs/rule-maturity-model.md` 声明目标 **Level**（建议：首个迭代 Level 0，核心域上线前 Level 1–2）。不必一次接入全部 43 个 shared 文件。

同时声明项目画像，二选一：

| 画像 | 默认读取 | 不默认启用 |
|---|---|---|
| 绿场 / 普通 Spring API | Level 0 + 实际命中场景规则 | `43`、CodeGen、RuoYi / Jeecg 菜单与系统模块约定 |
| 成熟后台二开 | Level 0–1 + `43` + business playbook | 重复实现平台已有的用户、权限、字典和日志能力 |

本包技术边界是 Spring Boot + MyBatis-Plus。JPA / jOOQ、NestJS、Go 项目只能复用通用治理资产，不应直接套用本包的持久化和分层实现细则。

## 1. 复制规则包

```text
your-backend/
├─ AGENTS.md                 ← rules/codex/AGENTS.md
├─ rules/                    ← 整包 web-backend/rules
├─ contracts/openapi.yaml    ← 可与 monorepo 根 contracts/ 同步
├─ .cursor/rules/*.mdc
└─ src/main/java/...
```

## 2. 推荐技术选型

- Java 17+、Spring Boot 3.x（默认基线）；Spring Boot 4.x 仅在依赖、插件、CI、运行环境完成迁移评估后采用
- MyBatis-Plus 3.x + Flyway
- 数据库：MySQL 8、PostgreSQL 15（按环境启用）
- MapStruct、Springdoc/OpenAPI、ArchUnit、Testcontainers

版本策略：

1. Spring Boot 版本由 Boot BOM / Gradle plugin 统一管理，禁止在业务模块散落覆盖 Spring 管理的依赖版本。
2. 从 3.x 升到 4.x 前，先跑 `spring-boot-properties-migrator` 或等价配置迁移检查；迁移完成后移除迁移依赖。
3. 升级 PR 必须说明 Jakarta EE / Servlet / Validation / Persistence 相关兼容性，以及 MyBatis-Plus、Springdoc、测试插件是否支持目标版本。

## 3. 最小包结构

见 `docs/scaffold-module-system.md`，先落地 `modules/system` 一个域。

## 4. 源码与配置样板

- `examples/scaffold/` — common + `modules/system` Java 与 Mapper XML
- `examples/pom-dependencies.sample.xml` — Maven 依赖参考
- `examples/gradle/` — Gradle（`build.gradle.kts.sample`、OWASP / ArchUnit）
- `examples/config/application-mybatis.sample.yml`
- `examples/config/MybatisPlusConfig.sample.java`
- `examples/config/SecurityConfig.sample.java`
- `docs/backup-restore-runbook.md`、`docs/PERFORMANCE_BUDGET.template.md`

## 5. 硬门禁接入

1. `examples/archunit/LayeredArchitectureTest.java` → `src/test/java`
2. `mvn verify` / `./gradlew check` 进 CI（`examples/ci/backend-ci-required.yml` 自动识别构建工具）
3. OpenAPI diff（契约 PR 必跑）
4. Flyway：MySQL + PostgreSQL 各跑迁移（若声明多库；Maven 样板见 `examples/ci/backend-ci-optional.yml`，Gradle 样板见 `examples/ci/backend-ci-optional-gradle.yml` 且须接 Flyway 插件）

## 6. 与前端联调

1. 共用 `contracts/openapi.yaml`
2. 后端先发兼容版本 → 前端 `api:gen`
3. 对齐 `traceId`、`errorCode`、分页字段（`docs/fullstack-contract.md`）

## 7. 验证

- `evals/adoption-checklist.md` 按目标 Level 勾选
- 日常：**Smoke**（`evals/smoke-prompts.md`）；发版：**Full** B01–B67（P0 8/8，P1 ≥53/59）
- 成熟后台新增业务：优先跑 **Business Extension** B55–B63（建议 9/9）
- 业务仓 PR：复制 `rules/examples/.github/` → 仓库根 `.github/`
- 契约 baseline：首次稳定后生成 `contracts/openapi.baseline.yaml` 供 CI diff（见 `examples/README.md`）
- 企业级 DoD / 豁免 / 接入验收：monorepo `docs/definition-of-done.md`、`docs/enterprise-governance.md`、`scripts/check-project-adoption.py`
