# 代码规则仓库说明

## 适用范围

本仓库维护可复用的管理端、后端、小程序和跨端治理规则包，不是业务应用。

## 权威来源

- 可执行编码规则位于各技术栈包的 `rules/shared/`。
- Codex 路由位于各包的 `rules/codex/AGENTS.md`，Cursor 路由位于 `rules/cursor/`。
- 根目录 `docs/` 是治理 SSOT；`common-governance/docs/` 为生成目录，不得直接修改。
- 立项、架构方案和上线前评审使用 `docs/architect-engineering-checklist.md`；合并与发布强制门禁以 `docs/definition-of-done.md` 为准。
- 项目路径、脚本、技术选择和采纳 Level 写入业务仓的 `AGENTS.md` 与 `99-project-local.mdc`。
- 存量项目接入时，目标规则仍保留在规则包，以机器基线记录现有债务；遵循 `docs/migration-baseline.md`，不得通过弱化共享规则迁移。

## 变更收口

修改规则时，同步更新路由、验证清单、行为变化对应的评测覆盖、包 VERSION、CHANGELOG、README/索引和发布清单。不得新增没有触发路径或验证路径的规则。

Level 0 只写所有项目都要遵守的条款。遇到具体场景，再读对应规则和成熟度说明。

## 验证

先运行最近的包校验器和测试，再运行仓库治理套件：

```text
python web-front/rules/scripts/validate-rules-package.py
python web-backend/rules/scripts/validate-rules-package.py
python miniapp/rules/scripts/validate-rules-package.py
python -m unittest discover -s web-front/rules/scripts/tests -v
python -m unittest discover -s web-backend/rules/scripts/tests -v
python -m unittest discover -s miniapp/rules/scripts/tests -v
python -m unittest discover -s scripts/tests -v
python scripts/validate-repository.py
python scripts/generate-rule-catalog.py
python scripts/sync-common-governance.py
python common-governance/scripts/validate-package.py
git diff --check
```

报告跳过的检查和剩余风险。校验器通过只能证明规则包一致，不能单独证明业务正确。
