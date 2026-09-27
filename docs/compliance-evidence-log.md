# 合规证据留痕（模板）

> 金融、政务、医疗等监管场景：除规则本身外，须能回答 **谁、何时、依据何标准、做了什么、证据在哪**。与 [`rule-exception-process.md`](rule-exception-process.md) 豁免单、[`data-classification-matrix.md`](data-classification-matrix.md) 配合。

## 适用

| 场景 | 须留痕 |
|---|---|
| 等保 / 密评差距项关闭 | 测评项编号、整改 PR、复测日期 |
| 个人信息影响评估 | 字段分级、法律依据、保留周期 |
| 安全门禁豁免 | 链接 `EXC-YYYY-NNN` |
| 生产数据操作 | 工单号、dry-run、审批人 |
| 发版 / 灰度 | release-checklist 勾选、回滚验证 |
| 供应链例外 | GPL 评审结论、CVE 风险登记 |

## 记录表（业务仓 `docs/compliance/evidence-log.md`）

| ID | 日期 | 类型 | 关联标准 / 测评项 | 变更 / 措施 | 证据（PR / 工单 / 报告链接） | Owner | 复查日 |
|---|---|---|---|---|---|---|---|
| EV-2026-001 | 2026-06-01 | 等保整改 | 8.1.4 访问控制 | 补 BOLA 测试 B34 | PR #120 | @sec | 2026-12-01 |
| EV-2026-002 | 2026-06-15 | PII 新字段 | L2 手机脱敏 | OpenAPI 标注 + 前端脱敏 | PR #125 | @api | — |

### 单条模板（复制使用）

```markdown
## EV-YYYY-NNN — 标题

- **类型**：等保整改 | PII | 豁免 | 生产数据 | 发版 | 供应链
- **标准 / 测评项**：
- **措施摘要**：
- **证据**：PR / 扫描报告 / 演练记录 URL
- **Owner**：
- **复查日**：（无则 N/A）
- **关联豁免**：EXC-YYYY-NNN（若有）
```

## 与规则包映射

| 合规主题 | 规则落点 | 建议证据 |
|---|---|---|
| 访问控制 | `06`、`24`、evals B34 | 越权测试报告、PR |
| 审计 | `27` | 审计样例、日志截图（脱敏） |
| 个人信息 | `29`、数据分级矩阵 | 字段分级表、导出审批 |
| 备份恢复 | `32`、`backup-restore-runbook` | 演练记录、RTO/RPO 实测 |
| 供应链 | `20`、`supply-chain-baseline` | audit 报告、SBOM 链接 |
| 应急 | `incident-postmortem-template` | 复盘文档 |

国内条款索引：`web-backend/rules/docs/compliance-cn-mapping.md`（非法律意见）。

## PR 自检

- [ ] 监管相关 PR 已在 `docs/compliance/evidence-log.md` 增一行或链工单
- [ ] 证据可访问（内网 Wiki / 工单系统 / 制品库）
- [ ] 无真实生产 PII 写入证据附件
