# Schema 单一事实来源

生成或修改业务页面、API 封装、表单、筛选、表格前：

1. 读取 `contracts/schema.json` 或项目约定的 schema 文件。
2. 读取 `src/api/generated` 中对应类型。
3. 定位 service 与 operation，例如 `system.User.create`、`system.User.page`。
4. 仅根据契约生成字段与类型。
5. 禁止重复定义 generated 中已有的 DTO interface。

## 禁止

- 添加 schema 中不存在的表单字段。
- 表格列引用响应中不存在的字段。
- 手写与 generated 冲突的 interface。
- 手改 `src/api/generated`。
- 枚举展示忽略 unknown fallback。

## 必须

- 查询表单类型来自 schema / generated。
- 校验规则与 schema 的 required、length、enum、format 一致。
- 表格列使用 schema 字段名。
- API 调用走 `src/api` 薄封装或 generated client。
- 契约变更后执行 `schema:sync`、`api:gen`、`api:check`（若项目已配置）。

## AI 固定指令

```text
Read contracts/schema.json first.
Use generated DTOs.
Do not invent fields.
Use Base components only.
```
