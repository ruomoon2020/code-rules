# Codex 页面生成规则

用于创建或修改 `src/views/**`（及 monorepo 内 `packages/*/src/views/**`）。

## 编辑前必读

1. `rules/shared/00-must-follow.md`
2. `rules/shared/04-ui-patterns.md`
3. `rules/shared/19-list-pagination.md`（列表页含分页 / 筛选时）
4. `rules/shared/13-form-and-detail.md`（含表单弹窗 / 详情时）
5. `rules/shared/05-api-contract.md`（有 API / 表单 / 表格字段时）
6. `rules/shared/06-state-route-permission.md`（有路由 / 权限时）
7. `rules/shared/11-base-components-context.md`
8. `rules/shared/12-schema-ssot.md`

## 页面骨架

```vue
<BasePage>
  <BasePageHeader />
  <BaseFilterBar />
  <BaseToolbar />
  <BaseTable />
  <BasePagination />
  <EntityEditDialog />
</BasePage>
```

必须处理：loading、empty、error（含重试）、permission、提交 loading、破坏性操作确认。

列表页优先 `useTable`（或项目等价封装），须含 error 态；分页、筛选、竞态见 `rules/shared/19-list-pagination.md`。

## 缓存页（Keep-Alive）

```ts
defineOptions({ name: 'RouteName' })
```

`RouteName` 与路由 `name` 完全一致。

## 输出检查清单

见 `rules/shared/10-verification-checklist.md`。
