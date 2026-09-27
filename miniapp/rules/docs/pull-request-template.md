# PR 模板说明（维护者）

业务仓将 `rules/examples/.github/pull_request_template.md` 复制到仓库根 `.github/pull_request_template.md`。

与 `shared/00`、`evals/adoption-checklist.md` 对齐；成熟业务分包 PR 额外勾选 Business Extension（M21–M29）。

业务 PR 还须包含需求 / Issue、逐条验收条件、实现 / 契约和测试证据矩阵，并按 `common-governance/docs/business-correctness-review.md` 复核工作流、数据、权限、端到端状态与回归风险。

发布相关 PR 还须填写灰度范围、审核环境、回滚步骤与 Owner，并附可观察指标。
