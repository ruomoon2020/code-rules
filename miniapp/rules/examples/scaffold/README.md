# 小程序最小样板（参考）

供 AI 与新人对照结构，**非**可直接运行的完整工程。复制到业务仓后按项目调整。

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

落地路径：

- `src/api/request.ts` ← `request.ts.sample`
- `src/api/allowed-hosts.ts` ← `allowed-hosts.ts.sample`
- `src/auth/login.service.ts` ← `auth-login.service.ts.sample`
- `src/App.vue` ← `App.vue.sample`
- `src/app/bootstrap.ts` ← `app-bootstrap.ts.sample`
- `src/app/error-handler.ts` ← `app-error-handler.ts.sample`
- `src/platform/webview-allowlist.ts` ← `webview-allowlist.ts.sample`
- `src/platform/open-webview.ts` ← `open-webview.ts.sample`
