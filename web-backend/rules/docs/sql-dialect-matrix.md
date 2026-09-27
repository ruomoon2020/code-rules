# SQL 方言登记矩阵（维护者）

AI 新增/修改**不可移植** SQL 时，必须在本表登记。

| Mapper 方法 | databaseId | 数据库 | 说明 | 负责人 |
|---|---|---|---|---|
| （示例）`UserMapper.searchByJson` | `postgresql` | PostgreSQL | 使用 `jsonb` | |
| （示例）`UserMapper.upsert` | `mysql` | MySQL | `ON DUPLICATE KEY` | |
| （示例）`UserMapper.upsert` | `postgresql` | PostgreSQL | `ON CONFLICT` | |

## 规则

1. 无登记记录的方言 SQL 不得合并。
2. CI 应对登记项在对应库跑集成测试。
3. 可移植 SQL 不需登记。

## 目录约定

```text
resources/mapper/common/          # 无 databaseId，双库可跑
resources/mapper/dialect/mysql/
resources/mapper/dialect/postgresql/
```
