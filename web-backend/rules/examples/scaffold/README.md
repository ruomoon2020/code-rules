# Java 源码样板

**非可运行模块**：复制到业务项目后修改包名 `com.company.product`，补全依赖与 Security 配置。

| 路径 | 说明 |
|---|---|
| `java/common/` | 统一响应、异常、traceId、`audit/AuditContext` |
| `java/modules/system/` | 用户域 + 审计读写（`AuditRecorder`、`AuditLog*` API） |
| `java/test/` | `UserControllerIT`、`AuditLogControllerIT` 集成测试样板 |
| `db/migration/*/V2__init_system_audit_log.sql` | 审计表样板，字段对齐 OpenAPI |
| `resources/mapper/system/UserMapper.xml` | 可移植列表 SQL |

| `../config/SecurityConfig.sample.java` | Security 鉴权样板（**复制前必读** CSRF / Swagger / Actuator 注释） |

配套：`docs/scaffold-module-system.md`、`../config/`、`../db/migration/`。

异常样板保证响应 `traceId` 可关联到一条诊断主事件：`BusinessException` 要求非空 `errorCode` 且只允许 4xx，记录 WARN 与抛出堆栈；基础设施/未知 5xx 不得降级成业务异常，记录 ERROR 与完整 cause；参数校验（含方法级校验）返回 400 并只记录字段/约束摘要；401/403/404/429 只记结构化原因。`path` 优先路由模板。复制后须用日志捕获测试验证结构化字段、分级和敏感信息过滤。
