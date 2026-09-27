# 07 Network Security

改 `request`、`uploadFile`、`downloadFile`、`web-view` 时：

1. 先读 `shared/21-network-security.md`、`shared/05-api-contract-request.md`。
2. 所有出站 URL 经 `assertAllowedUrl`；生产 HTTPS。
3. `web-view` 仅白名单 URL；禁止向 H5 透传 token。
4. baseURL 仅来自 `import.meta.env`，禁止页面按体验版切换生产域名。
5. 样板：`examples/scaffold/allowed-hosts.ts.sample`、`webview-allowlist.ts.sample`、`open-webview.ts.sample`。
