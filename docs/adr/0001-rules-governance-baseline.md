# ADR 0001 - Rules Governance Baseline

- **Status**: accepted
- **Date**: 2026-07-28
- **Owner**: `@rules-governance-team`
- **Reviewers**: `@architecture-team`, `@devops-team`, `@security-team`

## Context
本仓库同时维护多端规则包（web-backend / web-front / miniapp）以及跨端治理文档（DoD、成熟度、豁免流程、供应链基线、Owner/Review 矩阵、SLO 与合规留痕等）。

当规则体系发生“重大变更”时，如果缺少统一的决策记录入口，容易出现：
- 变更影响评估不一致（不同团队对 Required/Optional 理解漂移）
- 无法追溯决策原因与替代方案（例如为何选择某项安全门禁为 Required）
- 例外/豁免边界不清（绕过规则的风险不可审计）

因此需要一个根级 ADR（Architecture Decision Record）基线，用于固化治理原则并提升可追溯性。

## Options
### Option A: 仅用文档更新，不记录 ADR
- Pros: 更快
- Cons: 缺少决策可追溯性；重大变更的影响难以审计

### Option B: 仅每个端内记录 ADR
- Pros: 分散治理
- Cons: 跨端原则难以统一；重大变更仍可能造成一致性问题

### Option C: 新增 monorepo 根级 ADR 目录并对重大治理变更落 ADR（Chosen）
- Pros: 跨端一致、决策可追溯、可作为组织级基线资产复用
- Cons: 需要在流程上付出一定开销

## Decision
选择 Option C：
1. 根级 `docs/adr/` 作为治理重大变更的统一决策记录入口。
2. 满足以下任一条件时，要求新增 ADR：
   - 将某类门禁从 Optional 提升为 Required（或反向）
   - 修改豁免/例外边界或审批矩阵的关键条款
   - 修改跨端 SSOT（例如契约生成/校验、DoD SSOT 口径）
   - 修改供应链基线的 SLA/Required 策略（Critical/High/Medium 时限或阻断规则）
3. ADR 必须链路引用现有治理资产：`docs/definition-of-done.md`、`docs/rule-exception-process.md`、`docs/supply-chain-baseline.md`、`docs/codeowners-matrix.md`。

## Impact
- 受影响范围：根级治理文档、根级模板（PR/Issue）、业务团队接入与成熟度推进方法。
- 对变更流程的影响：重大治理变更必须提供 ADR 决策与影响说明，降低理解漂移与审计成本。

## Migration and Rollback
本 ADR 属于治理原则固化，不包含对运行时系统的迁移。
如未来需要调整治理原则：
- 需要新增后续 ADR 进行“演进决策”，而非直接覆盖历史记录
- 旧规则/旧口径的过渡期以豁免流程或迁移窗口文档为准

## Follow-up
- 为后续 ADR 准备目录索引（可在 `docs/README.md` 中扩展 ADR 条目）。
- 明确“重大变更”判定的模板化说明（可复用根级 PR 模板的风险等级与契约影响字段）。

