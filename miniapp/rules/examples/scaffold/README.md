# 小程序运行边界样板

本目录用于说明请求、登录、应用启动、全局错误和 web-view 白名单应如何分层，供 AI 和开发者在实现真实业务时参考。

> 这些文件不是可直接运行的完整工程。复制后必须接入项目现有的环境配置、token 生命周期、隐私授权、日志脱敏和平台构建流程。

| 文件 | 说明 |
|---|---|
| `request.ts.sample` | 统一 request + `assertAllowedUrl` |
| `allowed-hosts.ts.sample` | 出站域名白名单与 HTTPS |
| `auth-login.service.ts.sample` | 登录封装 |
| `App.vue.sample` | 应用级生命周期 |
| `app-bootstrap.ts.sample` | 非阻塞 onLaunch |
| `app-error-handler.ts.sample` | 全局错误与 404 兜底 |
| `webview-allowlist.ts.sample` | web-view URL 白名单 |
| `open-webview.ts.sample` | 安全打开 web-view |

## 建议落地路径

- `src/api/request.ts` ← `request.ts.sample`
- `src/api/allowed-hosts.ts` ← `allowed-hosts.ts.sample`
- `src/auth/login.service.ts` ← `auth-login.service.ts.sample`
- `src/App.vue` ← `App.vue.sample`
- `src/app/bootstrap.ts` ← `app-bootstrap.ts.sample`
- `src/app/error-handler.ts` ← `app-error-handler.ts.sample`
- `src/platform/webview-allowlist.ts` ← `webview-allowlist.ts.sample`
- `src/platform/open-webview.ts` ← `open-webview.ts.sample`

## 使用步骤

1. 先在 `99-project-local.mdc` 声明目标平台、合法域名、登录态位置和分包路径。
2. 按实际需要选择样板，不整体覆盖已有 `request`、`App.vue` 或认证实现。
3. 将示例常量和占位回调替换为项目真实配置与服务。
4. 补齐成功、失败、超时、登录过期、弱网和非法 URL 测试。
5. 运行 lint、type-check、目标平台构建、契约检查和包体积检查。
