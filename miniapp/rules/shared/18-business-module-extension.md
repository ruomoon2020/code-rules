# 18 Business Module Extension

适用于 uni-app 小程序**新增业务域分包**（如 order、member、coupon）。本文是业务二开装配层：不替代 `00`–`17`，只规定如何复用主包能力与契约。

全栈联调见 monorepo `web-backend/rules/docs/fullstack-contract.md` §小程序；步骤清单见 `docs/business-feature-playbook-miniapp.md`。

## 默认原则

1. 新业务默认进入 `src/subpackages/{domain}/`，不污染主包 `pages/`、`auth/`、`platform/` 全局逻辑，除非经 Owner 评审。
2. 主包只保留启动、登录、tabBar、request、auth、platform adapter、高频 Base 组件。
3. 禁止业务分包互相 import 页面或业务组件；公共能力上提主包公共层。
4. 后端 OpenAPI / 登录态 / 支付未就绪时，不得先写「假字段」页面联调。
5. 涉及支付、订阅消息、分享、隐私能力时，同步读 `14`、`09` 与对应 codex 任务包。

## 契约与 API

1. 字段、列表列、表单以 `contracts/openapi.yaml` 与 `src/api/generated` 为 SSOT（`05`）。
2. 改接口先改契约，再 `api:gen` → `api:check`；**禁止**手改 `generated`。
3. 页面禁止直接 `uni.request`；API 走 `src/api`（`00`）。

## 分包与 pages.json

1. 新页面登记 `pages.json`：分包 root、标题、必要时 `preloadRule`（`07`）。
2. 预下载须有收益说明；禁止预下载过多低频分包。
3. 新增依赖、静态资源须评估主包 / 分包体积（`10`）。

## 页面与列表

1. 列表页须含加载、空、错误、正常、分页到底、下拉刷新（`12`）。
2. 查询、分页字段与 OpenAPI 一致；删末条回退页码；防重复请求与离页竞态（`04`）。
3. 平台能力走 `platform/` / `privacy/` / `auth/`，禁止页面直调（`00`）。

## 支付 / 分享 / 订阅（若涉及）

1. 支付参数来自后端下单；最终状态以后端订单为准（`14`）。
2. 分享参数白名单；禁止 token、手机号（`14`）。
3. 订阅消息用户触发，处理拒绝与模板失效（`14`）。

## 禁止

- 虚构 OpenAPI 字段、分包路径、`pages.json` 配置。
- 页面直调 `uni.request`、`uni.login`、支付、订阅消息、手机号授权。
- 跨业务分包依赖；主包塞低频业务、大图、大型 SDK。
- 未同步隐私说明 / manifest 即调用敏感能力。
- 分包 PR 不跑 `build:mp-weixin` / `size:check`。

## 与其他规则的关系

结构见 `01`；分包见 `07`；契约见 `05`；收尾见 `16`、`codex/05-verification.md`。后端模块边界见 `web-backend/rules/shared/43-business-module-extension.md`。
