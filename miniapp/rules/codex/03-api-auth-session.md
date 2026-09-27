# 03 API Auth Session

改 API、登录态或手机号绑定时：

1. 先确认 OpenAPI / schema 是否更新。
2. request 封装必须统一处理 token、traceId、平台、版本、错误码。
3. 401 / session 过期进入统一登录恢复流程。
4. 手机号授权必须由用户动作触发，并处理拒绝、失败、平台不可用。
5. logout 必须清理 store、storage、缓存和待重试任务。
6. 禁止前端保存平台密钥或自行换取敏感 session。
