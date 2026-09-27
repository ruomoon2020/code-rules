<!--
复制并以本文件作为业务仓根级 PR 默认模板（组织级治理入口）。
端内模板已有更细分字段；根模板关注“必填治理输入”与“可审计证据”。
维护者说明见 `docs/definition-of-done.md` / `docs/rule-exception-process.md`。
-->

## 变更摘要
<!-- 1–3 句话：做什么、为什么、影响范围 -->

## 需求 / Issue 与验收证据（必填）
<!--
每个可观察行为或治理要求独立一行。纯文档或无行为变更也必须写明 N/A 原因，不能留空。
验收条件使用“前置状态 + 动作 + 可观察结果”，不要只写“功能正常”或“测试通过”。
-->

| 需求 / Issue | 验收条件 | 影响面 | 实现 / 契约 | 验证证据 | 状态 |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 变更类型（勾选）
<!-- 至少选择 1 项，必要时补充“其他” -->
- [ ] API / 契约 / OpenAPI
- [ ] DB / Flyway / 数据修复
- [ ] 安全 / 鉴权 / 权限码 / 输入校验
- [ ] 依赖 / 许可证
- [ ] 定时任务 / 批处理 / MQ
- [ ] 配置 / 密钥 / IaC / 容器
- [ ] 规则包 `rules/**` 变更
- [ ] 仅文档：规则/治理文档
- [ ] 其他：__________

## 风险等级（必填，勾选 1 项）
<!-- 与 `SECURITY.md` 及 DoD 安全门禁口径对齐；高风险/关键通常需要额外 Review -->
- [ ] Low（低风险，按常规门禁执行）
- [ ] Medium（需验证证据更充分）
- [ ] High（可能影响权限/PII/稳定性，需更严格 Review）
- [ ] Critical（安全/供应链重大风险：需 Security Owner 签字与证据）

## Owner / Reviewer（必填）
<!-- 填写并确保 CODEOWNERS 矩阵已指派对应 Reviewer -->
- Owner（开发负责人）：__________
- Security/合规 Owner（如涉及安全/PII/依赖）：__________
- CODEOWNERS Reviewer 已完成指派（见 `docs/codeowners-matrix.md`）：[ ] 是 [ ] 否
- 跨端契约变更已完成消费端 Owner Review（见 `docs/codeowners-matrix.md`）：[ ] 是 [ ] 否

## 必填检查（Required）

### 1) 契约影响（Contracts / API）
- [ ] 不涉及 / N/A
- [ ] 已更新 `contracts/openapi.yaml`（或项目约定契约路径）
- [ ] 已运行 OpenAPI diff / Spectral（并附结论或链接）：__________
- [ ] 破坏性变更已标注 `deprecated` / 版本策略 / 迁移说明：__________
- [ ] 若改 API：消费端已完成 `api:gen` + `api:check`（或说明已配置跳过原因）：__________

### 2) 测试证据（Quality / Verification）
- [ ] 不涉及 / N/A（仅限纯文档、模板或无执行入口变更）
- [ ] 已运行关键门禁：`mvn verify` / `./gradlew check` / `pnpm lint` / `pnpm type-check` / `pnpm build`（按端选择）
- [ ] 单测/集成测已通过（或说明项目未配置）：__________
- [ ] 安全/质量静态门禁已通过（如启用 ArchUnit/Checkstyle/views 扫描）：__________
- [ ] SLO / 降级 / 外部依赖超时策略（仅在影响核心链路时必填）：__________

### 3) 安全 / PII / 权限（Security & Privacy）
- [ ] 不涉及 / N/A
- [ ] 已覆盖鉴权/未登录/无权限/跨租户/BOLA 等用例（如涉及）
- [ ] 无密码/Token/敏感 PII 明文写入日志或异常
- [ ] 若涉及 PII/导出/留存：已对照 `docs/data-classification-matrix.md` 完成脱敏与审计要求
- [ ] 高风险接口有越权/可用性回归测试或威胁建模记录（按项目策略）：__________

### 4) 数据与持久化（DB / Migration）
- [ ] 不涉及 / N/A
- [ ] DB migration 已执行并 validate（Flyway/Liquibase 在目标方言 validate）
- [ ] 已附 dry-run、影响行数（仅在生产数据修复时必填）
- [ ] 回滚方案已准备：可执行逆向 migration 或可回滚策略（见下方“回滚方案”）
- [ ] 无用户输入进入 SQL `${}` 或等价风险写法（如适用）：[ ] 是 [ ] 否

### 5) 依赖 / 供应链（Dependencies / Supply chain）
- [ ] 不涉及 / N/A
- [ ] 若新增依赖：供应链 Required CI 已跑（见 `docs/supply-chain-baseline.md` + `examples/ci/supply-chain-required.yml`）
- [ ] 已处理许可证合规结论（GPL/AGPL/未知许可证等需评审）：__________
- [ ] 若引入依赖漏洞：已按 SLA 修复或走豁免流程（见 `docs/rule-exception-process.md`）

### 6) 治理（DoD / 豁免 / 发布前）
- [ ] 企业 DoD Required CI 全绿（见 `docs/definition-of-done.md`）
- [ ] 若跳过 Required 门禁：已填写豁免单（见 `docs/rule-exception-process.md`，含有效期与风险接受人）
- 豁免单 / 风险接受记录 ID（未跳过填 N/A）：__________
- [ ] 规则包 `rules/**` 变更：已通过相应 `validate-rules-package.py` 校验（见 `.github/workflows/validate-rules-packages.yml`）

## 回滚方案（必填）
<!-- 上线风险、功能开关、回滚步骤、影响范围 -->
- 不涉及 / N/A 原因（仅限纯文档、模板或无发布影响变更）：__________
- 回滚触发条件（如：错误率/告警/金丝雀失败）：__________
- 回滚步骤（镜像/配置回退/逆向 migration）：__________
- 回滚验证方式（回滚后如何验证是否恢复）：__________
- Owner（发布/回滚负责人）：__________

## 风险与 PII / 数据影响勾选（必填）
<!-- 与上面的必填检查一致；用于快速审计 -->
- [ ] 安全/鉴权
- [ ] PII / 隐私
- [ ] DB migration / 数据修复
- [ ] 依赖/供应链
- [ ] 契约/事件/对外接口（OpenAPI diff / 版本策略）

## 已运行命令（粘贴或链接 CI）
```text
# 示例
mvn verify
# 或 ./gradlew check
# 或 pnpm lint / type-check / build
```

## 关联
- Issue / 工单：
- ADR：
- 性能预算 / Runbook：
