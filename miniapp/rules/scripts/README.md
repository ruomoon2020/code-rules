# 小程序规则包校验脚本

`validate-rules-package.py` 用于发现规则包内部漂移，包括 VERSION/CHANGELOG、evals 编号与套件、README 路径，以及 Cursor/AGENTS 对 shared 的引用。它不执行 AI 对话评测，也不构建小程序。

## 运行方式

```bash
python miniapp/rules/scripts/validate-rules-package.py
# 业务仓内 rules/ 目录：
python rules/scripts/validate-rules-package.py --rules-dir rules
```

## 校验范围

| 项 | 说明 |
|---|---|
| VERSION ↔ CHANGELOG | 最新版本一致 |
| evals 计数 | 仅 `prompts.md` 的 `### Mxx` 计条数；rubric 与套件编号一致 |
| smoke-prompts | **索引**：禁止 `### Mxx`；M 编号须存在于 prompts |
| 套件 | Smoke、Security、Contract、Business Extension、Resilience、Enterprise Hardening、Component Engineering、Testing Governance 与 `evals/README.md` 一致 |
| 门槛 | P0 `8/8`、核心 P1 `10/12` 及各专项门槛一致 |
| 硬规则 | `shared/00-must-follow.md` 条数、主题与 `cursor/00-project-overview.mdc` 一致 |
| README / 路径 | README 清单路径、Cursor 与 Codex 对 shared 的引用存在 |
| 跨包 | 前端、后端与 common-governance 引用在 monorepo 中存在 |

## 什么时候运行

- 维护仓修改 `miniapp/rules/**` 后运行第一条命令。
- 业务仓升级嵌入的 `rules/` 后运行第二条命令。
- 规则、路由或 evals 变更后，同时运行 `python -m unittest discover -s miniapp/rules/scripts/tests -v`。

monorepo PR 改动 `miniapp/rules/**` 时，`.github/workflows/validate-rules-packages.yml` 会自动执行校验。业务功能仍须另行运行 `pnpm lint`、`pnpm type-check`、目标平台构建、契约检查和包体积检查。
