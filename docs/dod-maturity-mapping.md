# DoD 与采纳成熟度对照（Level 0–3）

> **DoD SSOT**：[`definition-of-done.md`](definition-of-done.md)。**采纳分层 SSOT**：各端 `rules/docs/rule-maturity-model.md`（后端 Level 0–3 最完整）。本文把二者对齐，避免「Level 到了但 DoD 没过」或「DoD 过了但能力未采纳」。

## 六道门禁 × Level

| DoD 门禁 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| **1. 代码** | Required：lint / compile / build / 分层 | + 单测 / ArchUnit 或 views 扫描；测试确定性 | + 并发幂等、兼容迁移、性能预算自检 | + 变异/模糊/混沌等风险专项与跨域门禁 |
| **2. 契约** | OpenAPI SSOT；改 API 须 diff | + 消费端 api:gen / api:check | + 事件契约（若有 MQ） | + 多范式 API 治理（`33`） |
| **3. 安全** | 鉴权 / 输入 / secret scan | + dependency audit；PII 脱敏（`29`） | + 威胁建模；越权测试；供应链 Required | + 密评映射；服务间认证 |
| **4. 数据** | migration validate（若改库） | + 生产数据操作工单（`31`） | + 备份演练；归档策略 | + 冷热分层 / 大规模归档 |
| **5. 可观测** | traceId；无敏感日志 | + 指标 / 错误率观察 | + SLO / 告警 Owner（[`slo-alerting-template.md`](slo-alerting-template.md)） | + 成本 / 容量治理 |
| **6. 发布** | PR 说明 + 可回滚 | + release-checklist 核心项 | + 结构化发布证据、SBOM / attestation、灰度与事故响应 | + 不可变产物多环境晋级、演练与跨项目治理 |

所有 Level 的业务变更都要求需求与验收条件可追溯；Level 2 起生产发布须归档通过校验的 `release-evidence.yaml` 并遵守 [`environment-promotion.md`](environment-promotion.md)，同时提交 90 天内的平台控制快照。生产事故按 [`incident-response.md`](incident-response.md) 留痕和复盘。使用 AI 读取外部内容或调用工具时，各 Level 均须遵守 [`ai-tool-security.md`](ai-tool-security.md) 的行为边界；**AI Tool Safety 5/5 套件**是发版、规则包升级与高风险 AI 变更的条件门禁（见控制目录 `CR-AI-001`），不是业务仓 Level 0 采纳检查。结果由 `validate-ai-eval-results.py` 校验并绑定套件摘要。

Level 2 的平台快照须记录组织 MFA、最小默认权限、主干保护和生产非自审配置；仓内脚本只校验快照结构，发布负责人还须核对平台当前状态。外部标准与内部控制的版本化映射见 [`control-catalog.yaml`](control-catalog.yaml)；映射用于审计追踪，不代表仅凭规则包即可获得标准认证。

**金融 / 政务**：在 Level 1 基础上，Level 2 前须完成 `27`/`29`/`15` 越权与留存，并启用 [`compliance-evidence-log.md`](compliance-evidence-log.md) 留痕。

---

## 后端（Spring Boot）

| Level | DoD 最低集 | CI 样板 | Evals |
|---|---|---|---|
| **0** | 1–2 全绿；3 secret scan；使用 AI 时遵守工具安全行为边界 | `backend-ci-required.yml` | P0 B01–B08 |
| **1** | + 3 audit；5 traceId；PR 模板 | + `supply-chain-required.yml` | Smoke ≥18/21 |
| **2** | 1–6 核心项；数据 / 发版清单；SBOM / attestation；发版时 AI 5/5（若本变更使用 AI） | + `backend-ci-optional.yml`（Maven）或 `backend-ci-optional-gradle.yml`（Gradle）+ `artifact-trust-required.yml` | Security + Business B55–B63；发版 Full |
| **3** | + 镜像扫描 / 事件契约 / 跨项目 Scorecard | 自定义平台 workflow | Full + Contract |

详见 `web-backend/rules/docs/rule-maturity-model.md`。

---

## 管理端（Vue3）

| Level | DoD 最低集 | CI 样板 | Evals |
|---|---|---|---|
| **0** | 1 全绿；2 schema 一致；使用 AI 时遵守工具安全行为边界 | lint + `lint:views-el` | P0 E01–E08 |
| **1** | + 3；5 日志脱敏 | + `api:check` | Smoke 核心 P1 ≥10/12 |
| **2** | + 4–6；性能预算；SBOM / attestation；发版时 AI 5/5（若本变更使用 AI） | + `supply-chain-required.yml` + `artifact-trust-required.yml` | Full P1 ≥39/42；业务 E32–E40；受监管 E44–E49；测试治理 E31/E50 |
| **3** | + RUM / 看板 / 季度演练 | 自定义 | Full + Platform E41–E43 + Enterprise Hardening E44–E49（若适用） |

i18n / 实时 / 富文本 PR 另跑 **Platform Extension** E41–E43（Level 2 起建议 Required）。
金融、政务、高敏数据、第三方脚本或嵌入通信 PR 另跑 **Enterprise Hardening** E44–E49（命中场景时建议 Required）。

详见 `web-front/rules/docs/rule-maturity-model.md`。

---

## 小程序（uni-app）

| Level | DoD 最低集 | CI 样板 | Evals |
|---|---|---|---|
| **0** | 1 全绿；request 封装；使用 AI 时遵守工具安全行为边界 | lint + build:mp-weixin | P0 M01–M08 |
| **1** | + 2 api:check；+ size:check | + api:check | Smoke 核心 P1 ≥10/12 |
| **2** | + 3 隐私；5 指标；6 发版；SBOM / attestation；发版时 AI 5/5（若本变更使用 AI） | + audit；Resilience 套件；`artifact-trust-required.yml` | Full M01–M52；专项套件按场景 |
| **3** | 多平台 / 多环境隔离；跨项目 Scorecard | 自定义 | Full + Security Extension / Hardening 满配 |

详见 `miniapp/rules/docs/rule-maturity-model.md`。

---

## PR 合并判定（简表）

| 变更类型 | 最低 Level | 必过 DoD 节 |
|---|---|---|
| 普通功能 | 0 | 1；若改 API 加 2 |
| 新依赖 | 1 | 1 + 3 + 供应链 CI |
| 权限 / PII | 1 | 1 + 3 + [`data-classification-matrix.md`](data-classification-matrix.md) |
| DB migration | 1 | 1 + 4 |
| 发版 | 2 | 1–6 全勾；豁免须单 |
| 规则包升级 | 维护者 | validate-rules-package + eval manifest + Full evals |

## 相关

- [`definition-of-done.md`](definition-of-done.md)
- [`requirements-traceability.md`](requirements-traceability.md)
- [`business-correctness-review.md`](business-correctness-review.md)
- [`release-evidence.md`](release-evidence.md)
- [`rule-exception-process.md`](rule-exception-process.md)
- `web-backend/rules/docs/compliance-cn-mapping.md`
