# 06 App Runtime

改 `App.vue`、`src/app/**` 时：

1. 先读 `shared/20-app-runtime.md`。
2. `onLaunch` 禁止阻塞式重业务；scene/分享入参白名单后交给 `auth` / 路由。
3. `onError`、`onUnhandledRejection` 须统一上报（`15`）。
4. `onPageNotFound` 须跳转兜底页。
5. 样板：`examples/scaffold/App.vue.sample`、`app-bootstrap.ts.sample`、`app-error-handler.ts.sample`。
