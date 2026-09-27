# Cursor ↔ Shared 编号对照（后端）

> **编号不相等**：`cursor/NN` 是 Cursor 触发文件名，`shared/NN` 是规则正文编号。模型与维护者均以本表为准，禁止按数字猜映射。

| Cursor | Shared 正文 | 主题 |
|---|---|---|
| `00-project-overview.mdc` | `00-must-follow.md` | 总览 / Level 0 |
| `01-architecture.mdc` | `01-project-structure.md` | 工程结构 |
| `02-java-style.mdc` | `03-code-style.md`（兼 `02-naming`） | 代码风格 |
| `03-validation.mdc` | `13-validation.md` | 入参校验 |
| `04-rest-controller.mdc` | `04-rest-api-design.md`、`12-dto-mapping.md` | REST / DTO |
| `05-service-transaction.mdc` | `07`、`18`、`28` | 事务与集成边界 |
| `06-persistence-mybatis.mdc` | `07-persistence-mybatis.md` | 持久化 |
| `07-review-checklist.mdc` | `10-verification-checklist.md` | 收尾 |
| `08-exception-logging.mdc` | `08-exception-errorcodes.md`、`09-logging-observability.md` | 异常与日志 |
| `09-security-authz.mdc` | `06-security-authz.md` | 鉴权 |
| `10-domain-model.mdc` | `11-domain-model.md` | 领域模型 |
| `11-testing.mdc` | `15-testing.md` | 测试 |
| `12-openapi-contract.mdc` | `05-openapi-contract.md`、`04` | 契约 |
| `13-pagination-query.mdc` | `19-pagination-query.md` | 分页查询 |
| `14-import-export.mdc` | `14-file-import-export.md` | 导入导出 |
| `15-naming-conventions.mdc` | `02-naming.md` | 命名 |
| `16-quality-gates.mdc` | `23-quality-gates.md` | CI 门禁 |
| `17-data-access-cache.mdc` | `24-data-access-cache.md` | 数据权限 / 缓存 |
| `18-jobs-scheduling.mdc` | `25-jobs-scheduling.md` | 定时任务 |
| `19-audit-log.mdc` | `27-audit-log.md` | 审计 |
| `20-external-integration.mdc` | `28-external-integration.md` | 外部集成 |
| `21-data-privacy-lifecycle.mdc` | `29-data-privacy-lifecycle.md` | 隐私生命周期 |
| `22-ownership-adr.mdc` | `30-ownership-adr.md` | Owner / ADR |
| `23-production-data-ops.mdc` | `31-production-data-ops.md` | 生产数据操作 |
| `24-service-reliability.mdc` | `32-service-reliability.md` | 可靠性 |
| `25-alternate-api-paradigms.mdc` | `33-alternate-api-paradigms.md` | 多范式 API |
| `26-data-archival.mdc` | `34-data-archival.md` | 归档 |
| `27-threat-modeling.mdc` | `35-threat-modeling.md` | 威胁建模 |
| `28-crypto-key-management.mdc` | `36-crypto-key-management.md` | 密钥 |
| `29-service-to-service-auth.mdc` | `37-service-to-service-auth.md` | 服务间认证 |
| `30-cloud-native-runtime.mdc` | `38-cloud-native-runtime.md` | 云原生 |
| `31-event-contracts.mdc` | `39-event-contracts.md` | 事件契约 |
| `32-money-time-precision.mdc` | `40-money-time-precision.md` | 金额 / 时间 |
| `33-dictionary-state-machine.mdc` | `41-dictionary-state-machine.md` | 字典 / 状态机 |
| `34-cost-governance.mdc` | `42-cost-governance.md` | 成本治理 |
| `35-business-module-extension.mdc` | `43-business-module-extension.md` | 业务模块扩展 |
| `36-platform-boundary.mdc` | `43`、`30` | 平台边界 |
| `37-performance.mdc` | `16-performance.md` | 性能 |
| `38-messaging-async.mdc` | `17-messaging-async.md`、`18` | 消息异步 |
| `39-configuration-secrets.mdc` | `21-configuration-secrets.md` | 配置密钥 |
| `40-operability.mdc` | `22-operability.md` | 可运维 |
| `42-ai-generation.mdc` | `26-ai-generation.md` | AI 生成 |

无 `cursor/41`：故意留空，避免与 shared `41` 混淆。

Codex 不读 `cursor/*.mdc`；对照表仅供 Cursor 部署与维护者消歧。
