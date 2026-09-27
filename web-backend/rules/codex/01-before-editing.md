# Before Editing

1. 读 `00-must-follow.md`。
2. 确认任务类型：API、Service、Mapper/SQL、安全、配置、测试。
3. 按 `AGENTS.md` 追加 `shared/`、`codex/`。
4. 收集上下文：OpenAPI、既有 Mapper/XML、MP 配置、支持的数据库列表。

## 不要开写直到

- 明确改动在哪一层（api / application / infrastructure）。
- 字段是否在 OpenAPI 中存在。
- 是否涉及方言 SQL（须查 `sql-dialect-matrix.md`）。
