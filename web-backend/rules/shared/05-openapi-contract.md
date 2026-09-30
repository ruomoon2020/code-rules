# OpenAPI 契约（SSOT）

## 优先级

```text
contracts/openapi.yaml（或 openapi/ 目录）
  -> 生成 / 校验 Controller DTO（若项目使用）
  -> modules.*.api（Controller + 默认 Request/Response；存量命名按项目显式约定）
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
7. 受保护接口须在 `components/securitySchemes` 与顶层 / operation `security` 中声明认证方案；公开接口使用显式 `security: []`，不得依赖口头约定。
8. 每个 operation 声明主要成功和失败响应；错误体、限流头和追踪头使用 `components/responses` / `headers` 复用。
9. 契约样例与脚手架 Controller / DTO 必须由机器比对：HTTP method、status、required、字段、枚举、默认值和安全方案任一漂移均应阻断。
10. 顶层声明 `x-api-style: RESOURCE_REST` 或 `x-api-style: GET_POST_COMPAT`；契约门禁须校验 Controller 与所选方法/路径风格一致。
11. 雪花或可能超过 JavaScript 安全整数的主键，在路径、查询和响应中使用 `string`（十进制文本）。禁止 `integer` / `int64`。服务端可以把该文本解析为 `long`。

## 变更流程

1. PR 必须包含 OpenAPI 变更及兼容性检查结果。
2. 运行契约 lint 与固定版本的 `oasdiff breaking --fail-on WARN`。Monorepo 根建议维护 `contracts/openapi.baseline.yaml` 作为对比基线；首次建立 baseline 必须使用 Owner 施加的 `openapi-baseline-bootstrap-approved` 标签，已有目标分支契约时初始 baseline 必须与它完全一致，绿地项目则必须与本次新增契约一致。契约稳定后由 Owner 在不混入新 API 变更的独立步骤更新 baseline（见 `examples/README.md`）。
3. 通知前端执行 `api:gen` 或等价脚本。
4. 下列变更视为 **breaking**，须 Review、版本说明与迁移计划（见下方兼容策略）。

主版本提升和迁移说明不自动绕过 breaking 门禁。有意接受的不兼容变更须由 Owner 逐项审查并配置精确的工具原生忽略文件（error 与 warning 分开），限定源/目标版本与到期条件。禁止通过覆盖 baseline 或关闭门禁放行。

## API 兼容策略（细则）

### 非 breaking（允许）

- 新增**可选**响应字段。
- 新增可选请求字段（不改变既有字段语义）。
- 新增 API 路径或 `operationId`（不修改既有 operation 语义）。
- 枚举**仅扩展**新值，且消费端已有未知值兜底并经过验证；否则按潜在 breaking 处理，不得只凭“新增”判断兼容。

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

### 版本策略（未声明时使用 URL 版本）

项目未显式声明时，默认使用 URL 版本 `/api/v1`。Header 版本或兼容字段策略只在项目明确选择并写入契约文档后使用。

| 策略 | 示例 |
|---|---|
| URL 版本 | `/api/v1/users`、`/api/v2/users` |
| Header | `Accept-Version: 2024-01-01` 或 `X-Api-Version` |
| 兼容字段 | 同一路径，响应同时含新旧字段至迁移完成 |

**禁止**混用多种策略且无文档；默认使用 **URL `/api/v1`**（与 `04-rest-api-design.md` 一致）。

### 删除接口

1. 先 `deprecated` 接口与文档。
2. 提供迁移说明（新接口、字段映射、截止时间）。
3. CI 的 openapi-diff 须能检出 breaking。

## 生成代码

若使用 OpenAPI Generator：

- 生成代码目录**禁止手改**；定制通过接口继承或 wrapper。
- 生成失败不得绕过契约手写 Controller 签名。
