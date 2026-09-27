# CODEOWNERS 强制 Review 矩阵

> 路径级模板见 `web-backend/rules/docs/codeowners-guidance.md`。本文按**变更类型**定义必须 Reviewer，适用于 GitHub/GitLab CODEOWNERS 与人工 PR 分配。

## 矩阵

| 改动类型 | 必须 Reviewer | 路径 / 触发示例 |
|---|---|---|
| **OpenAPI / DTO / 错误码** | 后端 Owner + 管理端 Owner（+ 小程序 Owner 若共用契约） | `contracts/**`、`openapi.yaml`、`*Dto.java`、`*VO.java` |
| **DB migration / 手工 SQL** | DBA 或数据 Owner + 后端 Owner | `**/db/migration/**`、`**/flyway/**`、`scripts/sql/**` |
| **鉴权 / 安全模型** | 安全 Owner + 后端 Owner | `**/*Security*`、`**/auth/**`、权限注解、CORS |
| **密钥 / 加密 / Token** | 安全 Owner | `**/*Crypto*`、`**/*Secret*`、JWT 配置 |
| **CI / 发布流水线** | DevOps Owner | `.github/workflows/**`、Jenkinsfile、`Dockerfile` |
| **依赖 / 锁文件 / SBOM** | 领域 Owner + 安全（高危时） | `pom.xml`、`build.gradle*`、`gradle.lockfile`、`package.json`、`pnpm-lock.yaml` |
| **规则包 `rules/**`** | Rules Owner + 架构 | `rules/shared/**`、`rules/evals/**` |
| **公共模块 / Starter** | 架构 Owner + 领域 Owner | `common/**`、`framework/**`、全局拦截器 |
| **生产配置 / 密钥引用** | DevOps + 安全 | `application-prod*`、`helm/**`、`k8s/**` |
| **事件 / MQ 契约** | 平台 Owner + 消费方 Owner | `contracts/events/**`、Consumer/Producer |
| **前端壳层 / 路由 / 全局 store** | 前端架构 Owner | `layouts/**`、`components/layout/**`、`router/**`、`stores/global*` |
| **小程序分包 / 支付 / 隐私** | 小程序 Owner + 合规（若涉及） | `pages.json` 分包、支付、隐私弹窗 |
| **性能 / SLO 预算变更** | 领域 Owner + SRE（若有） | `PERFORMANCE_BUDGET.md`、告警阈值 |
| **数据分级 / PII 新字段** | 安全 + 数据 Owner + 各端 Owner | OpenAPI 敏感标注、导出、日志 |
| **核心业务规则 / 验收条件** | 领域 Owner + 产品 / 需求 Owner | 状态机、计费、审批、取消、补偿、需求追踪矩阵 |
| **生产发布证据 / 高风险灰度** | 发布 Owner + 领域 Owner（高风险加 SRE / 安全） | `release-evidence.yaml`、发布工单、回滚 Runbook |

## 双人规则

1. **高风险**（上表含「安全」行）：至少 **1 领域 Owner + 1 安全或架构**。
2. **跨端契约**：至少 **后端 + 1 消费端** Owner。
3. **>400 行核心逻辑**：建议拆分；无法拆分须第二 Senior Reviewer。

## CODEOWNERS 片段示例

```text
# 契约 — 全栈
/contracts/                    @backend-leads @frontend-leads @miniapp-leads

# 数据
**/db/migration/               @dba-team @backend-leads

# 安全
**/security/                   @security-team @backend-leads

# CI
/.github/workflows/            @devops-team @security-team

# 规则包
/rules/                        @architecture-team @rules-maintainers

# 前端壳层（若业务仓使用 layout/ 单数，请在本地 CODEOWNERS 改写）
/src/layouts/                  @frontend-arch
/src/components/layout/        @frontend-arch
/src/router/                   @frontend-arch
```

业务仓按实际团队替换 `@` 账号。

## PR 模板挂钩

业务仓 PR 模板应含：

- [ ] 已按本矩阵指派 Reviewer
- [ ] 跨端契约变更已 @ 消费端 Owner
- [ ] 安全 / 数据 / 豁免项已链工单或 `docs/exceptions/`

## 相关

- [`definition-of-done.md`](definition-of-done.md)
- [`rule-exception-process.md`](rule-exception-process.md)
- `web-backend/rules/docs/codeowners-guidance.md`
