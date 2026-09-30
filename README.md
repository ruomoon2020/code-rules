# Code Rules：全栈研发规则与治理基线

本仓库是一套可分发、可路由、可校验的研发规则源库，覆盖 Web 前端、Spring Boot 后端、uni-app 小程序和跨技术栈工程治理。它解决三个问题：让开发者知道业务应该怎样开展，让 AI 只读取当前任务需要的规则，让 CI 能验证规则是否真正落地。

当前版本为 **2.0.0.0**。仓库根 `VERSION` 与四个可分发包的 `VERSION` 保持一致。

| 目录 | 技术栈 | 说明 |
|---|---|---|
| [web-front/rules/](web-front/rules/README.md) | Vue 3 + TypeScript + Element Plus | 前端规则包 |
| [web-backend/rules/](web-backend/rules/README.md) | Spring Boot 3 + MyBatis-Plus + 多数据库 | 后端规则包 |
| [miniapp/rules/](miniapp/rules/README.md) | Vue 3 + TypeScript + uni-app + Vite | 小程序规则包 |
| [common-governance/](common-governance/README.md) | 技术栈无关 | DoD、需求追踪、业务评审、AI 工具安全、环境晋级、事故响应、发布证据与组织治理 |

## 适用对象与使用结果

| 角色 | 从这里获得什么 |
|---|---|
| 项目负责人 / 架构师 | 选择规则包和采纳 Level，明确契约、Owner、门禁与例外机制 |
| 业务开发者 | 按需求、契约、实现、验证和发布的顺序开展业务，不靠记忆拼规则 |
| Codex / Cursor 使用者 | 用根 `AGENTS.md` 和 `.cursor/rules/` 自动路由到必要规则，减少长提示词 |
| 规则维护者 | 维护 SSOT、路由、评测、版本和发布包，并用脚本阻止漂移 |

本仓库不提供具体业务系统，也不能仅靠校验器证明业务正确。真实项目仍需结合需求、领域规则、权限模型、数据口径和测试证据完成验收。

## 先从哪个入口开始

| README | 作用 | 读者 |
|---|---|---|
| 本文件 | 规则包总览、组合部署、业务研发主流程 | 架构 / 项目负责人 / 规则维护者 |
| `web-front/rules/README.md` | 前端规则怎么部署、Codex/Cursor 怎么用、怎么写页面 | 前端团队 / AI |
| `web-backend/rules/README.md` | 后端规则怎么部署、Codex/Cursor 怎么用、怎么写业务接口 | 后端团队 / AI |
| `miniapp/rules/README.md` | 小程序规则怎么部署、登录授权/分包/支付分享怎么约束 | 小程序团队 / AI |

外层 README 负责导航，不替代各规则包 README。真正写代码时，开发者先确认业务要求和契约，AI 从业务仓最近的 `AGENTS.md` 进入，再按任务读取少量规则。

**新业务接入**：全栈 monorepo / 前后端分仓 / 单端三种形态的完整步骤见 **[`docs/project-adoption-guide.md`](docs/project-adoption-guide.md)**。

已有项目采用更高目标规则时，按 [`docs/migration-baseline.md`](docs/migration-baseline.md) 分离目标规范与当前基线；不得因为存量不合规而降低共享规则。

## 五分钟接入路径

1. 判断项目形态：全栈 monorepo、前后端分仓、单端项目或小程序。
2. 整包引入对应技术栈的 `rules/`；企业项目同时引入 `common-governance/`。
3. 将包内 `codex/AGENTS.md` 作为业务仓根入口，将 `cursor/*.mdc` 放入 `.cursor/rules/`。
4. 用 `99-project-local.mdc` 和根 `AGENTS.md` 记录真实目录、技术选择、命令、契约路径和采纳 Level。
5. 接入最近的规则包校验、项目编译测试和 `check-project-adoption.py`。
6. 故意制造一次违规，确认 PR 门禁能够失败；恢复后再把检查设为 Required。

完整命令、目录布局和存量迁移方式见 [`docs/project-adoption-guide.md`](docs/project-adoption-guide.md)。

## 业务研发主流程

```text
需求与验收条件
  → 影响分析（流程 / 数据 / 权限 / 契约 / 兼容）
  → 契约和设计先行
  → 各端实现
  → 确定性检查与场景测试
  → 人工业务正确性评审
  → 发布证据、灰度与回滚
```

每个业务需求至少回答以下问题：

- 业务状态如何变化，取消、重试、重复提交和回滚如何处理？
- 哪些角色、租户或数据 Owner 可以查看和操作？
- API、字段、分页、错误码、时间和金额口径由谁定义？
- 前端、后端和小程序如何对齐同一契约？
- 正常、失败、边界和兼容路径分别由什么证据证明？
- 上线后如何观测，出现问题如何回滚？

立项和方案阶段使用 [`docs/architect-engineering-checklist.md`](docs/architect-engineering-checklist.md)；开发与合并阶段以 [`docs/definition-of-done.md`](docs/definition-of-done.md) 为准。

## 推荐目录结构

### 全栈 monorepo

适合一个仓库同时放前端、后端、契约和规则。

```text
your-monorepo/
├─ common-governance/          # 业务仓使用的可分发治理包
├─ contracts/
│  ├─ openapi.yaml
│  └─ openapi.baseline.yaml
├─ web-front/
│  ├─ AGENTS.md
│  ├─ rules/
│  ├─ .cursor/rules/
│  └─ src/
├─ web-backend/
│  ├─ AGENTS.md
│  ├─ rules/
│  ├─ .cursor/rules/
│  └─ src/main/java/
├─ miniapp/
│  ├─ AGENTS.md
│  ├─ rules/
│  ├─ .cursor/rules/
│  └─ src/
└─ docs/                       # 维护 SSOT，生成 common-governance
```

前后端字段、权限码、分页、审计、导入导出、业务模块扩展对齐见：

- `web-backend/rules/docs/fullstack-contract.md`
- `web-front/rules/docs/business-feature-playbook-frontend.md`
- `web-backend/rules/docs/business-feature-playbook.md`

### 前后端分仓

适合前端仓、后端仓独立发布。

```text
frontend-repo/
├─ AGENTS.md
├─ rules/
├─ .cursor/rules/
└─ contracts/ 或 generated API

backend-repo/
├─ AGENTS.md
├─ rules/
├─ .cursor/rules/
└─ contracts/openapi.yaml
```

要求：

1. 权威契约是 `contracts/openapi.yaml`（或项目明确声明的等价 OpenAPI 路径）；schema / client 仅为生成结果。
2. 前端 `api:gen` 来源与后端契约一致。
3. 本源仓发布时各规则包版本保持一致；业务仓可按需采用单个包，但须记录实际采用版本，并由同一 Owner 维护 fullstack contract。
4. 发版前至少跑后端 Contract / Business Extension 与前端 schema / build 检查。OpenAPI 必须声明 `x-api-style`（`RESOURCE_REST` 或 `GET_POST_COMPAT`），覆盖 HTTP method/status、security、主要错误响应，并与 Controller / DTO 机器对齐。

## 部署步骤

### 通用治理包

1. 企业项目将 `common-governance/` 整包复制、发布或作为独立 submodule 放到业务仓根。
2. 各端最小安全硬规则仍保留在对应 `rules/shared/00-must-follow.md`，不依赖通用包加载。
3. 业务仓 CI 运行 `python common-governance/scripts/validate-package.py`。
4. 企业项目推荐 `check-project-adoption.py --level 2`（自动要求完整治理包）；Level < 2 若仍要强制校验治理包，再显式加 `--require-governance`。需要 CODEOWNERS / PR 模板时叠加 `--strict`。
5. 按成熟度使用 `--level 0..3`：Level 2 检查完整治理包、严格 Review 资产与控制声明的静态结构；Level 3 再检查平台治理 Scorecard 与证据项。平台当前配置、Required check 状态和实际执行须另行核对。
6. 从包内 `examples/ci/` 复制凭据扫描、供应链和产物信任 Required workflows；Node 供应链样板要求恰好一个 pnpm/npm 锁文件。

根 `docs/` 是维护 SSOT；`common-governance/docs/` 由同步脚本生成，禁止手工双写。

### 后端规则包

1. 将 `web-backend/rules/` 整包复制或作为 submodule 放入后端仓 `rules/`。
2. 复制 `web-backend/rules/codex/AGENTS.md` 到后端仓根 `AGENTS.md`。
3. 复制 `web-backend/rules/cursor/*.mdc` 到后端仓 `.cursor/rules/`。
4. 按需接入 `examples/` 中的 ArchUnit、Checkstyle、固定版本 `oasdiff breaking --fail-on WARN`、CI 样板。
5. 运行 `python rules/scripts/validate-rules-package.py`。

详细说明见 `web-backend/rules/README.md`。

### 前端规则包

1. 将 `web-front/rules/` 整包复制或作为 submodule 放入前端仓 `rules/`。
2. 复制 `web-front/rules/codex/AGENTS.md` 到前端仓根 `AGENTS.md`。
3. 复制 `web-front/rules/cursor/*.mdc` 到前端仓 `.cursor/rules/`。
4. 接入 `examples/` 中 views 禁 Element Plus、schema check、CI 扫描样板。
5. 运行 `python rules/scripts/validate-rules-package.py`。

详细说明见 `web-front/rules/README.md`。

### 小程序规则包

1. 将 `miniapp/rules/` 整包复制或作为 submodule 放入小程序仓 `rules/`。
2. 复制 `miniapp/rules/codex/AGENTS.md` 到小程序仓根 `AGENTS.md`。
3. 复制 `miniapp/rules/cursor/*.mdc` 到小程序仓 `.cursor/rules/`。
4. 复制 `miniapp/rules/examples/99-project-local.mdc.sample` 到 `.cursor/rules/99-project-local.mdc` 并按项目修改。
5. 接入 lint、type-check、`build:mp-weixin`、api check 和包体积检查。

详细说明见 `miniapp/rules/README.md` 与 `miniapp/rules/docs/onboarding-new-project.md`。

## Codex / Cursor 使用方式

### Codex

Codex 只看业务仓根 `AGENTS.md`。不要让它一次读全部 `shared/`。

推荐提示：

```text
后端：新增客户模块 API，按 OpenAPI + 04/05/08 + playbook。
前端：新增客户列表页，先读 `contracts/openapi.yaml`，再核对同步生成的 schema / API 类型，并按列表/表单规则实现。
全栈：先改 OpenAPI，再后端实现，再前端 api:gen + 联调（对齐 errorCode / traceId / 分页）。
成熟后台二开：复用平台菜单权限字典，按业务扩展规则 + playbook；平台差异写 99-project-local。
公共层变更：按 Owner / ADR 与平台边界规则。
```

### Cursor

Cursor 靠 `.cursor/rules/*.mdc` 的 `alwaysApply` 和 `globs` 触发。

建议：

- 只保留概览规则 `alwaysApply: true`。
- 业务模块靠路径 glob 触发。
- 公共层 / generator 由专门边界规则触发。
- 项目路径差异用业务仓 `99-project-local.mdc` 描述。

## 业务仓本地覆盖层

通用规则包无法知道每个项目的真实包名、Base 组件路径、OpenAPI 路径和成熟度目标。每个业务仓建议额外补一层本地配置。

后端 `AGENTS.md` 可追加：

```md
## 本项目约定

- 业务模块路径：`src/main/java/{basePackagePath}/modules/{biz}/`
- 占位符替换：`{basePackagePath}` 使用 Java 基础包的目录形式（如 `com/example/project`），`{biz}` 使用实际业务模块名。
- OpenAPI：`contracts/openapi.yaml`
- 采纳 Level：1
- （可选）成熟后台栈名、成功码取值、响应壳字段映射：见 `99-project-local.mdc`
```

前端 `.cursor/rules/99-project-local.mdc`：复制 `web-front/rules/examples/99-project-local.mdc.sample` 并按项目修改。

后端 `.cursor/rules/99-project-local.mdc`：复制 `web-backend/rules/examples/99-project-local.mdc.sample` 并按项目修改。

小程序 `.cursor/rules/99-project-local.mdc`：复制 `miniapp/rules/examples/99-project-local.mdc.sample` 并按项目修改（目标平台、分包路径、主包预算、登录态与隐私路径）。

本地覆盖层只写项目路径、技术栈、脚本名，不要复制大段 shared 规则。

## 业务场景落地示例

### 成熟后台新增 CRUD

1. 后端先确认是否复用平台用户、权限、字典、日志、文件、任务、租户、数据权限、CodeGen。
2. 先改 `contracts/openapi.yaml`。
3. 后端实现 Controller / Service / Mapper / 权限 / 审计 / 数据权限。
4. 前端执行 schema / api 生成，使用 Base 组件实现列表、表单、详情。
5. 菜单、路由、按钮权限码三端一致。
6. 导入导出、树表、主子表按前后端 playbook 检查。
7. 跑后端 Business Extension evals 与前端 lint / type-check / build。

关键文档：

- `web-backend/rules/shared/43-business-module-extension.md`
- `web-backend/rules/docs/business-feature-playbook.md`
- `web-front/rules/shared/22-business-module-extension.md`
- `web-front/rules/docs/business-feature-playbook-frontend.md`
- `web-backend/rules/docs/fullstack-contract.md`

### 普通接口 + 页面

1. OpenAPI 先行。
2. 后端不返回 Entity，前端不手写 generated 类型。
3. 分页字段、错误码、traceId、权限码一致。
4. 前端列表四态、删除末条回退页码、错误恢复完整。
5. 后端跑 `mvn verify` / `./gradlew check`，前端跑 `pnpm lint` / `type-check` / `build`。

## 跨端治理文档

规则正文之外，仓库还提供这些配套文档和脚本：

| 文档 / 脚本 | 用途 |
|---|---|
| [`docs/definition-of-done.md`](docs/definition-of-done.md) | 跨端统一 DoD（代码 / 契约 / 安全 / 数据 / 可观测 / 发布） |
| [`docs/architect-engineering-checklist.md`](docs/architect-engineering-checklist.md) | 立项、方案和上线评审提问单 |
| [`docs/rule-exception-process.md`](docs/rule-exception-process.md) | 例外与豁免流程（审批、有效期、ADR） |
| [`docs/codeowners-matrix.md`](docs/codeowners-matrix.md) | 按变更类型的强制 Review 矩阵 |
| [`docs/supply-chain-baseline.md`](docs/supply-chain-baseline.md) | 供应链强制基线（许可证、CVE SLA、SBOM） |
| [`docs/data-classification-matrix.md`](docs/data-classification-matrix.md) | 数据分类分级跨端表 |
| [`docs/slo-alerting-template.md`](docs/slo-alerting-template.md) | 管理端 / 小程序 SLO 与告警 Owner |
| [`docs/dod-maturity-mapping.md`](docs/dod-maturity-mapping.md) | DoD × 采纳 Level 0–3 对照 |
| [`docs/adoption-scorecard.md`](docs/adoption-scorecard.md) | 成熟度评分卡：Required Evidence / Owner / 到期复查 |
| [`docs/compliance-evidence-log.md`](docs/compliance-evidence-log.md) | 合规证据留痕（金融 / 政务） |
| [`docs/control-catalog.yaml`](docs/control-catalog.yaml) | SSDF / ASVS / OSPS / SLSA 版本化控制映射 |
| [`docs/branch-protection.md`](docs/branch-protection.md) | 分支保护与 Required Checks 实施指南（含豁免链路） |
| [`docs/git-pr-governance.md`](docs/git-pr-governance.md) | Conventional Commits、PR 证据、本地 hook 与 CI 边界 |
| [`docs/adr/0001-rules-governance-baseline.md`](docs/adr/0001-rules-governance-baseline.md) | 根级治理原则基线（ADR） |
| [`SECURITY.md`](SECURITY.md) | 安全策略与漏洞报告入口（含 SLA / secret 泄露处置） |
| [`scripts/check-project-adoption.py`](scripts/check-project-adoption.py) | **业务仓**接入验收（AGENTS、rules、cursor、契约） |
| [`scripts/check-debt-baseline.py`](scripts/check-debt-baseline.py) | 存量债务回归门禁：数量上限与路径白名单只能收敛 |
| [`scripts/validate-release-evidence.py`](scripts/validate-release-evidence.py) | 生产发布证据 YAML 校验 |
| [`scripts/validate-control-catalog.py`](scripts/validate-control-catalog.py) | 控制目录版本、映射与验证路径校验 |
| [`scripts/validate-workflow-security.py`](scripts/validate-workflow-security.py) | CI action 固定 SHA 与最小权限校验 |
| [`scripts/validate-ai-eval-results.py`](scripts/validate-ai-eval-results.py) | AI Tool Safety 5/5 结果与套件摘要绑定校验 |
| [`scripts/validate-exceptions.py`](scripts/validate-exceptions.py) | 机器校验豁免有效期、审批、补偿控制与关闭证据 |
| [`scripts/validate-pr-governance.py`](scripts/validate-pr-governance.py) | 校验实际 PR 描述中的需求追踪、风险等级和占位符 |
| [`scripts/generate-eval-topic-manifest.py`](scripts/generate-eval-topic-manifest.py) | Eval 全量 topic manifest（防 prompts/rubric drift） |

接到业务仓库后可以运行：

```bash
python scripts/check-project-adoption.py --repo /path/to/your-app --stack frontend --strict
python scripts/check-project-adoption.py --repo /path/to/your-app --stack frontend --level 2
```

## 验证与 CI

| 范围 | 命令 / 套件 |
|---|---|
| 后端规则包 | `python web-backend/rules/scripts/validate-rules-package.py` |
| 前端规则包 | `python web-front/rules/scripts/validate-rules-package.py` |
| 小程序规则包 | `python miniapp/rules/scripts/validate-rules-package.py` |
| 通用治理 SSOT 漂移 | `python scripts/sync-common-governance.py` |
| 通用治理发布包 | `python common-governance/scripts/validate-package.py`（一致性） |
| 控制目录 / CI 安全 | `python scripts/validate-control-catalog.py` + `python scripts/validate-workflow-security.py` |
| AI 工具安全证据 | `python scripts/validate-ai-eval-results.py --file examples/ai-eval-results.yaml --suite web-front/rules/evals/ai-tool-safety.md` |
| 豁免与 PR 治理 | `python scripts/validate-exceptions.py`；PR 事件运行 `python scripts/validate-pr-governance.py --event "$GITHUB_EVENT_PATH"` |
| 后端业务仓 | `mvn verify` 或 `./gradlew check` |
| 前端业务仓 | `pnpm lint`、`pnpm type-check`、`pnpm build` |
| 小程序业务仓 | `pnpm lint`、`pnpm type-check`、`pnpm build:mp-weixin`、`pnpm api:check`、`pnpm size:check`、`pnpm audit`（若配置） |
| 后端成熟业务扩展 | Business Extension B55–B63（建议 9/9） |
| 前端成熟业务扩展 | Business Extension E32–E40（建议 9/9） |
| 前端 i18n / 实时 / 富文本 | Platform Extension E41–E43（建议 3/3） |
| 前端金融 / 政务 / 高敏 Web | Enterprise Hardening E44–E49（建议 6/6） |
| 小程序 UGC / 富文本 / 恢复 | Resilience Extension M35–M38（建议 4/4） |
| 小程序安全加固 / 无障碍 / 多平台 / 实验 | Enterprise Hardening Extension M39–M44（建议 6/6） |
| 前端发版 / 大改规则 | Smoke / Full evals（E01–E50，P1 ≥39/42） |
| 全栈契约 | 固定版本 `oasdiff breaking --fail-on WARN` + 前端 api:gen / api:check |

本仓库 CI：PR 改任一端 `rules/**` 时运行对应 `validate-rules-package.py`（含 miniapp），见 `.github/workflows/validate-rules-packages.yml`。

## 接到业务仓库后检查

把规则包复制到真实项目后，按下面顺序检查。建议由项目负责人在第一个 PR 里做完。

### 必做

- [ ] 后端仓存在 `rules/`、根 `AGENTS.md`、`.cursor/rules/*.mdc`。
- [ ] 前端仓存在 `rules/`、根 `AGENTS.md`、`.cursor/rules/*.mdc`。
- [ ] 小程序仓存在 `rules/`、根 `AGENTS.md`、`.cursor/rules/*.mdc`。
- [ ] 根 `AGENTS.md` 中的路径能解析到 `rules/shared/...`、`rules/codex/...`。
- [ ] Cursor 只保留概览类规则 `alwaysApply: true`；不要把所有 `.mdc` 都设为 alwaysApply。
- [ ] 已补业务仓本地覆盖层：真实包名、业务模块路径、Base 组件路径、权威 OpenAPI 路径及生成物目录、采纳 Level。
- [ ] 企业项目已引入 `common-governance/` 并通过 `--level 2`（或显式 `--require-governance`）验收。
- [ ] `contracts/openapi.yaml`（或项目明确声明的等价 OpenAPI 路径）已写为契约 SSOT，schema / client 只由它生成，前后端不各维护字段定义。
- [ ] 后端接入 `mvn verify` / `./gradlew check`，前端接入 `pnpm lint`、`type-check`、`build`。
- [ ] 小程序接入 `pnpm lint`、`type-check`、`build:mp-weixin`、api check 和包体积检查。
- [ ] 业务 PR 模板已复制或等价接入，能覆盖契约、权限、数据权限、审计、导入导出和回滚。
- [ ] 成熟后台新增业务时，后端跑 Business Extension B55–B63、前端跑 E32–E40（均建议 9/9）。
- [ ] 前端 i18n / 实时 / 富文本相关 PR 跑 Platform Extension E41–E43（建议 3/3）。
- [ ] 前端金融 / 政务 / 高敏 Web 相关 PR 跑 Enterprise Hardening E44–E49（建议 6/6）。
- [ ] 小程序 UGC / 富文本 / 错误恢复相关 PR 跑 Resilience Extension M35–M38（建议 4/4）。
- [ ] 小程序安全加固 / 无障碍 / 多平台 / 实验相关 PR 跑 Enterprise Hardening Extension M39–M44（建议 6/6）。

### 推荐

- [ ] 后端接入 ArchUnit、Checkstyle、固定版本 `oasdiff breaking --fail-on WARN`、Flyway validate。
- [ ] 前端接入 schema / api check、views 禁 Element Plus 扫描。
- [ ] CODEOWNERS 覆盖契约、DB migration、安全、CI、规则包。
- [ ] 新项目声明采纳 Level：前端 / 后端至少 Level 0，成熟后台二开建议 Level 1。
- [ ] 发版前跑后端 Full evals；前端规则大改后跑 Smoke / Full。

## 常见误用

| 误用 | 后果 | 正确做法 |
|---|---|---|
| 只复制 `AGENTS.md`，不复制 `rules/` | AI 读不到 shared 全文，容易幻觉补规则 | 整包复制 `rules/`，或保证路径可解析 |
| 所有 `.mdc` 都 `alwaysApply: true` | 上下文膨胀，规则互相干扰 | 只让概览 alwaysApply，其余靠 globs |
| 让 AI 一次读完全部 shared | 慢、贵、容易丢重点 | 按这次改动和文件路径读取 |
| 业务仓不写本地路径 | Cursor / Codex 只能猜包名和目录 | 加 `99-project-local.mdc` 与本项目约定 |
| 前后端各写字段 | 字段、权限码、分页、错误码漂移 | 以 OpenAPI 为契约 SSOT，schema / client 只作生成物 |
| CodeGen 后直接上线 | 漏权限、审计、数据权限、测试 | 按前后端 playbook 补齐 |
| 改 common / system 做单业务 | 平台层污染，后续升级困难 | 业务进业务模块；平台变更走 ADR |

## 快速开始

| 场景 | 文档 |
|---|---|
| **全形态接入（首选）** | [`docs/project-adoption-guide.md`](docs/project-adoption-guide.md) — monorepo / 分仓 / 单端 |
| 新建前端项目 | `web-front/rules/README.md` |
| 新建后端项目 | `web-backend/rules/docs/onboarding-new-project.md` |
| 新建小程序项目 | `miniapp/rules/docs/onboarding-new-project.md` |
| 共享 API 契约 | `contracts/openapi.yaml` + `openapi.baseline.yaml`（CI diff） |
| 全栈 monorepo 布局 | `docs/monorepo-layout.md` |
| 企业治理文档索引 | `docs/README.md` |
| 通用治理发布包 | `common-governance/README.md` |
| 跨包 shared 编号对照 | `web-backend/rules/docs/fullstack-contract.md` §跨包编号说明 |
| 规则包自动校验 | PR 改任一侧 `rules/**` 时运行 `validate-rules-package.py`（见 `.github/workflows/validate-rules-packages.yml`） |
| 企业级 DoD / 豁免 / Owner | [`docs/definition-of-done.md`](docs/definition-of-done.md)、[`docs/rule-exception-process.md`](docs/rule-exception-process.md)、[`docs/codeowners-matrix.md`](docs/codeowners-matrix.md) |
| 业务仓接入验收 | [`scripts/check-project-adoption.py`](scripts/check-project-adoption.py) |
| 后端 Java 样板 | `web-backend/rules/examples/scaffold/` |

## 维护规则包

维护建议：

1. 不要把所有规则合成一个大文件。
2. 不要把所有 `.mdc` 设成 `alwaysApply: true`。
3. 新增 shared 编号文件时，同步 README、AGENTS、Cursor、evals、release checklist。
4. 改 eval 数量时，同步 prompts、rubric、results-template、smoke、README 和校验脚本。
5. 跨包引用 shared 编号时，见 `web-backend/rules/docs/fullstack-contract.md` §跨包编号说明，勿只报「读 08 / 22」。
6. 外层 README 只写全栈部署和协作，不复制前后端规则全文。
