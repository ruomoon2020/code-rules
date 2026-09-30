# Web 前端研发规则包

版本见 `VERSION`，变更见 `CHANGELOG.md`。维护者发版见 `RELEASE.md`。

本目录是 Vue 3 + TypeScript 管理端项目的规则执行入口，覆盖架构边界、Base 组件、OpenAPI 生成类型、列表与表单状态、权限路由、质量门禁和高敏场景。它既服务于开发者，也为 Codex 和 Cursor 提供按任务加载的路由。

## 使用后应达到的结果

- 业务页面只负责编排，不绕过项目 Base 组件和请求边界。
- API 字段、分页、错误码和权限码来自契约或项目明确的 SSOT。
- Codex/Cursor 能按文件和任务读取必要规则，不需要在提示词中重复整套规范。
- lint、type-check、测试、构建、契约和关键 UI 行为有可追踪的验证证据。
- 规则校验与业务评审分开：工具通过不代表页面流程、权限和数据口径正确。

- **Codex**：`codex/AGENTS.md` → 复制到业务仓库根目录 `AGENTS.md`。
- **Cursor**：`cursor/*.mdc` → 复制到业务仓库 `.cursor/rules/`。
- **共用**：`shared/` 为 Codex 与 Cursor 的 SSOT；Cursor 的 `.mdc` 多为触发摘要，正文以 `shared/` 为准。
- **历史来源**：旧母文档仅作迁移期来源记录，AI 日常不直接当执行规则读取；规则包应可独立使用。
- **测试治理**：`shared/15-testing.md` 覆盖确定性、失败证据、竞态恢复与 N/N-1；具体阈值和条件工具由项目覆盖层声明。

## 首次接入

1. 优先选择“整包同步”，将本目录作为业务仓 `rules/`。
2. 将 `codex/AGENTS.md` 复制到业务仓根 `AGENTS.md`，将 `cursor/*.mdc` 复制到 `.cursor/rules/`。
3. 从 `examples/99-project-local.mdc.sample` 创建本地覆盖层，填写真实目录、Base 组件、OpenAPI、脚本和采纳 Level。
4. 接入规则包校验、views Element Plus 扫描、lint、type-check、测试、构建和 API 检查。
5. 用一个真实页面 PR 验证路由和门禁，而不是只检查文件是否存在。

完整的新项目步骤见 `docs/onboarding-new-project.md`；存量项目接入见仓库根的 [项目接入指南](../../docs/project-adoption-guide.md)。

## 使用原则

1. 必须先遵守 `shared/00-must-follow.md`。
2. 按任务追加阅读，避免一次加载全部规则。
3. 冲突优先级：安全与合规 > `00-must-follow` > 项目本地配置（ESLint 等）> 场景规则。
4. 规则只写可执行约束；长篇说明留在设计文档或业务仓 README。
5. 语言约定见 `LANGUAGE.md`（shared/codex 中文，cursor 正文中文）。

## 规则层级（维护时遵守）

```text
L0  shared/00-must-follow.md          — 可拒 PR 的硬规则
L1  shared/01–25 等场景文件          — 细节与流程
L2  codex/*.md、cursor/*.mdc         — 任务索引 + 触发摘要（不重复 L1 全文）
```

使用原则：**不要一次加载全部规则**。Codex 先读 `AGENTS.md`，Cursor 先读 `00-project-overview.mdc`，再按任务、路径和 glob 读取少量 shared 全文。

```text
Cursor alwaysApply 概览
  → Cursor globs / Codex 任务表
  → 按需读取 shared 全文
  → pnpm lint / type-check / api:check / evals
```

## 部署方式（三选一，团队需固定一种）

### 方式 A — 整包同步（推荐）

将整个 `rules/` 目录放入业务仓库（submodule、子目录或内部 npm 包）。保证：

- 根目录或约定路径存在 `rules/shared/`、`rules/codex/`。
- `AGENTS.md` 内容来自 `rules/codex/AGENTS.md`，其中路径 `rules/shared/...` 可解析。
- `.cursor/rules/*.mdc` 来自 `rules/cursor/`，且 `.mdc` 内 `Read rules/shared/...` 可解析。

业务仓目录示例：

```text
your-front/
├─ AGENTS.md                    # 复制自 rules/codex/AGENTS.md
├─ rules/                       # 整包
├─ .cursor/rules/*.mdc          # 复制自 rules/cursor/
├─ contracts/openapi.yaml       # 权威契约 SSOT
├─ contracts/schema.json        # 可选生成物，禁止手改
├─ src/
│  ├─ views/
│  ├─ components/
│  ├─ api/generated/
│  └─ router/
└─ package.json
```

### 方式 B — 仅复制 Cursor + 根 AGENTS

复制 `cursor/*.mdc` 与 `AGENTS.md` 时，**必须**同步 `shared/`（或把 shared 要点内联进 `.mdc`），否则 `Read rules/shared/...` 会断链。

### 方式 C — Cursor `@` 引用

保留 `rules/` 在固定路径，在对话中用 `@rules/shared/00-must-follow.md` 等显式拉取；仍建议方式 A。

## Codex 读取顺序

1. `codex/01-before-editing.md`
2. `shared/00-must-follow.md`
3. 按 `AGENTS.md` 任务表追加 `shared/`、`codex/`
4. 收尾：`shared/10-verification-checklist.md`、`codex/05-verification.md`

推荐问法：

```text
新增 CRM 客户列表页，成熟后台二开，按 shared/22 + frontend playbook。
只改 schema generated 后的页面，按 12 + 11 + 19。
做导入导出，按 14 + 18 logging。
改路由菜单权限，按 06 + 17。
```

不要要求 Codex “通读全部 shared”。如果任务复杂，先让它说明命中的任务和准备读取的规则。

## Cursor 说明

- 复制 `cursor/*.mdc` 到 `.cursor/rules/`。
- 除 `00-project-overview.mdc` 外，其余规则用 `globs` 触发，避免 `alwaysApply: true`。
- 编辑 `src/views/**/*.vue` 时可能同时命中多条规则，属正常；以 `shared/` 为准，`.mdc` 保持简短。

关键路由：

| 场景 | Cursor 规则 |
|---|---|
| 业务页面 / 列表 / 表单 | `10-base-components.mdc`、`11-schema-ssot.mdc`、列表 / 页面相关规则 |
| 成熟后台新增业务页 | `cursor/18-business-module-extension.mdc` + `shared/22-business-module-extension.md` |
| API / generated / schema | `11-schema-ssot.mdc`、API 相关规则 |
| 路由 / 菜单 / 权限 | 路由权限相关 `.mdc` |
| 设计 Token / 样式 | design token 相关 `.mdc` |

完整的 25 个 Cursor 文件名、场景主题与 shared 正文映射见 `docs/cursor-shared-map.md`，不要按编号猜映射。

不要把所有 `.mdc` 设成 `alwaysApply: true`。项目特有路径用业务仓本地 `99-project-local.mdc` 描述。

## 业务仓本地覆盖层

规则包是通用规则。真实前端项目建议加一层很薄的本地约定。

根 `AGENTS.md` 可追加：

```md
## 本项目约定

- 业务页面路径：`src/views/{module}/`
- Base 组件路径：`src/components/Base*/` 或项目实际目录
- API 生成目录：`src/api/generated/`
- 契约来源：`contracts/openapi.yaml`；`contracts/schema.json` 与 generated types 是生成物
- 成熟后台栈：RuoYi-Vue-Plus / 自研管理端
- 新增业务页默认对齐后端 `web-backend/rules/docs/fullstack-contract.md`
```

`.cursor/rules/99-project-local.mdc`：复制 `examples/99-project-local.mdc.sample` 并按项目修改（views 路径、Base 组件、契约路径、测试治理参数）。

本地覆盖层只写项目路径、脚本和业务栈，不要复制 `00`、`11`、`12` 或 `22` 全文。

## 业务研发流程

无论是新页面还是成熟后台二开，都按以下顺序推进：

```text
需求与验收条件
  → 核对 OpenAPI / 权限 / Base 组件
  → 设计页面状态与失败恢复
  → 实现 API、状态和页面编排
  → lint / type-check / test / build / api:check
  → 浏览器验证与业务 Review
```

业务 Review 重点检查：字段与后端是否一致，角色和按钮权限是否闭环，加载/空/错误/无权限/成功状态是否完整，重复提交和竞态是否可恢复，删除末条、分页、导入导出等边界是否正确。

### 成熟后台新增业务页面

适用于 RuoYi / Jeecg / 自研后台的 CRUD、列表、详情、导入导出页面。

1. 先确认后端权威契约 `contracts/openapi.yaml` 已更新，并已同步生成 schema / API 类型。
2. 页面只使用项目 Base 组件；`src/views/**` 禁止直接写 `el-*` 或导入 `element-plus`。
3. 列表页按 Header / Filter / Toolbar / Table / Pagination 骨架组织。
4. 表格列、表单字段、详情字段必须来自 `contracts/openapi.yaml` 及其同步生成的类型，禁止手改生成物。
5. 菜单、路由 `name`、按钮权限码与后端一致；禁止只隐藏 UI。
6. 导入导出要有模板下载、任务状态、错误明细和下载鉴权，做完后刷新操作记录。
7. 树表 / 主子表页面要处理非法父节点禁选、子表错误明细、失败态回滚提示。

必读：

- `shared/22-business-module-extension.md`
- `docs/business-feature-playbook-frontend.md`
- `shared/11-base-components-context.md`
- `shared/12-schema-ssot.md`
- `shared/19-list-pagination.md`
- `shared/14-upload-import-export.md`（若涉及文件）

### 普通页面 / 组件

1. 写 `views` 前先读真实 Base 组件源码或 `11-base-components-context.md`。
2. 写字段前先读 `contracts/openapi.yaml`，再核对同步生成的 schema / API 类型。
3. 列表页必须有加载、空、错误、正常四态。
4. 组件 props / emits / slots 以源码为准，禁止猜。
5. 单文件超过 400 行时拆组合函数、子组件或配置。

### OpenAPI 契约变更

1. 后端先更新权威契约 `contracts/openapi.yaml`；不得直接修改生成的 `schema.json`。
2. 前端运行 `schema:sync` / `api:gen` / `api:check`（按项目脚本）。
3. 禁止手改 `src/api/generated`。
4. 删除或改名字段要同步页面、表单、导入导出、权限与测试。

## 验证与回归

日常改动按项目实际脚本运行：

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build
```

API 或 schema 变更后，若项目有以下脚本，必须运行：

```bash
pnpm schema:sync
pnpm api:gen
pnpm api:check
```

规则包一致性：

```bash
python rules/scripts/validate-rules-package.py
```

AI 行为回归：

| 场景 | 套件 |
|---|---|
| 日常 PR | Smoke |
| 发版 / 规则包升级 | Full |
| 成熟后台业务页 | 业务扩展相关 evals / playbook checklist |

CI 硬门禁建议至少包含：`lint`、`type-check`、`build`、schema check、views 禁 Element Plus 扫描。

## 完整文件清单

| 文件 | 职责 | 何时读 |
|---|---|---|
| `shared/00-must-follow.md` | 硬规则 | 始终 |
| `shared/01-project-structure.md` | 目录与依赖 | 新模块、架构调整 |
| `shared/02-naming.md` | 命名、路径、变量、样式、环境变量 | 新文件、重命名 |
| `shared/03-code-style.md` | TS / Vue / import | 写代码 |
| `shared/04-ui-patterns.md` | 页面骨架与 UI | 做页面 |
| `shared/05-api-contract.md` | API 与契约 | 接口、表单、表格字段 |
| `shared/06-state-route-permission.md` | 路由 / Store / 权限 | 路由、登录、权限 |
| `shared/07-security-performance.md` | 安全 / a11y / 性能 | 安全、体验、性能相关 |
| `shared/08-quality-gates.md` | 测试 / CI / 发布 | 提测、发布 |
| `shared/09-ai-generation.md` | AI 生成、不可信内容与工具安全约束 | AI 生成代码、读取外部内容或调用工具 |
| `shared/10-verification-checklist.md` | 完成前检查 | 收尾 |
| `shared/11-base-components-context.md` | Base 组件锚定 | 写 `views` 前 |
| `shared/12-schema-ssot.md` | Schema 锚定 | 写字段 / API 前 |
| `shared/13-form-and-detail.md` | 表单 / 详情页 | 表单、详情场景 |
| `shared/14-upload-import-export.md` | 上传 / Excel / CSV / JSON / Word 导入导出 | 文件、模板与批量数据 |
| `shared/15-testing.md` | 测试约定 | 写测、改契约后 |
| `shared/16-design-tokens.md` | 设计 Token | 样式、主题 |
| `shared/17-shell-navigation.md` | 壳层 / 菜单 / 特殊页型 | layout、router |
| `shared/18-logging-observability.md` | 结构化日志 / 监控 | 错误处理、埋点 |
| `shared/19-list-pagination.md` | 列表分页与竞态 | 列表页、useTable |
| `shared/20-dependency-governance.md` | 依赖治理 | 新增 / 升级依赖 |
| `shared/21-error-recovery.md` | 错误恢复 / 白屏治理 | 全局异常、路由失败 |
| `shared/22-business-module-extension.md` | 成熟后台业务页扩展 | 新 CRUD / 菜单 / 权限 |
| `shared/23-i18n-locale.md` | 国际化、金额、日期与时区 | locale / formatter / 错误码文案 |
| `shared/24-realtime-rich-content.md` | WebSocket、SSE 与富文本 | 实时消息、编辑器、预览 |
| `shared/25-regulated-web-hardening.md` | 受监管 Web 条件加固 | 金融、政务、高敏数据、第三方脚本、嵌入页面 |
| `LANGUAGE.md` | 中英维护约定 | 维护规则时 |
| `codex/AGENTS.md` | Codex 入口与路由 | Codex 会话开始 |
| `codex/01-before-editing.md` | 改前上下文 | 任意改动 |
| `codex/02-page-generation.md` | 页面生成 | `views` |
| `codex/03-component-generation.md` | 组件生成 | `components` |
| `codex/04-api-and-schema.md` | API / schema | `api`、契约 |
| `codex/05-verification.md` | Codex 验证说明 | 收尾 |
| `cursor/*.mdc` | Cursor 触发摘要 | 按 glob 自动 |
| `evals/prompts.md` | AI 规则回归提示词 | 发版前 / 季度 |
| `evals/ai-tool-safety.md` | AI 工具安全独立门禁 EAT01–EAT05（5/5） | AI 读取外部内容或调用工具 |
| `evals/smoke-prompts.md` | 回归套件索引（不计提示词正文） | 日常 Smoke |
| `evals/adoption-checklist.md` | 业务仓落地勾选 | 新项目 onboarding |
| `scripts/validate-rules-package.py` | 规则包一致性校验 | 发版前 |
| `scripts/README.md` | 校验脚本说明 | 维护者 |
| `docs/contributing-rules-package.md` | 维护者变更治理 | 改 rules |
| `docs/enterprise-governance.md` | 独立规则包的治理入口 | 治理接入 |
| `docs/fullstack-contract.md` | 管理端本地全栈契约摘要 | 独立复制 rules/、联调 |
| `docs/onboarding-new-project.md` | 新项目接入步骤 | 首次接入 rules/ |
| `docs/rules-package-index.md` | 规则主题索引 | 不确定读哪个规则 |
| `docs/rule-maturity-model.md` | 成熟度与证据要求 | 规划治理提升 |
| `docs/cursor-shared-map.md` | Cursor ↔ shared 编号对照 | 部署 / 排障 |
| `docs/release-checklist.md` | 业务发布、灰度与回滚证据 | 提测 / 发布 |
| `docs/pull-request-template.md` | 前端 PR 模板 | 接入 CI / review |
| `docs/PERFORMANCE_BUDGET.template.md` | 性能预算样板 | 重依赖、大列表、性能治理 |
| `docs/owasp-web-mapping.md` | OWASP Web 映射 | 安全评审 |
| `examples/99-project-local.mdc.sample` | 业务仓 Cursor 本地覆盖样板 | 复制到 `.cursor/rules/` |
| `examples/ci/rules-package-validate.yml` | 业务仓 CI 校验样板 | 嵌入 rules/ |
| `RELEASE.md` | 维护者发版 checklist | 发版前 |
| `docs/business-feature-playbook-frontend.md` | 成熟后台新增业务页面落地 | 新 CRUD / 菜单 / 权限 |
| `examples/ci-scan-views-el-tags.mjs` 等 | CI 检查样板 | 业务仓 CI 接入 |
| `examples/run-ci-scan-fixtures.mjs` | ci-scan 回归 | 规则包发版前 |
| `examples/scaffold/` | 工具链、request、store、列表状态、bundle budget 样板 | 新项目接入 |

## 规则评测（evals）

发版或大改 `shared/` 后，在测试仓库执行 `evals/prompts.md` 中 **E01–E50**，按 `evals/rubric.md` 记分，结果记入 `evals/results-YYYY-MM-DD.md`（由 `results-template.md` 复制）。

通过门槛：**P0 8/8 Pass**，**P1 至少 39/42 Pass**，AI Tool Safety **EAT01–EAT05 5/5**。日常 Smoke、成熟后台 Business E32–E40、i18n/实时/富文本 Platform E41–E43、受监管 Web Enterprise Hardening E44–E49、测试治理 E31/E50、发版 Full（见 `evals/README.md`、`evals/smoke-prompts.md`）。

维护者发版前运行 `python scripts/validate-rules-package.py`；本 monorepo 见 `.github/workflows/validate-rules-packages.yml`。


全栈 monorepo 与后端规则见仓库根 [docs/monorepo-layout.md](../../docs/monorepo-layout.md)、[web-backend/rules/README.md](../../web-backend/rules/README.md)。

## 软约束与硬门禁

- **软约束**：写 `views` 前读 `11-base-components-context`、`12-schema-ssot`。
- **硬门禁**：业务项目用 ESLint、type-check、schema check、CI 保证违规即失败；样板见 `examples/`。

## CI 检查样板

见 `examples/README.md`，须**组合**使用：

| 能力 | 文件 |
|---|---|
| 禁 `import 'element-plus'` 及 `element-plus/*` | `eslint-views-ban-el.mjs` |
| 禁模板 `<el-*>`、动态 `is`、denylist 内 `<ElButton>` 等 | `ci-scan-views-el-tags.mjs` + `element-plus-pascal-denylist.mjs`（CI **勿**加 `--allow-empty`） |
| scripts 示例 | `package-scripts.sample.json` |

### CI 推荐接入顺序（业务仓）

1. 将 `rules/examples/eslint-views-ban-el.mjs` 并入 ESLint flat config（覆盖 `src/views` 与 `packages/**/src/views`）。
2. 在 `package.json` 增加并接入 **PR 必跑** 链路（不要只放 nightly / 可选 job）：

```json
{
  "scripts": {
    "lint": "eslint . && pnpm lint:views-el",
    "lint:views-el": "node ./rules/examples/ci-scan-views-el-tags.mjs"
  }
}
```

3. 发版前在规则包目录执行：`node rules/examples/run-ci-scan-fixtures.mjs`。

仅接 ESLint 而不跑 `ci-scan`，无法覆盖模板标签；`lint:views-el` 应与 `lint` 同级进入 PR 检查。
