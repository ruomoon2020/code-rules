# 21 Network Security

网络出站与 `web-view` 安全边界。request 契约与封装见 `05-api-contract-request.md`。

## 统一出站

1. `uni.request`、`uni.uploadFile`、`uni.downloadFile` 必须经统一封装；禁止页面直调。
2. 生产环境必须 HTTPS；禁止降级到 HTTP。
3. 禁止动态拼接非白名单域名（含变量 host、用户输入 URL、后端返回未校验的跳转地址）。
4. baseURL 仅从构建环境变量读取（如 `import.meta.env.VITE_API_BASE_URL`），禁止页面按「是否体验版」切换生产域名。

## 合法域名

1. 业务 API、上传、下载、第三方 SDK 域名须在团队白名单登记，并与微信后台「服务器域名」一致。
2. 新增域名须说明用途、备案/合规、是否进小程序后台配置。
3. 封装层须提供 `assertAllowedUrl(url)`（或等价）并在 request / upload / download 入口强制校验。

## web-view

1. 仅允许打开白名单内的 H5 URL（路径前缀或完整 URL 列表由项目维护）。
2. 禁止把 token、手机号、refreshToken、支付凭证通过 URL query、hash、`postMessage` 传给 H5。
3. 禁止 `web-view` 加载用户输入或后端返回的任意 URL 而不校验。
4. 发版勾选见 `docs/compliance-wechat-checklist.md`；编码约束以本文件与 `00` 为准。

## 第三方 SDK

1. 新 SDK 须登记其网络域名、隐私采集范围、主包体积影响。
2. SDK 初始化不得绕过统一 request 白名单逻辑。

## 禁止

- 禁止 `eval`、动态执行远程脚本加载业务逻辑。
- 禁止为了调试在 production 构建放开「任意域名」开关。
