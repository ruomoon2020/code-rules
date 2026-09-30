# 持久化规则（MyBatis-Plus 与多数据库）

## 技术栈（默认）

| 组件 | 用途 |
|---|---|
| MyBatis-Plus 3.x | CRUD、`Wrapper`、分页插件、逻辑删除、乐观锁 |
| MyBatis XML | 多表 JOIN、报表、方言函数 |
| Flyway | 结构迁移（按库分目录或 databaseId） |
| HikariCP | 连接池 |

**写代码前**阅读项目：`MybatisPlusConfig`、`Mapper` 样例、分页与 `databaseId` 配置。

## 分层职责

| 层 | 职责 |
|---|---|
| Controller | 无 SQL、无 Mapper |
| Application Service | 事务、编排、DTO ↔ Entity |
| Mapper | 数据访问 |
| XML | 复杂 SQL、方言 |

## MyBatis-Plus 使用

1. 单表 CRUD：`interface UserMapper extends BaseMapper<User>`。
2. 新代码由 Application Service 组合 Mapper；已经继承 MyBatis-Plus `IService` 的存量项目可继续维护，但不得为普通 CRUD 新增只转发 `IService` 的浅层。
3. 条件查询：`LambdaQueryWrapper`，避免硬编码列名字符串。
4. 逻辑删除、乐观锁和自动填充沿用项目已有的 MyBatis-Plus 配置。
   - 使用 `@Version` 时必须注册 `OptimisticLockerInnerInterceptor`。
   - 分页插件不得传入固定 `DbType`，应按当前连接识别方言。分页作用于查询，乐观锁作用于更新；插件顺序不影响版本条件。
   - 未声明字段时，自动填充使用 `created_at` / `updated_at`，不新增 `createTime`。
   - 实体字段 `is_deleted` 必须使用 `@TableField("is_deleted")` 固定列名，避免 `is` 前缀被映射为 `deleted`。
5. 主键未声明时使用 `ASSIGN_ID`（雪花，由应用分配）。表已使用数据库自增时沿用自增，不把同一张表改成雪花。禁止同一库内混用多种主键生成方式。

## XML 规则

1. 路径：`src/main/resources/mapper/**/*.xml`，namespace = Mapper 全限定名。
2. 参数使用 `#{}`；**禁止**对用户输入使用 `${}`。
3. 动态列名/排序：仅允许通过 **白名单 Map** 映射后的 `${}`，见 `19-pagination-query.md`。
4. `resultMap` 显式映射；避免 `SELECT *` 上生产。
5. 大结果集必须分页；禁止一次拉取超阈值行数（见 `16-performance.md`）。

## 多数据库（MySQL / PostgreSQL 等）

### 策略

1. **默认写可移植 SQL**（标准类型、避免专有函数）。
2. 无法移植时：
   - 使用 MyBatis **`databaseId`**（`mysql`、`postgresql`），或
   - XML 放在 `mapper/dialect/mysql/`、`mapper/dialect/postgresql/`（与团队配置一致）。
3. **禁止**在 Service 写 `if (dbType == MYSQL)` 业务分支；顶多在基础设施层选择 Mapper 方法。
4. 方言 SQL 须在 **`docs/sql-dialect-matrix.md`** 登记。

### 配置示例

```yaml
mybatis-plus:
  mapper-locations: classpath*:mapper/**/*.xml
  configuration:
    map-underscore-to-camel-case: true
  global-config:
    db-config:
      logic-delete-field: isDeleted
      logic-delete-value: 1
      logic-not-delete-value: 0
      # 过滤只看 is_deleted。deleted_at 只留删除时间，不要配成逻辑删除字段。
      # 删除时在同一次更新里写入 delete_token、deleted_at、deleted_by。不要只调用 deleteById。
```

`databaseId` 由 `DatabaseIdProvider` 或 vendor 自动识别（MySQL、PostgreSQL）。

### 差异对照（禁止 AI 默认只写 MySQL）

| 能力 | 处理 |
|---|---|
| 分页 | 统一 MP `Page`，禁止手写 `LIMIT` 三套 |
| JSON | 方言 XML 或 Java 处理 |
| UPSERT | 分 dialect 文件，禁止混用 `ON DUPLICATE` 与 `ON CONFLICT` |
| 布尔 | 由 Flyway 迁移定义类型，Java 用 `Boolean` |
| 时刻 | Java 用 `Instant` 或 `OffsetDateTime`；列注释写明 UTC 或偏移 |
| 自然日 | Java 用 `LocalDate`；写明业务时区与闭开区间，禁止用本地时区把无时区时间猜成业务日 |
| 主键 | 未声明时用雪花 ID；已有自增表沿用自增 |

## 读写分离

1. 若使用主从库：写后读敏感路径（创建后立即详情、支付后查单）须明确是否**读主库**，避免复制延迟导致「刚写入查不到」。
2. 只读查询默认走从库须在文档与代码注释中说明；事务内读写在同一连接。
3. 从库延迟须监控；超阈值时告警或自动读主（按项目策略）。

## 事务

1. `@Transactional` 在 application 层；`rollbackFor = Exception.class`（按项目默认）。
2. 只读：`@Transactional(readOnly = true)`。
3. 禁止同类内自调用导致事务失效（须拆分或使用 `TransactionTemplate`）。
4. 跨库操作禁止本地 `@Transactional` 假装分布式事务；须 Seata 等显式方案。

## 归档与历史数据

大表归档、冷热表、历史库查询限制见 `34-data-archival.md`；在线库禁止无计划全表扫描归档。

## 迁移（Flyway）

1. 脚本版本 `V{version}__{description}.sql`。
2. 多库：`*-mysql.sql` / `*-postgresql.sql` 或分目录执行（CI 对各库各跑一遍）。
3. 禁止生产依赖 Hibernate `ddl-auto=update`。
4. **破坏性表结构变更**推荐 expand → migrate → contract 三阶段（见 `22-operability.md`），避免代码回滚后无法读库。

### DDL 注释规范（表 / 字段）

1. 新建表时必须包含**表注释**与**字段注释**，禁止“只有类型没有语义说明”的 DDL。
2. 变更字段语义（名称、业务含义、取值约束）时，必须同步更新字段注释。
3. 注释要求写“业务语义 + 取值约束/单位（如适用）”，不要只写“字段名翻译”。
4. 涉及状态、枚举、金额、时间语义时，注释中必须说明范围或格式（例如 `status: ENABLED/DISABLED`）。
5. 多数据库项目须保证各方言脚本中的注释语义一致（MySQL / PostgreSQL 注释同步维护）。

示例（MySQL）：

```sql
CREATE TABLE biz_order (
  id BIGINT NOT NULL COMMENT '订单ID',
  status VARCHAR(16) NOT NULL COMMENT '状态：CREATED/PAID/CANCELLED'
) COMMENT='订单主表';
```

示例（PostgreSQL）：

```sql
CREATE TABLE biz_order (
  id BIGINT PRIMARY KEY,
  status VARCHAR(16) NOT NULL
);
COMMENT ON TABLE biz_order IS '订单主表';
COMMENT ON COLUMN biz_order.status IS '状态：CREATED/PAID/CANCELLED';
```

## 建表设计基线

1. 表名、字段名、约束名、索引名必须符合 `02-naming.md` 的数据库命名规范；业务表须有稳定业务前缀，禁止临时缩写和拼音混用。
2. 主键未声明时使用雪花 ID，由应用分配。已有自增表沿用自增。禁止同一库内混用多种主键生成方式。
3. 可更新业务表统一 `created_at`、`updated_at`、`created_by`、`updated_by`。逻辑删除沿用项目已启用的字段。未声明时：`is_deleted` 用 `SMALLINT`，`0` 未删除、`1` 已删除，`@TableLogic` 只绑这一列；`delete_token` 未删除为 `0`，删除时写成该行主键，唯一约束是 `(业务键, delete_token)`；`deleted_at`、`deleted_by` 只记录删除时间和操作者，类型与 `created_at`、`created_by` 一致，并在同一次更新里写入。禁止只调用 `deleteById`。禁止用 `(业务键, is_deleted)` 做唯一约束，也禁止把可空的 `deleted_at` 放进唯一键。已有 `del_flag` 或 `deleted` 时继承该字段，不另造 `is_deleted`。恢复时改回 `is_deleted = 0`、`delete_token = 0`，并清空删除时间和操作者，且先确认没有另一行活数据占用同一业务键。逻辑删除不是销毁；保留期过后由任务清除或匿名化个人信息，并另记审计。回收站查询必须显式关闭该表的逻辑删除条件。只追加的审计、流水和日志表不加逻辑删除、`updated_at` 和 `version`。`version` 只加在会被并发修改的行上。租户模型不是 `NONE` 时再统一 `tenant_id`；`NONE` 不把 `tenant_id` 当作缺省列。
4. 字符集与排序规则须统一；MySQL 默认 `utf8mb4`，是否指定 `collation` 由项目基线决定，禁止单表随意漂移。
5. 状态 / 枚举字段须有取值来源：字典表、代码枚举、OpenAPI schema enum 或数据库 `CHECK`；禁止只有 `VARCHAR` 但无取值约束。
6. 金额列禁止 `FLOAT` / `DOUBLE`，并写明币种、精度和舍入。时刻写明时区或明确 UTC；自然日使用日期类型，并写明业务时区与闭开区间。复杂账期再读 `40-money-time-precision.md`。
7. 业务唯一性必须落数据库唯一约束。需要未删除数据唯一时，未声明用 `(业务键, delete_token)`。禁止 `(业务键, is_deleted)`，也禁止把可空 `deleted_at` 放进唯一键。已有逻辑删除字段的库沿用既有令牌或部分唯一索引，不要再加一套。禁止只靠应用层判断。
8. 租户模型不是 `NONE` 时，租户表的唯一约束和查询索引通常须包含 `tenant_id`；跨租户全局唯一必须在注释和 PR 中说明。`NONE` 不追加租户列。
9. 高频查询索引命名：唯一索引用 `uk_{table}_{cols}`，普通索引用 `idx_{table}_{cols}`；索引字段顺序须按等值过滤、范围过滤、排序和选择性评估。
10. 审计、流水、日志类大表须提前定义保留周期、归档方式和核心查询索引，禁止无限增长后再补救。
11. PII / 敏感字段须在注释中标识脱敏或用途边界；禁止把 Token、密码、证件号等敏感明文落普通业务表。
12. DDL 必须可演进：新增字段优先兼容旧代码，删除 / 改类型 / 改语义走 expand → migrate → contract，并提供回滚或前滚策略。

## 索引与约束

1. **查询条件、排序字段、JOIN 键**须在设计与 Review 时评估索引；慢查询须 EXPLAIN。
2. **唯一业务约束**必须落数据库唯一索引（或唯一约束），禁止仅靠应用层「先查再插」。
3. **外键**：是否使用 `FOREIGN KEY` 由项目约定；但无论是否物理外键，引用完整性须有策略（应用校验 / 软关联 / 定期对账）。
4. **大字段**（`TEXT`/`BLOB`/大 JSON）禁止进入高频列表默认 `SELECT`；列表接口只查展示列。
5. **新增索引**须在 PR 说明：选择性预估、写入影响、是否在线 DDL、回滚方式。
6. **禁止**在大表上对未约束关键词做无条件 `LIKE '%keyword%'`（leading `%` 通常无法走索引）；须前缀匹配、搜索引擎或异步检索方案。

## 禁止

- Controller 注入 Mapper。
- Entity 直接返回给 HTTP 客户端。
- XML 拼接用户输入的 `${}`。
- 循环内逐条查询（N+1）；须 JOIN 或批量查询。
