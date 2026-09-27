# Operability

## 运行时

1. Spring Boot Actuator：`health`、`readiness`、`liveness`（K8s）。
2. 优雅停机：完成进行中请求再退出。
3. 发布关联 Git commit、构建版本；日志带 `release`（可选）。
4. 数据库连接、线程池、JVM 指标接入监控。
5. 禁止生产暴露敏感 actuator 端点于公网。
6. 登录、验证码、导入、导出、批量操作等高风险接口须有异常频率监控或限流告警（见 `06-security-authz.md`）。

## 发布与回滚

1. **代码回滚**须考虑 **DB 兼容**：旧版本代码能否读新 schema、新字段是否可空。
2. 发布前确认：旧实例读新数据、新实例读旧数据（滚动发布）无致命错误。
3. **破坏性 DB 变更**采用三阶段（expand → migrate → contract）：
   - **Expand**：加列/加表/加索引，新旧代码均可运行；
   - **Migrate**：双写或回填数据；
   - **Contract**：删除旧列/收紧约束，仅在新代码全量后执行。
4. Flyway 脚本须可重复 validate；回滚优先**前滚修复**（新迁移），禁止依赖手工改表。

## Feature Flag 与灰度

1. 灰度开关须有 owner、默认关闭策略、过期时间（见 `21-configuration-secrets.md`）。
2. 禁止「临时」灰度开关存活超过约定周期（如 2 个发布周期）。
3. 开关关闭后须删除分支逻辑，避免死代码。
