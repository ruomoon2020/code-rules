# 前端规则成熟度模型（采纳分层）

> `shared/00` 是所有项目的 Level 0 不变量；其他 shared 按任务与 Level 读取。Level 不是文件数量评分，必须有可运行命令、Owner 和回归证据。

`00` 文末的条件触发路由只负责“命中场景时应读什么”，不会把 Level 1–3 或受监管能力变成所有 Level 0 项目的默认门禁。

## 总览

| Level | 目标 | 建议时限 | 最低证据 |
|---|---|---|---|
| **0** | 能安全构建，页面与契约不失真 | 第 1 个迭代 | lint、type-check、build、rules validator |
| **1** | 具备上线所需的权限、测试、错误恢复和依赖治理 | 首次上线前 | api check、核心测试、Smoke eval、回滚说明 |
| **2** | 企业治理与可观测证据闭环 | 核心域 / 企业客户上线前 | E2E、性能预算、数据分级、发布清单、Full eval |
| **3** | 平台化持续治理 | 平台团队持续维护 | 组件兼容策略、视觉回归、SLO 看板、演练记录 |

DoD × Level 全栈对照见 common governance 包 `docs/dod-maturity-mapping.md`；在本 monorepo 中源文件为 `docs/dod-maturity-mapping.md`。

## Level 0：必须接入

**能力**：目录与依赖方向、TypeScript 基线、Base 组件边界、schema SSOT、列表基本状态、基础安全。

| 类型 | 文件 / 资产 |
|---|---|
| 硬规则 | `shared/00-must-follow.md` |
| 工程基础 | `01-project-structure.md`、`02-naming.md`、`03-code-style.md` |
| 页面 / 契约 | `04-ui-patterns.md`、`05-api-contract.md`、`11-base-components-context.md`、`12-schema-ssot.md` |
| 权限 / 安全 | `06-state-route-permission.md`、`07-security-performance.md` |
| AI | `09-ai-generation.md`、`codex/01-before-editing.md` |
| CI | `pnpm lint`、`pnpm type-check`、`pnpm build`、rules validator、views 禁 Element Plus 扫描 |
| Evals | P0 E01–E08（8/8） |

## Level 1：上线基线

**能力**：表单详情、测试、设计 Token、错误恢复、分页竞态、依赖治理、发布回滚。

| 类型 | 文件 / 资产 |
|---|---|
| 业务页面 | `13-form-and-detail.md`、`14-upload-import-export.md`、`19-list-pagination.md` |
| 工程质量 | `08-quality-gates.md`、`15-testing.md`、`20-dependency-governance.md`、`21-error-recovery.md` |
| UI 基础 | `16-design-tokens.md`、`17-shell-navigation.md` |
| CI | `api:check`、核心单测 / 组件测试、依赖检查、包体积基线 |
| PR / 发布 | `docs/pull-request-template.md`、`docs/release-checklist.md` |
| Evals | Smoke：P0 8/8，核心 P1 ≥10/12 |

若基于 RuoYi / Jeecg 等成熟后台持续扩展 CRUD，Level 1 起追加 `22-business-module-extension.md`、frontend playbook 和 Business Extension E32–E40。

## Level 2：企业治理

**能力**：可观测、数据分级展示、性能预算、关键链路 E2E、Owner 与例外治理。

| 类型 | 文件 / 资产 |
|---|---|
| 可观测 | `18-logging-observability.md`、错误率 / 白屏率 / Web Vitals 看板 |
| 数据治理 | `07-security-performance.md` §客户端数据通道 + common governance 数据分级矩阵 |
| 性能 / 测试 | `docs/PERFORMANCE_BUDGET.template.md`、关键路径 E2E、a11y、视觉回归（按项目） |
| 治理 | common governance DoD、豁免、CODEOWNERS、供应链与发布证据 |
| 受监管 Web | 金融、政务、高敏数据或第三方脚本 / 嵌入页面命中时追加 `25-regulated-web-hardening.md` 与 Enterprise Hardening E44–E49 |
| CI | `supply-chain-required.yml`、`artifact-trust-required.yml`（SBOM / attestation） |
| AI | 使用 AI 时遵守工具安全行为边界；发版 / 高风险 AI 变更另跑 **AI Tool Safety 5/5**（EAT01–EAT05） |
| Evals | Full E01–E50：P0 8/8，P1 ≥39/42；相关场景追加专项套件 |

## Level 3：平台化治理

**能力**：Base 组件与 Token 平台化、兼容窗口、持续证据和故障演练。

| 类型 | 最低要求 |
|---|---|
| 组件生命周期 | experimental / stable / deprecated 状态、迁移期和删除版本 |
| 平台变更 | Owner + ADR / 等价设计记录 + 兼容矩阵 + 回滚与消费方回归 |
| 视觉证据 | Storybook 或等价组件目录；核心组件视觉回归（按项目工具） |
| 运行治理 | SLO 看板、规则升级记录、季度复盘和恢复演练 |
| AI | 使用 AI 时继续要求 AI Tool Safety 5/5，并纳入跨项目 Scorecard |

## 推广原则

1. 业务仓在 `99-project-local.mdc` 和根 `AGENTS.md` 声明当前 Level、目标 Level、Owner 与计划迭代。
2. 不因规则包包含某主题就声称项目已采用；命令、配置或证据不存在时必须标记“未配置”。
3. 普通业务团队默认目标 Level 1；核心域和企业客户项目升至 Level 2；Level 3 由平台团队维护。
