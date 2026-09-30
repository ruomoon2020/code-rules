# OpenAPI 契约单一事实来源

生成或修改业务页面、API 封装、表单、筛选、表格前：

1. 读取权威契约 `contracts/openapi.yaml`（或项目明确声明的等价 OpenAPI 路径）。
2. 读取由权威契约同步出的 `contracts/schema.json`（若存在）与 `src/api/generated` 对应类型；两者都是生成物，不得反向成为契约源。
3. 定位 service 与 operation，例如 `system.User.create`、`system.User.page`。
4. 仅根据契约生成字段与类型。
5. 禁止重复定义 generated 中已有的 DTO interface。

## 禁止

- 添加 `contracts/openapi.yaml` 中不存在的表单字段，或通过手改生成物补字段。
- 表格列引用响应中不存在的字段。
- 手写与 generated 冲突的 interface。
- 手改 `contracts/schema.json` 或 `src/api/generated` 等生成物。
- 枚举展示忽略 unknown fallback。

## 必须

- 查询表单字段先以 `contracts/openapi.yaml` 为准，类型使用其同步生成的 schema / API 类型；生成物不得反向成为契约源。
- 校验规则与 OpenAPI 的 required、length、enum、format 一致。
- 表格列使用 `contracts/openapi.yaml` 及其同步生成类型中的字段名。
- API 调用走 `src/api` 薄封装或 generated client。
- 契约变更后执行 `schema:sync`、`api:gen`、`api:check`（若项目已配置）。

## AI 固定指令

```text
Read contracts/openapi.yaml first; treat contracts/schema.json and src/api/generated as generated outputs.
Use generated DTOs.
Do not invent fields.
Do not edit generated schema or clients by hand.
Use Base components only.
```
