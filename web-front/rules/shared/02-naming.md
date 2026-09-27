# 命名规则

命名目标：读名字即可理解职责、类型和作用域。

## 总原则

1. 命名使用英文语义，不用拼音、缩写黑话或无意义数字后缀。
2. 同一概念全项目只用一个词：`user` / `account` / `member` 不得混用。
3. 命名先看项目既有约定；若无约定，按本文件执行。
4. 禁止用 `new`、`old`、`temp`、`test`、`demo`、`final`、`copy` 表示业务含义。
5. 业务缩写必须是团队公认词，如 `URL`、`ID`、`API`；自造缩写需避免。

## 文件与目录

| 类型 | 规则 | 示例 |
|---|---|---|
| 目录 | kebab-case 或项目既有约定 | `user-management/` |
| Vue 组件 | PascalCase | `UserEditDialog.vue` |
| composable | `useXxx.ts` | `useTable.ts` |
| API 文件 | `module.api.ts` | `user.api.ts` |
| 类型文件 | `module.types.ts` | `user.types.ts` |
| 常量文件 | `module.constants.ts` | `route.constants.ts` |
| 枚举文件 | `module.enums.ts` | `user.enums.ts` |
| Store 文件 | `module.store.ts` 或 `useModuleStore.ts`（按项目约定二选一） | `user.store.ts` |
| 工具文件 | kebab-case 或 `module.util.ts` | `date-format.ts`, `user.util.ts` |
| 测试文件 | 与被测文件同名 + `.spec.ts` / `.test.ts` | `user.api.spec.ts` |
| 样式文件 | kebab-case 或与组件同名 | `user-list.scss`, `UserCard.module.scss` |

## Views 路径

1. `src/views/**` 目录使用 kebab-case，按业务域分层：`system/user/`、`order/refund/`。
2. 页面入口优先使用 `index.vue`；页面私有组件放同级 `components/`。
3. 页面私有 composable 放同级 `composables/`，如 `useUserList.ts`。
4. 路由 `name` 使用 PascalCase，稳定且全局唯一：`SystemUser`、`OrderRefundDetail`。
5. `keepAlive` 页面组件 `defineOptions({ name })` 必须与路由 `name` 一致。
6. URL path 使用 kebab-case，不使用 camelCase、PascalCase 或中文：`/system/user-role`。

## 变量

1. 普通变量使用清晰名词：`userName`、`orderTotal`。
2. 布尔值使用 `is`、`has`、`can`、`should`。
3. 数量使用 `total`、`count`、`max`、`min`。
4. 集合使用复数或明确后缀：`users`、`selectedRows`。
5. ID 字段按项目约定统一使用 `id` / `xxxId`，不要混用 `xxxID`、`xxx_id`（除非接口契约要求）。
6. 禁止单独使用模糊变量名：`data`、`info`、`obj`、`temp`、`flag`；禁止用裸名 `list`、`item` 表示业务数据（`for (const item of rows)` 等循环短作用域除外）。表格/列表数据优先 `rows`、`tableData`、`records`、`userList`。

## 方法

| 动作 | 前缀 |
|---|---|
| 获取本地/同步数据 | `get` |
| 异步请求 | `fetch` / `query` |
| 新增 | `create` |
| 更新 | `update` |
| 保存 | `save` |
| 删除 | `delete` / `remove` |
| 导入导出 | `import` / `export` |
| 事件处理 | `handle` |
| 校验 | `validate` |
| 格式化 | `format` |
| 重置 | `reset` |
| 转换 | `map` / `to` |

示例：

```ts
function fetchUserPage() {}
function handleSearch() {}
function handleBatchDelete() {}
```

## Type / Interface / Enum

1. 类型、接口使用 PascalCase：`UserQueryParams`、`UserPageResult`。
2. Props / Emits 类型使用组件名后缀：`UserEditDialogProps`、`UserEditDialogEmits`。
3. Enum 名使用 PascalCase，成员使用 PascalCase 或项目统一风格，不混用：`UserStatus.Enabled`。
4. 常量枚举映射使用 `UPPER_SNAKE_CASE` 或 `PascalCaseMap`，按项目约定统一：`USER_STATUS_LABEL`、`UserStatusLabelMap`。
5. 后端生成类型以 generated 为准，不为 generated 类型另造近似名称。

## CSS / SCSS / Modules

1. class 使用 kebab-case：`.user-list`、`.filter-bar`。
2. BEM 可用但须统一：`.user-list__toolbar`、`.user-list__action--danger`。
3. CSS Modules 导入名使用 `styles`；禁止 `s`、`css` 等模糊名。
4. Token 变量使用项目约定；CSS 自定义属性使用 kebab-case：`--app-header-height`。
5. 禁止用颜色或视觉位置命名业务 class：`.red-button`、`.left-box`；应使用语义：`.danger-action`、`.summary-panel`。

## 环境变量

1. Vite 环境变量必须使用 `VITE_` 前缀。
2. 环境变量使用 `UPPER_SNAKE_CASE`：`VITE_API_BASE_URL`、`VITE_APP_RELEASE`。
3. 禁止把密钥、Token、私有证书放入前端环境变量。
4. 布尔环境变量须明确约定字符串值，如 `'true'` / `'false'`，读取时统一转换。

## 权限、路由、事件名

1. 权限码按项目约定统一，推荐 `domain:resource:action`：`system:user:create`。
2. 埋点 / 日志事件名见 `18-logging-observability.md`，使用 `domain.resource.action.result`。
3. 路由 path、权限码、事件名不得互相借用；各自保持稳定语义。

## 禁止示例

```ts
const data = {}
const flag = true
const userInfo2 = {}
enum status { enable, disable }
```

```text
src/views/System/UserList.vue
src/views/userManage/
VITE_token
.red-button
```
