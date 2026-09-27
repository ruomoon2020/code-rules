# 规则成熟度模型（小程序）

DoD × Level 对照：monorepo [`docs/dod-maturity-mapping.md`](../../../docs/dod-maturity-mapping.md)。

团队声明目标 Level，evals 与 CI 按 Level 勾选，避免「规则包全有、业务仓全没」。`00` 的 15 条在各 Level 适用；支付、分包、UGC 等规则在项目实际使用相应能力时即生效，不等待升到 Level 2。

| Level | 适用 | 最低要求 |
|---|---|---|
| **0 — 基线** | 新项目首迭代 | `00` + `05`/`06` + `07`；lint、type-check、build:mp-weixin；request 封装 |
| **1 — 标准** | 上线前 / 对外小程序 | Level 0 + `09`/`14`/`21`/`20`；api:check；size:check；Smoke evals P0 8/8 |
| **2 — 企业** | 支付 / 多分包 / 多环境 | Level 1 + `18` playbook；Full M01–M52；PR 模板；`22`/`23`/`25`/`26`；**Security Extension** 5/5 + Resilience 4/4 + Enterprise Hardening 6/6 + Component Engineering 6/6 + Testing Governance 2/2；`docs/observability-metrics.md`；`docs/release-checklist.md` |
| **3 — 平台** | 多应用 / 多平台 / 集中治理 | Level 2 + `governance-adoption.yaml` Level 3 证据；多环境晋级、统一发布证据、事故演练和跨项目 Scorecard；发版 / 高风险 AI 变更时 AI Tool Safety 5/5 Required |

在 `99-project-local.mdc` 写明：`采纳 Level: 0 | 1 | 2 | 3`。
