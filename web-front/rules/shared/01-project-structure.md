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

目录、文件、views 路径命名见 **`shared/02-naming.md`**。
