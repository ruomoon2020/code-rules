# Validation

1. Controller 入参 `@Valid` / `@Validated`。
2. 分组：`Create` / `Update` 使用 validation groups。
3. 校验消息与 OpenAPI `description` 一致；支持 i18n（按项目）。
4. 业务规则（跨字段）在 Service 校验，返回明确 `errorCode`。
5. 枚举使用契约枚举，禁止魔法字符串。
6. **Mass Assignment**：`UpdateRequest` 仅含允许修改字段；禁止 `BeanUtils.copyProperties(entity, request)` 无字段白名单；敏感字段（角色、租户、状态）仅能通过受权接口修改。
7. Bean Validation、绑定、类型转换、消息不可读等输入错误须由全局处理器映射为稳定 4xx 错误码；日志记录字段名与约束类型，不记录 rejected value、完整请求体或框架堆栈。Spring 6.1+ 同时覆盖 `MethodArgumentNotValidException` 与 `HandlerMethodValidationException`。
