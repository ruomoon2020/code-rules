# 全栈契约（小程序端）

> 维护者 / 架构文档。Codex 日常以 `shared/05-api-contract-request.md` 为准。
> 与后端、管理端对齐的完整版见 monorepo `web-backend/rules/docs/fullstack-contract.md`。

## 单一来源

```text
contracts/openapi.yaml
  → 后端：Controller/DTO、校验、测试
  → 管理端：schema / src/api/generated
  → 小程序：src/api/generated（api:gen）+ api:check
```

## 统一字段（小程序 request）

| 字段 | 后端 | 小程序 |
|---|---|---|
| `traceId` | MDC + 响应头（名以项目为准） | request 自动携带；日志关联 |
| `errorCode` | `BusinessException` / 枚举 | 统一错误处理；禁止页面硬编码文案与码不一致 |
| `message` | 用户可读文案 | `uni.showToast` / 模态提示 |
| 分页 `page` / `pageSize` | `Page` 查询 | 列表 composable（`12`） |
| 分页 `total` / `records` | `IPage` | 列表底部、空态判断 |
| `Idempotency-Key` | 可重试写操作 Header | 下单、支付、创建类请求；重试复用同一键 |

## 小程序扩展约定

| 主题 | 说明 |
|---|---|
| `code` 换 session | 微信 `uni.login` code 仅一次有效；换 token 走后端，禁止前端拼密钥 |
| `scene` / 二维码 | 分享打开参数白名单校验（`14`） |
| 订阅消息模板 ID | 集中配置，禁止页面散落字符串 |
| 支付结果 | 以后端订单状态为准；前端回调只触发刷新 |

## 权限模型边界

| 项 | 管理端 | 小程序 |
|---|---|---|
| 默认模型 | 菜单 / 路由 / 按钮权限码 + 后端鉴权 | 登录态 + 后端鉴权；不默认复制管理端 RBAC 壳层 |
| C 端小程序 | 通常不适用 | 未登录 / 已登录 / 已绑手机号 / 会员等轻量状态 |
| B 端小程序 | 可共用权限码主数据 | 只消费后端 `roles` / `permissions[]` 子集，用于入口展示 |
| 安全来源 | 后端 `@PreAuthorize` / 数据权限 | 后端鉴权；前端 `hasPermission()` 仅 UX |
| 错误处理 | 403 / 业务错误码 | 401 走登录恢复；403 / `NO_PERMISSION` 走无权限提示，不跳登录循环 |

禁止小程序维护第二套角色、菜单、权限主数据。若与管理端共用权限码，权限码来源必须在后端 / OpenAPI 中可追溯，小程序只消费业务需要的子集。

## 错误响应示例

与后端一致（字段名以 OpenAPI 为准）：

```json
{
  "code": 40001,
  "message": "用户不存在",
  "errorCode": "USER_NOT_FOUND",
  "traceId": "abc123",
  "data": null
}
```

## 发布顺序

1. OpenAPI PR + openapi-diff
2. 后端兼容发布
3. 管理端 `api:gen`（若涉及）
4. 小程序 `api:gen` + `api:check` + 联调

## 新业务功能（三端）

| 步骤 | 后端 | 管理端 | 小程序 |
|---|---|---|---|
| 契约 | OpenAPI 路径、DTO、枚举 | schema + api:gen | api:gen + api:check |
| 权限 | `@PreAuthorize`、数据权限 | 按钮 / 路由权限 | 登录态 + 后端鉴权（不单靠 UI 隐藏） |
| 列表 | 分页、租户、BOLA | useTable 四态 | 四态 + 删末条回退（`12`） |
| 支付 | 下单、幂等、订单状态 | 若涉及 | `14` + 后端订单查询 |
| 网络 | 服务端域名与鉴权 | 若涉及 | `21`：白名单、HTTPS；禁止向 H5 透传 token |
| App 运行时 | — | — | `20`：全局错误、scene、非阻塞 onLaunch |
| 环境 | 多环境配置 | 构建变量 | `19`：体验/审核版禁连生产 API 与支付 |
| 审计 | 写库 | 操作记录 UI | 不伪造成功；敏感字段脱敏展示 |

细则：后端 `shared/43` + playbook；管理端 `web-front/rules/shared/22`；小程序 `shared/18` + `docs/business-feature-playbook-miniapp.md`。

## 与管理端 Platform Extension 的边界

管理端 **E41–E43**（`web-front/rules/evals`）仅适用于 Vue 管理端 i18n / WebSocket·SSE / 富文本编辑器场景，**小程序不适用该 eval 套件**。

| 主题 | 管理端 | 小程序 |
|---|---|---|
| i18n / 区域格式 | `web-front/rules/shared/23-i18n-locale.md` | 文案与 `errorCode` 映射走项目 i18n；禁止硬编码与后端码不一致 |
| 实时通道 | `web-front/rules/shared/24-realtime-rich-content.md` | 长连接按 `21`；鉴权禁止 Token 放 URL query |
| 富文本 / UGC | `24` + sanitizer | `shared/23-content-safety.md`：消毒或白名单；禁止不可信 HTML |

小程序 evals 以 **M01–M52** 为准；富文本/UGC 相关见 Security / Resilience，安全加固/多平台/实验相关见 Enterprise Hardening，组件工程见 Component Engineering，并发/回调重放/兼容相关见 Testing Governance 套件（`evals/README.md`）。
