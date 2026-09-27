# Gradle 样板（Spring Boot 3.x + ArchUnit + OWASP + Flyway）

> **非可运行模块**：复制到业务仓根目录后改 `rootProject.name`、包名与依赖版本。Maven 等价物见 `../pom-dependencies.sample.xml`、`../scaffold/`。Spring Boot 4.x 项目须先按 `../../shared/20-dependency-governance.md` 完成迁移评估。

## 复制清单

| 样板 | 复制目标 |
|---|---|
| `build.gradle.kts.sample` | `build.gradle.kts`（含 ArchUnit / OWASP / Flyway 样板依赖） |
| `settings.gradle.kts.sample` | `settings.gradle.kts` |
| `../archunit/LayeredArchitectureTest.java` | `src/test/java/.../LayeredArchitectureTest.java` |
| `../scaffold/java/**` | `src/main/java/**`（改包名） |

初始化 wrapper（若尚无）：

```bash
gradle wrapper --gradle-version 8.10
```

## 硬门禁命令

```bash
./gradlew check          # 编译 + 单测 + ArchUnit（test 内）
./gradlew dependencyCheckAnalyze   # 供应链 CI（须已应用 OWASP 插件）
./gradlew flywayValidate           # DB migration CI（须已应用 Flyway 插件）
```

CI 自动识别见 `../ci/backend-ci-required.yml`；供应链见 `common-governance/examples/ci/supply-chain-required.yml` 的 `gradle-dependency-check` job；Gradle Flyway 条件门禁见 `../ci/backend-ci-optional-gradle.yml`。

## 与 Maven 样板对照

| 能力 | Maven | Gradle（本目录） |
|---|---|---|
| 编译 / 单测 | `mvn verify` | `./gradlew check` |
| ArchUnit | `archunit-junit5` test 依赖 | 同左 |
| OWASP SCA | `dependency-check-maven` | `org.owasp.dependencycheck` 插件 |
| Flyway | `flyway-maven-plugin` | `org.flywaydb.flyway` 插件（CI 样板见 `../ci/backend-ci-optional-gradle.yml`） |

脚本名对照：`../package-scripts.sample.json`。
