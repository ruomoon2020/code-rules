# 推荐可观测指标（小程序）

> 与 `shared/15-logging-observability.md` 配合；项目实际上报名写入 `99-project-local.mdc`。

## 性能

| 指标 | 说明 | 建议关注 |
|---|---|---|
| `cold_start_ms` | 冷启动到首屏可交互 | P95 按项目预算 |
| `first_interactive_ms` | 首屏可交互耗时 | P95 按核心页面 |
| `first_api_ms` | 首屏关键 API 耗时 | 与后端 trace 对齐 |
| `white_screen` | 首屏超时/白屏 | 率 + route |
| `subpackage_load_fail` | 分包加载失败 | 按分包 root |
| `main_package_size_kb` | 主包体积 | warning / fail 阈值 |
| `subpackage_size_kb` | 分包体积 | 按分包 root |
| `image_load_fail` | 图片加载失败 | CDN / route / 资源类型 |
| `long_task_ms` | 长任务或卡顿指标（若采集） | 页面 + 操作 |

## 稳定性

| 指标 | 说明 |
|---|---|
| `app_error` | `onError` / `onUnhandledRejection` 次数 |
| `page_not_found` | `onPageNotFound` |
| `request_fail` | 按 `errorCode`、HTTP 状态聚合 |
| `crash_free_session` | 会话无崩溃占比（若平台提供） |

## 业务漏斗

| 指标 | 说明 |
|---|---|
| `login_success` / `login_fail` | 含拒绝授权 |
| `pay_invoke` / `pay_success` / `pay_fail` | 以后端订单为准 |
| `share_open` | scene 合法命中 |
| `subscribe_accept` / `subscribe_reject` | 订阅消息 |

## 字段规范

- 每条须含：`traceId`、`page`、`appVersion`、`platform`、`networkType`（可选）。
- 禁止：`token`、完整手机号、身份证、支付凭证。
- 与后端日志用同一 `traceId` 关联。

## SLO 示例（按项目调整）

- 冷启动 P95 &lt; 2500ms（主包预算内）。
- 首屏可交互 P95 &lt; 1800ms（核心页面）。
- 首屏关键 API P95 &lt; 800ms（与后端 trace 对齐）。
- 白屏率 &lt; 0.1%。
- 分包加载失败率 &lt; 0.1%。
- 核心 API 错误率 &lt; 0.5%（排除用户取消）。
- `app_error` 日环比异常 &gt; 50% 触发告警。

## 发版观察

- 发版后至少观察 30 分钟、2 小时、24 小时三个窗口（按项目调整）。
- 观察项：冷启动、白屏率、分包加载失败、核心 API、支付失败、app_error。
- 指标 Owner、告警渠道、阈值写入 `examples/99-project-local.mdc.sample` 复制后的业务仓文件。
