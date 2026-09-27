# Examples（硬门禁样板）

业务仓接入参考；路径相对于后端项目根。

## ArchUnit 分层

复制 `archunit/LayeredArchitectureTest.java` 到 `src/test/java/...`，按包名修改。

```bash
mvn test -Dtest=LayeredArchitectureTest
# 或
./gradlew test --tests LayeredArchitectureTest
```

规则：Controller 不依赖 Mapper、不使用 `@Transactional`；domain 不依赖 Spring Web；application 不依赖 api（可按项目调整）。

## Checkstyle

复制 `checkstyle/checkstyle-snippet.xml` 片段到项目 Checkstyle 配置。

## CI 样板

**推荐（按成熟度）**：

| 文件 | 复制目标 | 适用 |
|---|---|---|
| `ci/backend-ci-required.yml` | `.github/workflows/backend-ci-required.yml` | Level 0+：verify（Maven/Gradle 自动识别）、OpenAPI diff、secret scan |
| `ci/backend-ci-optional.yml` | `.github/workflows/backend-ci-optional.yml` | Level 1–2：Maven dependency-check、Maven Flyway 多库 |
| `ci/backend-ci-optional-gradle.yml` | `.github/workflows/backend-ci-optional-gradle.yml` | Level 1–2：Gradle Flyway 多库（须应用 Flyway 插件） |

合并版（兼容）：`ci/github-actions-backend.yml` = required + optional。

规则包维护（嵌入 `rules/` 的业务仓）：`ci/rules-package-validate.yml` → `.github/workflows/rules-package-validate.yml`。

### 门禁分级（与 `shared/23-quality-gates.md` 一致）

| 级别 | 建议 job / 工具 |
|---|---|
| **Required** | `mvn verify` / `./gradlew check`（CI 自动识别）、OpenAPI diff、secret scan（gitleaks） |
| **Conditional** | Flyway validate（Maven / Gradle 样板）、OWASP dependency-check（Maven 样板；Gradle 见 `common-governance/examples/ci/supply-chain-required.yml`） |
| **Optional** | SBOM、container scan、Pact、license report、perf smoke — 本仓库样板未包含，按项目另加 workflow |

**跨端供应链 Required**：治理包 `common-governance/examples/ci/supply-chain-required.yml`（npm/pnpm audit + Maven/Gradle OWASP + license-checker）。

**未配置的门禁不得在 PR 中声称已通过**（见 `shared/23-quality-gates.md`）。

## Cursor 规则与本地覆盖

| 文件 | 复制目标 | 说明 |
|---|---|---|
| `cursor/*.mdc` | 业务仓 `.cursor/rules/` | 仅 `00-project-overview.mdc` 建议 `alwaysApply: true` |
| `99-project-local.mdc.sample` | `.cursor/rules/99-project-local.mdc` | 填写真实包名、模块路径、栈与 Level |
| `35-business-module-extension.mdc` | 同上 | RuoYi / Jeecg 二开；非成熟后台可删除或改 globs |
| `36-platform-boundary.mdc` | 同上 | 改 common / system / generator 时触发 |

## PR 模板

复制 `examples/.github/` → 业务仓根目录 `.github/`（含 `pull_request_template.md`）。说明见 `docs/pull-request-template.md`。

## OpenAPI baseline

Monorepo 根已提供 `contracts/openapi.baseline.yaml`（与当前 `openapi.yaml` 同步）。**每次有意接受的契约变更合并后**，由 Owner 更新 baseline：

```bash
cp contracts/openapi.yaml contracts/openapi.baseline.yaml
```

无 baseline 时 CI 会 skip openapi-diff，须在 PR 说明原因。

## OpenAPI

```bash
# 示例：破坏性变更检测（工具按项目选择）
npx @redocly/cli diff contracts/openapi.yaml contracts/openapi.baseline.yaml
```

## Flyway 多库 CI

Maven 样板见 `ci/backend-ci-optional.yml`；Gradle 样板见 `ci/backend-ci-optional-gradle.yml`（须已应用 `org.flywaydb.flyway` 插件）。对 MySQL、PostgreSQL 各执行：

```bash
mvn -Dflyway.url=... flyway:migrate
# 或
./gradlew flywayValidate -Dflyway.url=...
```

或使用 Testcontainers（见 `15-testing.md`）。

## 危险 `${}` 扫描（可选）

```bash
# 人工审查：禁止未在白名单工具类中的 ${}
rg '\$\{' src/main/resources/mapper
```

## 生产数据修复

- `scripts/data-fix-template.sql` — dry-run、影响行数、备份表、执行与回滚草案。
- `scripts/data-fix-runbook.md` — 工单、Owner、执行窗口、验证与复盘记录。

规则见 `shared/31-production-data-ops.md`。

## 配置样板

- `config/application-mybatis.sample.yml` — 数据源、MP、Flyway
- `config/MybatisPlusConfig.sample.java` — 分页插件、databaseId
- `db/migration/mysql/`、`postgresql/` — Flyway 建表示例

## Java 源码样板

`scaffold/` — `UserController`、`UserService`、`UserMapper`、DTO、MapStruct、`ApiResult`、`GlobalExceptionHandler` 等。复制后改包名。

## Gradle 样板

`gradle/` — `build.gradle.kts.sample`、`settings.gradle.kts.sample`（Spring Boot + ArchUnit + OWASP dependency-check）。ArchUnit 测试类仍用 `archunit/LayeredArchitectureTest.java`。

## 新建项目

见 `docs/onboarding-new-project.md`、`docs/scaffold-module-system.md`。

全栈目录见仓库根 `docs/monorepo-layout.md`。

## Maven / Gradle 脚本示例

见 `package-scripts.sample.json`（`mvn verify` 与 `./gradlew check` 等价）。
