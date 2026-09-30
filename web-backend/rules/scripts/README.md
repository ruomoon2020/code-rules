# 后端规则包校验脚本

`validate-rules-package.py` 用于校验后端规则包的版本、路由、文件引用、示例约束和评测套件是否一致。它服务于规则包维护和业务仓接入，不执行 AI 对话评测，也不能代替 `mvn verify`、`./gradlew check` 或业务正确性评审。

## 运行方式

```bash
# 在 web-backend/rules 目录
python scripts/validate-rules-package.py

# 指定 rules 根目录（业务仓嵌入 rules/ 时）
python rules/scripts/validate-rules-package.py --rules-dir rules
```

## 校验范围

| 项 | 说明 |
|---|---|
| VERSION ↔ CHANGELOG | 最新版本一致 |
| evals 计数 | 仅 `prompts.md` 的 `### Bxx` 计条数；`rubric` / `results-template` 对齐；高风险 ID 主题守卫防止 rubric 语义换位 |
| smoke-prompts | **索引**：禁止 `### Bxx`；B 编号须存在于 prompts |
| 套件 | Smoke 核心 P1、Security、Contract、**Architecture**（B01/B10/B55/B67–B69）、**Business Extension**（B55–B63）、**Testing Governance**（B29/B42）与 `evals/README.md` 一致 |
| 门槛 | 多文件 `57/63`（随 rubric 动态）一致 |
| 异常样板 | 业务异常 WARN + stack、5xx ERROR + cause、方法级校验 400、401/403/404/429 无堆栈、路由模板 path |
| 跨包 | `web-front/rules/` 引用须存在于 monorepo（见 `CROSS_FRONT_REF`） |
| 硬规则 | `00` 条数与 `cursor/00-project-overview.mdc` 一致 |
| README 清单 | `shared/`、`docs/` 等路径存在（排除 monorepo 外链路径） |
| cursor | `shared/NN-*.md` 引用存在，禁止裸 `NN-*.md` shared 引用 |
| Codex 路由 | `codex/AGENTS.md` 的 `rules/shared|docs|codex/...` 路径存在 |

单元测试（CI 同时执行）：

```bash
python -m unittest discover -s scripts/tests -v
```

## CI 接入

| 场景 | Workflow |
|---|---|
| 本 monorepo | 仓库根 `.github/workflows/validate-rules-packages.yml` |
| 业务仓 | 复制 `examples/ci/rules-package-validate.yml` |

规则正文、Codex/Cursor 路由、示例或 evals 发生变化时，应同时执行本脚本和单元测试。业务代码变更还必须运行项目实际的编译、测试、契约和数据库迁移检查。
