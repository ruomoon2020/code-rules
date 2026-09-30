# 业务仓要接的治理文档

> 本目录 `rules/` 侧重 **AI 编码规则**。组织级 DoD、豁免、Owner、供应链与数据分级由 `common-governance/` 独立分发；code-rules 根 `docs/` 是其维护 SSOT。

## 仅 submodule 本规则包时

业务仓若只有 `rules/`，请从上游仓库额外引入：

| 复制源（monorepo） | 建议目标（业务仓） |
|---|---|
| `common-governance/` 整包 | `common-governance/` |
| `scripts/check-project-adoption.py` | `scripts/` 或 CI 工具目录 |

## 文档清单

| 主题 | monorepo 路径 |
|---|---|
| Definition of Done | `docs/definition-of-done.md` |
| 豁免流程 | `docs/rule-exception-process.md` |
| CODEOWNERS 矩阵 | `docs/codeowners-matrix.md` |
| 供应链基线 | `docs/supply-chain-baseline.md` |
| 数据分级 | `docs/data-classification-matrix.md` |
| 受监管 Web | 金融 / 政务 / 高敏数据项目追加 `shared/25-regulated-web-hardening.md` 与 E44–E49 |
| SLO / 告警 | `docs/slo-alerting-template.md` |
| DoD × Level | `docs/dod-maturity-mapping.md` |
| 合规证据留痕 | `docs/compliance-evidence-log.md` |

全索引：`docs/README.md`（monorepo 根）。

## 验收

企业项目推荐：

```bash
python common-governance/scripts/check-project-adoption.py --repo /path/to/your-app --stack frontend --level 2
```

`--level 2` 已隐含完整治理包校验。Level < 2 仍要强制治理包时再加 `--require-governance`；需要 CODEOWNERS / PR 模板时叠加 `--strict`。

发版与 PR 合并标准见 DoD；超预算或跳过门禁须走豁免流程。
