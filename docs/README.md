# 企业级治理文档索引

> 本目录是治理文档 SSOT。业务仓优先引入由它生成的 [`common-governance/`](../common-governance/README.md) 可分发包；不要手工维护第二份副本。

## 文档

| 文档 | 用途 |
|---|---|
| [`project-adoption-guide.md`](project-adoption-guide.md) | **业务项目接入总指南**（全栈 monorepo / 分仓 / 单端） |
| [`migration-baseline.md`](migration-baseline.md) | 目标规则与存量兼容分离、债务基线和 CI 双通道 |
| [`requirements-traceability.md`](requirements-traceability.md) | 需求 / Issue → 验收条件 → 实现 → 测试 → 发布证据追踪 |
| [`business-correctness-review.md`](business-correctness-review.md) | 业务流程、数据、权限、契约与回归评审基线 |
| [`ai-tool-security.md`](ai-tool-security.md) | 提示注入、不可信内容、工具权限与数据出站边界 |
| [`release-evidence.md`](release-evidence.md) | 可机器校验的发布证据规范 |
| [`environment-promotion.md`](environment-promotion.md) | Dev/Test/Staging/Production 晋级、配置漂移与回滚治理 |
| [`incident-response.md`](incident-response.md) | 跨端事故分级、响应、沟通与证据保全 |
| [`incident-postmortem-template.md`](incident-postmortem-template.md) | 无责复盘与行动项模板 |
| [`definition-of-done.md`](definition-of-done.md) | 跨端 DoD（代码 / 契约 / 安全 / 数据 / 可观测 / 发布） |
| [`architect-engineering-checklist.md`](architect-engineering-checklist.md) | 立项、方案和上线评审提问单（不替代 DoD） |
| [`rule-exception-process.md`](rule-exception-process.md) | 例外与豁免流程 |
| [`exceptions/README.md`](exceptions/README.md) | 机器可读豁免记录目录与 CI 接入方式 |
| [`codeowners-matrix.md`](codeowners-matrix.md) | 按变更类型的 Review 矩阵 |
| [`supply-chain-baseline.md`](supply-chain-baseline.md) | 供应链强制基线 |
| [`data-classification-matrix.md`](data-classification-matrix.md) | 数据分类分级跨端表 |
| [`slo-alerting-template.md`](slo-alerting-template.md) | 管理端 / 小程序 SLO 与告警 |
| [`dod-maturity-mapping.md`](dod-maturity-mapping.md) | DoD × 采纳 Level 0–3 对照 |
| [`adoption-scorecard.md`](adoption-scorecard.md) | 成熟度评分卡：Required Evidence / Owner / 到期复查 |
| [`compliance-evidence-log.md`](compliance-evidence-log.md) | 合规证据留痕模板（金融 / 政务） |
| [`control-catalog.yaml`](control-catalog.yaml) | SSDF / ASVS / OSPS / SLSA 版本化控制与证据映射 |
| [`branch-protection.md`](branch-protection.md) | 分支保护与 Required Checks 实施指南（含豁免链路） |
| [`git-pr-governance.md`](git-pr-governance.md) | Conventional Commits、PR 证据、本地 hook 与 CI 边界 |
| [`monorepo-layout.md`](monorepo-layout.md) | 全栈 monorepo 推荐布局（**仅维护仓**；不随 `common-governance` 分发） |
| [`adr/0001-rules-governance-baseline.md`](adr/0001-rules-governance-baseline.md) | 根级治理原则基线 ADR（**仅维护仓**） |
| [`rule-catalog.yaml`](rule-catalog.yaml) | 编码规则索引（由 `scripts/generate-rule-catalog.py` 生成并在 CI 校验；引用覆盖不等于行为评测覆盖） |
| [`research/exception-observability-practices.md`](research/exception-observability-practices.md) | 国内外官方异常日志实践研究（研究依据，不是执行 SSOT） |
| [`../SECURITY.md`](../SECURITY.md) | 安全策略与漏洞报告入口（含 SLA / secret 泄露处置） |

## 脚本

| 脚本 | 用途 |
|---|---|
| [`scripts/check-project-adoption.py`](../scripts/check-project-adoption.py) | 业务仓接入验收 |
| [`scripts/check-debt-baseline.py`](../scripts/check-debt-baseline.py) | 存量债务数量/路径白名单防增长门禁 |
| [`scripts/validate-release-evidence.py`](../scripts/validate-release-evidence.py) | 发布证据 YAML 校验 |
| [`scripts/validate-control-catalog.py`](../scripts/validate-control-catalog.py) | 控制目录版本、引用和验证路径校验 |
| [`scripts/validate-workflow-security.py`](../scripts/validate-workflow-security.py) | GitHub Actions action 固定 SHA 与最小权限校验 |
| [`scripts/validate-ai-eval-results.py`](../scripts/validate-ai-eval-results.py) | AI Tool Safety 结果与套件摘要绑定校验 |
| [`scripts/prepare-ai-eval-run.py`](../scripts/prepare-ai-eval-run.py) | AI 评测准备：打印 digest / 写 fail 骨架（不调模型） |
| [`scripts/validate-exceptions.py`](../scripts/validate-exceptions.py) | 豁免期限、审批、补偿控制与关闭证据校验 |
| [`scripts/validate-pr-governance.py`](../scripts/validate-pr-governance.py) | 实际 PR 描述的追踪矩阵、风险和占位符校验 |
| [`common-governance/examples/ci/supply-chain-required.yml`](../common-governance/examples/ci/supply-chain-required.yml) | 可分发供应链 Required CI（npm/pnpm audit + Maven/Gradle OWASP） |
| [`common-governance/examples/ci/credential-scan-required.yml`](../common-governance/examples/ci/credential-scan-required.yml) | 凭据泄露扫描 Required CI 样板 |
| [`common-governance/examples/ci/rules-adoption-required.yml`](../common-governance/examples/ci/rules-adoption-required.yml) | 规则采纳 Level 2 Required CI 样板 |
| [`common-governance/examples/ci/debt-baseline-required.yml`](../common-governance/examples/ci/debt-baseline-required.yml) | 存量债务不可增长 Required CI 样板 |
| [`common-governance/examples/ci/exceptions-required.yml`](../common-governance/examples/ci/exceptions-required.yml) | 豁免记录期限与关闭证据 Required CI 样板 |
| [`common-governance/examples/ci/ai-eval-results-required.yml`](../common-governance/examples/ci/ai-eval-results-required.yml) | AI Tool Safety 结果 YAML 校验（不跑模型） |

## 业务仓最小落地

```bash
# 从 code-rules 发布物复制 common-governance/ 到业务仓根

# 接入验收
python common-governance/scripts/check-project-adoption.py --repo . --stack frontend --level 2
```

各规则包内链：`web-*/rules/docs/enterprise-governance.md`。
