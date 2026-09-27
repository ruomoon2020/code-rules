# Common Governance Package

跨前端、后端、小程序和其他技术栈复用的治理发布包。它约束 DoD、测试闭环、例外、Owner、供应链、数据分级、Git / PR 和发布证据，不替代各端编码规则，也不要求 AI 每次读取全部文档。

## 安装

将整个 `common-governance/` 复制、发布或以独立子模块放到业务仓根：

```text
your-project/
├─ AGENTS.md
├─ rules/                  # 对应技术栈规则包
├─ common-governance/      # 本包
├─ .cursor/rules/
└─ ...
```

项目在根 `AGENTS.md` 或 README 中声明采纳 Level；只有命中合并、发布、例外、数据分级、供应链等任务时才读取对应治理文档。

## 内容

| 入口 | 用途 |
|---|---|
| `docs/project-adoption-guide.md` | 业务项目接入总指南 |
| `docs/definition-of-done.md` | 合并与发布 DoD |
| `docs/architect-engineering-checklist.md` | 立项、方案和上线评审提问单 |
| `docs/requirements-traceability.md` | 需求、验收条件、实现和证据追踪 |
| `docs/business-correctness-review.md` | 人工业务正确性评审基线 |
| `docs/ai-tool-security.md` | 不可信内容与 AI 工具调用边界 |
| `docs/release-evidence.md` | 结构化发布证据规范 |
| `docs/environment-promotion.md` | 环境晋级、产物不可变、配置漂移和回滚 |
| `docs/incident-response.md` | 事故分级、响应、沟通和证据保全 |
| `docs/incident-postmortem-template.md` | 无责复盘与行动项模板 |
| `docs/rule-exception-process.md` | 门禁例外和到期复查 |
| `docs/codeowners-matrix.md` | 强制 Review 路由 |
| `docs/supply-chain-baseline.md` | 依赖、许可证、SBOM 和漏洞处置 |
| `docs/data-classification-matrix.md` | 跨端数据分级与出站控制 |
| `docs/slo-alerting-template.md` | SLO、告警和演练证据模板 |
| `docs/dod-maturity-mapping.md` | DoD 与 Level 0–3 映射 |
| `docs/adoption-scorecard.md` | 采纳成熟度、Owner 和到期复查 |
| `docs/migration-baseline.md` | 目标规则、当前基线、例外与 CI 双通道 |
| `docs/compliance-evidence-log.md` | 合规证据留痕模板 |
| `docs/control-catalog.yaml` | SSDF / ASVS / OSPS / SLSA 版本化控制映射 |
| `docs/branch-protection.md` | Required Checks 与紧急流程 |
| `docs/git-pr-governance.md` | Commit、PR 和本地 hook / CI 边界 |
| `examples/` | PR、commitlint、SECURITY、ADR 与 Required CI 样板 |
| `examples/ci/credential-scan-required.yml` | 凭据泄露扫描 Required Check |
| `examples/ci/rules-adoption-required.yml` | 规则采纳 Level 2 Required Check |
| `examples/ci/debt-baseline-required.yml` | 存量债务不可增长 Required Check |
| `examples/ci/supply-chain-required.yml` | 锁文件、依赖漏洞与许可证 Required Check |
| `examples/ci/artifact-trust-required.yml` | SBOM 与构建 provenance / attestation 样板 |
| `examples/ci/exceptions-required.yml` | 豁免期限、审批与关闭证据 Required Check |
| `examples/ci/ai-eval-results-required.yml` | AI Tool Safety 结果 YAML 校验（不跑模型） |
| `examples/ai-eval-results.yaml` | AI Tool Safety 结果样板 |
| `examples/governance-adoption.yaml` | Level 2+ 控制声明与静态证据清单样板；平台现状须另行核对 |
| `examples/governance-platform-evidence.json` | 分支、组织权限与生产环境控制快照样板 |
| `examples/PROJECT_RULES.md.sample` | 项目真实路径、命令、采纳级别和测试治理参数覆盖层样板 |
| `examples/contract-baseline.md.sample` | 契约现状与迁移窗口样板 |
| `examples/migration-baseline.json` | 存量债务机器基线样板 |
| `scripts/check-project-adoption.py` | 业务仓规则与治理接入验收（Level 1 起校验测试治理参数已填写） |
| `scripts/check-debt-baseline.py` | 正则计数与路径白名单债务防增长门禁 |
| `scripts/validate-control-catalog.py` | 版本化控制目录与本地验证路径校验 |
| `scripts/validate-workflow-security.py` | Workflow action SHA 与最小权限校验 |
| `scripts/validate-ai-eval-results.py` | AI Tool Safety 结果与套件摘要绑定校验 |
| `scripts/prepare-ai-eval-run.py` | AI 评测准备：digest / fail 骨架（不调模型、不自动满分） |
| `scripts/validate-exceptions.py` | 豁免期限、审批、补偿控制与关闭证据校验 |
| `scripts/validate-pr-governance.py` | 实际 PR 描述的需求追踪、风险和占位符校验 |
| `scripts/validate-release-evidence.py` | 发布证据 YAML 机器校验 |
| `examples/release-evidence.yaml` | 生产发布证据样板 |
| `examples/rule-exception.yaml` | 已关闭豁免记录样板 |

`docs/` 是从 code-rules 根目录 SSOT 生成的发布副本。维护者不得直接修改包内副本，应修改根 `docs/` 后运行同步脚本。

文档中出现的 `web-front/rules/`、`web-backend/rules/`、`miniapp/rules/` 路径是对应技术栈的扩展依据；业务仓未安装该端规则包时可忽略，不应改写治理结论。

## 验证

业务仓验证发布文件与 manifest 的一致性：

```bash
python common-governance/scripts/validate-package.py
```

code-rules 维护者验证副本未漂移：

```bash
python scripts/sync-common-governance.py
```

业务仓强制验收（企业项目推荐）：

```bash
python common-governance/scripts/check-project-adoption.py --repo . --stack frontend --level 2
```

`--level 2` 会自动要求完整治理包，并校验固定资产清单、版本和 SHA-256；只存在同名文件不算通过。SHA-256 用于发现复制或发布漂移，不替代来自可信发布渠道的签名或 release checksum。

仅当 Level < 2 仍要强制校验治理包时，再显式加 `--require-governance`；需要 CODEOWNERS / PR 模板时叠加 `--strict`：

```bash
python common-governance/scripts/check-project-adoption.py --repo . --stack frontend --strict --require-governance
```

成熟度门禁也可直接使用 `--level 0..3`。Level 2 会核验 `governance-adoption.yaml` 中的规则采纳、凭据扫描、供应链和分支保护证据；Level 3 还要求至少三项已完成的平台治理证据：

```bash
python common-governance/scripts/check-project-adoption.py --repo . --stack frontend --level 3 --report-only
python common-governance/scripts/check-debt-baseline.py --config migration-baseline.json
python common-governance/scripts/validate-control-catalog.py
python common-governance/scripts/validate-release-evidence.py --file releases/1.8.0/release-evidence.yaml --artifact dist/app.tar.gz
python common-governance/scripts/validate-exceptions.py --root .
```
