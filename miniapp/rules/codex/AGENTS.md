# AGENTS.md

本仓库为企业级 uni-app 小程序项目。Codex 必须以 `rules/` 作为 AI 规则唯一入口。

技术栈：Vue 3 + TypeScript + uni-app + Vite。目标端为小程序优先，暂不覆盖 App / nvue / 原生插件。

## 每次改代码前必读

1. `rules/codex/01-before-editing.md`
2. `rules/shared/00-must-follow.md`

## 改代码前先说明

改代码前，先用 3-8 行说明本轮规则路由；纯问答、只审查不修改时可不声明。

- **这次改动**：对应下表哪一行。
- **将读取**：本轮实际会读的 `rules/` 文件路径。
- **不读取及原因**：例如“未涉及支付 / 未改隐私授权 / 非分包变更”。

未声明即开始写代码，视为未遵守本文件。

## 按改动类型追加阅读

先判断属于下表哪一行，只读该行和被点名的细则；不要一次加载全部 `shared/`。

| 任务 | 必读规则 |
|---|---|
| 任意小程序改动 | `rules/codex/01-before-editing.md`、`rules/shared/00-must-follow.md` |
| 新建项目 / 调整目录 / 移动跨层文件 | `rules/shared/01-project-structure.md`、`rules/shared/02-naming.md` |
| 立项 / 架构方案 / 上线评审 | `common-governance/docs/architect-engineering-checklist.md`、`common-governance/docs/definition-of-done.md`、`common-governance/docs/dod-maturity-mapping.md` |
| 需求分析 / 业务 PR / 缺陷修复 | `common-governance/docs/requirements-traceability.md`、`common-governance/docs/business-correctness-review.md` |
| 写页面 / 组件 / 生命周期 | `rules/shared/02-naming.md`、`rules/shared/03-vue3-typescript-uniapp.md`、`rules/shared/04-page-ui-lifecycle.md`、`rules/shared/12-list-form-pagination.md`、`rules/shared/24-design-system-mobile.md`、`rules/codex/02-page-generation.md` |
| App.vue / 应用级生命周期 | `rules/shared/20-app-runtime.md`、`rules/codex/06-app-runtime.md`、`rules/shared/14-payment-subscribe-share.md`（若 scene/分享） |
| API / 契约 / request | `rules/shared/05-api-contract-request.md`、`rules/shared/21-network-security.md`、`rules/shared/12-list-form-pagination.md` |
| 网络 / web-view / 上传域名 | `rules/shared/21-network-security.md`、`rules/codex/07-network-security.md`、`rules/shared/05-api-contract-request.md` |
| 登录态 / token / 手机号 | `rules/shared/06-login-auth-session.md`、`rules/shared/09-privacy-permission.md`、`rules/codex/03-api-auth-session.md` |
| pages.json / 路由 / 分包 / 页面栈 | `rules/shared/07-pages-routing-subpackages.md`、`rules/shared/10-performance-package-size.md` |
| storage / store / 缓存 | `rules/shared/08-state-storage-cache.md`、`rules/shared/06-login-auth-session.md` |
| 隐私 / 授权 / 敏感能力 | `rules/shared/09-privacy-permission.md`、`rules/shared/11-platform-differences.md`、`rules/codex/04-platform-capability.md` |
| 性能 / 包体积 / 首屏 / 渲染 / 图片 | `rules/shared/10-performance-package-size.md`、`rules/shared/07-pages-routing-subpackages.md`、`rules/shared/15-logging-observability.md` |
| 平台差异 / adapter | `rules/shared/11-platform-differences.md`、`rules/codex/04-platform-capability.md` |
| 上传 / 下载 / 媒体 | `rules/shared/13-upload-download-media.md`、`rules/shared/09-privacy-permission.md` |
| 支付 / 订阅消息 / 分享 | `rules/shared/14-payment-subscribe-share.md`、`rules/shared/06-login-auth-session.md`、`rules/shared/09-privacy-permission.md` |
| 弱网 / 错误恢复 / 离线 | `rules/shared/22-error-recovery-offline.md`、`rules/codex/08-error-recovery.md` |
| 富文本 / UGC / 内容安全 | `rules/shared/23-content-safety.md`、`rules/codex/09-content-safety.md` |
| 样式架构 / 主题 / 设计系统 / Base 组件 | `rules/shared/02-naming.md`、`rules/shared/24-design-system-mobile.md` |
| 依赖 / 供应链 | `rules/shared/25-dependency-supply-chain.md` |
| 安全加固 / 风控 / 远程配置 / 多平台矩阵 | `rules/shared/26-security-hardening-risk.md`、`rules/shared/19-release-ops.md`、`rules/shared/21-network-security.md` |
| 日志 / 埋点 / 监控 | `rules/shared/15-logging-observability.md`、`rules/docs/observability-metrics.md` |
| 单元 / 组件 / 快照 / E2E / flaky / 回调重放 / 兼容 / CI / 发布 | `rules/shared/16-testing-quality-gates.md`、`rules/shared/19-release-ops.md`、`rules/codex/05-verification.md` |
| 生产发布 / 灰度 / 回滚 | `common-governance/docs/environment-promotion.md`、`common-governance/docs/release-evidence.md` |
| 生产事故 / 安全事件 / 复盘 | `common-governance/docs/incident-response.md`、`common-governance/docs/incident-postmortem-template.md` |
| 新业务分包 / 二开 | `rules/shared/18-business-module-extension.md`、`rules/docs/business-feature-playbook-miniapp.md`（修 bug/样式可不读 18，见 `99-project-local`） |
| AI 生成复杂小程序代码；读取网页 / Issue / 日志；调用外部工具 | `rules/shared/17-ai-generation.md` |

## 路径触发

- 编辑 `src/pages/**`、`src/subpackages/**/*.vue` → 追加读取 `04` + `12`。
- 编辑 `src/pages.json` → 追加读取 `07` + `10`。
- 编辑 `src/manifest.json` → 追加读取 `09` + `11`。
- 编辑 `src/App.vue`、`src/app/**` → 追加读取 `20`。
- 编辑 `src/api/**`、`contracts/**`、`src/api/generated/**` → 追加读取 `05` + `21`。
- 编辑 `src/auth/**` → 追加读取 `06` + `09`。
- 编辑 `src/privacy/**` → 追加读取 `09`。
- 编辑 `src/platform/**` → 追加读取 `11`，若涉及支付 / 分享 / 订阅消息则追加 `14`。
- 编辑 `src/platform/**` 中多平台能力矩阵、风控信号或敏感能力 adapter → 追加读取 `26`。
- 编辑 `src/stores/**` → 追加读取 `08`。
- 编辑项目声明的 Base 组件目录、`src/components/**`、`src/composables/**` → 追加读取 `02` + `03` + `04` + `16` + `24`。
- 编辑 `src/styles/**` 或主题配置 → 追加读取 `02` + `10` + `16` + `24`。
- 编辑 `src/subpackages/**`（新业务域 / CRUD / 支付链路）→ 追加读取 `18` + `07` + `10`。
- 编辑 `package.json`、`.github/**` → 追加读取 `16` + `19`，若涉及第三方 SDK 或供应链风险则追加 `25` + `26`。
- 编辑远程配置、灰度、实验、审核临时开关、source map 或生产构建脚本 → 追加读取 `26` + `19`。

## 冲突优先级

安全与合规 > `00-must-follow` > 项目本地约定（`99-project-local`、ESLint）> 场景 shared。

## Level 0 与场景规则摘要

`rules/shared/00-must-follow.md` 的 15 条基础条款是所有项目都要遵守的。以下摘要涉及具体能力时，仅在任务命中该能力后强制执行；按上面的任务表读取对应 shared 全文。

- 页面禁止直接 `uni.request`、`uni.login`、支付、订阅消息、手机号授权。
- API 字段来自 `contracts/openapi.yaml` 和由其生成的类型，禁止手写后端字段，也禁止手改生成物。
- 新业务页默认分包，主包禁止放低频业务、大图、大 JSON、大型 SDK。
- 敏感能力必须有业务必要性、用户触发、隐私用途说明和拒绝态。
- 支付最终状态以后端订单查询为准，分享参数不得携带敏感信息。
- 平台差异进 `src/platform/`，禁止页面堆大量条件编译。
- 生产禁止 mock、console、调试入口和硬编码密钥。
- 禁止非白名单域名与向 H5 透传 token；体验/审核版不得连生产支付。
- App 级错误与 onPageNotFound 须有统一兜底与上报。
- 弱网/401 须统一 recovery；富文本/UGC 须消毒；关键链路须指标上报。
- 生产构建禁止公开 source map、调试资源和高风险开关；第三方 SDK 与实验配置须有数据流、Owner、回滚和清理计划。

## 完成前

运行项目中实际存在的脚本；若不存在则明确说明未配置，不得伪造通过结果：

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build:mp-weixin
pnpm api:check
pnpm size:check
pnpm audit
```

详见 `rules/shared/16-testing-quality-gates.md` 与 `rules/codex/05-verification.md`。全栈契约见 `rules/docs/fullstack-contract.md`。
