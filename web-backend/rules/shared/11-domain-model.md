# 领域模型规则

1. Entity 对应表结构，放 `domain` 或 `infrastructure.persistence`（按项目分层）。
2. 默认 `CRUD_LITE` 由 Application Service 编排业务规则，Entity 保持轻量；只有模块显式声明 `DOMAIN_HEXAGONAL` 时，才将聚合不变量放入 Entity、值对象或 Domain Service。
3. `DOMAIN_HEXAGONAL` 的聚合根对外仅通过 Application Service 修改；其他架构档同样禁止 Controller 承载或拼装业务规则。
4. 禁止 Entity 携带 `@RestController`、HTTP 相关注解。
5. 乐观锁、逻辑删除字段与 MP 全局配置一致。未声明时 `@TableLogic` 只绑 `is_deleted`；`delete_token` 保证未删除唯一；`deleted_at` 只留删除时间。只追加的日志和流水不加逻辑删除和 `version`。

轻量项目默认使用 Application Service + Mapper/Repository 组合，仍遵守 Entity 不出 API；不得为普通 CRUD 额外创建只做转发的 Domain Service。

## 存量经典分层对象兼容

已有项目使用 `CLASSIC_LAYERED` 和以下对象后缀时可继续维护；它是存量兼容写法，不是与默认 Entity/Request/Response 并列的新项目标准，也不要求每种对象都存在：

| 类型 | 职责与流向 |
|---|---|
| DO | 与持久化结构对应，`DAO -> Service/Manager`；不得直接作为接口响应 |
| Query / Param | 查询或命令入参；Controller 校验后传给 Service |
| DTO | 跨 Service、模块、RPC 或开放接口传输 |
| BO | Service 内部封装复杂业务计算或组合结果 |
| VO | 面向页面或调用场景的展示对象，`Web -> Client` |
| AO | 可选的 Web 与 Service 之间应用对象；复用度低时不要引入 |

不得为了“对象齐全”机械地在 DO、BO、DTO、VO 之间逐层复制相同字段。只有安全边界、字段语义或调用场景发生变化时才增加转换接缝；不得为了套用默认规则而批量重命名稳定存量对象。
