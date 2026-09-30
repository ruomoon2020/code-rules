# 模块脚手架：system（示例）

可复制为首个业务域模板。

本样板用轻量分层：应用服务直接调用 Mapper（`CRUD_LITE`）。核心业务如果改成六边形，仓储接口放在领域层，由 infrastructure 实现，不要在这个样板上再加一层只做转发的类。

接口对象默认用 Request / Response（`ENTITY_REQUEST_RESPONSE`），与 `examples/99-project-local.mdc.sample`、`examples/AGENTS.project-section.md.sample` 一致。旧项目已经稳定使用 DO / DTO / BO / VO（`DO_DTO_BO_VO_QUERY`）时，保持原来的名字和转换关系。新项目不要为了凑齐这些后缀再加一层对象，旧项目也不要只为了统一后缀做大规模改名。

可执行样板默认采用单租户（`NONE`），用户、审计、数据库和 OpenAPI 均不含租户字段。项目已有 `tenant_id`、租户插件或拦截器时改为共享表加租户列（`SHARED_COLUMN`），并在实体、所有查询与写入入口、审计、索引、契约和隔离测试中成套适配。逻辑删除用 `isDeleted` 过滤，`deleteToken` 保证未删除用户名唯一，`deletedAt` 只记录删除时间。

## 目录

```text
src/main/java/com/company/product/
├─ common/
│  ├─ exception/BusinessException.java
│  ├─ exception/GlobalExceptionHandler.java
│  ├─ web/ApiResult.java
│  ├─ web/PageResponse.java
│  ├─ observability/TraceIdFilter.java
│  └─ audit/AuditContext.java
├─ config/
│  ├─ MybatisPlusConfig.java          ← 见 examples/config/MybatisPlusConfig.sample.java
│  └─ SecurityConfig.java           ← 见 examples/config/SecurityConfig.sample.java
└─ modules/system/
   ├─ api/
   │  ├─ UserController.java
   │  ├─ AuditLogController.java
   │  ├─ dto/UserCreateRequest.java
   │  ├─ dto/AuditLogPageQuery.java
   │  ├─ dto/AuditLogSummaryResponse.java
   │  └─ dto/UserSummaryResponse.java
   ├─ application/
   │  ├─ UserService.java
   │  ├─ AuditLogService.java
   │  ├─ audit/AuditRecorder.java
   │  ├─ audit/AuditLogRecorder.java
   │  └─ converter/UserConverter.java
   ├─ domain/
   │  ├─ User.java
   │  └─ AuditLog.java
   └─ infrastructure/
      └─ mapper/UserMapper.java, AuditLogMapper.java

src/main/resources/
├─ application.yml
├─ mapper/system/UserMapper.xml
└─ db/migration/
   ├─ mysql/V1__init_system_user.sql
   ├─ mysql/V2__init_system_audit_log.sql
   ├─ postgresql/V1__init_system_user.sql
   └─ postgresql/V2__init_system_audit_log.sql
```

## 职责

| 类 | 职责 |
|---|---|
| UserController | 校验、鉴权、调 Service、返回 DTO |
| UserService | `@Transactional`、业务、转 DTO、调 Mapper；删除时写审计 |
| AuditRecorder | 敏感操作结构化审计落库 |
| UserMapper | `BaseMapper<User>` + 自定义 XML |
| UserConverter | MapStruct Entity ↔ DTO |

## 禁止

- `UserController` 注入 `UserMapper`
- `UserController` 返回 `User` Entity

## 契约

接口定义以 `contracts/openapi.yaml` 中 `systemUser*` 为准。

- 当前样板声明 `x-api-style: GET_POST_COMPAT`，适配只放行 GET/POST 的企业网关。
- 创建：`201 Created` + `Location`。
- 部分更新：`POST /users/{id}/update`。
- 删除：`POST /users/{id}/delete`，成功 `204 No Content` + 可选 `X-Trace-Id`。
- 用户与审计接口均有 `@PreAuthorize`；权限码须与菜单、前端按钮和项目 OpenAPI 可追溯。

## 可复制源码

完整 Java/XML 样板（改包名后粘贴到 `src/`）：

```text
rules/examples/scaffold/java/...
rules/examples/scaffold/resources/mapper/...
```

见 `examples/scaffold/README.md`。
