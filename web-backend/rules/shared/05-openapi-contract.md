# OpenAPI Contract（SSOT）

## 优先级

```text
contracts/openapi.yaml（或 openapi/ 目录）
  -> 生成 / 校验 Controller DTO（若项目使用）
  -> modules.*.api（Controller + Request/Response）
  -> application / mapper
```

与前端：同一份 OpenAPI 或由其生成 `web-front/contracts/schema.json`（见 `docs/fullstack-contract.md`）。

## 规则

1. 新增/修改接口**先改 OpenAPI**，再写 Java。
2. 禁止实现契约中不存在的字段；禁止私自改响应结构。
3. `operationId` 稳定，便于生成与追踪。
4. 枚举在 OpenAPI 中声明；后端 DTO 与之一致。
5. 分页参数、错误响应模型在 OpenAPI 中复用 `#/components/schemas`。
6. 可重试写操作（支付、下单、创建资源等）在 OpenAPI 声明 **`Idempotency-Key`** Header（`#/components/parameters/IdempotencyKey`），与 `04-rest-api-design.md`、`18-idempotency-concurrency.md` 一致；未支持幂等须在描述中写明不可安全重试。

## 变更流程

1. PR 含 OpenAPI diff。
2. 运行契约校验（Spectral / openapi-diff）。Monorepo 根建议维护 `contracts/openapi.baseline.yaml` 作为对比基线；契约稳定后由 Owner 更新 baseline（见 `examples/README.md`）。
3. 通知前端执行 `api:gen` 或等价脚本。
4. 下列变更视为 **breaking**，须 Review、版本说明与迁移计划（见下方兼容策略）。

## API 兼容策略（细则）

### 非 breaking（允许）

- 新增**可选**响应字段。
- 新增可选请求字段（不改变既有字段语义）。
- 新增 API 路径或 `operationId`（不修改既有 operation 语义）。
- 枚举**仅扩展**新值（旧客户端可忽略未知值）。

### breaking（须版本 / 迁移）

| 变更 | 说明 |
|---|---|
| 删除字段 | 须 `deprecated` 至少一个版本周期后再删 |
| `required` 新增 | 旧客户端未传则失败 |
| `nullable` / 类型变化 | `string`→`int`、格式变更等 |
| 枚举值删除或**改语义** | 禁止静默改已有枚举含义 |
| 改 `operationId`、路径、HTTP 方法 | 破坏生成代码与路由 |
| 改分页 / 错误体结构 | 与 `04`、`08` 冲突 |

### 废弃字段

1. OpenAPI 使用 `deprecated: true` + 描述替代字段与下线时间。
2. 至少保留**一个发布周期**（或团队约定的 N 个 sprint）再物理删除。
3. 删除接口须在 CHANGELOG / 迁移文档写明：替代接口、下线日期、影响范围。

### 版本策略（项目三选一，文档化）

| 策略 | 示例 |
|---|---|
| URL 版本 | `/api/v1/users`、`/api/v2/users` |
| Header | `Accept-Version: 2024-01-01` 或 `X-Api-Version` |
| 兼容字段 | 同一路径，响应同时含新旧字段至迁移完成 |

**禁止**混用多种策略且无文档；新仓库默认推荐 **URL `/api/v1`**（与 `04-rest-api-design.md` 一致）。

### 删除接口

1. 先 `deprecated` 接口与文档。
2. 提供迁移说明（新接口、字段映射、截止时间）。
3. CI 的 openapi-diff 须能检出 breaking。

## 生成代码

若使用 OpenAPI Generator：

- 生成代码目录**禁止手改**；定制通过接口继承或 wrapper。
- 生成失败不得绕过契约手写 Controller 签名。
