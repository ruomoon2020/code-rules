# 规则包变更治理（维护者）

> 修改 `miniapp/rules/**` 时适用。

## 硬变更清单

- [ ] `VERSION`、`CHANGELOG.md`
- [ ] `README.md` 文件清单与磁盘一致
- [ ] `codex/AGENTS.md`、`cursor/*.mdc` 引用有效
- [ ] 新增 `shared/*.md` 时同步 `README.md` 文件清单与 `codex/AGENTS.md` 任务表（若 AI 可读）
- [ ] `evals/prompts.md`、`evals/rubric.md`、`evals/results-template.md` **仅此三文件**按 `### Mxx` 计数
- [ ] `evals/smoke-prompts.md`：**只校验 M 编号覆盖**，禁止 `### Mxx` 标题
- [ ] `evals/README.md` 回归套件表与 smoke 一致（含 **Business Extension** M21–M29）
- [ ] 改 eval 主题后：更新 `evals/topic-manifest.yaml`（monorepo `python scripts/generate-eval-topic-manifest.py --rules-dir miniapp/rules`）
- [ ] `RELEASE.md`
- [ ] `docs/rules-package-index.md` 与 `shared/00–26` 一致
- [ ] `examples/README.md` 与新增样板同步
- [ ] `python scripts/validate-rules-package.py` 通过

## Evals 计数约定

| 文件 | 计入提示词条数 |
|---|---|
| `evals/prompts.md` | **是**（SSOT） |
| `evals/rubric.md` | 是 |
| `evals/results-template.md` | 是 |
| `evals/smoke-prompts.md` | **否**（套件索引） |

## 发版

见 `RELEASE.md`；大版本须跑 **Full** evals M01–M52（P0 8/8，核心 P1 >=10/12，Extension 套件建议满配）。
