# 前端规则包校验脚本

`validate-rules-package.py` 面向规则维护者和已嵌入 `rules/` 的业务仓，用于发现版本、路由、引用、评测清单和硬规则摘要之间的漂移。它只做确定性静态校验，**不会**执行 AI 对话评测，也不会证明前端业务功能正确。

## 运行方式

```bash
python scripts/validate-rules-package.py
python rules/scripts/validate-rules-package.py --rules-dir rules
```

## 校验范围

| 项 | 说明 |
|---|---|
| VERSION ↔ CHANGELOG | 最新版本一致 |
| evals 计数 | 仅 `prompts.md` 的 `### Exx` 计条数 |
| smoke-prompts | **索引**：禁止 `### Exx`；E 编号须存在于 prompts |
| 套件 | Smoke 核心 P1、Security、Contract、Business、Platform、**Enterprise Hardening**（E44–E49）、Testing Governance（E31/E50）与 `evals/README.md` 一致 |
| 门槛 | 多文件 `39/42`（随 rubric 动态）一致 |
| 硬规则 | `00` 固定 34 条、条件路由边界、主题防回流，并与 `cursor/00` 一致 |
| README / cursor | 清单路径与 shared 引用；**README 须列出全部 `shared/*.md`** |
| 跨包 / Codex | `web-backend/rules/` 引用存在；`codex/AGENTS.md` 的 `rules/...` 路径存在 |

单元测试（CI 同时执行）：

```bash
python -m unittest discover -s scripts/tests -v
```

## CI 接入

| 场景 | Workflow |
|---|---|
| code-rules monorepo | 仓库根 `.github/workflows/validate-rules-packages.yml` |
| 业务仓 | 复制 `examples/ci/rules-package-validate.yml` |

建议将该校验与业务仓的 `lint`、`type-check`、测试和构建并列执行。修改规则正文、Codex/Cursor 路由或 evals 后，应先运行本脚本，再运行单元测试；仅修改业务页面时，仍以业务仓自身的质量门禁为主。
