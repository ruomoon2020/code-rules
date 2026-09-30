# Java 业务模块源码样板

本目录展示 Controller、应用服务、领域对象、Mapper、审计、数据权限和集成测试之间的最小协作方式，适合在新模块设计时按需参考。

> 这不是可直接运行的模块。复制到业务项目后，必须修改包名 `com.company.product`，接入项目现有响应结构、鉴权、数据权限、事务、数据库迁移和测试基础设施。

| 路径 | 说明 |
|---|---|
| `java/common/` | 统一响应、异常、traceId、`audit/AuditContext`、显式 `DataScopePolicy` |
| `java/modules/system/` | 用户域 + 审计读写（`AuditRecorder`、`AuditLog*` API） |
| `java/test/` | `UserControllerIT`、`AuditLogControllerIT` 集成测试样板，含旧版本更新/删除与审计回滚 |
| `db/migration/*/V2__init_system_audit_log.sql` | 审计表样板，字段对齐 OpenAPI |
| `resources/mapper/system/UserMapper.xml` | 可移植列表 SQL |

| `../config/SecurityConfig.sample.java` | Security 鉴权样板（**复制前必读** CSRF / Swagger / Actuator 注释） |

## 落地顺序

1. 先确认 OpenAPI、权限码、数据范围和审计要求。
2. 只复制当前业务需要的源码，不整目录覆盖已有平台模块。
3. 修改包名、表名、错误码和 Security 配置，并补齐真实依赖。
4. 将 migration、Mapper 与 DTO 字段和契约逐项对齐。
5. 运行项目的单元测试、集成测试、ArchUnit、契约检查和数据库迁移验证。

配套说明见 `docs/scaffold-module-system.md`、`../config/` 和 `../db/migration/`。

异常样板要求响应中的 `traceId` 能关联到一条诊断主事件：`BusinessException` 使用非空 `errorCode` 且只表达 4xx，记录 WARN 与抛出堆栈；基础设施或未知 5xx 不得降级为业务异常，应记录 ERROR 与完整 cause；参数校验返回 400，仅记录字段和约束摘要；401/403/404/429 只记录结构化原因。`path` 优先使用路由模板。复制后必须用日志捕获测试验证字段、分级和敏感信息过滤。
