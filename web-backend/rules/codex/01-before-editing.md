# 修改前检查

1. 读 `00-must-follow.md`。
2. 读取业务仓根 `AGENTS.md` 里已经写明的分层、接口风格或租户差异，并查看现有表、租户插件或租户拦截器。没有写明时用轻量分层和 Request / Response，查询用 GET、写入用 POST（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`、`GET_POST_COMPAT`），SQL 只访问本模块的表。看不出租户时按单租户处理（`NONE`）。已有 `tenant_id`、租户插件或租户拦截器时，沿用共享表加租户列（`SHARED_COLUMN`），不要再做一套。只有公网接口、要改隔离方式，或出现跨模块写入时，才补决策。
3. 确认任务类型：API、Service、Mapper/SQL、安全、配置、测试。
4. 按 `AGENTS.md` 追加 `shared/`、`codex/`。
5. 收集上下文：OpenAPI、既有 Mapper/XML、MP 配置、支持的数据库列表。

## 不要开写直到

- 明确改动在哪一层（api / application / infrastructure）。
- 本轮用默认的轻量分层和 Request / Response（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`），或项目已经写明的经典分层、六边形。普通增删改查不因为没写这些就停下来。
- 普通单模块默认只写自己的表。看不出租户时用单租户（`NONE`）；已有租户列、插件或拦截器时用共享表加租户列（`SHARED_COLUMN`）。要改隔离方式，或要写其他模块的表时，先写清隔离方式、哪些表不按租户隔离，以及这张表由哪个模块写入。
- 字段是否在 OpenAPI 中存在。
- 是否涉及方言 SQL（须查 `sql-dialect-matrix.md`）。
