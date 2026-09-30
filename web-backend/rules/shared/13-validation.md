# 参数校验规则

1. Controller 入参必须使用 `@Valid` / `@Validated`，并覆盖 body、query、path 与方法级参数校验。
2. `Create` / `Update` 必须使用 validation groups 或不同 Request DTO，禁止用同一套可空字段模糊两种语义。
3. 校验约束必须与 OpenAPI 的 required、长度、格式、范围和枚举一致；`message` 只作 fallback / 诊断文案，稳定业务语义使用 `errorCode`。
4. 集合、字符串和批量请求必须声明可验证的大小上限；嵌套对象、树结构和递归输入必须声明最大深度或节点数，禁止无界绑定后再在 Service 截断。
5. 业务规则（跨字段）必须在 Service / domain 校验并返回明确 `errorCode`，禁止仅依赖客户端校验。
6. 枚举必须使用契约枚举，禁止魔法字符串。
7. **Mass Assignment**：`UpdateRequest` 必须只包含允许修改字段；禁止 `BeanUtils.copyProperties(entity, request)` 无字段白名单；敏感字段（角色、租户、状态）只能通过授权接口修改。
8. Bean Validation、绑定、类型转换、消息不可读等输入错误必须由全局处理器映射为稳定 4xx 错误码；日志记录字段名与约束类型，不记录 rejected value、完整请求体或框架堆栈。Spring 6.1+ 同时覆盖 `MethodArgumentNotValidException` 与 `HandlerMethodValidationException`。
