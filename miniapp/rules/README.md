# Miniapp AI Rules

版本见 `VERSION`，变更见 `CHANGELOG.md`。维护者发版见 `RELEASE.md`。

本目录是企业级小程序项目 AI 编码规则的**唯一执行入口**。

测试治理由 `shared/16-testing-quality-gates.md` 统一约束确定性、失败证据、支付/回调重放与兼容窗口；具体阈值和平台工具由项目覆盖层声明。

技术栈：

```text
Vue 3 + TypeScript + uni-app + Vite
目标端：小程序优先，第一阶段以微信小程序为最严格基线
暂不覆盖：App、nvue、原生插件、App 打包
```

## 使用原则

1. 必须先遵守 `shared/00-must-follow.md`。
2. 按任务追加阅读，避免一次加载全部规则。
3. 冲突优先级：安全与合规 > `00-must-follow` > `99-project-local` / 项目 ESLint > 场景 shared。
4. 规则只写可执行约束；长篇说明留在 `docs/` 或业务仓 README。
5. 语言约定见 `LANGUAGE.md`（shared/codex 中文，cursor 正文中文）。

## 规则层级

```text
L0  shared/00-must-follow.md       — 通用不变量（15 条）；场景规则命中时强制
L1  shared/01–26                  — 场景规则
L2  codex/*.md、cursor/*.mdc       — 任务入口与触发摘要
```

使用原则：不要一次加载全部规则。Codex 先读 `codex/AGENTS.md`，Cursor 先读 `00-project-overview.mdc`，再按任务、路径和 glob 读取少量 shared 全文。

```text
Cursor alwaysApply 概览
  → Cursor globs / Codex 任务表
  → 按需读取 shared 全文
  → pnpm lint / type-check / build:mp-weixin / api:check / size:check / evals
```

## 部署到业务仓

1. 将 `miniapp/rules/` 整包复制或作为 submodule 放入小程序仓 `rules/`。
2. 复制 `rules/codex/AGENTS.md` 到业务仓根目录 `AGENTS.md`。
3. 复制 `rules/cursor/*.mdc` 到业务仓 `.cursor/rules/`。
4. 复制 `rules/examples/99-project-local.mdc.sample` 到 `.cursor/rules/99-project-local.mdc`，并按项目填写路径、预算和测试治理参数。
5. 按 `examples/package-scripts.sample.json` 接入 `lint`、`type-check`、`build:mp-weixin`、`api:check`、`size:check`。
6. 新建项目逐步清单见 `docs/onboarding-new-project.md`；复制 `examples/.github/` 作 PR 模板。

业务仓目录建议：

```text
your-miniapp/
├─ AGENTS.md
├─ rules/
├─ .cursor/rules/
├─ contracts/
│  └─ openapi.yaml 或 schema.json
├─ src/
│  ├─ pages/
│  ├─ subpackages/
│  ├─ components/
│  ├─ base/
│  ├─ api/
│  ├─ api/generated/
│  ├─ services/
│  ├─ stores/
│  ├─ composables/
│  ├─ platform/
│  ├─ auth/
│  ├─ privacy/
│  ├─ static/
│  ├─ pages.json
│  └─ manifest.json
└─ package.json
```

## 架构原则

- 页面只做编排：生命周期、UI 状态、用户事件。
- 业务流程进 `services/`，例如登录、支付、订单刷新、订阅消息。
- API 进 `api/`，禁止页面直接 `uni.request`。
- 平台能力进 `platform/`，禁止页面堆大量条件编译。
- 登录态、token、用户信息进 `auth/` 与 `stores/`，禁止散落 storage。
- 隐私授权进 `privacy/`，采集能力必须和隐私用途一致。
- 字段来自 OpenAPI / schema / generated 类型，禁止页面手写后端字段。

## Codex 怎么用

推荐问法：

```text
新增订单列表小程序页面，放 subpackages/order，按 04 + 07 + 10 + 12。
接入微信登录和手机号绑定，按 06 + 09。
接入支付和订阅消息，按 14 + 06 + 09。
优化主包体积，按 07 + 10。
新增 member 分包，按 18 + business-feature-playbook-miniapp。
```

Codex 必须在改代码前输出「实现前命中声明」：任务包、将读取规则、不读取原因。

## Cursor 怎么用

- 只让 `cursor/00-project-overview.mdc` 使用 `alwaysApply: true`。
- 其他 `.mdc` 通过 globs 触发（见 `cursor/` 各文件 frontmatter）。
- 项目真实业务域、主包预算、分包路径写在 `.cursor/rules/99-project-local.mdc`。

| 场景 | Cursor 规则 |
|---|---|
| 页面 / 生命周期 | `02-vue3-uniapp.mdc`、`12-list-form-pagination.mdc` |
| API / 登录态 | `05-api-auth.mdc` |
| Store / 缓存 | `08-state-storage.mdc` |
| 分包 / pages.json | `07-pages-subpackages.mdc` |
| 隐私 | `09-privacy-permission.mdc` |
| 性能 / 包体积 | `10-performance-package-size.mdc` |
| 平台 adapter | `11-platform-differences.mdc` |
| 上传 / 媒体 | `13-upload-media.mdc` |
| 支付 / 分享 / 订阅 | `14-payment-subscribe-share.mdc` |
| 日志 / 埋点 | `15-logging-observability.mdc` |
| CI / 发版 | `16-quality-gates.mdc` |
| App 运行时 | `20-app-runtime.mdc` |
| 网络 / web-view | `21-network-security.mdc` |
| 错误恢复 / 弱网 | `22-error-recovery.mdc` |
| 内容安全 / UGC | `23-content-safety.mdc` |
| 设计系统 / Base | `24-design-system.mdc` |
| 依赖 / 供应链 | `25-dependency-supply-chain.mdc` |
| 安全加固 / 风控 | `26-security-hardening-risk.mdc` |
| 新业务分包 | `18-business-module-extension.mdc`（仅新业务扩展；见 `99-project-local`） |

## 真实业务开发流程

1. 先确认后端 OpenAPI / schema（见 `docs/fullstack-contract.md`）。
2. 新业务页默认放分包，主包只放启动链路、tabBar、登录和基础能力。
3. 页面读取 generated 类型和 API 方法，不手写字段。
4. 涉及登录、手机号、位置、相册、相机、订阅消息、支付时先读对应 shared。
5. 支付结果以后端订单状态为准；分享参数、scene、二维码参数必须白名单校验。
6. 完成前运行项目实际存在的 lint、type-check、build、api:check、size:check、audit（若配置）。

新业务分包逐步清单：`docs/business-feature-playbook-miniapp.md`。

## 完整文件清单

### shared/

| 文件 | 职责 |
|---|---|
| `shared/00-must-follow.md` | 小程序硬规则 |
| `shared/01-project-structure.md` | 工程结构与边界 |
| `shared/02-naming.md` | 命名 |
| `shared/03-vue3-typescript-uniapp.md` | Vue3 / TS / uni-app 风格 |
| `shared/04-page-ui-lifecycle.md` | 页面 UI 与生命周期 |
| `shared/05-api-contract-request.md` | API 契约与 request |
| `shared/06-login-auth-session.md` | 登录态、token、手机号 |
| `shared/07-pages-routing-subpackages.md` | pages.json、页面栈、分包 |
| `shared/08-state-storage-cache.md` | Pinia、storage、缓存 |
| `shared/09-privacy-permission.md` | 隐私合规与授权 |
| `shared/10-performance-package-size.md` | 性能与包体积 |
| `shared/11-platform-differences.md` | 平台差异与 adapter |
| `shared/12-list-form-pagination.md` | 列表、表单、分页 |
| `shared/13-upload-download-media.md` | 上传、下载、媒体 |
| `shared/14-payment-subscribe-share.md` | 支付、订阅消息、分享 |
| `shared/15-logging-observability.md` | 日志、埋点、监控 |
| `shared/16-testing-quality-gates.md` | 测试与质量门禁 |
| `shared/17-ai-generation.md` | AI 生成、不可信内容与工具安全约束 |
| `shared/18-business-module-extension.md` | 新业务分包二开 |
| `shared/19-release-ops.md` | 发版、灰度、审核、环境隔离 |
| `shared/20-app-runtime.md` | App 级生命周期与全局错误 |
| `shared/21-network-security.md` | 域名白名单、HTTPS、web-view |
| `shared/22-error-recovery-offline.md` | 错误恢复、弱网离线 |
| `shared/23-content-safety.md` | 富文本、UGC 安全 |
| `shared/24-design-system-mobile.md` | 设计 Token、Base 组件 |
| `shared/25-dependency-supply-chain.md` | 依赖 audit、供应链 |
| `shared/26-security-hardening-risk.md` | 安全加固、风控、实验、多平台矩阵 |
| `docs/observability-metrics.md` | 推荐指标与 SLO |
| `docs/owasp-miniapp-mapping.md` | OWASP 裁剪对照 |

### codex / cursor / docs / evals / scripts

| 路径 | 职责 |
|---|---|
| `codex/AGENTS.md` | Codex 任务表与路径触发 |
| `codex/01`–`09` | 改代码前、页面、登录、平台、验证、运行时、网络、恢复、内容安全 |
| `cursor/*.mdc` | Cursor 触发摘要 |
| `docs/fullstack-contract.md` | 与后端/管理端契约对齐 |
| `docs/business-feature-playbook-miniapp.md` | 新业务分包步骤 |
| `docs/compliance-wechat-checklist.md` | 微信合规与审核 |
| `docs/contributing-rules-package.md` | 维护者变更清单 |
| `docs/onboarding-new-project.md` | 新建小程序项目落地 |
| `docs/release-checklist.md` | 业务发布 / 灰度 / 回滚证据清单 |
| `docs/component-engineering-coverage.md` | 组件、样式、生命周期、测试与性能覆盖矩阵 |
| `docs/rules-package-index.md` | shared 00–26 索引 |
| `docs/rule-maturity-model.md` | 采纳 Level 0–3 |
| `docs/cursor-shared-map.md` | Cursor ↔ shared 编号对照（含 AI `27`→`17`） |
| `examples/README.md` | 脚本、CI、脚手架说明 |
| `evals/prompts.md` | 回归提示词 M01–M52 |
| `evals/ai-tool-safety.md` | AI 工具安全独立门禁 MAT01–MAT05（5/5） |
| `evals/rubric.md` | P0 8/8；核心 P1 >=10/12；Security 5/5；Resilience 4/4；Enterprise Hardening 6/6；Component Engineering 6/6；Media 1/1 |
| `evals/smoke-prompts.md` | 套件索引 |
| `evals/adoption-checklist.md` | 业务仓落地清单 |
| `scripts/validate-rules-package.py` | 规则包一致性校验 |
| `examples/scaffold/` | request / 登录最小样板 |
| `RELEASE.md` | 发版 Checklist |

## Evals

| 级别 | 范围 | 门槛 |
|---|---|---|
| P0 | M01–M08 | 8/8 |
| 核心 P1 | M09–M20 | >=10/12 |
| Business Extension | M21–M29 | 建议 9/9 |
| Security Extension | M30–M34 | 建议 5/5 |
| Resilience Extension | M35–M38 | 建议 4/4 |
| Enterprise Hardening Extension | M39–M44 | 建议 6/6 |
| Component Engineering Extension | M45–M50 | 建议 6/6 |
| Media Extension | M51 | 建议 1/1 |
| Testing Governance | M49、M52 | 建议 2/2 |

详见 `evals/README.md`。

## 参考口径

- Google / Airbnb：强制性措辞、TypeScript 与 lintable code style。
- 腾讯 / 微信小程序：分包、包体积、隐私授权、平台能力、审核风险。
- DCloud / uni-app：Vue3、TypeScript、`pages.json`、`manifest.json`、跨小程序平台差异。
- 企业移动端实践：页面瘦身、能力封装、弱网、幂等、埋点和灰度开关。
