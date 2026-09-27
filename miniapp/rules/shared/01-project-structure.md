# 01 Project Structure

## 推荐目录

```text
src/
├─ App.vue                # 应用级生命周期（见 20-app-runtime）
├─ app/                   # bootstrap、全局错误、scene 解析（可选目录名）
├─ pages/                 # 主包页面：登录、首页、tabBar、启动链路
├─ subpackages/           # 业务分包：order、member、coupon、after-sale
├─ components/            # 通用展示组件
├─ base/                  # 项目 Base 组件与基础移动组件封装
├─ api/                   # request 封装、allowed-hosts、API 方法
├─ api/generated/         # OpenAPI / schema 生成，禁止手改
├─ services/              # 业务流程服务
├─ composables/           # 页面组合逻辑
├─ stores/                # Pinia store
├─ auth/                  # 登录态、token、手机号绑定
├─ privacy/               # 隐私授权、权限用途登记
├─ platform/              # 小程序平台能力 adapter
├─ utils/
├─ styles/
├─ static/                # 必要小图标；大资源不得进主包
├─ pages.json
└─ manifest.json
```

## 分层职责

1. `pages/` 与 `subpackages/`：只处理页面生命周期、UI 状态、用户事件。
2. `composables/`：处理分页、刷新、表单状态、页面局部组合逻辑。
3. `services/`：处理跨 API 的业务流程，例如下单后支付、授权后绑定手机号。
4. `api/`：只负责 request、接口方法和 generated 类型衔接。
5. `platform/`：封装 `uni.login`、支付、分享、订阅消息、扫码、位置、媒体、web-view 白名单。
6. `auth/`：封装 token、session、登录态刷新、手机号绑定。
7. `privacy/`：维护敏感能力用途、授权前置检查、用户拒绝后的降级。
8. `App.vue` / `app/`：应用级 onLaunch、全局错误、scene 分发；禁止堆页面级业务（`20`）。

## 禁止

- 禁止页面直接依赖后端字段、平台 API 和 storage key。
- 禁止单业务修改公共 adapter 后影响所有业务，除非有 Owner 和回归说明。
- 禁止把低频业务、活动页、大组件放进主包。
