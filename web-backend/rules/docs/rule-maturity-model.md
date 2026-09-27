# 规则成熟度模型（采纳分层）

> **与文件编号区分**：`shared/00` 只保存 Level 0 不变量；`shared/01–43` 是按场景读取的正文，不代表全部属于 Level 1；`codex/`、`cursor/` 是索引与触发入口。本文 **Level 0–3** 指企业分阶段采纳节奏，避免新项目被 43 个 shared 一次性压垮。

## 总览

| Level | 名称 | 目标 | 建议时限 |
|---|---|---|---|
| **0** | 必须接入 | 能安全上线、契约一致、分层正确 | 第 1 个迭代 |
| **1** | 推荐接入 | 可观测、测试、依赖、审计、隐私、性能基线 | 第 2–3 个迭代 |
| **2** | 企业治理 | SLO、威胁建模、生产数据、备份演练、合规映射 | 核心域上线前 |
| **3** | 平台化治理 | 成本、云原生、事件契约、归档、状态机、多范式 API | 平台团队 / 多域成熟后 |

**CI 复制**：Level 0 → `backend-ci-required.yml`（Maven/Gradle 自动识别）；Level 1–2 追加 `backend-ci-optional.yml`（Maven）或 `backend-ci-optional-gradle.yml`（Gradle Flyway）+ 根 `supply-chain-required.yml`；维护 `rules/` 时追加 `rules-package-validate.yml`（见 `examples/README.md`）。

行业监管较强（金融、政务、医疗）时：在 Level 0 基础上，**至少**完成 Level 1 的 `27`/`29`/`15` 越权测试，并按 `docs/compliance-cn-mapping.md` 追加 Level 2 项。

---

## Level 0 — 必须接入

**能力**：分层架构、OpenAPI SSOT、鉴权与输入校验、事务与 SQL 安全、统一错误与分页。

| 类型 | 文件 / 资产 |
|---|---|
| 硬规则 | `00-must-follow.md` |
| 结构 | `01-project-structure.md`、`02-naming.md`、`03-code-style.md` |
| API / 契约 | `04-rest-api-design.md`、`05-openapi-contract.md`、`08-exception-errorcodes.md`、`12-dto-mapping.md`、`13-validation.md` |
| 安全基础 | `06-security-authz.md`（鉴权、BOLA、输入；限流可后补） |
| 持久化 | `07-persistence-mybatis.md`、`18-idempotency-concurrency.md`、`19-pagination-query.md` |
| AI | `26-ai-generation.md`（生成边界） |
| Codex | `codex/01-before-editing.md`、`codex/02-api-implementation.md` |
| 契约 | 仓库根 `contracts/openapi.yaml` |
| CI 最低 | `mvn verify` / `./gradlew check`、ArchUnit、`examples/archunit` |
| Evals | **P0** B01–B08（8/8） |

`00` 文末的条件触发路由只负责“命中场景时应读什么”，不会把 Level 2/3 能力变成所有 Level 0 项目的默认门禁。

---

## Level 1 — 推荐接入

**能力**：日志追踪、测试与 CI 映射、依赖治理、配置密钥、导入导出、数据权限、任务与消息基础。

| 类型 | 文件 / 资产 |
|---|---|
| 可观测 | `09-logging-observability.md`、`22-operability.md` |
| 测试 / 门禁 | `15-testing.md`、`23-quality-gates.md` |
| 依赖 / 配置 | `20-dependency-governance.md`、`21-configuration-secrets.md` |
| 领域 / 性能 | `11-domain-model.md`、`16-performance.md` |
| 文件 / 消息 | `14-file-import-export.md`、`17-messaging-async.md` |
| 数据权限 | `24-data-access-cache.md`、`25-jobs-scheduling.md` |
| 审计 / 外部 / 隐私 | `27-audit-log.md`、`28-external-integration.md`、`29-data-privacy-lifecycle.md` |
| **成熟后台二开** | `43-business-module-extension.md`、`docs/business-feature-playbook.md`（**基于 RuoYi / Jeecg 等且持续加 CRUD 时，Level 1 起必读**） |
| Docs | `fullstack-contract.md`、`sql-dialect-matrix.md` |
| CI | OpenAPI diff、secret scan（见 `examples/README.md` 必选清单） |
| PR | `docs/pull-request-template.md`（复制到业务仓） |
| Evals | **Smoke**：B01–B08 + 核心 P1（见 `evals/README.md`，建议 ≥18/21） |

---

## Level 2 — 企业治理

**能力**：Owner/ADR、生产数据操作、SLO 与可靠性、威胁建模与合规对照、发版与事故流程。

| 类型 | 文件 / 资产 |
|---|---|
| 治理 | `30-ownership-adr.md`、`31-production-data-ops.md`、`32-service-reliability.md` |
| 安全高阶 | `35-threat-modeling.md` |
| Docs | `release-checklist.md`、`incident-postmortem-template.md`、`backup-restore-runbook.md`、`PERFORMANCE_BUDGET.template.md`、`owasp-api-top10-mapping.md`、`compliance-cn-mapping.md`、`codeowners-guidance.md` |
| CI | Flyway 多库（若声明多库）、dependency-check（按策略）、`artifact-trust-required.yml`（SBOM / attestation） |
| AI | 使用 AI 时遵守工具安全行为边界；发版 / 高风险 AI 变更另跑 **AI Tool Safety 5/5**（BAT01–BAT05） |
| Evals | **Security** 子集（见 `evals/README.md`）；成熟后台业务 PR 加 **Business Extension** B55–B63；发版前建议 **Full** |

---

## Level 3 — 平台化治理

**能力**：多 API 范式治理、归档、加密与服务间认证、云原生、事件契约、金额时间、状态机、成本。

| 类型 | 文件 / 资产 |
|---|---|
| Shared | `33-alternate-api-paradigms.md`、`34-data-archival.md`、`36`–`42` |
| Cursor | 对照 `docs/cursor-shared-map.md`；Level 3 正文见 shared `33`/`34`/`36`–`42`（Cursor `25`/`26`/`28`–`34`）；威胁建模 `cursor/27`↔shared `35` 属 Level 2 |
| CI 可选 | 容器扫描、Pact、性能冒烟（见 `23-quality-gates.md`）；跨项目 Scorecard |
| Evals | **Contract** 子集 + 全量 **Full**（规则包发版 / 大版本必跑） |

---

## 与 Evals 套件对照

| 套件 | 范围 | 门槛 | 典型场景 |
|---|---|---|---|
| Smoke | B01–B08 + 核心 P1 21 条 | P0 8/8；核心 P1 ≥18/21 | 日常 PR、AI 快速回归 |
| Security | 见 `evals/README.md` | 建议全 Pass | 鉴权/安全/隐私 PR |
| Contract | 见 `evals/README.md` | 建议全 Pass | OpenAPI / 事件契约 PR |
| Business Extension | B55–B63 | 建议 9/9 | 成熟后台新增业务 / CRUD / 树表主子表 PR |
| Full | B01–B67 | P0 8/8；P1 ≥53/59 | 发版、规则包升级、大版本 |

索引提示词：`evals/smoke-prompts.md`（仅索引，正文在 `prompts.md`）。

---

## 推广建议

采纳 Level 与 DoD 六道门禁对照见 monorepo [`docs/dod-maturity-mapping.md`](../../../docs/dod-maturity-mapping.md)。金融 / 政务须配合 [`docs/compliance-evidence-log.md`](../../../docs/compliance-evidence-log.md)。

1. 新项目在 `onboarding-new-project.md` 中声明目标 Level 与计划完成迭代。
2. `adoption-checklist.md` 按 Level 勾选，不必一次勾满。
3. **基于成熟后台平台**（RuoYi / Jeecg 等）的团队：Level 1 起纳入 `43` + playbook；Level 2 前须跑通 **Business Extension** evals。
4. 平台架构团队维护 Level 3 高阶治理；纯业务团队默认目标 Level 1，核心域升至 Level 2。
