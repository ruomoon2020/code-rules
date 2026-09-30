# 跨端研发治理中心

本目录是治理文档的维护 SSOT，面向规则维护者、架构师和项目负责人。业务仓应优先使用由这里生成的 [`common-governance/`](../common-governance/README.md) 发布包，不得手工维护第二份副本。

## 按研发阶段使用

| 阶段 | 先读 | 产出 |
|---|---|---|
| 项目接入 / 存量迁移 | `project-adoption-guide.md`、`migration-baseline.md` | 采纳 Level、项目覆盖层、债务基线、接入 PR |
| 立项 / 架构方案 | `architect-engineering-checklist.md`、`requirements-traceability.md` | 边界、Owner、风险、验收条件、ADR |
| 开发 / Review | `business-correctness-review.md`、`definition-of-done.md` | 业务评审结论、测试与契约证据 |
| 合并 / 发布 | `environment-promotion.md`、`release-evidence.md`、`branch-protection.md` | Required Checks、发布证据、灰度与回滚计划 |
| 例外 / 事故 | `rule-exception-process.md`、`incident-response.md` | 有时限的豁免、响应记录、复盘行动项 |

如果只是开发某个页面或接口，不需要通读本目录；应从业务仓 `AGENTS.md` 进入对应技术栈规则。这里负责跨端和组织级治理。

## 文档目录

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
| [`rule-catalog.yaml`](rule-catalog.yaml) | 编码规则索引（由 `scripts/generate-rule-catalog.py` 生成并在 CI 校验；规范动词词频不是规则强度，引用覆盖不等于行为评测覆盖） |
| [`../SECURITY.md`](../SECURITY.md) | 安全策略与漏洞报告入口（含 SLA / secret 泄露处置） |

## 配套脚本

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

接入完成后，用一个真实 PR 验证规则入口、Required Checks 和证据链均能工作。各规则包的治理入口见 `web-*/rules/docs/enterprise-governance.md`。

## 规则文件命名与标题

- `rules/shared/` 的文件名必须使用稳定的英文 kebab-case，并保留两位编号，例如 `13-form-and-detail.md`；文件名用于路由、交叉引用和机器目录，不随展示语言变化。
- Markdown 一级标题必须使用中文，不重复文件名前的编号；OpenAPI、DTO、CI、Vue 等技术专名可保留英文。
- 新增或修改规则后必须运行 `python scripts/validate-repository.py` 和 `python scripts/generate-rule-catalog.py`；前者阻止标题语言再次漂移，后者将标题同步到根目录及各规则包目录。
