# 全栈契约（前后端对齐）

> 维护者 / 架构文档；Codex 日常以各自 `rules/shared/05`（后端 OpenAPI）与前端 `12-schema-ssot` 为准。

## 单一来源

```text
contracts/openapi.yaml
  → 后端：实现 Controller/DTO、校验、MockMvc
  → 管理端：生成 schema / src/api/generated（按 web-front 项目脚本）
  → 小程序：src/api/generated（api:gen + api:check，见 miniapp/rules/docs/fullstack-contract.md）
```

## 统一字段

| 字段 | 后端 | 管理端 | 小程序 |
|---|---|---|---|
| `traceId` | MDC + 响应头 `X-Trace-Id`（名以项目为准） | request wrapper、logger | request header + 日志（`miniapp/rules/shared/15`） |
| `errorCode` | `BusinessException` / `ErrorCodes`；稳定业务契约 | `normalizeError` 后映射 i18n / 字典 | 统一错误处理后映射端侧文案；枚举见 OpenAPI |
| `message` | fallback / 诊断文案，不保证语言和长期稳定性 | 仅作项目允许的 fallback，禁止据此分支 | 仅作项目允许的 fallback，禁止据此分支 |
| 排序 `sortField` / `sortOrder` | 白名单列；`sortOrder` 仅 `asc` / `desc` | 组件的 `ascending` / `descending` 映射后再请求 | 同管理端 |
| 分页 `total` / `records` | `IPage` 转换 | `useTable` | 列表 composable |
| 权限码 | `@PreAuthorize` | 按钮权限指令 | 后端鉴权为主；不单靠 UI 隐藏 |
| `Idempotency-Key` | 可重试写操作 Header | 支付/下单/创建类请求 | 同上；重试复用同一键 |

## HTTP 语义与安全契约

接口风格未声明时默认使用 `GET_POST_COMPAT`；公网开放接口、标准 REST 网关或跨组织集成显式使用 `RESOURCE_REST`，并写入 OpenAPI 顶层 `x-api-style`。兼容风格是 HTTP 命令接口，不宣称为纯 REST，但仍保留资源路径、HTTP 状态、认证授权和错误契约。

| 场景 | 契约要求 |
|---|---|
| 创建资源 | `201 Created` + `Location`；若不支持安全重试，OpenAPI 显式说明 |
| 部分更新 | `RESOURCE_REST` 使用 `PATCH /resources/{id}`；`GET_POST_COMPAT` 使用 `POST /resources/{id}/update` |
| 删除资源 | `RESOURCE_REST` 使用 `DELETE /resources/{id}`；`GET_POST_COMPAT` 使用 `POST /resources/{id}/delete`；成功可返回 `204 No Content` |
| 错误 | operation 显式列出主要 `4xx` / `5xx`，复用 `ApiError` / `components.responses` |
| 认证 | `securitySchemes` + 顶层或 operation `security`；公开接口显式 `security: []` |
| 授权 | OpenAPI 表达认证方式，Controller 仍须用 `@PreAuthorize` 或等价机制校验权限码 |
| 资源主键 | 路径、查询和响应使用 `string`。雪花 ID 不用 `integer` / `int64`，避免生成客户端按数字截断 |

## 错误响应示例

```json
{
  "code": 40001,
  "message": "用户不存在",
  "errorCode": "USER_NOT_FOUND",
  "traceId": "abc123",
  "data": null
}
```

## 既有响应壳适配

若业务仓已有统一响应包装（数字码 + 文案 + data），**不要平行维护第二套外壳**。在公共层映射到本契约字段：

| 目标字段 | 要求 |
|---|---|
| `code` | 保留稳定数字码 |
| `message` | fallback / 诊断文案（由现有文案字段映射）；不是稳定业务契约 |
| `errorCode` | 稳定业务语义码 `DOMAIN_REASON`；禁止只靠文案做分支 |
| `traceId` | 响应体或约定响应头（名写入项目本地覆盖） |

客户端经 `normalizeError`（或等价）归一化后，必须按 `errorCode` 决定 i18n 文案和恢复行为；禁止按 `message` 分支或自行拼接业务句。未知码展示通用文案与 `traceId`。平台特有字段名、成功码取值写在 `99-project-local`，不进各端通用 `shared/`。

## 发布顺序

1. OpenAPI PR + lint + openapi-diff + 契约/脚手架对齐检查
2. 后端发布（兼容旧前端）
3. 前端 `api:gen` + 联调

## 参考实现

- 后端样板：`examples/scaffold/`（`ApiResult`、`PageResponse`、`UserController` 与 OpenAPI 对齐）
- 契约占位：`contracts/openapi.yaml`（仓库根）

## 导入导出

后端 `14-file-import-export` 与前端 `14-upload-import-export` 对齐：幂等、错误明细、下载鉴权。

| 能力 | 后端 | 前端 |
|---|---|---|
| 幂等键 | `18-idempotency-concurrency` | 导入任务 `taskId` / 文件 hash |
| 错误明细 | 行列级错误码 + `errorCode` | 表格展示 + 错误报告下载 |
| 下载鉴权 | 短期 token / 鉴权 URL | 禁止缓存永久公开 URL |
| 审计（见下节） | 服务端写入 | 操作完成后刷新记录 / 管理端列表 |

---

## 审计日志（前后端对齐）

> 细则：后端 `shared/27-audit-log.md`；前端导入导出审计 `web-front/rules/shared/14-upload-import-export.md`（权限、审计与日志）；详情页操作记录 `13-form-and-detail.md`。

### 职责划分

| 侧 | 职责 |
|---|---|
| **后端** | 敏感操作**必须**落库（或审计服务）；字段完整；禁止仅用 `log.info` |
| **前端** | 不伪造审计；展示操作记录列表/详情；导入导出后提示成功并引导查看记录；敏感字段脱敏展示 |
| **契约** | 查询类接口在 OpenAPI 定义 `AuditLog`（或等价）DTO，与下表一致 |

### 统一字段映射

后端持久化与 API 响应使用**同一套 camelCase**（与 OpenAPI / 前端 generated 一致）：

| 字段 | 类型（建议） | 后端含义 | 前端展示 |
|---|---|---|---|
| `operatorId` | string | 操作人 ID | 操作人（可联表 `operatorName` 仅展示，不入库审计主字段） |
| `tenantId` | string | 租户 ID（租户模型不是 `NONE` 时必填） | 租户列（非 `NONE` 项目） |
| `action` | string | 稳定动作码，如 `USER_DELETE`、`IMPORT_USERS` | 操作类型（走字典 / i18n，**禁止**前端硬编码文案与后端码不一致） |
| `resourceType` | string | 资源类型，如 `User`、`ImportTask` | 模块 / 资源类型 |
| `resourceId` | string | 资源主键 | 资源 ID（列表可省略或折叠） |
| `requestSummary` | string | 条件摘要（筛选、批量数量、文件名等） | 条件摘要 |
| `beforeSummary` | string | 变更前摘要（非敏感明文） | 变更前（详情抽屉） |
| `afterSummary` | string | 变更后摘要 | 变更后 |
| `occurredAt` | string (date-time) | 服务端操作时间 | 操作时间（统一 `utils/format`） |
| `result` | string | `SUCCESS` / `FAIL` | 结果标签 |
| `errorCode` | string | 失败时业务码（可选） | 与全局 `errorCode` 一致，便于对照 |
| `traceId` | string | 与当次 HTTP 请求一致 | 运维排障可跳转日志（不对普通用户强展示） |
| `ip` | string | 客户端 IP | 可选列 |
| `userAgent` | string | 客户端 UA | 一般仅详情展示 |

### 导入 / 导出专项（与前端 `14` 对齐）

前端要求：操作人、时间、模块、条件摘要、文件名、任务 ID、结果。映射如下：

| 前端 `14` 描述 | 后端审计字段 |
|---|---|
| 操作人 | `operatorId`（+ 展示名由用户服务解析，不写审计明文 PII） |
| 时间 | `occurredAt` |
| 模块 | `resourceType` + `action`（如 `IMPORT` / `EXPORT`） |
| 条件摘要 | `requestSummary` |
| 文件名 | 写入 `requestSummary` 或扩展字段 `fileName`（须在 OpenAPI 与 DB 同时约定） |
| 任务 ID | 异步任务：`resourceId` = `taskId`，或 `resourceType` = `ImportTask` |
| 结果 | `result` + 失败时 `errorCode` |

`action` 建议枚举在 OpenAPI `components/schemas` 或团队字典文档维护，前后端共用（与 API 枚举扩展策略见 `05-openapi-contract.md`）。

### 与 `traceId` / 错误体关系

1. 业务 API 响应中的 `traceId`（见上节）与审计记录中的 `traceId` **同名同值**，便于从 UI 操作记录关联到网关 / 应用日志。
2. 审计**禁止**记录：密码、Token、完整证件号、完整银行卡号、密钥明文（后端 `27`、前端 `14` 日志节一致）。
3. 审计查询接口的成功响应仍使用统一 `ApiResult` 包装；单条审计 DTO **不要**套用业务 Entity。

### OpenAPI（已落地）

仓库根 `contracts/openapi.yaml` 已包含：

| 路径 | operationId | 说明 |
|---|---|---|
| `GET /api/v1/system/audit-logs` | `systemAuditLogPage` | 分页；筛选 `action`、`resourceType`、`operatorId`、`result`、时间范围 |
| `GET /api/v1/system/audit-logs/{id}` | `systemAuditLogDetail` | 详情（含 `beforeSummary`、`afterSummary`、`ip`、`userAgent`） |

Schema：`AuditLogSummaryResponse`（列表）、`AuditLogResponse`（详情）、`AuditResult`（`SUCCESS` / `FAIL`）。
可选展示字段 `operatorName`、`fileName` 已标为 optional，新增字段须向后兼容。
Java 样板 DTO / Controller 见 `examples/scaffold/java/modules/system/api/` 下 `AuditLog*`。

### 必审操作（全栈一致）

以下操作后端**必须**写审计；前端若有对应按钮，须在 PR 中确认不会跳过二次确认 / 权限校验：

- 登录成功/失败、权限与角色变更、用户启停
- 单条/批量删除、批量更新、强制状态变更
- 导入、导出、敏感报表下载
- 系统配置、Feature Flag（不记密钥明文）
- 跨租户操作（另见 `24-data-access-cache`）

### 审计失败策略（联调须知）

| 场景 | 后端 | 前端 |
|---|---|---|
| 阻断型（删数据、改权限、导出敏感） | 审计写入失败 → API 失败 | 展示错误，**不得**提示成功 |
| 记录型（可选查询审计） | 可异步补写 + 告警（项目文档声明） | 列表可延迟刷新 |

---

## 新增业务功能（成熟后台全栈对齐）

> 后端细则：`shared/43-business-module-extension.md`、`docs/business-feature-playbook.md`。
> 前端细则：`web-front/rules/shared/22-business-module-extension.md`、`web-front/rules/docs/business-feature-playbook-frontend.md`（菜单、权限、页面、契约）。

| 步骤 | 后端 | 前端 |
|---|---|---|
| 契约 | 先改 `contracts/openapi.yaml`：路径、DTO、枚举、`errorCode`、权限相关字段 | `schema:sync` + `api:gen` + `api:check`；禁止手改 `generated` |
| 权限码 | OpenAPI / 常量 / `@PreAuthorize` 与菜单按钮码一致（如 `system:xxx:create`） | 按钮权限指令 / helper；路由守卫；**禁止**仅隐藏 UI |
| 菜单 / 路由 | 平台菜单注册（SQL 或管理端配置）；API 路径稳定 | 路由 `name` PascalCase = keep-alive；菜单与权限码对齐（`06-state-route-permission`） |
| 字典 / 枚举 | OpenAPI 枚举 + 平台字典；禁止静默改语义（`41`） | 字典组件 + unknown fallback；禁止硬编码与后端 action 文案不一致 |
| 列表 / 详情 | 分页、排序白名单、数据权限 + BOLA（`24`、`06`）。租户模型不是 `NONE` 时同时校验租户 | `useTable` 四态；删除末条回退页码；与后端分页字段一致 |
| 树表 / 主子表 | 父子归属、同事务与循环关系校验；非 `NONE` 时禁止跨租户挂父节点（`43`） | 树选择禁选非法父节点；主子表错误明细；失败态与后端回滚一致（`22` §树表/主子表） |
| 导入 / 导出 | 平台文件/OSS、幂等、审计、下载鉴权（`14`、`27`） | 模板下载、错误明细、操作记录刷新（`14-upload-import-export`） |
| 任务 / 批处理 | 平台调度、防重、幂等、任务日志（`25`、`43`） | 任务状态页、轮询/通知；禁止前端伪造成功 |
| 审计 | 写库 `action` / `resourceType` 稳定码 | 操作记录列表/详情；`action` 走字典/i18n，与后端码一致 |
| 测试 | 越权、导出、Job、树表/主子表；非 `NONE` 时另覆盖跨租户。evals **Business Extension** B55–B63 | 权限、列表四态、树表/主子表；evals **Business Extension** E32–E40；i18n/实时/富文本 PR 加 **Platform Extension** E41–E43（无后端 B 对称项） |

发布顺序仍为：OpenAPI PR → 后端兼容发布 → 前端 `api:gen` + 菜单/权限配置 + 联调。

---

## 管理端 Platform Extension（i18n / 实时 / 富文本）

> 无后端 B 对称 eval；管理端专项 **E41–E43**（建议 3/3）。规则：`web-front/rules/shared/23-i18n-locale.md`、`24-realtime-rich-content.md`。

| 主题 | 后端 | 管理端 |
|---|---|---|
| i18n / 区域格式 | `errorCode`、枚举、审计 `action` 稳定码；时区与账期边界 | 文案走 i18n / 字典；金额日期用 formatter；禁止 `errorCode` 直出（`web-front/rules/shared/23-i18n-locale.md`） |
| WebSocket / SSE | 握手鉴权、会话与权限校验；消息 schema 与幂等 | 禁止长期 Token 放 URL query；卸载取消订阅；未知消息安全降级（`24`） |
| 富文本 / 编辑器 | 存储格式、消毒策略、下载鉴权 | 禁止裸 `v-html`；sanitizer；编辑器按需加载（`24`） |
| 测试 | 接口鉴权、消息越权、存储型 XSS 边界 | evals **Platform Extension** E41–E43 |

---

## 小程序（uni-app）

> 细则：`miniapp/rules/docs/fullstack-contract.md`；规则包 `miniapp/rules/`。

| 主题 | 后端 | 小程序 |
|---|---|---|
| OpenAPI SSOT | `shared/05-openapi-contract.md` | `shared/05-api-contract-request.md` |
| 登录 | session / token API | `uni.login` code 换 token；禁止前端拼密钥（`06`） |
| 支付 | 下单、订单状态、幂等 | 回调仅刷新；成功以后端订单为准（`14`） |
| 分享 / scene | 参数校验、防伪造 | 白名单；禁止 token/手机号（`14`） |
| 隐私 | 最小必要、审计 | manifest + 用途说明 + 用户触发（`09`） |
| 分包体积 | — | 主包预算、`size:check`（`10`） |
| 网络 / web-view | 服务端域名与鉴权 | `21`：白名单、HTTPS；禁止向 H5 透传 token |
| App 运行时 | — | `20`：全局错误、scene、非阻塞 onLaunch |
| 环境隔离 | 多环境 API/支付配置 | `19`：体验/审核版禁连生产 |
| 业务扩展 | `shared/43` + playbook | `shared/18` + `business-feature-playbook-miniapp.md` |

发布顺序：OpenAPI PR → 后端兼容发布 → 管理端 `api:gen`（若涉及）→ 小程序 `api:gen` + `build:mp-weixin` 联调。

---

## 参考规则路径

### 跨包编号说明

各端规则编号独立设计，**编号不表示跨端同一主题**；全栈任务须按文件名和下表路由，不可只报“读 08 / 09 / 22”。

| 编号 | 后端含义 | 管理端含义 | 全栈任务应读 |
|---|---|---|---|
| 08 | 异常与错误码 | 质量门禁 | `shared/08-exception-errorcodes.md` + `web-front/rules/shared/08-quality-gates.md` |
| 09 | 日志与可观测 | AI 生成 | `shared/09-logging-observability.md` + `web-front/rules/shared/09-ai-generation.md` |
| `CR-BE-018` / `CR-FE-018` | 幂等与并发 | 日志与可观测 | `shared/18-idempotency-concurrency.md` + `web-front/rules/shared/18-logging-observability.md` |
| 22 | 可运维性 | 业务模块扩展 | `shared/22-operability.md` + `web-front/rules/shared/22-business-module-extension.md` |
| `CR-FE-023` / `CR-MA-023` | — | i18n / 区域格式 | `web-front/rules/shared/23-i18n-locale.md` + `miniapp/rules/shared/23-content-safety.md`（UGC/富文本；**非同主题**） |
| `CR-FE-024` / `CR-MA-024` | — | 实时 / 富文本 | `web-front/rules/shared/24-realtime-rich-content.md` + `miniapp/rules/shared/24-design-system-mobile.md`（**非同主题**） |
| 43 / 22 | 后端业务模块扩展 | 管理端业务模块扩展 | `shared/43-business-module-extension.md` + `web-front/rules/shared/22-business-module-extension.md` |

管理端 evals **E41–E43**（Platform Extension）仅适用于 `web-front/rules`；小程序无对称 M 套件，富文本/UGC 见 **M35–M38**（Resilience Extension）。

前端本地摘要：`web-front/rules/docs/fullstack-contract.md`；小程序本地摘要：`miniapp/rules/docs/fullstack-contract.md`。

| 主题 | 后端 | 管理端 | 小程序 |
|---|---|---|---|
| OpenAPI SSOT | `shared/05-openapi-contract.md` | `shared/12-schema-ssot.md` | `miniapp/rules/shared/05-api-contract-request.md` |
| 审计写入 | `shared/27-audit-log.md` | `shared/14-upload-import-export.md` §权限、审计与日志 | 不伪造审计；脱敏展示 |
| 操作记录 UI | — | `shared/13-form-and-detail.md` | — |
| 日志 traceId | `shared/09-logging-observability.md` | `shared/18-logging-observability.md` | `miniapp/rules/shared/15-logging-observability.md` |
| 业务模块扩展 | `shared/43` + playbook | `shared/22` + playbook-frontend | `miniapp/rules/shared/18` + playbook-miniapp |
| i18n / 实时 / 富文本 | `errorCode`、枚举稳定码 | `web-front/rules/shared/23-i18n-locale.md`、`24-realtime-rich-content.md`；evals **E41–E43** | `miniapp/rules/shared/23-content-safety.md`（UGC）；**无 E41–E43** |
| 网络 / App | — | — | `miniapp/rules/shared/21-network-security.md`、`20-app-runtime.md` |
