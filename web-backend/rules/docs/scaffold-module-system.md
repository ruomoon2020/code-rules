# 模块脚手架：system（示例）

可复制为首个业务域模板。

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

## 可复制源码

完整 Java/XML 样板（改包名后粘贴到 `src/`）：

```text
rules/examples/scaffold/java/...
rules/examples/scaffold/resources/mapper/...
```

见 `examples/scaffold/README.md`。
