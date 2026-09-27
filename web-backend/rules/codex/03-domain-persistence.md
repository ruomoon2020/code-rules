# Domain & Persistence

- Entity 与表结构、Flyway 脚本同步变更。
- 复杂 SQL 放 XML；简单 CRUD 用 MP。
- 多库：优先可移植 SQL；方言登记 `docs/sql-dialect-matrix.md`。
- 禁止 N+1；批量用批处理接口。

详见 `07-persistence-mybatis.md`、`11-domain-model.md`。
