# 规则包索引（shared）

| 编号 | 文件 | 一句话 |
|---|---|---|
| 00 | `00-must-follow.md` | 所有项目都要遵守的基础条款（15 条）与场景路由 |
| 01 | `01-project-structure.md` | 目录与分层 |
| 02 | `02-naming.md` | 命名 |
| 03 | `03-vue3-typescript-uniapp.md` | Vue3 / TS 风格 |
| 04 | `04-page-ui-lifecycle.md` | 页面 UI 与生命周期 |
| 05 | `05-api-contract-request.md` | OpenAPI / request |
| 06 | `06-login-auth-session.md` | 登录态 / token |
| 07 | `07-pages-routing-subpackages.md` | pages.json / 分包 |
| 08 | `08-state-storage-cache.md` | Pinia / storage |
| 09 | `09-privacy-permission.md` | 隐私与授权 |
| 10 | `10-performance-package-size.md` | 性能与包体积 |
| 11 | `11-platform-differences.md` | 平台 adapter |
| 12 | `12-list-form-pagination.md` | 列表 / 表单 / 分页 |
| 13 | `13-upload-download-media.md` | 上传 / 媒体 |
| 14 | `14-payment-subscribe-share.md` | 支付 / 订阅 / 分享 |
| 15 | `15-logging-observability.md` | 日志 / 埋点 |
| 16 | `16-testing-quality-gates.md` | 测试与 CI |
| 17 | `17-ai-generation.md` | AI 生成、不可信内容与工具安全约束 |
| 18 | `18-business-module-extension.md` | 新业务分包二开 |
| 19 | `19-release-ops.md` | 发版 / 环境隔离 |
| 20 | `20-app-runtime.md` | App 级生命周期 |
| 21 | `21-network-security.md` | 域名 / web-view |
| 22 | `22-error-recovery-offline.md` | 错误恢复 / 弱网 |
| 23 | `23-content-safety.md` | 富文本 / UGC 安全 |
| 24 | `24-design-system-mobile.md` | 设计 Token / Base |
| 25 | `25-dependency-supply-chain.md` | 依赖与 audit |
| 26 | `26-security-hardening-risk.md` | 安全加固 / 风控 / 实验 |

文档：`docs/observability-metrics.md`、`docs/owasp-miniapp-mapping.md`、`docs/fullstack-contract.md`（含与管理端 E41–E43 边界说明）、`docs/enterprise-governance.md`（DoD / 豁免 / 接入验收）。

Evals：M01–M52；核心 P1 ≥10/12；Component Engineering M45–M50 建议 **6/6**；Testing Governance M49/M52 建议 **2/2**；AI Tool Safety MAT01–MAT05 独立 **5/5**，见 `evals/README.md` 与 `evals/ai-tool-safety.md`。

Codex：`codex/AGENTS.md`。Cursor：`cursor/*.mdc`。
