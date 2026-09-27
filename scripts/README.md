# Monorepo 脚本

| 脚本 | 用途 |
|---|---|
| [`generate-eval-topic-manifest.py`](generate-eval-topic-manifest.py) | 从 `evals/prompts.md` + `rubric.md` 生成 `topic-manifest.yaml` |
| [`eval_topic_manifest.py`](eval_topic_manifest.py) | 共享库：manifest 生成与校验（被各端 validator 引用） |
| [`check-project-adoption.py`](check-project-adoption.py) | **业务仓**接入验收：入口、契约、构建、Level 1 测试治理项目参数、结构化 PR、治理包与 Level 2/3 控制声明的静态结构 |
| [`check-debt-baseline.py`](check-debt-baseline.py) | 存量迁移基线：正则计数与路径白名单防增长 |
| [`validate-release-evidence.py`](validate-release-evidence.py) | 校验 schema v2 发布证据、产物摘要、回滚、可观测、门禁与结构化豁免 |
| [`validate-control-catalog.py`](validate-control-catalog.py) | 校验版本化 SSDF / ASVS / OSPS / SLSA 控制映射和本地验证路径 |
| [`validate-workflow-security.py`](validate-workflow-security.py) | 校验 GitHub Actions 固定完整 SHA、顶层只读权限和受限写权限 |
| [`validate-ai-eval-results.py`](validate-ai-eval-results.py) | 校验 AI Tool Safety 5/5 结果、模型元数据和被测套件摘要 |
| [`prepare-ai-eval-run.py`](prepare-ai-eval-run.py) | 打印套件 digest / 写 fail 骨架（不调模型、不自动满分） |
| [`validate-exceptions.py`](validate-exceptions.py) | 校验机器可读豁免的 90 天期限、审批、补偿控制和关闭证据 |
| [`validate-pr-governance.py`](validate-pr-governance.py) | 校验实际 PR 描述中的追踪矩阵、风险等级、变更类型和占位符 |
| [`sync-common-governance.py`](sync-common-governance.py) | 从根 `docs/` 生成 / 校验 `common-governance/` 发布包，防双 SSOT 漂移 |
| [`generate-rule-catalog.py`](generate-rule-catalog.py) | 校验三端编码规则目录与路由、评测文本引用；语义覆盖仍须人工审查 |
| [`validate-repository.py`](validate-repository.py) | 校验维护文件尾随空白、Markdown 本地链接和 YAML 语法 |

CI 自测：`examples/adoption-fixture/frontend/`、`examples/adoption-fixture/backend-gradle/` + `python -m unittest discover -s scripts/tests`。

## 业务仓接入检查

```bash
# 前端仓
python scripts/check-project-adoption.py --repo /path/to/frontend --stack frontend

# 后端仓（严格：CODEOWNERS + PR 模板必填）
python scripts/check-project-adoption.py --repo /path/to/backend --stack backend --strict

# Gradle 后端自测 fixture
python scripts/check-project-adoption.py --repo examples/adoption-fixture/backend-gradle --stack backend

# 小程序
python scripts/check-project-adoption.py --repo /path/to/miniapp --stack miniapp

# 企业项目：推荐 --level 2（已隐含完整治理包校验）
python common-governance/scripts/check-project-adoption.py --repo /path/to/frontend --stack frontend --level 2

# Level < 2 但仍要强制治理包时，再显式加 --require-governance；需要 CODEOWNERS / PR 模板时叠加 --strict
python common-governance/scripts/check-project-adoption.py --repo /path/to/frontend --stack frontend --strict --require-governance

# 更高目标只报告差距，不伪装成当前已采纳
python common-governance/scripts/check-project-adoption.py --repo /path/to/frontend --stack frontend --level 3 --report-only

# 存量债务 Required 门禁
python common-governance/scripts/check-debt-baseline.py --config migration-baseline.json

# 生产发布证据
python scripts/validate-release-evidence.py --file releases/1.8.0/release-evidence.yaml --artifact dist/app.tar.gz

# 控制目录、Workflow 和 AI Tool Safety 结果
python scripts/validate-control-catalog.py
python scripts/validate-workflow-security.py
python scripts/validate-ai-eval-results.py --file examples/ai-eval-results.yaml --suite web-front/rules/evals/ai-tool-safety.md
python scripts/validate-exceptions.py

# 维护者：校验 common governance 与根 docs 一致
python scripts/sync-common-governance.py
```

## Eval topic manifest

改 `evals/prompts.md` 或 `rubric.md` 后：

```bash
python scripts/generate-eval-topic-manifest.py --all
python web-front/rules/scripts/validate-rules-package.py
```

依赖：`pip install pyyaml`（CI 已装 Python 3.12；若缺 PyYAML 见 workflow）。

## 治理文档

见 [`docs/definition-of-done.md`](../docs/definition-of-done.md) 与 [`docs/rule-exception-process.md`](../docs/rule-exception-process.md)。
