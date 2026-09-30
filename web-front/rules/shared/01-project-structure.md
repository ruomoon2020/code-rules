# 项目结构规则

用于约束目录职责、依赖方向和文件归属。

## 推荐结构

```text
src/
├─ api/
├─ assets/
├─ components/
│  ├─ base/
│  ├─ business/
│  └─ layout/
├─ composables/
├─ constants/
├─ directives/
├─ enums/
├─ layouts/
├─ plugins/
├─ router/
├─ store/
├─ styles/
├─ types/
├─ utils/
└─ views/
```

上述结构适用于单应用、中小规模管理端。当业务域增多，一个需求持续跨 `views` / `api` / `types` / `store` 修改时，转为「业务域优先 + shared 稳定复用层」：

```text
src/
├─ app/                       # 启动、路由、全局 Provider
├─ modules/
│  └─ user/
│     ├─ api/                 # 业务薄封装，不重复 generated DTO
│     ├─ model/               # 业务状态与规则
│     ├─ pages/
│     ├─ components/
│     └─ tests/
├─ shared/
│  ├─ api/generated/          # 契约生成，禁止手改
│  ├─ components/base/
│  ├─ composables/
│  └─ utils/
└─ layouts/
```

两种结构选一种作为项目主模式，写入 `99-project-local`；禁止同一业务一半放 `modules/{domain}`、一半散落在全局横向目录。

## 依赖方向

允许：

```text
views -> business components -> base components
views -> composables -> api
views -> store
api -> request wrapper
components -> types / constants / enums
```

禁止：

```text
base components -> views
base components -> business API
utils -> Vue component instance
store -> DOM operation
api -> Element Plus message directly
```

## 放置规则

1. 页面独用组件放在页面附近的 `components/`。
2. 两个及以上页面复用后，再沉淀到 `components/business`。
3. 与业务无关、可跨模块使用的 UI 能力才进入 `components/base`。
4. 纯函数进入 `utils`，带 Vue 状态的复用逻辑进入 `composables`。
5. 请求声明进入 `api`，不要散落在组件里。
6. 常量、枚举、类型分别进入 `constants`、`enums`、`types`。
7. 多应用场景下，公共 UI 和工具抽到 `packages`，应用只依赖 packages。
8. 业务域优先结构中，模块只能通过对方公开出口或 shared 契约协作；禁止深路径导入对方内部文件。
9. 采用默认横向 `views/`、`store/`、`api/` 结构时也必须标识业务域边界；一个业务域禁止直接导入另一业务域的 store、页面私有组件、页面 composable 或手写请求封装。
10. 横向结构的跨域协作只能使用 `components/base` 等稳定共享能力、OpenAPI 同步生成的 API 类型和壳层公开接口；业务专属代码不得为了跨域引用迁入全局 store、`utils` 或公共组件。

目录、文件、views 路径命名见 **`shared/02-naming.md`**。
