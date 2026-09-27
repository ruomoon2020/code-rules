# 基础组件上下文（Context Pinning）

生成或修改 `src/views/**` 前，必须先阅读目标仓库中对应 Base 组件源码。

常见路径示例：

```text
src/components/base/BaseTable/
src/components/base/BaseForm/
src/components/base/BaseDialog/
src/components/base/BaseFilterBar/
src/components/base/BasePagination/
src/components/base/BasePage/
```

Monorepo 中若在 `packages/ui` 等目录，以该包内 `components/base/` 为准。

## 规则

- 禁止虚构 Base 组件 props、slots、events。
- 存在 Base 封装时，`views` 不得回退为原生 Element Plus（含 `el-*` 与 denylist 内 `<ElButton>` 等，见 `00-must-follow` §5–7）。
- prop 名称不确定时，打开组件文件核对，禁止凭记忆或示例猜测。

## 契约来源

唯一有效契约是**目标仓库中的组件源码**，须核对：

- props、events、slots、v-model 名称
- loading / empty / error 行为
- 可访问性行为

源码缺失或不清时，停止实现并询问，不得猜测 API。

## 行为期望（非 prop 契约）

- 表格：loading、empty、error、行操作、分页组合（行为见 `19-list-pagination.md`）。
- 表单：字段来自 schema / generated DTO；提交有 loading。
- 筛选：搜索、重置、页码重置。
- 弹窗 / 抽屉：脏数据关闭提示、焦点管理。

## 标准列表页骨架

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

组件名以项目实际导出为准。
