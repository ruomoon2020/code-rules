# 后端工程与 CI 样板

本目录提供可选择复制的架构测试、质量门禁、OpenAPI、数据库迁移、配置和源码样板。路径均相对于后端业务仓根目录。

样板的作用是缩短接入时间，不是替代项目设计。使用前必须明确架构档、构建工具、数据库、权限模型和采纳 Level；复制后需要修改包名、路径、依赖版本、表结构与 CI 条件。

## 推荐使用顺序

1. 在项目本地覆盖层声明架构档、API 风格、持久化栈、租户模式和验证命令。
2. 只选择与项目一致的 ArchUnit、Maven/Gradle、Flyway 和 CI 样板。
3. 接入 OpenAPI baseline 与固定版本的兼容性检查。
4. 将配置、migration 和源码样板改造成项目真实实现。
5. 用故意失败的变更验证 Required Check 确实阻断，再进入正式开发。

## ArchUnit 分层

新项目默认复制 `CRUD_LITE` 测试；只有项目已显式采用存量 Classic 或经 ADR 升级 Hexagonal 时，才复制对应的一份测试到 `src/test/java/...`，按包名修改：

| 架构档 | 样板 |
|---|---|
| `CRUD_LITE` | `archunit/LayeredArchitectureTest.java` |
| `CLASSIC_LAYERED` | `archunit/ClassicLayeredArchitectureTest.java.sample` |
| `DOMAIN_HEXAGONAL` | `archunit/HexagonalArchitectureTest.java.sample` |

禁止同时复制三份后通过改包名或排除规则规避冲突；切换档位须同步 ADR 和依赖迁移。

```bash
mvn test -Dtest=LayeredArchitectureTest
# 或
./gradlew test --tests LayeredArchitectureTest
```

规则：轻量分层禁止 Controller 直接调用 Mapper。经典分层锁定 Web、Service、Manager、DAO 只能从上往下调用。六边形锁定 domain、application 的依赖方向，以及 infrastructure 里的实现方向。

## Checkstyle

复制 `checkstyle/checkstyle-snippet.xml` 片段到项目 Checkstyle 配置。

## CI 样板

**推荐（按成熟度）**：

| 文件 | 复制目标 | 适用 |
|---|---|---|
| `ci/backend-ci-required.yml` | `.github/workflows/backend-ci-required.yml` | Level 0+：verify（Maven/Gradle 自动识别）、固定版本 `oasdiff breaking --fail-on WARN`、secret scan |
| `ci/backend-ci-optional.yml` | `.github/workflows/backend-ci-optional.yml` | Level 1–2：Maven dependency-check、Maven Flyway 多库 |
| `ci/backend-ci-optional-gradle.yml` | `.github/workflows/backend-ci-optional-gradle.yml` | Level 1–2：Gradle Flyway 多库（须应用 Flyway 插件） |

合并版（兼容）：`ci/github-actions-backend.yml` = required + optional。

规则包维护（嵌入 `rules/` 的业务仓）：`ci/rules-package-validate.yml` → `.github/workflows/rules-package-validate.yml`。

### 门禁分级（与 `shared/23-quality-gates.md` 一致）

| 级别 | 建议 job / 工具 |
|---|---|
| **Required** | `mvn verify` / `./gradlew check`（CI 自动识别）、固定版本 `oasdiff breaking --fail-on WARN`、secret scan（gitleaks） |
| **Conditional** | Flyway validate（Maven / Gradle 样板）、OWASP dependency-check（Maven 样板；Gradle 见 `common-governance/examples/ci/supply-chain-required.yml`） |
| **Optional** | SBOM、container scan、Pact、license report、perf smoke — 本仓库样板未包含，按项目另加 workflow |

**跨端供应链 Required**：治理包 `common-governance/examples/ci/supply-chain-required.yml`（npm/pnpm audit + Maven/Gradle OWASP + license-checker）。

**未配置的门禁不得在 PR 中声称已通过**（见 `shared/23-quality-gates.md`）。

## Cursor 规则与本地覆盖

| 文件 | 复制目标 | 说明 |
|---|---|---|
| `cursor/*.mdc` | 业务仓 `.cursor/rules/` | 仅 `00-project-overview.mdc` 建议 `alwaysApply: true` |
| `99-project-local.mdc.sample` | `.cursor/rules/99-project-local.mdc` | 填写真实包名、模块路径、栈与 Level |
| `AGENTS.project-section.md.sample` | 业务仓根 `AGENTS.md` 对应章节 | Codex 使用的默认档 / 显式偏离、API 风格和项目决策；须与 Cursor/OpenAPI 一致 |
| `35-business-module-extension.mdc` | 同上 | RuoYi / Jeecg 二开；非成熟后台可删除或改 globs |
| `36-platform-boundary.mdc` | 同上 | 改 common / system / generator 时触发 |

## PR 模板

复制 `examples/.github/` → 业务仓根目录 `.github/`（含 `pull_request_template.md`）。说明见 `docs/pull-request-template.md`。

## OpenAPI baseline

Monorepo 根已提供 `contracts/openapi.baseline.yaml`，代表最近一次已发布/已接受契约，PR 中不得为了让 diff 归零而提前覆盖。**每次有意接受的契约变更合并后**，由 Owner 更新 baseline：

```bash
cp contracts/openapi.yaml contracts/openapi.baseline.yaml
```

业务仓 CI 从 PR **目标分支**读取已接受的 baseline；删除 baseline 或在改 API 的同一 PR 覆盖 baseline 都会失败。只有契约未变化、baseline 更新为已接受的当前契约时，允许 Owner 单独提交 baseline 提升 PR。首次建立 baseline 须由 Owner 添加 `openapi-baseline-bootstrap-approved` 标签并完成 Code Owner 审核：存量 API 的新 baseline 必须与目标分支契约逐字节一致，仍需对比目标分支 API；全新 API 的 baseline 必须与本次新契约一致。仓库须启用 Code Owner Review 保护；仅有标签不能替代人工批准。规则维护仓的 PR 直接比较目标分支中的 `contracts/openapi.yaml`。

兼容性门禁统一使用固定版本 [oasdiff v1.32.1](https://github.com/oasdiff/oasdiff/releases/tag/v1.32.1)，不复制或维护自研 diff 脚本。业务仓复制 CI 样板即可；本地需 Go 1.26.8+，执行 `go install github.com/oasdiff/oasdiff@v1.32.1`。`--fail-on WARN` 同时阻断 error 和潜在不兼容 warning；尤其要审查 `allOf` / `oneOf`、枚举和客户端行为。主版本升级和 `x-breaking-change` 迁移说明不自动放行；确需接受时，由 Owner 审核并使用工具原生 `--err-ignore` / `--warn-ignore` 文件逐项精确匹配，记录迁移原因与有效版本，发布新 baseline 后删除旧例外。

规则维护仓的 `contracts/oasdiff-approved-v1-to-v2.txt` 和 `contracts/oasdiff-approved-warnings-v1-to-v2.txt` 仅记录示例契约 1.0→2.0 的三项 error、二十六项 warning。CI 核验旧/新版本及迁移元数据；版本不符时例外失效，并要求删除。业务仓默认没有例外文件。上述示例批准不表示真实消费端已验证兼容；业务仓须证明旧客户端迁移后才能沿用类似策略。

`examples/openapi-diff-fixtures/` 保存新增必填 Header、`$ref` 参数类型变化、请求与响应 Schema 类型变化的最小样例。规则维护仓 CI 直接运行固定版本 CLI，核对四类错误码及失败退出码。

## OpenAPI

```bash
# 示例：固定版本的破坏性变更检测
npx --yes --package @redocly/cli@2.14.0 redocly lint contracts/openapi.yaml
go install github.com/oasdiff/oasdiff@v1.32.1
oasdiff breaking --fail-on WARN -- contracts/openapi.baseline.yaml contracts/openapi.yaml
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

SQL 样板在 `shared/31-production-data-ops.md`。执行清单在 `docs/backup-restore-runbook.md`。

## 配置样板

- `config/application-mybatis.sample.yml` — 数据源、MP、Flyway
- `config/MybatisPlusConfig.sample.java` — 分页插件、databaseId
- `config/SecurityConfig.sample.java` — Spring Security 与方法鉴权配置样板
- `pom-dependencies.sample.xml` — Maven 依赖与插件片段
- `mapper/SampleMapper.xml.example` — MyBatis XML 与 `databaseId` 方言语句样板
- `db/migration/mysql/`、`postgresql/` — Flyway 建表示例

MySQL 样板使用 `DEFAULT (UTC_TIMESTAMP(3))`，要求 MySQL 8.0.13+ 的表达式默认值能力；`updated_at` 由应用以 `Instant` 显式写入，不依赖会话时区驱动的 `ON UPDATE CURRENT_TIMESTAMP`。旧版本数据库须改为等价的应用写入或经评审的 UTC 触发器，不得退回服务器本地时区默认值。Connector/J 样板同时设置 UTC connection time zone 并强制同步到 session。

## Java 源码样板

`scaffold/` — `UserController`、`UserService`、`UserMapper`、DTO、MapStruct、`ApiResult`、`GlobalExceptionHandler` 等。复制后改包名。可执行样板默认采用单租户（`NONE`），因此用户、审计、建表脚本和示例 OpenAPI 都不含 `tenant_id` / `tenantId`，也不要求租户上下文。只有业务仓已有 `tenant_id`、租户插件或拦截器时，才按 `SHARED_COLUMN` 在实体、所有查询与写入入口、审计、索引、契约和隔离测试中成套补齐，禁止只改其中一层。`isDeleted` 是逻辑删除过滤列，`deleteToken` 保证未删除用户名唯一，`deletedAt` 只记录删除时间。删除时在同一次更新里写完这三列和 `deletedBy`，不要只调用 `deleteById`。列表和按 ID 的读取、修改、删除调用 `DataScope`，不要只留权限码。创建响应带回初始 `version`。更新成功的响应带回加一后的 `version`。更新和删除带回客户端当前持有的 `version`，与当前行不一致时返回冲突，不要先读出最新版本再覆盖写入。业务时刻用 `Instant` 或 `OffsetDateTime`，只有日期的字段用 `LocalDate`。

## Gradle 样板

`gradle/` — `build.gradle.kts.sample`、`settings.gradle.kts.sample`（Spring Boot + ArchUnit + OWASP dependency-check）。ArchUnit 测试类仍用 `archunit/LayeredArchitectureTest.java`。

## 新建项目

见 `docs/onboarding-new-project.md`、`docs/scaffold-module-system.md`。

全栈目录见仓库根 `docs/monorepo-layout.md`。

## Maven / Gradle 脚本示例

见 `package-scripts.sample.json`（`mvn verify` 与 `./gradlew check` 等价）。
