# Pull Request 模板（业务仓）

> 复制到业务仓：直接使用 `examples/.github/pull_request_template.md`（复制整个 `examples/.github/` 到仓库根 `.github/`）。
> 本文与 `examples/.github/pull_request_template.md` 同源，便于 docs 内链接。

---

## 变更摘要

<!-- 1–3 句话说明做什么、为什么 -->

## 需求追踪

| 需求 / Issue | 验收条件 | 实现 / 契约 | 测试证据 | 状态 |
|---|---|---|---|---|
|  |  |  |  |  |

- [ ] 工作流、数据、权限、API / UI 一致性和回归风险已按 `common-governance/docs/business-correctness-review.md` 人工复核

## 变更类型（勾选）

- [ ] API / OpenAPI
- [ ] DB / Flyway / 数据修复
- [ ] 安全 / 鉴权 / 权限码
- [ ] 依赖 / 许可证
- [ ] 定时任务 / 批处理 / MQ
- [ ] 配置 / 密钥 / IaC / 容器
- [ ] 新增业务模块 / CRUD / CodeGen（成熟后台二开）
- [ ] 仅文档 / 规则包
- [ ] 其他：__________

---

## 必填检查

### 契约与 API

- [ ] 已更新 `contracts/openapi.yaml`（或项目约定路径）
- [ ] 已运行 OpenAPI diff / Spectral（或说明 skip 原因）：__________
- [ ] 破坏性变更已标注 `deprecated` / 版本策略 / 迁移说明（`05-openapi-contract.md`）
- [ ] 可重试写操作已声明 `Idempotency-Key` 或业务幂等键（若适用）

### 数据与持久化

- [ ] Flyway 脚本已 `validate`；多库项目已在 MySQL + PostgreSQL（或 Testcontainers）验证（若改库）
- [ ] 无用户输入进入 SQL `${}`；排序/列名白名单
- [ ] 生产数据修复（若有）：已附 dry-run、影响行数、审批、回滚（`31-production-data-ops.md`）

### 安全与权限

- [ ] 敏感接口已覆盖：未登录 / 无权限 / 跨租户 / BOLA（他人资源 id）（`06`、`15`）
- [ ] 数据权限 / 多租户条件与列表、导出一致（`24`）
- [ ] 无密码、Token、完整 PII 写入日志或异常
- [ ] 用户可控 URL 出站已防 SSRF（若适用）（`28`）

### 质量与性能

- [ ] 已运行：`mvn verify` / `./gradlew check`（结果：Pass / Fail — 链接：__________）
- [ ] ArchUnit / Checkstyle（若项目启用）已通过或说明未配置
- [ ] 核心接口 / 批处理 / 导入导出已说明性能预算或数据量上限（`16`、`docs/PERFORMANCE_BUDGET.template.md`）
- [ ] SLO / 降级 / 外部依赖超时（若改核心链路）（`32`、`28`）

### 合规与审计

- [ ] 涉及 PII / 导出 / 留存：已对照 `29-data-privacy-lifecycle.md`
- [ ] 敏感操作（删改权限、导入导出、配置变更等）已落审计（`27`）
- [ ] 高风险变更（支付、Webhook、跨租户）：已威胁建模或链接记录（`35`）

### 治理

- [ ] 公共抽象 / 新依赖 / breaking API：已确认 Owner；需 ADR 时已补（`30`）
- [ ] 已请求 CODEOWNERS 对应 Reviewer（契约 / DB / security / CI / rules）；矩阵见 monorepo `docs/codeowners-matrix.md`
- [ ] 规则包变更（若改 `rules/**`）：见 `docs/contributing-rules-package.md`

### 企业 DoD（monorepo，合并 / 发版前）

- [ ] 代码 / 契约 / 安全 Required CI 全绿（`docs/definition-of-done.md`）
- [ ] 新依赖 / 锁文件：供应链门禁已跑（`docs/supply-chain-baseline.md`）
- [ ] 新 PII / 敏感字段：已对照 `docs/data-classification-matrix.md`
- [ ] 跳过 Required 门禁：已填豁免单（`docs/rule-exception-process.md`）
- [ ] 监管 / 等保相关：已更新证据留痕（`docs/compliance-evidence-log.md`）

### 新增业务模块（成熟后台 / RuoYi 系，若适用）

- [ ] 变更仅在业务模块 `modules/{biz}`，未污染 `common` / `framework` / `system`（`43-business-module-extension.md`）
- [ ] 已复用平台用户、角色、菜单、权限、字典、文件、日志、任务、租户、数据权限（非重复造轮子）
- [ ] CodeGen 后已补：OpenAPI、权限码、菜单/按钮、数据权限、审计、索引、错误码、测试（`docs/business-feature-playbook.md`）
- [ ] 后端权限注解、菜单权限码、前端按钮权限码一致或可追踪；禁止仅有菜单 / 前端权限
- [ ] 模块名、表前缀、权限码、错误码、字典 type 前缀一致；全局表已说明非租户隔离原因
- [ ] list / detail / export / delete / batch / job 数据权限与 BOLA 口径一致（`24`、`06`）
- [ ] 树表 / 主子表已检查父子归属、跨租户、循环关系、事务回滚和孤儿数据
- [ ] 未为单个业务修改 generator 全局模板；若修改，已补 Owner、ADR、兼容、回滚和生成场景回归
- [ ] 建议跑 evals **Business Extension** B55–B63（建议 9/9；或说明 N/A：非成熟后台栈）

**前端（若同 PR 含管理端页面）**

- [ ] 已 `schema:sync` + `api:gen` + `api:check`；未手改 `src/api/generated`（`12-schema-ssot`）
- [ ] 路由 `name`、菜单、按钮权限码与后端一致；禁止仅隐藏 UI（`06-state-route-permission`）
- [ ] 树表 / 主子表（若有）：非法父节点禁选、主子表错误明细、失败态与后端一致（`22` §树表/主子表）
- [ ] 列表四态、删除末条回退页码、导入导出 UI 与 `web-front/rules/shared/22-business-module-extension.md`、`web-front/rules/docs/business-feature-playbook-frontend.md` 一致
- [ ] i18n / 实时 / 富文本（若有）：对照 `web-front/rules/shared/23`、`24`；建议跑 **Platform Extension** E41–E43
- [ ] 已跑 `pnpm lint` / `type-check`（或项目等价命令）

---

## 已运行命令（粘贴或链接 CI）

```text
# 示例
mvn verify
# 或 ./gradlew check
npx @redocly/cli diff contracts/openapi.baseline.yaml contracts/openapi.yaml
```

---

## 风险与回滚

<!-- 上线风险、功能开关、回滚步骤 -->

## 关联

- Issue / 工单：
- ADR：
- 性能预算 / Runbook：
