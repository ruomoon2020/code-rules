# API 契约与请求规则

## SSOT

1. 接口字段以 `contracts/openapi.yaml` 为唯一来源。若项目生成 `schema.json`，它和 `src/api/generated/**` 一样是生成结果，禁止手改。
2. `src/api/generated/**` 禁止手改；字段变化先改 OpenAPI，再重新生成。
3. 页面、表单、列表、分享参数中出现的后端字段必须能追溯到契约。
4. breaking change 必须同步后端、前端 generated、页面和测试。

## request 封装

1. 统一封装 `uni.request`，页面禁止直接调用。
2. 封装入口必须校验 URL 在白名单内、生产为 HTTPS（见 `21-network-security.md`）。
3. 请求必须自动带 traceId、token、平台、版本、渠道等必要上下文。
4. 401 / session 过期统一进入登录态恢复流程。
5. 错误体必须保留 `errorCode`、`message`、`traceId`；`errorCode` 是稳定业务契约，页面禁止按 `message` 分支或自行拼业务句。
6. 用户文案必须由统一错误处理层按 `errorCode` 映射；未知码展示通用文案和可查询的 `traceId`，`message` 仅可作为项目明确允许的 fallback。
7. `uploadFile` / `downloadFile` 使用专门封装，须同样做域名校验，不和普通 JSON request 混写。

## 幂等与重试

1. 写操作须防重复点击；必要时传幂等键。
2. 重试只允许用于安全的读请求或后端声明幂等的写请求。
3. 超时、取消、离页后的响应不得覆盖新页面状态。
