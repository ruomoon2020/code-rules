# Backup & Restore Runbook（企业模板）

> 与 `shared/31-production-data-ops.md`、`shared/32-service-reliability.md`（RTO/RPO）配合使用。复制到业务仓 `docs/` 并按环境填写。

## 1. 范围与 RTO / RPO

| 系统 / 库 | RPO | RTO | 备份 Owner |
|---|---|---|---|
| 示例：业务 MySQL | 15 min | 2 h | @dba |

## 2. 备份策略

| 类型 | 频率 | 保留周期 | 加密 | 存储位置 |
|---|---|---|---|---|
| 全量 | 每日 | 30 天 | 是 | |
| 增量 / binlog | 持续 | 7 天 | 是 | |

## 3. 恢复演练

1. **频率**：至少每季度一次（核心系统建议每月）。
2. **环境**：独立演练库，禁止直接覆盖生产。
3. **步骤**：恢复备份 → 校验行数 /  checksum / 核心接口冒烟 → 记录耗时与问题。
4. **未演练不得**在合规/对外材料中声称「具备恢复能力」。

## 4. 生产恢复审批

1. 工单：背景、影响、执行人、Reviewer、回滚方案。
2. 恢复窗口与业务通知。
3. 恢复后校验清单（见 §6）。

## 5. 恢复到非生产

1. **必须脱敏**（见 `29-data-privacy-lifecycle.md`）；禁止把生产 PII 原样导入开发 fixture。
2. 网络隔离：非生产库不得被公网访问。
3. 审计：谁申请、谁批准、数据来源与时间范围。

## 6. 恢复后校验清单

- [ ] 核心表行数 / 抽样与预期一致
- [ ]  Flyway schema 版本与代码匹配
- [ ]  应用 `health` / 只读查询正常
- [ ]  多租户 / 权限抽样正确
- [ ]  无敏感配置泄露到新环境
- [ ]  工单关闭并归档演练/恢复记录

## 7. 关联样板

- 数据修复 SQL：`examples/scripts/data-fix-template.sql`
- 修复流程：`examples/scripts/data-fix-runbook.md`
