# 规则包变更治理（维护者）

> 修改 `web-front/rules/**` 时适用。

## 硬变更清单

- [ ] `VERSION`、`CHANGELOG.md`
- [ ] `README.md` 文件清单与磁盘一致
- [ ] `codex/AGENTS.md`、`cursor/*.mdc` 引用有效
- [ ] 新增 `shared/*.md` 时同步 `README.md` 文件清单与 `codex/AGENTS.md` 任务表（若 AI 可读）；`validate-rules-package.py` 会校验 README 是否列出全部 `shared/*.md`
- [ ] `evals/prompts.md`、`evals/rubric.md`、`evals/results-template.md` **仅此三文件**按 `### Exx` 计数
- [ ] `evals/smoke-prompts.md`：**只校验 E 编号覆盖**，禁止 `### Exx` 标题
- [ ] `evals/README.md` 回归套件表与 smoke 一致（含 **Business Extension** E32–E40、**Platform Extension** E41–E43、**Enterprise Hardening** E44–E49、**Testing Governance** E31/E50）
- [ ] 改 eval 主题后：更新 `evals/topic-manifest.yaml`（monorepo `python scripts/generate-eval-topic-manifest.py --rules-dir web-front/rules`）
- [ ] `RELEASE.md`
- [ ] `node examples/run-ci-scan-fixtures.mjs` 通过
- [ ] `python scripts/validate-rules-package.py` 通过

## Evals 计数约定

| 文件 | 计入提示词条数 |
|---|---|
| `evals/prompts.md` | **是**（SSOT） |
| `evals/rubric.md` | 是 |
| `evals/results-template.md` | 是 |
| `evals/smoke-prompts.md` | **否**（套件索引） |

## 发版

见 `RELEASE.md`；大版本须跑 **Full** evals E01–E50（P0 8/8，P1 ≥39/42）。
