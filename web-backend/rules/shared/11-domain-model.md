# Domain Model

1. Entity 对应表结构，放 `domain` 或 `infrastructure.persistence`（按项目分层）。
2. 领域逻辑放在 Entity 或 Domain Service；避免 Controller 堆业务规则。
3. 聚合根对外仅通过 Application Service 修改。
4. 禁止 Entity 携带 `@RestController`、HTTP 相关注解。
5. 乐观锁、逻辑删除字段与 MP 全局配置一致。

轻量项目可简化：Entity + Service，仍遵守 Entity 不出 API。
