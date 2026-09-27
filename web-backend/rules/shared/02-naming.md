# Naming Rules（Java / Spring）

## 总原则

1. 英文语义命名；包名全小写；类名 PascalCase。
2. 同一概念全项目一词；先看项目既有约定，再按本文件。
3. 禁止 `Manager`、`Helper`、`Util` 膨胀；优先领域名 + 职责。

## 包与类

| 类型 | 规则 | 示例 |
|---|---|---|
| 包 | 小写，点分隔 | `modules.system.application` |
| Controller | `*Controller` | `UserController` |
| Service | `*Service` / `*AppService` | `UserService` |
| Mapper | `*Mapper` | `UserMapper` |
| Entity | 单数名词 | `User` |
| Request DTO | `*Request` | `UserCreateRequest` |
| Response DTO | `*Response` / `*VO` | `UserPageResponse` |
| 异常 | `*Exception` | `BusinessException` |
| 常量类 | `*Constants` | `ErrorCodes` |

## 方法与变量

| 动作 | 前缀 |
|---|---|
| 查询单条 | `get` / `find` |
| 查询列表/分页 | `list` / `page` / `query` |
| 新增 | `create` / `add` |
| 更新 | `update` |
| 删除 | `delete` / `remove` |
| 是否存在 | `exists` |
| 导入导出 | `import` / `export` |

布尔：`is`、`has`、`can`。禁止裸名 `data`、`flag`、`result`（除局部极短作用域）。

## 数据库

### 表名

1. 表名使用 `lower_snake_case`，禁止大写、驼峰、空格、连字符、拼音和临时缩写。
2. 表名使用**单数名词**或团队统一复数；同一业务库必须一致，推荐单数：`sys_user`、`biz_order`。
3. 业务表必须有稳定域前缀：`sys_`、`biz_`、`crm_`、`pay_`、`iam_` 等；禁止 `t_`、`tb_`、`tmp_` 作为正式业务表前缀。
4. 中间表命名为 `{left}_{right}_rel` 或 `{domain}_{relation}`，字段为 `{left}_id`、`{right}_id`，例如 `sys_user_role_rel`。
5. 审计 / 日志 / 流水表使用明确后缀：`_audit_log`、`_change_log`、`_operation_log`、`_flow`，并在表注释中写清保留周期或归档策略。
6. 历史 / 归档表使用 `_history`、`_archive` 后缀；禁止直接复制线上表后随意命名为 `_bak`、`_old`、`_new`。
7. 临时表仅允许迁移或数据修复脚本内部使用，命名为 `tmp_{ticket}_{purpose}`，必须有清理步骤和有效期说明。

### 字段名

1. 字段名使用 `lower_snake_case`；Java / OpenAPI 字段保持 camelCase 映射，例如 `created_at` ↔ `createdAt`。
2. 主键统一命名为 `id`；引用其他实体使用 `{entity}_id`，如 `user_id`、`order_id`，禁止 `uid`、`userId`、`userid` 混用。
3. 时间字段统一使用 `_at` 表示时刻，`_date` 表示自然日，`_time` 仅用于时分秒语义；常用字段为 `created_at`、`updated_at`、`occurred_at`、`expired_at`。
4. 操作人字段统一使用 `_by` 后缀：`created_by`、`updated_by`、`deleted_by`；字段类型须与用户 ID 主键策略一致。
5. 布尔 / 标记字段禁止含糊的 `flag`、`type_flag`；使用 `is_`、`has_`、`can_` 前缀或明确状态字段，例如 `is_default`、`has_children`。
6. 状态字段优先使用 `status`；多个状态必须加业务限定，例如 `payment_status`、`approval_status`。取值必须在注释、字典或 OpenAPI enum 中登记。
7. 类型字段使用 `{domain}_type` 或 `type`，但必须有明确字典来源；禁止 `kind`、`category`、`class` 混用表达同一概念。
8. 金额字段必须带语义和单位策略，例如 `amount_cent`、`paid_amount`、`currency_code`；禁止裸 `money`、`price1`、`fee_tmp`。
9. 数量字段使用 `_count`，比率字段使用 `_rate`，百分比字段使用 `_percent`，并在注释中说明单位、精度和范围。
10. 外部系统字段须有来源前缀或后缀，例如 `wechat_open_id`、`alipay_trade_no`、`external_order_no`。
11. 敏感字段命名应表达用途边界，例如 `phone_masked`、`id_card_ciphertext`、`token_hash`；禁止 `password` 存明文，禁止字段名掩盖敏感属性。
12. 大字段使用明确后缀：`_json`、`_text`、`_summary`、`_snapshot`，并避免进入列表默认查询。

### 约束与索引命名

| 类型 | 命名格式 | 示例 |
|---|---|---|
| 主键 | `pk_{table}`（数据库需显式命名时） | `pk_sys_user` |
| 唯一约束 / 唯一索引 | `uk_{table}_{cols}` | `uk_sys_user_username` |
| 普通索引 | `idx_{table}_{cols}` | `idx_sys_audit_log_operator_occurred` |
| 外键约束（若使用） | `fk_{table}_{ref_table}_{cols}` | `fk_order_user_user_id` |
| 检查约束 | `ck_{table}_{column}` | `ck_order_status` |

1. 索引名中的列名按索引实际字段顺序排列；过长时可保留关键字段，但必须能从名称看出用途。
2. 唯一约束优先表达业务唯一性；多租户唯一通常包含 `tenant_id`，例如 `uk_crm_customer_tenant_phone`。
3. 逻辑删除表若需要“未删除数据唯一”，必须明确采用组合唯一、部分索引或归档释放策略，禁止只写普通唯一导致删除后无法重建。
4. 同一张表禁止出现语义重复索引，例如 `idx_user_name` 与 `idx_sys_user_username` 同时存在。

### Mapper / XML

1. Mapper 方法名与 XML `id` 一致。
2. 自定义查询方法按动作 + 条件命名，例如 `selectByUsername`、`pageByTenantId`、`countActiveUsers`。
3. 批量方法必须带 `Batch`，异步 / 补偿方法必须体现语义，禁止 `handleData`、`doProcess`。

## 错误码与权限

1. 业务错误码：`DOMAIN_RESOURCE_REASON`，如 `USER_NOT_FOUND`（与 `08` 一致）。
2. 权限码：`domain:resource:action`，如 `system:user:create`（与前端对齐）。

## REST 与 OpenAPI

1. 路径 kebab-case 复数资源：`/api/v1/system/users`。
2. 查询参数 camelCase，与 DTO 字段一致。
