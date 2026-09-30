# 规则包变更治理（维护者）

> 修改 `web-backend/rules/**` 时适用。业务仓日常 PR 用 `docs/pull-request-template.md`。

## 谁必须 Review

- `rules/**` 须在业务仓或 monorepo 的 **CODEOWNERS** 中配置架构 / 后端 Owner（见 `codeowners-guidance.md`）。
- 改动 `00-must-follow.md`、evals 门槛、新增 `shared/` 编号文件：须 **安全或架构** 第二人 Review。

## 变更分类

| 类型 | 示例 | 必做更新 |
|---|---|---|
| **硬变更** | 改 `00`、增删 eval 用例、改 P0/P1 门槛、新增 `shared/NN-*.md` | 下表「硬变更清单」全部 |
| **软变更** | 仅扩写某 shared 段落、docs 附录、examples 注释 | `CHANGELOG.md` + 交叉引用；evals 门槛不变则不必改 rubric |
| **契约变更** | `contracts/openapi.yaml` | 相对 PR base / 上一发布 baseline 做 diff；合并后 Owner 更新 baseline，PR 中不得提前覆盖隐藏差异 |

## 硬变更清单（逐项勾选）

- [ ] `VERSION`（语义化版本）
- [ ] `CHANGELOG.md`
- [ ] `README.md` 文件清单与磁盘一致
- [ ] `docs/rules-package-index.md`
- [ ] `codex/AGENTS.md`（新 shared 主题须增加「按任务阅读」行）
- [ ] `shared/00-must-follow.md`（若上升为硬规则）
- [ ] `shared/10-verification-checklist.md`（若新增检查项）
- [ ] `shared/26-ai-generation.md`（若 AI 须必读新文件）
- [ ] `cursor/*.mdc`：引用路径有效；`alwaysApply` 概览条数/版本与 `00` 一致
- [ ] `evals/README.md`（含 Smoke / Security / Contract / **Business Extension** / Full 套件）
- [ ] `evals/prompts.md`、`evals/rubric.md`、`evals/results-template.md` 用例数与门槛**一致**（**仅此三文件**按 `### Bxx` / 表格计数）
- [ ] 改 eval 主题后：更新 `evals/topic-manifest.yaml`（`python scripts/generate-eval-topic-manifest.py --rules-dir ...`）
- [ ] `evals/smoke-prompts.md`（若改核心 P1 / 套件列表）：**只校验 B 编号覆盖**，不参与提示词正文计数；禁止添加 `### Bxx` 标题
- [ ] 运行 `python scripts/validate-rules-package.py`（或 CI 等价）通过
- [ ] `evals/adoption-checklist.md`、`RELEASE.md`、`docs/onboarding-new-project.md`
- [ ] `cursor/00-project-overview.mdc` 中硬规则条数、evals 门槛
- [ ] 仓库根 `contracts/openapi.yaml` 与 `05-openapi-contract.md` 描述一致
- [ ] 发版前：`evals/prompts.md` **Full** B01–B71（P0 8/8，P1 ≥57/63）

## Evals 计数约定

| 文件 | 是否计入提示词条数 | 校验方式 |
|---|---|---|
| `evals/prompts.md` | **是**（SSOT，`### Bxx` 标题） | 与 rubric、results-template 条数一致 |
| `evals/rubric.md` | 是（P1 表格行） | 与 prompts P1 一致 |
| `evals/results-template.md` | 是（`\| Bxx \|` 行） | 与 prompts 全量一致 |
| `evals/smoke-prompts.md` | **否**（套件索引） | 只校验引用的 B 编号 ⊆ `prompts.md` |

管理端 evals **E41–E43**（Platform Extension：i18n / 实时 / 富文本）**无后端 B 对称用例**；全栈边界见 `docs/fullstack-contract.md` §跨包编号说明与 §管理端 Platform Extension。

自动化：`python scripts/validate-rules-package.py`（发版前 / 改 evals 后必跑）。本 monorepo 已在 `.github/workflows/validate-rules-packages.yml` 接入。

## 发版流程

见 `RELEASE.md`；大版本 / 硬规则变更须跑 Full evals。

## 不要做

- 不要在未配置 CI 工具时文档暗示「默认已通过」。
- 不要未经 ADR 在 `00` 中堆叠无法落地的硬规则。
