# 列表分页与表格状态规则

适用于带筛选、排序、分页的列表页（`src/views/**`）。若项目有 `useTable` 或等价 composable，**这些行为应在 composable 内默认实现**，页面只编排 UI。

## 单一数据源

分页、筛选、排序参数须有**唯一主来源**（三选一为主，其余只读同步）：

1. composable / store 内的 reactive 状态（推荐）
2. URL query（适合可分享、可书签的列表）
3. 组件 local state（仅简单单页、无 URL 同步时）

禁止同一页面多处各自维护 `page` / `pageSize` / `filters` 导致不同步。

## 页码行为（offset 分页）

1. **筛选条件变化**（含搜索关键词、下拉筛选、日期范围）：`page` 必须重置为 `1` 再请求。
2. **`pageSize` 变化**：`page` 必须重置为 `1` 再请求。
3. **删除当前页最后一条**：删除成功后，若当前页已无数据且 `page > 1`，须 `page -= 1` 再请求（或 composable 等价逻辑）。
4. **编辑成功**：通常保持当前 `page` 与筛选条件，刷新当前页数据。
5. **新增成功**：是否回到第一页由业务约定；默认「仍停留当前筛选，回到第 1 页展示新数据」须在 PR 说明中写清。

## 批量操作后刷新

1. 批量删除、批量启用、批量停用、批量分配等操作成功后，必须清空当前 selection，避免旧选中项继续参与下一次操作。
2. 批量删除后若当前页剩余数据不足或为空，须按删除数量与最新 `total` 重新计算页码；不能固定请求原页导致空页。
3. 批量状态变更通常保持当前筛选与页码并刷新当前页；若操作会改变当前筛选命中结果（如筛选「启用」后批量停用），须刷新并修正页码。
4. 批量操作部分失败时，应展示成功 / 失败数量与可重试项，不要只显示“操作失败”。

## 请求竞态

搜索、筛选、翻页、排序触发的列表请求必须防竞态，**禁止旧响应覆盖新数据**。至少采用一种：

- `AbortController` 取消过期请求
- 递增 `requestId`，仅应用最新一次响应
- `useTable` 内置的 stale 忽略

快速连续操作时，UI loading 状态应与「当前有效请求」一致。

## URL 同步

- 非敏感筛选（如状态、分类）可按项目约定 sync 到 URL query。
- **敏感筛选**（手机号、证件号、完整姓名等）**不得**写入 URL 或浏览器历史。
- URL 与 composable 双向同步时，仍遵守「筛选变化 → page=1」。

## offset 分页 vs cursor 分页

- 契约为 `page` + `pageSize` 时，使用 offset 分页组件与上述行为。
- 契约为 `cursor` / `nextToken` 时，**不要硬套** `page/pageSize`；翻页只追加或替换 cursor，遵循 schema 定义。
- 改分页模型须与 `contracts/schema.json` 及后端一致。

## 与 UI 模式的关系

表格 loading、empty、error、pagination 骨架见 `04-ui-patterns.md`；`useTable` error 态与重试见 `00-must-follow` §16。

## 大列表

单页渲染行数超过项目性能预算（见 `07-security-performance.md`）时，须服务端分页或虚拟滚动，禁止一次性 bind 数千行到 DOM。
