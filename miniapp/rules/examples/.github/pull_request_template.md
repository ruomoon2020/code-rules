# Pull Request（小程序）

> 复制自 `rules/examples/.github/` → 业务仓 `.github/pull_request_template.md`

## 变更摘要

<!-- 1–3 句话 -->

## 变更类型（勾选）

- [ ] OpenAPI / `api/generated`
- [ ] 新页面 / 分包 / `pages.json`
- [ ] 登录 / 隐私 / 授权
- [ ] 支付 / 订阅消息 / 分享
- [ ] App 运行时（`App.vue`、全局错误、scene）
- [ ] 网络 / web-view / 域名白名单
- [ ] 错误恢复 / 弱网 / 富文本 UGC
- [ ] 环境 / 发版配置
- [ ] 新业务分包（二开）
- [ ] 仅文档 / 规则包
- [ ] 其他：__________

---

## 必填检查

### 契约与 API

- [ ] 已更新 `contracts/openapi.yaml`（若改接口）
- [ ] 已运行 `pnpm api:gen` + `pnpm api:check`（或说明未配置）
- [ ] 未手改 `src/api/generated/**`

### 架构

- [ ] 页面未直调 `uni.request` / `uni.login` / 支付 / 订阅消息
- [ ] 新业务页在分包（非主包塞低频业务）
- [ ] 涉及 `18` 时：仅新业务扩展；修 bug/样式已对照 `99-project-local`

### 合规与安全（若涉及）

- [ ] 敏感能力：用途说明 + 用户触发 + 拒绝降级
- [ ] 分享/scene 白名单；无 token/手机号
- [ ] 域名 / web-view 白名单；生产 HTTPS
- [ ] 体验/审核版未连生产 API 与支付

### 验证

- [ ] `pnpm lint`、`pnpm type-check`、`pnpm build:mp-weixin`
- [ ] `pnpm size:check`（或说明预算与 skip 原因）

### 企业 DoD（monorepo）

- [ ] Required CI 全绿（`docs/definition-of-do.md`）
- [ ] 改依赖 / 锁文件：`docs/supply-chain-baseline.md` + `pnpm audit`
- [ ] UGC / PII / storage：`docs/data-classification-matrix.md`
- [ ] 跳过门禁：豁免单 `docs/rule-exception-process.md`
- [ ] CODEOWNERS：`docs/codeowners-matrix.md`

---

## Evals（建议）

| 套件 | 何时跑 |
|---|---|
| Smoke | 日常 PR |
| Security Extension M30–M34 | App / 网络 / 环境 PR |
| Business Extension M21–M29 | 新业务分包 PR |
| Resilience M35–M38 | 错误恢复 / UGC / 可观测 PR |
| Full M01–M38 | 规则包升级 / 发版前 |
