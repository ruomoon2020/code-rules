# Cursor ↔ Shared 编号对照（小程序）

> **编号多数对齐，但不保证恒等**：以本表与各 `.mdc` 内 `Read`/`全文` 路径为准；`27-ai-generation` → shared `17` 是刻意错位。

| Cursor | Shared 正文 | 主题 |
|---|---|---|
| `00-project-overview.mdc` | `00-must-follow.md` | 总览 / Hard Rules |
| `02-vue3-uniapp.mdc` | `02`、`03`、`04`、`12`、`16`、`24` | Vue3 / uni-app 基础 |
| `05-api-auth.mdc` | `05-api-contract-request.md`、`06-login-auth-session.md`、`09` | API / 登录 |
| `07-pages-subpackages.mdc` | `07-pages-routing-subpackages.md`、`10` | 页面 / 分包 |
| `08-state-storage.mdc` | `08-state-storage-cache.md`、`06` | 状态与缓存 |
| `09-privacy-permission.mdc` | `09-privacy-permission.md`、`11` | 隐私权限 |
| `10-performance-package-size.mdc` | `10-performance-package-size.md`、`07` | 性能 / 包体积 |
| `11-platform-differences.mdc` | `11-platform-differences.md` | 平台差异 |
| `12-list-form-pagination.mdc` | `12-list-form-pagination.md`、`04` | 列表表单 |
| `13-upload-media.mdc` | `13-upload-download-media.md`、`09` | 上传媒体 |
| `14-payment-subscribe-share.mdc` | `14-payment-subscribe-share.md` | 支付订阅分享 |
| `15-logging-observability.mdc` | `15-logging-observability.md` | 日志可观测 |
| `16-quality-gates.mdc` | `16-testing-quality-gates.md`、`19-release-ops.md` | 门禁 / 发版 |
| `18-business-module-extension.mdc` | `18-business-module-extension.md` | 业务分包扩展 |
| `20-app-runtime.mdc` | `20-app-runtime.md` | App 运行时 |
| `21-network-security.mdc` | `21-network-security.md`、`05` | 网络安全 |
| `22-error-recovery.mdc` | `22-error-recovery-offline.md`、`06` | 错误恢复 |
| `23-content-safety.mdc` | `23-content-safety.md` | 内容安全 |
| `24-design-system.mdc` | `24-design-system-mobile.md`（兼 `02`/`03`/`16`） | 设计系统 |
| `25-dependency-supply-chain.mdc` | `25-dependency-supply-chain.md` | 供应链 |
| `26-security-hardening-risk.mdc` | `26-security-hardening-risk.md` | 安全加固 |
| `27-ai-generation.mdc` | `17-ai-generation.md` | AI 生成（编号错位） |

无独立 Cursor 的 shared：`01-project-structure`、`19-release-ops`（经 overview / `16-quality-gates` 触发）。

Codex 不读 `cursor/*.mdc`。
