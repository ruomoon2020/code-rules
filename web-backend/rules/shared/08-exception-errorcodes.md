# Exception & Error Codes

## 统一模型

1. 使用 `@RestControllerAdvice` 全局处理异常。
2. 业务异常 `BusinessException`（或项目等价）携带非空 **errorCode**、可选 **4xx httpStatus** 与 **cause**；构造器或工厂必须拒绝空错误码和 5xx 状态。只有明确的下游业务拒绝才可保留 cause 后映射成 4xx；数据库、网络、RPC/MQ 不可用等基础设施失败不得降级成业务 4xx，必须保留原始原因进入 5xx 兜底。禁止只复制 `cause.getMessage()`。
3. 响应体字段与前端 normalizer 对齐：`code`、`message`、`errorCode`、`traceId`（见 `docs/fullstack-contract.md`）。

## 既有响应壳

若项目已有统一 API 包装，在公共层映射到上述四字段，禁止业务模块各自解析不同外壳。平台字段名差异只记在 `99-project-local`；细则见 `docs/fullstack-contract.md` §既有响应壳适配。

## 错误码

1. 格式：`DOMAIN_REASON`，全大写下划线，如 `USER_NOT_FOUND`。
2. 错误码须在枚举或常量类集中维护；禁止魔法字符串散落。
3. 未知系统异常映射为 `INTERNAL_ERROR`，不向客户端暴露堆栈。

## 日志

1. 每个失败请求在统一异常边界至少产生一条可由响应 `traceId` 找到的诊断主事件；同一异常堆栈只在最终分类边界记录一次。
2. 诊断主事件至少包含 `event`、`traceId`、`errorCode`、`httpStatus`、请求方法、无查询串路径、异常类型；服务名、环境、版本由日志底座统一补齐。
3. 未知 5xx 使用 `ERROR`，异常对象作为 logger 最后的异常参数，保留完整堆栈与 cause chain；响应只返回通用文案、`INTERNAL_ERROR` 和 `traceId`。
4. 应用代码主动抛出的 4xx `BusinessException` 使用 `WARN` 并传入异常对象，使第一条业务帧指向实际 `throw` 行；高频正常分支只能按明确错误码做限频或采样，不能让响应 `traceId` 完全找不到诊断事件。
5. Bean Validation、绑定、类型转换和消息不可读须单独映射为 400。日志记录字段名与约束类型，默认不记录无价值的 Spring 框架堆栈；自定义校验器自身异常仍进入 5xx。
6. 401、403、404、429 等高频客户端事件按安全/流量策略记录结构化原因和指标，不要求无差别打印堆栈。
7. 禁止记录 Authorization、Cookie、密码、Token、连接串、完整请求体、默认 rejected value、SQL 参数中的敏感字段；异常 message 也须按敏感数据审查。

## 与 OpenAPI

1. 文档中声明标准错误响应 schema。
2. 新增错误码须更新 `contracts/openapi.yaml` 中 `BusinessErrorCode` 枚举（或项目错误码表），并与 `ErrorCodes` 常量同步。
3. 禁止删除或静默修改已有 `errorCode` 语义（见 `05-openapi-contract.md`）。

## 样板代码

`examples/scaffold/java/common/exception/` — `BusinessException`、`GlobalExceptionHandler`、`ErrorCodes`。
