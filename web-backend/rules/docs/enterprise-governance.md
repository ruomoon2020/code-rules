# 企业级治理（业务仓落地）

> 本目录 `rules/` 侧重 **AI 编码规则**。组织级 DoD、豁免、Owner、供应链与数据分级由 `common-governance/` 独立分发；code-rules 根 `docs/` 是其维护 SSOT。

## 仅 submodule 本规则包时

从上游仓库整包引入 `common-governance/`，并提供 `scripts/check-project-adoption.py`。不要手工维护治理文档副本。

## 文档清单

| 主题 | monorepo 路径 |
|---|---|
| Definition of Done | `docs/definition-of-done.md` |
| 豁免流程 | `docs/rule-exception-process.md` |
| CODEOWNERS 矩阵 | `docs/codeowners-matrix.md` |
| 供应链基线 | `docs/supply-chain-baseline.md` |
| 数据分级 | `docs/data-classification-matrix.md` |
| SLO / 告警 | `docs/slo-alerting-template.md` |
| DoD × Level | `docs/dod-maturity-mapping.md` |
| 合规证据留痕 | `docs/compliance-evidence-log.md` |

后端 SLO 细则另见本包 `shared/32-service-reliability.md`、`docs/release-checklist.md`。

## 验收

企业项目推荐：

```bash
python common-governance/scripts/check-project-adoption.py --repo /path/to/backend --stack backend --level 2
```

`--level 2` 已隐含完整治理包校验。Level < 2 仍要强制治理包时再加 `--require-governance`；需要 CODEOWNERS / PR 模板时叠加 `--strict`。
