# 项目结构规则

## 推荐包结构（单模块）

```text
src/main/java/com/company/product/
├─ ProductApplication.java
├─ common/
│  ├─ exception/
│  ├─ web/              # GlobalExceptionHandler、统一响应
│  ├─ observability/    # TraceIdFilter、MDC
│  └─ util/
├─ config/              # Security、MyBatis、OpenAPI
└─ modules/
   └─ system/
      ├─ api/           # Controller、*Request、*Response
      ├─ application/   # *Service（@Transactional）
      ├─ domain/        # Entity、领域服务（可选）
      └─ infrastructure/
         └─ mapper/     # Mapper 接口

src/main/resources/
├─ application.yml
├─ mapper/
│  ├─ common/           # 可移植 SQL
│  └─ dialect/
│     ├─ mysql/
│     └─ postgresql/
└─ db/migration/        # Flyway
   ├─ mysql/            # 可选：按库分子目录
   └─ postgresql/
```

## Domain / Hexagonal 多模块（条件启用）

```text
product-api          # Controller + DTO（仅依赖 application 接口）
product-application  # Service、用例
product-domain       # Entity、仓储接口
product-infrastructure # Mapper、XML、外部适配
```

依赖：`api → application → domain`；`infrastructure` 实现 domain 接口并依赖 MyBatis。

## 默认架构与兼容档

新项目、普通管理端，以及没有写明分层的模块，直接用轻量分层：Controller、应用服务、Mapper，接口对象用 Request / Response（`CRUD_LITE`、`ENTITY_REQUEST_RESPONSE`）。不要先做三选一，也不要为了以后可能变复杂，预先加上 Manager、仓储端口或适配器。

| 代码 | 叫法 | 什么时候用 | 调用方向 | 数据访问 |
|---|---|---|---|---|
| `CRUD_LITE` | 轻量分层，新项目默认 | 普通增删改查、管理端、常规业务服务；没写明时就用这个 | `Controller -> ApplicationService -> Mapper/Repository` | 应用服务调用 Mapper 或 Repository。已经在用 MyBatis-Plus `IService` 的旧项目可以继续维护。表对象和接口的 Request / Response 分开 |
| `CLASSIC_LAYERED` | 经典分层，只留给旧项目 | 项目已经稳定使用 Web / Service / Manager / DAO，或 DO / DTO / BO / VO | `Web -> Service -> Manager(可选) -> DAO` | 继续用现有 DAO / Mapper。Manager 只放跨 DAO 组合、第三方封装或可复用逻辑 |
| `DOMAIN_HEXAGONAL` | 六边形，复杂业务才用 | 聚合或状态流转复杂，有多种入口或多种存储，或者测试必须替换数据库 | `api -> application -> domain` | 仓储接口放在 domain 或 application，`infrastructure` 提供实现 |

只有偏离默认分层时，才需要在项目中说明。存量项目使用经典分层时，将选择记录在 `99-project-local`。改用六边形架构时，ADR 须说明复杂度来源、预期收益、迁移方案和回滚方案，并通过 ArchUnit 或同等检查约束依赖方向。轻量分层不得增加只负责转发的层，也不得仅为统一后缀而重命名稳定对象。

## 经典应用分层（可选）

已采用经典企业分层的存量项目，可在 `99-project-local` 声明 `CLASSIC_LAYERED` 并继续维护：

```text
开放接口 / 网关 -> Web(Controller) -> Service -> Manager(可选) -> DAO -> DB
```

| 层 | 职责 | 约束 |
|---|---|---|
| 开放接口层 | HTTP / RPC 暴露、网关、限流、协议适配 | 不承载业务规则 |
| 终端显示层 | 服务端模板、BFF 的页面适配（如果有） | 前后端分离时，这一层通常在前端或 BFF，后端不必为它单独建目录 |
| Web | 参数接收、校验、鉴权、DTO/VO 转换 | 禁止直调 DAO |
| Service | 用例编排、事务、业务逻辑 | 对上提供稳定业务接口 |
| Manager | 第三方封装、跨 DAO 组合、可复用复杂能力 | 可选；禁止只转发 Service/DAO 的空壳 |
| DAO | 数据访问 | 禁止向上泄露 SQL、持久化框架细节 |

这套结构与 DO / DTO / BO / VO / Query 对象分类受国内企业 Java 规范广泛影响，但其中分层和对象分类是推荐 / 参考做法，不得写成所有项目的强制基线。存量项目可保持；新项目不以“国内规范”为理由复制整套后缀和空层。

经典分层和六边形都可以显式选用，但同一个模块不要同时保留 Manager/DAO 和端口/适配器两套做法。依赖只能从上往下。公共能力做成小接口，实现放在模块里面，不要再加只做转发的层。

## 依赖方向

允许：

```text
Controller -> ApplicationService -> Mapper      # CRUD / Lite
ApplicationService -> Domain Entity / Domain Service
Mapper XML -> 数据库
```

禁止：

```text
Controller -> Mapper
domain -> infrastructure 具体实现（应依赖接口）
common -> modules 业务包
```

## 放置规则

1. 一个业务域一个 `modules/{name}`，避免巨型 `service` 包。
2. Mapper 接口与 XML 同名：`UserMapper.java` ↔ `UserMapper.xml`。
3. 跨模块复用 DTO 放 `api` 或独立 `contract` 模块，禁止复制粘贴。
4. 命名与路径见 **`02-naming.md`**；持久化见 **`07-persistence-mybatis.md`**。
5. 首个业务域可复制 **`docs/scaffold-module-system.md`**。
6. 跨模块调用只经对方公开的 application/api 接口或事件；禁止导入对方 `infrastructure`、Mapper 或内部 Entity。
7. Level 0 项目未声明时按 `CRUD_LITE` 检查；显式采用 Classic 或 Hexagonal 时，用 ArchUnit 或等价检查锁定对应依赖方向，防止多套接缝无声混用。
8. 若采用经典应用分层，须用 ArchUnit 或等价检查禁止 `Controller -> DAO`、`DAO -> Service`、`Manager -> Controller` 等反向或跨层依赖。
9. 业务 SQL（含 Mapper XML、注解 SQL、批处理脚本）必须只读写本模块拥有的业务表；表前缀或项目表所有权清单用于判定归属，禁止通过 `JOIN`、子查询、存储过程或直接 `UPDATE` 绕过模块边界访问其他业务模块或平台系统表。
10. 跨模块只保存对方公开 ID，并经对方 application/api 接口或事件获取事实；需要跨域分析时可建立独立只读查询 / 报表模块或读模型，但该路径禁止回写源模块表。
11. 一个聚合或业务事实必须只有一个写入模块；其他模块只能保存关联 ID 或订阅事件维护自己的读模型，禁止共同更新同一状态列。
12. 同一个业务模块里，一组一起修改的数据可以用本地事务。一个 `@Transactional` 不能同时写两个业务模块的表。跨模块写入要调用对方的公开接口，或通过 Outbox、消息完成。不要用一个数据库事务把两个模块绑成同一次提交。
