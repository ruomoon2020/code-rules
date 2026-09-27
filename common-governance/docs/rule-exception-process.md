# 规则例外与豁免流程

> 规则体系必须同时回答：谁可以破例、破多久、谁承担风险、如何复查。适用于技术规则、性能预算、CI 门禁和安全策略的临时例外。

## 原则

1. 默认遵守各端 `rules/shared/00-must-follow.md` 与跨端 DoD，见 [`definition-of-done.md`](definition-of-done.md)。
2. 例外必须书面记录、限时、有 Owner，禁止口头永久豁免。
3. 能增加补偿控制时不得裸豁免，例如限流、审计、功能开关和额外测试。

## 机器可读记录

业务仓在 `docs/exceptions/` 保存 YAML 记录；使用外部工单系统时，也必须导出同等字段供 CI 校验。样板见 [`../examples/rule-exception.yaml`](../examples/rule-exception.yaml)。

```text
python common-governance/scripts/validate-exceptions.py --root .
```

每条记录包含：

| 字段 | 说明 |
|---|---|
| ID | `EXC-YYYY-NNN` |
| 规则 / 门禁 | 稳定规则 ID；暂未分配 ID 时使用规则路径和条目名称 |
| 原因 | 业务背景和技术约束 |
| 范围 | 模块、路由、依赖或环境 |
| Owner | 修复与关闭负责人 |
| 风险接受人 | 不低于 Team Lead 或领域 Owner |
| 补偿控制 | 监控、限流、人工复核、功能开关或额外测试 |
| 起止日期 | 默认有效期不超过 90 天 |
| 复查日 | 不晚于到期日 |
| 审批 | 审批角色、审批人和审批时间 |
| 关闭条件 | 量化指标或交付物 |

已关闭记录还必须保留关闭日期和关闭证据。不要删除历史记录。

## 审批矩阵

| 例外类型 | 最低审批 | 是否 ADR | 是否安全 Review |
|---|---|---|---|
| 代码风格 / lint 单条 | Tech Lead | 否 | 否 |
| 性能预算 | 领域 Owner + 技术 Owner | 建议 | 否 |
| 跳过测试 / 降低覆盖率 | QA Owner + Tech Lead | 是 | 否 |
| 安全门禁、漏洞或许可证 | 安全 Owner | 是 | 是 |
| 生产数据操作 | DBA + 数据 Owner | 是 | 按数据等级 |
| 公共模块或规则包 | 架构 Owner | 是 | 按场景 |
| CI Required 变 Optional | DevOps + 架构 Owner | 是 | 按门禁类型 |

## 禁止

- 无有效期、无复查日的永久豁免。
- 批量关闭静态规则且没有跟踪记录。
- Critical 安全风险没有缓解措施仍然上线。
- 多人共用的豁免没有明确 Owner。
- 通过删除、改名或移动记录来规避到期检查。

## 复查与关闭

1. 到达复查日必须关闭或重新审批；续期生成新的审批证据。
2. 修复合并后标记 `closed`，记录关闭日期并链接修复 PR、测试或报告。
3. 监管相关记录同步到 [`compliance-evidence-log.md`](compliance-evidence-log.md)。
4. PR、主干和每周定时任务运行 `validate-exceptions.py`；未关闭且过期、有效期超过 90 天、缺 Owner、审批或补偿控制时必须失败。
