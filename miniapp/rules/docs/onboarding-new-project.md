# 新建 uni-app 小程序项目落地指南

> 维护者与架构 onboarding；AI 日常读 `README.md`、`codex/AGENTS.md`。

## 1. 复制规则包

```text
your-miniapp/
├─ AGENTS.md                      ← rules/codex/AGENTS.md
├─ rules/                         ← 整包 miniapp/rules
├─ contracts/openapi.yaml         ← 可与 monorepo 根 contracts/ 同步
├─ .cursor/rules/*.mdc            ← rules/cursor/
├─ .cursor/rules/99-project-local.mdc  ← examples/99-project-local.mdc.sample
└─ src/
   ├─ App.vue
   ├─ pages/、subpackages/、api/、auth/、platform/、privacy/
   ├─ pages.json、manifest.json
   └─ ...
```

## 2. 推荐技术选型

- Vue 3 + TypeScript + uni-app + Vite
- Pinia、OpenAPI 生成 `src/api/generated`
- 目标端：微信小程序优先；按需扩展支付宝等（`11-platform-differences`）

## 3. 最小能力落地顺序

1. **契约**：`contracts/openapi.yaml` → `api:gen` → `api:check`
2. **网络**：`examples/scaffold/request.ts.sample` + `allowed-hosts.ts.sample`
3. **App 运行时**：`examples/scaffold/App.vue.sample` + `app-error-handler.ts.sample`
4. **登录**：`auth-login.service.ts.sample` → `src/auth/`
5. **主包页面**：登录、首页、tabBar；**业务页进分包**
6. **环境**：`VITE_APP_ENV`、`VITE_API_BASE_URL`（`19`；体验/审核版禁连生产）

## 4. 硬门禁接入

| 门禁 | 命令 / 文件 |
|---|---|
| Lint / 类型 | `pnpm lint`、`pnpm type-check` |
| 构建 | `pnpm build:mp-weixin` |
| 契约 | `pnpm api:check` |
| 主包体积 | `pnpm size:check`（见 `examples/scripts/check-miniapp-size.mjs.sample`） |
| 规则包一致性 | `python rules/scripts/validate-rules-package.py` |
| CI workflow | 复制 `examples/ci/rules-package-validate.yml` |

## 5. 与后端 / 管理端联调

1. 共用 `contracts/openapi.yaml`
2. 后端兼容发布 → 小程序 `api:gen` + 联调
3. 对齐 `traceId`、`errorCode`、分页（`docs/fullstack-contract.md`）

## 6. 验证

- 落地清单：`evals/adoption-checklist.md`
- 日常 PR：**Smoke**（`evals/smoke-prompts.md`）
- 发版：**Full** M01–M52（P0 8/8，核心 P1 >=10/12）
- 新业务分包：**Business Extension** M21–M29（建议 9/9）
- App/网络/环境 PR：**Security Extension** M30–M34（建议 5/5）
- 错误恢复/UGC/可观测 PR：**Resilience Extension** M35–M38（建议 4/4）
- 安全加固/无障碍/多平台/实验 PR：**Enterprise Hardening Extension** M39–M44（建议 6/6）
- 组件/样式/生命周期/测试/性能 PR：**Component Engineering Extension** M45–M50（建议 6/6）
- PR 模板：复制 `examples/.github/` → 仓库根 `.github/`
- 企业级 DoD / 豁免 / 接入验收：monorepo `docs/definition-of-done.md`、`docs/enterprise-governance.md`、`scripts/check-project-adoption.py`

## 7. 成熟度（可选）

见 `docs/rule-maturity-model.md` 声明 Level 0/1/2，不必一次接入全部 shared。
