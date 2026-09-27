# 20 App Runtime

应用级生命周期与全局初始化。页面级规则见 `04-page-ui-lifecycle.md`。

## 职责边界

1. `App.vue`（或 `src/app/bootstrap.ts`）只负责应用级编排：环境初始化、全局错误、更新、scene 入参分发。
2. 重业务逻辑进 `services/`、`auth/`；禁止在 `onLaunch` 同步拉取大量接口或解析大 JSON。
3. 冷启动 / 热启动差异须在 `onShow`（应用级）与页面 `onShow` 分层处理，避免重复初始化。

## onLaunch

1. 只做：读取构建环境、初始化日志/trace、注册全局错误处理、解析 `scene` / 分享入参并交给 `auth` 或路由服务。
2. 禁止阻塞：大量接口、支付预下单、全量字典、大缓存恢复。
3. 需要预热的接口应异步、可失败、不得拖死首屏。

## onShow（应用级）

1. 处理热启动：登录态校验、待处理 deeplink、订单状态刷新（按需）。
2. 与页面 `onShow` 分工明确，避免双份重复请求。

## 全局错误与兜底

1. `onError`、`onUnhandledRejection` 必须进入统一 handler：结构化上报（含 traceId、页面栈、平台、版本），禁止仅 `console`。
2. `onPageNotFound` 必须跳转统一兜底页或首页，禁止白屏。
3. 用户可见提示与内部日志分离（`15`）。

## 更新

1. `UpdateManager` 封装在 `platform/` 或 `app/update.ts`；说明强更 / 可选更策略。
2. 更新失败、用户取消须有提示；禁止无限弹窗。

## scene / 分享 / 扫码入参

1. 入参必须白名单解析（与 `14` 一致）；禁止直接把原始 `scene` 写入 storage 或传给 H5。
2. 全局初始化只分发到 `auth` / 路由服务，页面不各自解析一套规则。

## 禁止

- 禁止在 `onLaunch` 直接 `uni.login`、支付、订阅消息（走 `auth` / `platform`）。
- 禁止应用级与页面级重复注册相同全局监听且不清理。
- 禁止未处理的应用级 Promise rejection 静默失败。
