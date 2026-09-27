# Adoption Checklist

## 规则包

- [ ] `rules/` 整包可访问
- [ ] 根 `AGENTS.md` ← `codex/AGENTS.md`
- [ ] `.cursor/rules/*.mdc` ← `cursor/`
- [ ] `contracts/openapi.yaml` 与前端共享

## 工程

- [ ] MyBatis-Plus + 分页插件配置
- [ ] Flyway（MySQL + PostgreSQL 若支持多库）
- [ ] ArchUnit 测试（`examples/archunit`）
- [ ] GlobalExceptionHandler：业务异常 WARN + stack、未知 5xx ERROR + cause、参数校验 400 + 字段约束摘要；响应 traceId 可检索到诊断主事件
- [ ] TraceId Filter / MDC
- [ ] SecurityConfig / CORS / CSRF / Swagger / Actuator 生产策略已确认
- [ ] OpenAPI baseline 已生成，CI diff 策略已确认

## 企业治理

- [ ] CODEOWNERS 已配置，覆盖契约、DB migration、安全、CI、IaC、规则包
- [ ] `docs/release-checklist.md` 已纳入发版流程
- [ ] `docs/incident-postmortem-template.md` 已纳入事故复盘流程
- [ ] `docs/backup-restore-runbook.md` 已按项目填写 RTO/RPO 与演练计划
- [ ] `docs/PERFORMANCE_BUDGET.template.md` 已复制为项目性能预算
- [ ] OWASP API Top 10 与国内合规映射已由安全 / 架构 Owner 过目

## 流程资产

- [ ] `docs/rule-maturity-model.md` 已声明目标 Level
- [ ] `docs/pull-request-template.md` 或已复制 `examples/.github/` 到业务仓 `.github/`
- [ ] CI 已按 Required/Conditional 裁剪（`examples/README.md`）

## 成熟后台业务扩展（若适用）

- [ ] 已阅读 `docs/business-feature-playbook.md`；全栈联调见 `docs/fullstack-contract.md` §新增业务功能
- [ ] 前端已阅读 `web-front/rules/shared/22-business-module-extension.md` 与 `web-front/rules/docs/business-feature-playbook-frontend.md`（菜单、权限、api:gen）
- [ ] 新增业务默认在 `modules/{biz}`；改 `common`/`framework`/`system` 已有 Owner/ADR
- [ ] PR 模板已复制且勾选「新增业务模块」段（`examples/.github/`）

## 评测

- [ ] **Smoke**：B01–B08 + 核心 P1（≥18/21）；发版前 **Full** B01–B67（P0 8/8，P1 ≥53/59）
- [ ] AI 读取外部内容或调用工具时，`evals/ai-tool-safety.md` BAT01–BAT05 **5/5**
- [ ] 成熟后台新增业务时，跑 **Business Extension**：后端 B55–B63、前端 E32–E40（均建议 9/9）

## 企业治理（monorepo）

- [ ] 已阅读 `docs/enterprise-governance.md`；DoD / 豁免 / 供应链见 monorepo `docs/`
- [ ] 已运行 `scripts/check-project-adoption.py --stack backend`（`--strict` 推荐）
- [ ] `docs/release-checklist.md` 与 DoD 发布门禁对齐
