# 04 Page UI Lifecycle

> 应用级 `onLaunch` / 全局错误 / `scene` 见 `20-app-runtime.md`。弱网与统一 error 恢复见 `22-error-recovery-offline.md`。本文约束 Vue 组件与 uni-app 页面生命周期的协作边界。

## 页面骨架

页面建议按以下顺序组织：

1. 导航 / 标题 / 安全区。
2. 核心状态：loading、error、empty、content。
3. 表单 / 列表 / 卡片。
4. 底部操作区。
5. 授权、登录、支付、分享等弹层。

## 生命周期

1. `onLoad`：解析路由参数、初始化页面级不可变上下文。
2. `onShow`：处理返回刷新、登录态恢复、订单状态刷新。
3. `onPullDownRefresh`：只做刷新，不改变筛选条件。
4. `onReachBottom`：只触发下一页加载，须防重复触发。
5. `onHide`：暂停轮询、上报停留时长。
6. `onUnload`：清理 timer、事件监听、长连接、未完成任务。

## Vue 3 组件生命周期

1. `<script setup>` 顶层是 setup 阶段，只声明状态、computed、watch 和 composable；节点操作等待挂载。
2. `onBeforeMount` / `onMounted` 只处理节点测量、第三方实例和组件级监听；页面首批数据由 `onLoad` 统一组织。
3. `onBeforeUpdate` / `onUpdated` 不无条件写响应式状态；节点测量需节流并核验真实变化。
4. `onBeforeUnmount` / `onUnmounted` 清理 timer、watch、EventBus、平台监听、Observer、第三方实例和可取消任务。
5. 使用 `<KeepAlive>` 时，`onActivated` 恢复必要刷新/监听，`onDeactivated` 暂停轮询和高频监听。
6. `watch` / `watchEffect` 中的异步副作用使用 cleanup 或请求版本号，防止旧响应覆盖新状态。

## 应用、页面与组件执行边界

冷启动按“应用启动 → 页面加载/显示 → Vue 组件挂载”理解；热启动通常从应用和页面 `onShow` 恢复。具体顺序以目标平台和当前运行时验证结果为准，不依赖同阶段钩子的偶然精确排序。

| 任务 | 推荐位置 |
|---|---|
| 环境、错误处理、更新检查、scene 分发 | App `onLaunch` / bootstrap |
| 路由参数解析、页面首次上下文 | 页面 `onLoad` |
| 返回页后的按需刷新 | 页面 `onShow` |
| 节点测量、组件第三方实例 | 组件 `onMounted` |
| 页面不可见时暂停轮询 | 页面 `onHide` / 组件 `onDeactivated` |
| 组件资源清理 | `onBeforeUnmount` / `onUnmounted` |
| 页面资源和未完成任务清理 | 页面 `onUnload` |

同一请求、监听或 timer 必须有唯一 owner；创建者负责清理，跨生命周期资源上移到 App、service 或 store 管理。

## 禁止

- 禁止在 `onShow` 无条件重复拉取所有接口。
- 禁止在 `onLoad` 同步处理大数组或大 JSON。
- 禁止把授权弹窗、登录弹窗、业务弹窗互相嵌套成不可恢复状态。
- 禁止忽略页面栈，反复 `navigateTo` 导致返回链路异常。
- 禁止把同一首屏请求同时放进 setup、`onMounted`、`onLoad` 和 `onShow`。
- 禁止匿名注册无法注销的 EventBus、平台或全局监听器。
