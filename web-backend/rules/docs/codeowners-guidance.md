# CODEOWNERS 指引（模板）

> GitHub/GitLab 的 CODEOWNERS 由业务仓维护。按**变更类型**的强制 Review 矩阵见 monorepo 根 [`docs/codeowners-matrix.md`](../../../docs/codeowners-matrix.md)。

## 建议强制 Review 路径

| 路径模式 | 原因 |
|---|---|
| `contracts/**`、`openapi/**` | API 契约 |
| `contracts/events/**` | MQ / 事件契约 |
| `rules/**` | AI 规则入口与硬约束 |
| `**/db/migration/**`、`**/flyway/**` | 生产 schema |
| `**/security/**`、`**/*Security*.java` | 鉴权模型 |
| `**/*Crypto*`、`**/*Token*`、`**/*Secret*` | 加密、Token、密钥 |
| `common/**`、`shared-kernel/**` | 公共抽象 |
| `.github/workflows/**` | CI 与供应链 |
| `Dockerfile`、`**/Dockerfile`、`deploy/**`、`helm/**`、`charts/**`、`k8s/**`、`terraform/**` | 云原生运行时与 IaC |
| `**/integration/**`、`**/*Webhook*`、`**/*Consumer*`、`**/*Job*` | 外部攻击面 / MQ / 任务 |

## 实践

1. 至少 1 名领域 Owner + 1 名安全/架构 Reviewer（高风险变更）。
2. 生产数据脚本须额外链接 `31-production-data-ops` 与工单。
3. 超大 PR（如 >400 行核心逻辑）建议拆分，见 `30-ownership-adr.md`。

示例（GitHub，放仓库根 `CODEOWNERS`）：

```text
/contracts/                    @api-team
/contracts/events/             @platform-team @backend-leads
/db/migration/                 @dba-team @backend-leads
/rules/                        @architecture-team @backend-leads
/.github/workflows/            @devops-team @security-team
```
