# 新业务分包 Playbook（小程序）

新增 `src/subpackages/{domain}/` 时按序执行。

## 1. 契约

- [ ] `contracts/openapi.yaml` 已含列表 / 详情 / 写操作路径与 DTO
- [ ] 运行 `api:gen`、`api:check`
- [ ] 禁止手改 `src/api/generated/**`

## 2. 分包与路由

- [ ] 页面位于 `src/subpackages/{domain}/pages/**`
- [ ] `pages.json` 已登记分包、标题、导航栏
- [ ] 评估 `preloadRule`；无收益则不预下载
- [ ] 未引入跨业务分包依赖

## 3. 主包与体积

- [ ] 未把低频业务、大图、大型 SDK 放入主包
- [ ] `pnpm build:mp-weixin` + `size:check` 通过或在预算内

## 4. 页面实现

- [ ] 列表四态（`12`）；分页字段与 OpenAPI 一致
- [ ] 请求走 `src/api/request`；无页面直调 `uni.request`
- [ ] 平台能力走 `platform/` / `auth/` / `privacy/`

## 5. 合规（若涉及）

- [ ] 敏感能力：用途说明、用户触发、拒绝降级（`09`）
- [ ] manifest / 隐私政策与代码一致
- [ ] 支付 / 分享 / 订阅消息按 `14` 实现

## 6. 验证

- [ ] `pnpm lint`、`type-check`、`build:mp-weixin`、`api:check`
- [ ] 新业务分包 PR 跑 evals **Business Extension** M21–M29（建议 9/9）
- [ ] UGC / 富文本 / 错误恢复 / 可观测相关 PR 跑 **Resilience Extension** M35–M38（建议 4/4）
- [ ] 安全加固 / 无障碍 / 多平台 / 实验相关 PR 跑 **Enterprise Hardening Extension** M39–M44（建议 6/6）
- [ ] 涉及组件、主题、生命周期、测试或性能时跑 **Component Engineering Extension** M45–M50（建议 6/6）
- [ ] 管理端 **E41–E43**（Platform Extension）**不适用**小程序；见 `docs/fullstack-contract.md` §与管理端 Platform Extension 的边界

## 7. 联调

- [ ] traceId / errorCode 与后端日志可对齐
- [ ] 支付、登录、订单状态与后端一致
