# Security & Authorization

## 认证

1. 使用 Spring Security；Token 策略（JWT / Session）以项目为准。
2. 登录、刷新、登出接口须在 OpenAPI 标明 security scheme。
3. 禁止在日志中打印 Token 明文。

## 鉴权

1. 方法级 `@PreAuthorize` 或项目统一注解；权限码与前端 `system:user:create` 对齐。
2. 前端隐藏按钮不等于安全；**后端必须校验**。
3. 数据权限（本部门、本人）在 Service 或 MyBatis 拦截器统一实现，禁止每个 SQL 手写一套。
4. 多租户、数据权限、缓存权限边界见 `24-data-access-cache.md`。

## BOLA / IDOR（对象级授权）

1. 凡通过路径或参数中的 **资源 ID** 访问/修改/删除，须在 Service 层校验：当前用户对该资源**有归属权**（本人、本部门、本租户、数据权限范围）。
2. 禁止仅校验「已登录」而不校验资源归属（OWASP API1）；与 `24` 租户条件同时生效。
3. 列表接口返回的 ID 不得用于推断他人资源可访问性（错误信息勿泄露存在性，按产品约定统一 404/403）。

## 越权测试

1. 敏感接口至少覆盖：未登录、无权限、跨租户访问、普通用户访问管理员资源。
2. 管理端写操作须验证权限码，不得只测 happy path。
3. 数据权限查询须构造其他租户 / 其他部门 / 其他用户数据，证明后端过滤生效。
4. 导入、导出、批量删除、权限变更等高风险接口须同时覆盖鉴权、审计与限流 / 告警策略。

## 输入

1. 所有入参 `@Valid`；字符串长度、格式与 OpenAPI 一致。
2. **Mass Assignment**：Request DTO 仅声明允许字段；禁止用 `Entity` 接收入参；`PATCH` 禁止把未授权字段写入（见 `13-validation.md`）。
3. 文件上传：类型、大小、病毒扫描（按项目）；见 `14-file-import-export.md`。
4. 导出、下载链接须鉴权与有效期，见 `14`。

## 限流与防刷

1. 登录、验证码、密码重置、导入、导出、批量操作等高风险接口必须考虑限流、防刷、验证码、审计或告警。
2. 限流维度按场景选择：IP、用户、租户、设备、手机号、接口维度。
3. 限流错误码与提示必须统一，不暴露账户是否存在等敏感判断。
4. 触发限流时建议返回 `Retry-After` 与统一 `errorCode`（见 `04-rest-api-design.md`）。
5. 后台管理端的敏感操作即使低频，也应有审计与异常频率告警；审计字段与必审清单见 `27-audit-log.md`。

## Web 安全（管理后台）

1. **CORS**：生产禁止 `Access-Control-Allow-Origin: *` 且 `Allow-Credentials: true`；须白名单域名。
2. **CSRF**：Cookie Session 场景启用 CSRF；纯 JWT Header 无 Cookie 须在 ADR 中说明。
3. **安全响应头**：生产建议 `Content-Security-Policy`、`X-Content-Type-Options`、`X-Frame-Options` 等（按网关或 Spring 配置）。
4. **Cookie**：`HttpOnly`、`Secure`（HTTPS）、`SameSite` 按场景设置；禁止长期有效且不轮换的会话 Cookie。
5. **登录态**：登出、改密、冻结用户后须失效已有 Token/Session；刷新 Token 须防重放（按项目方案）。
6. **Swagger / OpenAPI UI、Actuator**：**生产禁止**对公网暴露；仅内网或 dev profile 启用。健康检查端点可单独放行最小集合。
7. 样板见 `examples/config/SecurityConfig.sample.java`。

## 脱敏

1. 日志、异常、审计中手机号、证件号脱敏。
2. 响应 DTO 按角色脱敏字段（若需要）。

## 可靠性交叉引用

限流熔断降级见 `32-service-reliability.md`、`28-external-integration.md`。
