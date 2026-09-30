# Spring Boot 后端研发规则包

版本见 `VERSION`，变更见 `CHANGELOG.md`，发版见 `RELEASE.md`。

本规则包面向 **Spring Boot 3.x + Java 17+ + MyBatis-Plus** 业务系统，覆盖 API 契约、模块边界、事务、权限与数据范围、持久化、多数据库、审计、可靠性、质量门禁和成熟后台二开。

支持 **MySQL、PostgreSQL** 等多数据库，方言 SQL 与迁移脚本分治。Spring Boot 4.x 项目可以复用架构、安全、契约与治理原则，但必须先完成依赖兼容性、Jakarta EE 版本和迁移评估；未验证 MyBatis-Plus、Springdoc、插件和 CI 前，不得直接把 3.x 基线改为 4.x。

## 使用后应达到的结果

- 业务模块边界明确，普通业务不污染 `common`、`framework`、`system` 或 generator。
- OpenAPI、DTO、权限码、错误码、分页、时间和金额口径保持一致。
- 鉴权、租户、数据权限、审计和对象级授权覆盖所有读写路径。
- 事务、幂等、并发、消息和外部调用的失败路径可恢复、可测试。
- 构建、测试、契约、迁移和安全门禁有真实执行证据；业务正确性另行人工评审。

- **Codex**：`codex/AGENTS.md` → 复制到后端仓库根目录 `AGENTS.md`
- **Cursor**：`cursor/*.mdc` → 复制到 `.cursor/rules/`
- **SSOT**：`shared/`；Cursor 摘要指向 shared，不重复全文
- **测试治理**：`shared/15-testing.md` 覆盖确定性、失败证据、并发幂等与兼容迁移；具体阈值和条件工具由项目覆盖层声明

## 首次接入

1. 将本目录整包放入后端业务仓 `rules/`。
2. 复制 `codex/AGENTS.md` 到根 `AGENTS.md`，复制 `cursor/*.mdc` 到 `.cursor/rules/`。
3. 从 `examples/99-project-local.mdc.sample` 和 `examples/AGENTS.project-section.md.sample` 建立项目覆盖层。
4. 明确架构档、API 风格、持久化栈、租户模式、OpenAPI 路径、构建命令和采纳 Level。
5. 按需接入 ArchUnit、Checkstyle、固定版本 `oasdiff breaking --fail-on WARN`、Flyway 和 CI 样板。
6. 运行规则包校验与项目构建，并用一个真实业务 PR 验证权限、契约和门禁链路。

新项目完整步骤见 `docs/onboarding-new-project.md`，成熟后台业务开发见 `docs/business-feature-playbook.md`。

## 规则层级

```text
L0  shared/00-must-follow.md
L1  shared/01–43
L2  codex/*.md、cursor/*.mdc
```

使用原则：**不要一次加载全部规则**。AI 先读 L2 入口，再按任务 / 路径 / 关键词读取少量 shared 全文，最后由 CI 与 evals 兜底。

```text
Cursor alwaysApply 概览
  → Cursor 按路径 / Codex 按改动类型
  → 按需读取 shared 全文
  → mvn verify / ./gradlew check / evals / PR checklist
```

## 部署到业务仓

### 方式 A：整包复制（最简单）

1. 整包 `rules/` 放入后端仓库（submodule 或子目录）。
2. 复制 `codex/AGENTS.md` → 根 `AGENTS.md`。
3. 复制 `cursor/*.mdc` → `.cursor/rules/`。
4. 与前端共享 `contracts/openapi.yaml`（见 `docs/fullstack-contract.md`）。
5. 接入 `examples/` 中 ArchUnit、Checkstyle、固定版本 `oasdiff breaking --fail-on WARN`。

业务仓目录示例：

```text
your-backend/
├─ AGENTS.md                    # 复制自 rules/codex/AGENTS.md
├─ rules/                       # 整包
├─ .cursor/rules/*.mdc          # 复制自 rules/cursor/
├─ contracts/openapi.yaml       # API 契约 SSOT
├─ src/main/java/...
└─ pom.xml / build.gradle
```

### 方式 B：submodule / 子树

适合多个项目共用同一套规则。要求：

1. `rules/` 在业务仓内路径稳定。
2. 根 `AGENTS.md` 能引用 `rules/codex/AGENTS.md` 中的路径。
3. `.cursor/rules/` 中的 `.mdc` 要能访问 `rules/shared/...`。
4. 升级规则包后运行 `python rules/scripts/validate-rules-package.py`。

## Codex 怎么用

Codex 入口是业务仓根目录 `AGENTS.md`。

推荐问法：

```text
新增 CRM 客户模块，RuoYi-Vue-Plus 二开，按 rules/shared/43 + playbook。
只改 OpenAPI 和 Controller，按 05 + 04。
改 common 拦截器，按 43 公共模块例外 + 30 ADR。
联调前端页面，按 fullstack-contract §新增业务功能。
```

Codex 路由逻辑：

1. 每次改代码先读 `codex/01-before-editing.md` + `shared/00-must-follow.md`。
2. 再按 `AGENTS.md` 的改动类型、触发词、路径追加读取。
3. 写完按 `shared/10-verification-checklist.md` + `codex/05-verification.md` 收尾。

不要要求 Codex 通读全部 shared。改动较大时，先让它说明这次改动对应哪一类，以及准备读取哪些规则。

## Cursor 怎么用

Cursor 入口是 `.cursor/rules/*.mdc`。

只建议 `cursor/00-project-overview.mdc` 使用 `alwaysApply: true`。其他规则靠 `globs` 按文件路径触发。

关键路由：

| 场景 | Cursor 规则 |
|---|---|
| 普通 API / Controller | `04-rest-controller.mdc`、`08-exception-logging.mdc`、`09-security-authz.mdc` |
| 业务模块 / CRUD / 菜单 SQL | `35-business-module-extension.mdc` |
| `common` / `framework` / `system` / `generator` | `36-platform-boundary.mdc` |
| OpenAPI 契约 | `12-openapi-contract.mdc` |
| MyBatis / Mapper XML | `06-persistence-mybatis.mdc` |

其余 Cursor 场景及完整文件名见 `docs/cursor-shared-map.md`；该表同时给出每个 `.mdc` 对应的 shared 正文，禁止按编号猜映射。

不要把所有 `.mdc` 设成 `alwaysApply: true`。如果业务仓不是 RuoYi / Jeecg 类成熟后台，可以不复制 `35`，或把它的 globs 改成真实业务包路径。

## 业务仓本地覆盖层

规则包是通用规则。真实项目建议额外加一层很薄的本地约定。

根 `AGENTS.md` 可追加：

```md
## 本项目约定

- 业务模块路径：`src/main/java/com/acme/modules/{biz}/`
- 成熟后台栈：RuoYi-Vue-Plus 5.x
- 采纳 Level：1（见 `rules/docs/rule-maturity-model.md`）
- 新增 CRUD 默认跑 evals Business Extension B55–B63
```

`.cursor/rules/99-project-local.mdc`：复制 `examples/99-project-local.mdc.sample`，按项目改路径、技术栈、采纳级别和测试参数。没写明、也看不出租户时，用轻量分层和 Request / Response，查询用 GET、写入用 POST，按单租户处理，SQL 只访问本模块的表（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`、`GET_POST_COMPAT`、`NONE`）。已有 `tenant_id`、租户插件或拦截器时，沿用共享表加租户列（`SHARED_COLUMN`）。普通增删改查不用先填决策表。只有旧项目的经典分层、复杂业务的六边形、公网接口、要改隔离方式，或要写其他模块的表时，才在根 `AGENTS.md` 和项目规则里写明差异。

本地覆盖层只写项目路径、技术栈、采纳 Level，不要复制 `00` 或 `43` 全文。

## 业务研发流程

```text
需求与验收条件
  → 领域 / 状态 / 权限 / 数据影响分析
  → OpenAPI 与数据库变更设计
  → Controller / Application / Domain / Persistence 实现
  → 正常、失败、并发、越权和兼容测试
  → 构建、契约、迁移和安全门禁
  → 人工业务正确性 Review
```

Review 时必须单独检查流程状态、事务与回滚、租户和数据范围、BOLA/IDOR、字段映射、排序与分页、金额和时区、旧客户端兼容以及发布回滚。CI 绿色只能证明相应工具通过，不能替代这些判断。

### 成熟后台新增业务模块

适用于 RuoYi-Vue-Plus / RuoYi-Cloud-Plus / ruoyi-vue-pro / JeecgBoot 等二开项目。

1. 先确认平台能力：用户、角色、菜单、权限、字典、文件、日志、任务、租户、数据权限、CodeGen。
2. 业务只进业务模块，禁止为单业务污染 `common` / `framework` / `system` / `generator`。
3. 先改 `contracts/openapi.yaml`，再写 DTO / Controller / Service / Mapper。
4. CodeGen 只作为初稿；生成后补权限、审计、数据权限、索引、错误码、测试。
5. list / detail / export / delete / batch / job 都要一致校验数据权限和 BOLA。租户模型不是 `NONE` 时租户条件也一致。
6. 树表 / 主子表额外检查父子归属、循环关系、事务回滚和孤儿数据。非 `NONE` 时再检查跨租户。
7. 后端完成后按 `docs/fullstack-contract.md` 与前端联调。

必读：

- `shared/43-business-module-extension.md`
- `docs/business-feature-playbook.md`
- `shared/06-security-authz.md`
- `shared/24-data-access-cache.md`
- `shared/27-audit-log.md`

### 普通 API / Controller

1. 先改 OpenAPI。
2. Request / Response DTO 不复用 Entity。
3. 分页字段与 `19-pagination-query.md` 一致。
4. 错误体带 `errorCode`、`traceId`。
5. 写操作事务在 Service 层。

必读：`04`、`05`、`08`、`12`、`13`、`19`。

### 公共层 / generator 变更

只在平台级能力变更时允许。必须有：

- Owner
- ADR
- 兼容策略
- 迁移脚本
- 回滚方案
- 回归用例

必读：`30-ownership-adr.md`、`43-business-module-extension.md`、`docs/adr/0000-template.md`。

## 验证与回归

日常改动：

```bash
mvn verify
# 或
./gradlew check
```

规则包一致性：

```bash
python rules/scripts/validate-rules-package.py
```

AI 行为回归：

| 场景 | 套件 |
|---|---|
| 日常 PR | Smoke |
| 安全 / 权限 / 隐私 | Security |
| OpenAPI / 事件契约 | Contract |
| 成熟后台业务扩展 | Business Extension B55–B63 |
| 发版 / 规则包升级 | Full |

## 持久化栈（本包默认）

| 项 | 约定 |
|---|---|
| ORM | MyBatis-Plus 3.x |
| 复杂 SQL | MyBatis XML（`resources/mapper/**`） |
| 多库 | `databaseId` + `mapper/dialect/{mysql,postgresql}/` |
| 迁移 | Flyway（`db/migration/`，可按库分子目录） |
| 分页 | MP `Page` / `IPage`，与 OpenAPI 对齐 |

## 完整文件清单

| 文件 | 职责 |
|---|---|
| `shared/00-must-follow.md` | 硬规则 |
| `shared/01-project-structure.md` | 包结构与依赖 |
| `shared/02-naming.md` | 命名 |
| `shared/03-code-style.md` | Java 风格与注释 |
| `shared/04-rest-api-design.md` | REST 设计 |
| `shared/05-openapi-contract.md` | OpenAPI SSOT |
| `shared/06-security-authz.md` | 安全与权限 |
| `shared/07-persistence-mybatis.md` | MyBatis-Plus、XML、多库 |
| `shared/08-exception-errorcodes.md` | 异常、错误码、cause 与 4xx/5xx 分类 |
| `shared/09-logging-observability.md` | traceId 可检索的结构化诊断主事件 |
| `shared/10-verification-checklist.md` | 收尾检查 |
| `shared/11-domain-model.md` | 领域与 Entity |
| `shared/12-dto-mapping.md` | DTO / MapStruct |
| `shared/13-validation.md` | Bean Validation |
| `shared/14-file-import-export.md` | 导入导出 |
| `shared/15-testing.md` | 测试 |
| `shared/16-performance.md` | 性能 |
| `shared/17-messaging-async.md` | 消息与异步（可选） |
| `shared/18-idempotency-concurrency.md` | 幂等与并发 |
| `shared/19-pagination-query.md` | 分页与排序白名单 |
| `shared/20-dependency-governance.md` | 依赖治理 |
| `shared/21-configuration-secrets.md` | 配置与密钥 |
| `shared/22-operability.md` | 可运维性 |
| `shared/23-quality-gates.md` | 质量门禁 / CI 映射 |
| `shared/24-data-access-cache.md` | 数据权限 / 多租户 / 缓存 |
| `shared/25-jobs-scheduling.md` | 定时任务 / 批处理 |
| `shared/26-ai-generation.md` | AI 生成、不可信内容与工具安全约束 |
| `shared/27-audit-log.md` | 审计日志 |
| `shared/28-external-integration.md` | 外部 HTTP / 第三方 |
| `shared/29-data-privacy-lifecycle.md` | 隐私与数据生命周期 |
| `shared/30-ownership-adr.md` | 架构归属 / ADR |
| `shared/31-production-data-ops.md` | 生产数据操作 / 手工 SQL |
| `shared/32-service-reliability.md` | SLO / 降级 / RTO·RPO / 故障演练 |
| `shared/33-alternate-api-paradigms.md` | GraphQL/gRPC/WS/SSE 引入约束 |
| `shared/34-data-archival.md` | 归档与冷热分层 |
| `shared/35-threat-modeling.md` | 威胁建模 |
| `shared/36-crypto-key-management.md` | 加密与密钥管理 |
| `shared/37-service-to-service-auth.md` | 服务之间的调用身份 |
| `shared/38-cloud-native-runtime.md` | 容器 / K8s / IaC 运行时 |
| `shared/39-event-contracts.md` | MQ / 事件契约 |
| `shared/40-money-time-precision.md` | 金额 / 时间 / 精度 |
| `shared/41-dictionary-state-machine.md` | 字典 / 枚举 / 状态机 |
| `shared/42-cost-governance.md` | 成本治理 |
| `shared/43-business-module-extension.md` | 成熟后台业务模块扩展 |
| `docs/backup-restore-runbook.md` | 备份恢复 Runbook 模板 |
| `evals/*` | AI 行为回归 B01–B71；`ai-tool-safety.md` 独立门禁 BAT01–BAT05 |
| `docs/owasp-api-top10-mapping.md` | OWASP API Top 10 映射 |
| `docs/compliance-cn-mapping.md` | 国内合规对照 |
| `docs/release-checklist.md` | 发版检查清单 |
| `docs/incident-postmortem-template.md` | 事故复盘模板 |
| `docs/codeowners-guidance.md` | CODEOWNERS 指引 |
| `docs/rule-maturity-model.md` | 采纳分层 Level 0–3 |
| `docs/cursor-shared-map.md` | Cursor 文件号 ↔ shared 正文对照（编号不相等） |
| `docs/enterprise-governance.md` | 独立规则包的治理入口 |
| `docs/migration-from-template.md` | 从后端模板迁移到业务仓的边界与步骤 |
| `docs/pull-request-template.md` | 业务仓 PR 模板 |
| `docs/contributing-rules-package.md` | 规则包维护者变更治理 |
| `scripts/validate-rules-package.py` | 规则包一致性校验（evals 计数、门槛、smoke 索引） |
| `scripts/README.md` | 校验脚本说明 |
| `examples/99-project-local.mdc.sample` | 业务仓 Cursor 本地覆盖样板 |
| `examples/ci/rules-package-validate.yml` | 业务仓 rules/ 一致性校验 workflow |
| `examples/scaffold/` | Java 源码样板（system 用户域） |
| `examples/*` | ArchUnit、Checkstyle、CI、配置、Flyway、POM 依赖样板；生产数据修复 SQL 见 `shared/31-production-data-ops.md` |
| `docs/fullstack-contract.md` | 前后端契约（含新增业务功能全栈表） |
| `docs/sql-dialect-matrix.md` | 方言 SQL 登记 |
| `docs/onboarding-new-project.md` | 新项目落地步骤 |
| `docs/scaffold-module-system.md` | system 模块目录样板 |
| `docs/adr/0000-template.md` | ADR 模板 |
| `docs/PERFORMANCE_BUDGET.template.md` | 性能预算模板 |
| `docs/business-feature-playbook.md` | 新增业务功能落地流程 |
| `docs/rules-package-index.md` | shared 规则索引（维护者） |
| `cursor/*.mdc` | Cursor 触发摘要（编号≠shared；对照 `docs/cursor-shared-map.md`） |
| 仓库根 `contracts/openapi.baseline.yaml` | OpenAPI CI diff 基线 |
| 仓库根 `docs/monorepo-layout.md` | 全栈 monorepo 布局 |

## Evals

**P0 8/8**，**P1 至少 57/63**（B09–B71），AI Tool Safety **BAT01–BAT05 5/5**。日常 **Smoke**、发版 **Full**；安全/契约/架构/业务扩展 PR 可跑对应子集（见 `evals/README.md`、`evals/smoke-prompts.md`）。

## 采纳与 PR

- 分阶段接入：`docs/rule-maturity-model.md`
- 业务仓 PR：复制 `examples/.github/` → 仓库根 `.github/`（或见 `docs/pull-request-template.md`）
- 改规则包：`docs/contributing-rules-package.md`；发版前运行 `python scripts/validate-rules-package.py`

## CI 样板说明

`examples/ci/github-actions-backend.yml` 标注 **Required / Conditional / Optional**；须按项目裁剪（见 `examples/README.md`、`23-quality-gates.md`）。

本 monorepo 改 `web-backend/rules/**` 时，CI 自动运行 `scripts/validate-rules-package.py`（见仓库根 `.github/workflows/validate-rules-packages.yml`）。**未接入的工具不得伪造「已通过」**。
