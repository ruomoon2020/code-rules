# 07 Pages Routing Subpackages

## pages.json

1. 新页面必须登记 `pages.json`。
2. 页面标题、导航栏、tabBar、分包配置必须和产品语义一致。
3. 开发调试用 `condition` 不得影响生产。
4. `preloadRule` 必须有收益说明，禁止预下载过多低频分包。

## 主包

主包只允许放：

- 启动页、登录页、首页、tabBar 页面。
- 基础组件、基础样式、request、auth、platform adapter。
- 高频首屏必需资源。

## 分包

1. 新业务域默认进 `src/subpackages/{domain}/`。
2. 分包内部优先自包含页面、组件和局部资源。
3. 分包不得依赖其他业务分包。
4. 跨分包公共代码需要上提到公共层，并评估主包体积。

## 页面栈

1. 普通详情使用 `navigateTo`，完成后可返回。
2. 登录完成、支付完成、关键流程重置可使用 `redirectTo` / `reLaunch`。
3. 禁止无限叠加页面栈。
