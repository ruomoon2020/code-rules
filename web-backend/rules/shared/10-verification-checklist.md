# 验证清单

## 自动化

```bash
mvn verify
# 或
./gradlew check
```

按项目可能包含：test、checkstyle、archunit、openapi-diff、flyway validate。

## 按变更选择规则

本清单只负责选择验证路径，不复制规则正文。先按 `codex/AGENTS.md` 或 Cursor 路由确定本次命中的 shared 文件，再逐条检查其原文：

| 变更 | 必读与验证指针 |
|---|---|
| 架构、模块、对象模型 | `01-project-structure.md`、`11-domain-model.md`、`12-dto-mapping.md`、ArchUnit |
| API、校验、错误、分页 | `04-rest-api-design.md`、`05-openapi-contract.md`、`08-exception-errorcodes.md`、`13-validation.md`、`19-pagination-query.md` |
| SQL、事务、并发 | `07-persistence-mybatis.md`、`18-idempotency-concurrency.md` |
| 权限、租户、敏感数据 | `06-security-authz.md`、`24-data-access-cache.md`、`29-data-privacy-lifecycle.md` |
| 导入导出、任务、事件、外部调用 | `14-file-import-export.md`、`17-messaging-async.md`、`25-jobs-scheduling.md`、`28-external-integration.md`、`39-event-contracts.md` |
| 测试、性能、质量门禁 | `15-testing.md`、`16-performance.md`、`23-quality-gates.md` |
| 生产、安全、可靠性 | `20-dependency-governance.md`、`27-audit-log.md`、`31-production-data-ops.md`、`32-service-reliability.md`、`35-threat-modeling.md`–`38-cloud-native-runtime.md` |
| 复杂账期、显式状态流、成本配额 | `40-money-time-precision.md`、`41-dictionary-state-machine.md`、`42-cost-governance.md` |
| 成熟平台业务扩展 | `43-business-module-extension.md`、`docs/business-feature-playbook.md` |
| AI / 外部内容 / 工具调用 | `26-ai-generation.md`、common governance 的 `ai-tool-security.md` |

结果记录与回复格式见 `codex/05-verification.md`；发布验证见 `docs/release-checklist.md`。
