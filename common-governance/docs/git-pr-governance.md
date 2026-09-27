# Git 与 Pull Request 治理

> 适用于各技术栈；服务端分支保护和 Required Checks 是最终门禁，本地 hook 只负责提前反馈，不能替代 CI。

## Commit Message

默认采用 Conventional Commits：

```text
<type>(<optional-scope>): <summary>
```

常用 `type`：`feat`、`fix`、`refactor`、`test`、`docs`、`build`、`ci`、`chore`、`revert`。

要求：

1. summary 描述可观察变更，不写“update”“misc”等无信息内容。
2. breaking change 使用 `!` 或 footer，并附兼容、迁移和回滚说明。
3. 一个提交只承载一个可审阅意图；生成文件与其源变更同提交。
4. 禁止在提交信息、分支名和 PR 标题中写入凭据、用户隐私或生产数据。

## 分支与 Pull Request

1. 受保护分支禁止直接推送；通过 PR、Required Checks 和 CODEOWNERS 合并。
2. PR 描述必须包含范围、需求 / Issue、逐条验收条件、风险、验证证据、跳过项和回滚方式；业务变更按 `requirements-traceability.md` 建立追踪矩阵。
3. 契约、数据库、安全、CI 和规则包变更按 `codeowners-matrix.md` 请求 Reviewer。
4. 跳过门禁或紧急合并必须走 `rule-exception-process.md`，记录 Owner、期限和补偿控制。
5. 合并策略由项目统一选择；禁止因个人偏好在同一仓库混用不可追溯策略。

## 自动化

- commitlint 可在 CI 中校验 PR 标题或提交；配置样板随 common governance 包分发。
- Husky / lint-staged 可作为前置反馈，但必须允许在受控场景绕过，并由 CI 重新验证。
- 不使用 Node.js 的仓库可以采用平台原生规则校验 PR 标题，无需为了 commitlint 引入 Node 工具链。
- 自动生成 changelog 时，release 仍须由 Owner 审阅 breaking change 和回滚信息。
- PR CI 运行 `scripts/validate-pr-governance.py --event "$GITHUB_EVENT_PATH"`，校验追踪矩阵、风险等级、变更类型和未清理占位符；模板存在不等于实际 PR 已填写。

落地时同时配置 `branch-protection.md`、`codeowners-matrix.md` 和业务仓 PR 模板。生产发布按 `release-evidence.md` 生成结构化证据。
