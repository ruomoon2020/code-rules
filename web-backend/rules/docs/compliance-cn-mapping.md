# 国内合规要点 → 本规则包映射（附录）

> 非法律意见；落地须结合法务与等保测评要求。仅映射到现有规则，避免重复立法原文。

| 领域 | 常见要求 | 本规则包落点 |
|---|---|---|
| 个人信息最小必要 | 采集与展示字段最小化 | `29-data-privacy-lifecycle`、`05` OpenAPI |
| 敏感个人信息 | 加强同意与脱敏 | `06`、`29`、`14` 导出 |
| 日志留存 | 操作可追溯、保留周期 | `27-audit-log`、`09`、`docs/backup-restore-runbook` |
| 访问控制 | 身份鉴别、权限分离 | `06`、`24`、越权测试 `15` |
| 数据备份与恢复 | 可恢复、演练 | `31`、`32` RTO/RPO、`backup-restore-runbook` |
| 出境 / 跨境 | 评估与审批 | `29`（须项目法务流程补充） |
| 安全开发 | 测试、漏洞修复 | `15`、`20` CVE SLA、`23` |
| 应急与审计 | 事件记录、复盘 | `27`、`32` 复盘、`docs/incident-postmortem-template.md` |
| 密码应用 / 密评 | 密码算法、密钥管理、传输保护、机器身份 | `36-crypto-key-management`、`37-service-to-service-auth`、`21-configuration-secrets`、`38-cloud-native-runtime` |
| 供应链安全 | 依赖漏洞、许可证、SBOM、CI 防篡改 | `20-dependency-governance`、`23-quality-gates`、`38-cloud-native-runtime` |
| 运维变更 | 发版、回滚、灰度、故障演练 | `22-operability`、`32-service-reliability`、`docs/release-checklist.md` |
| 数据生命周期 | 留存、归档、销毁、恢复至非生产脱敏 | `29`、`31`、`34-data-archival` |
| 权限与职责分离（二开） | 不重复造用户/角色/审计/任务；业务模块边界清晰；树表/主子表/generator 边界 | `43-business-module-extension`、`27-audit-log`、`25-jobs-scheduling`；evals B55–B63 |

等保 2.0 测评项请由安全团队做正式差距分析；本表仅作研发规则索引。整改关闭须留痕：monorepo [`docs/compliance-evidence-log.md`](../../../docs/compliance-evidence-log.md)。
