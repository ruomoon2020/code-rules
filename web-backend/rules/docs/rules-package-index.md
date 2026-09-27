# Shared 规则索引（维护者）

> AI 日常以 `00-must-follow.md` + `codex/AGENTS.md` 为准；本页便于检索全文。

| 编号 | 文件 | 主题 |
|---|---|---|
| 00 | `00-must-follow.md` | L0 硬规则 |
| 01 | `01-project-structure.md` | 分层与模块 |
| 02–03 | `02-naming.md`、`03-code-style.md` | 命名与风格 |
| 04–05 | `04-rest-api-design.md`、`05-openapi-contract.md` | REST 与 OpenAPI |
| 06 | `06-security-authz.md` | 鉴权、Web 安全、限流 |
| 07 | `07-persistence-mybatis.md` | MyBatis、索引、Flyway |
| 08–09 | `08-exception-errorcodes.md`、`09-logging-observability.md` | 异常、日志 |
| 10 | `10-verification-checklist.md` | 收尾检查 |
| 11–13 | `11`–`13` | 领域、DTO、校验 |
| 14 | `14-file-import-export.md` | 导入导出 |
| 15 | `15-testing.md` | 测试 |
| 16 | `16-performance.md` | 性能预算 |
| 17 | `17-messaging-async.md` | 消息与异步 |
| 18–19 | `18-idempotency-concurrency.md`、`19-pagination-query.md` | 幂等、分页 |
| 20 | `20-dependency-governance.md` | 依赖与 SBOM |
| 21–22 | `21-configuration-secrets.md`、`22-operability.md` | 配置、运维 |
| 23 | `23-quality-gates.md` | CI 映射 |
| 24–25 | `24-data-access-cache.md`、`25-jobs-scheduling.md` | 数据权限、任务 |
| 26 | `26-ai-generation.md` | AI 生成、不可信内容与工具安全 |
| 27–29 | `27-audit-log.md`、`28-external-integration.md`、`29-data-privacy-lifecycle.md` | 审计、外部、隐私 |
| 30–31 | `30-ownership-adr.md`、`31-production-data-ops.md` | ADR、生产数据操作 |
| 32–34 | `32-service-reliability.md`、`33-alternate-api-paradigms.md`、`34-data-archival.md` | 可靠性、API 范式、归档 |
| 35–42 | `35`–`42` | 威胁建模、加密密钥、服务间认证、云原生、事件契约、金额时间、状态机、成本 |
| 43 | `43-business-module-extension.md` | 成熟后台业务模块扩展 |

## Docs 附录

| 文件 | 用途 |
|---|---|
| `fullstack-contract.md` | 前后端字段对齐（含 §新增业务功能） |
| `backup-restore-runbook.md` | 备份恢复 |
| `PERFORMANCE_BUDGET.template.md` | 性能预算 |
| `business-feature-playbook.md` | 业务功能落地流程 |
| `../web-front/rules/shared/22-business-module-extension.md` | 前端业务页 SSOT（跨包） |
| `../web-front/rules/docs/business-feature-playbook-frontend.md` | 前端业务页面落地步骤（跨包） |
| `sql-dialect-matrix.md` | 方言 SQL 登记 |
| `adr/0000-template.md` | ADR 模板 |
| `owasp-api-top10-mapping.md` | OWASP API Top 10 ↔ shared 映射 |
| `compliance-cn-mapping.md` | 国内合规 ↔ 规则对照 |
| `release-checklist.md` | 发版前检查清单 |
| `incident-postmortem-template.md` | 事故复盘模板 |
| `codeowners-guidance.md` | CODEOWNERS 与 Review 路由 |
| `rule-maturity-model.md` | 采纳分层 Level 0–3 |
| `pull-request-template.md` | 业务仓 PR 模板（可复制） |
| `contributing-rules-package.md` | 规则包维护者变更治理 |
| `enterprise-governance.md` | 企业级 DoD / 豁免 / 接入验收（链 monorepo `docs/`） |
| `../scripts/validate-rules-package.py` | 规则包一致性校验 |
| `../scripts/README.md` | 校验脚本说明 |
| `../examples/ci/rules-package-validate.yml` | 业务仓 rules/ 校验 workflow |
| `../examples/.github/pull_request_template.md` | 业务仓 PR 模板 |
| `../cursor/35-business-module-extension.mdc` | Cursor 业务扩展触发规则 |
| `../cursor/36-platform-boundary.mdc` | Cursor 公共层 / system / generator 边界触发规则 |

## Evals

B01–B08 P0；B09–B67 P1（≥53/59）。套件：Smoke / Security / Contract / Business Extension / Full；AI Tool Safety BAT01–BAT05 独立 **5/5** — 见 `evals/README.md`、`evals/ai-tool-safety.md`、`evals/smoke-prompts.md`。
