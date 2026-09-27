# 状态、路由与权限规则

用于 Pinia、Vue Router、权限、缓存页面。

## Store

1. 全局状态只放用户、权限、主题、字典、租户等跨页面数据。
2. 页面临时状态留在页面或 composable。
3. 登出必须执行 `resetAllStores()` 或等价全局清理。
4. 持久化 store 必须明确字段白名单。
5. 敏感数据不要明文持久化。
6. store 禁止直接操作 DOM。

## Route

1. 路由 `name` 使用 PascalCase，并与菜单、权限、keep-alive 对齐。
2. 需要缓存的页面必须写 `defineOptions({ name })`。
3. `defineOptions({ name })` 必须与路由 `name` 完全一致。
4. 路由 **path** 使用 kebab-case，不用 camelCase、PascalCase 或中文（详见 `02-naming.md` §Views 路径）。
5. 路由 meta 至少明确 title、permission、keepAlive、hidden 等项目约定字段。
6. URL 中可同步筛选状态，但不要暴露敏感查询条件。

## Permission

1. 前端权限只控制展示和交互，后端必须做真实鉴权。
2. 按钮权限使用统一指令或 helper。
3. 权限码命名保持模块化，例如 `system:user:create`。
4. 字段级权限必须同时处理展示、编辑和提交。
5. 权限刷新后应更新菜单、路由、按钮和缓存页状态。
