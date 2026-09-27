# 业务项目规则包使用说明

> **读者**：新项目架构师、Tech Lead、首次接入 AI 规则包的开发者。
> **范围**：全栈 monorepo、前后端分仓、单端（管理端 / 后端 / 小程序）及组合场景。
> **原则**：必须整包落地 `rules/`；Codex 读根 `AGENTS.md`；Cursor 读 `.cursor/rules/*.mdc`；**禁止**只复制几个 `.mdc` 或只复制 `AGENTS.md`。

已有项目先填写 `examples/PROJECT_RULES.md.sample`，把真实目录、构建命令、契约现状、采纳级别和测试治理参数放进项目覆盖层。通用规则继续表达目标状态；存量偏差按 [`migration-baseline.md`](migration-baseline.md) 建立机器基线，二者不得混写。

---

## 0. 先选部署形态

```text
你的仓库里有哪些工程？
        │
        ├─ 管理端 + 后端 +（可选）小程序 在同一 Git 仓
        │       └─► 【A】全栈 monorepo（见 §1）
        │
        ├─ 管理端、后端、小程序 各自独立 Git 仓
        │       └─► 【B】前后端分仓（见 §2）
        │
        └─ 只有一端
                ├─ 仅 Vue 管理端     → 【C1】单端·管理端（§3.1）
                ├─ 仅 Spring Boot   → 【C2】单端·后端（§3.2）
                └─ 仅 uni-app 小程序 → 【C3】单端·小程序（§3.3）
```

| 形态 | 适用 | 契约 SSOT 放哪 | 规则包放哪 |
|---|---|---|---|
| **A 全栈 monorepo** | 一个产品团队、统一发版 | 仓根 `contracts/openapi.yaml` | 各子工程下 `rules/` 或仓根统一 `rules/` |
| **B 分仓** | 前后端独立发布、多团队 | **选一个仓**或独立 `contracts` 仓 | 每个业务仓各自 `rules/` |
| **C 单端** | 纯前端、纯后端、或小程序独立产品 | 本仓 `contracts/` 或消费方提供 | 本仓 `rules/` |

无论哪种形态，**OpenAPI / schema 只能有一份权威定义**；管理端 `api:gen`、小程序 `api:gen`、后端实现必须指向同一契约。

---

## 1. 全栈 monorepo

### 1.1 推荐目录结构

```text
product/                          # 你的业务 monorepo 根
├─ common-governance/             # 可版本化的通用治理发布包（仓库根，勿放 docs/ 下）
├─ contracts/
│  ├─ openapi.yaml                # API 契约 SSOT
│  └─ openapi.baseline.yaml       # CI diff 基线（稳定后生成）
├─ docs/                          # 业务仓可选：项目 ADR / 豁免 YAML 等
├─ web-front/                     # 管理端工程
│  ├─ AGENTS.md                   # ← web-front/rules/codex/AGENTS.md
│  ├─ rules/                      # ← 整包 web-front/rules
│  ├─ .cursor/rules/*.mdc
│  ├─ .cursor/rules/99-project-local.mdc
│  ├─ package.json
│  └─ src/
├─ web-backend/
│  ├─ AGENTS.md
│  ├─ rules/                      # ← 整包 web-backend/rules
│  ├─ .cursor/rules/*.mdc
│  ├─ .cursor/rules/99-project-local.mdc
│  ├─ pom.xml 或 build.gradle(.kts)
│  └─ src/main/java/
├─ miniapp/                        # 可选
│  ├─ AGENTS.md
│  ├─ rules/
│  ├─ .cursor/rules/
│  └─ src/
├─ .github/workflows/
└─ README.md
```

布局说明见 code-rules 维护仓 `docs/monorepo-layout.md`（不随本发布包分发）。

### 1.2 引入规则包（首次）

**方式 1 — Git submodule（推荐，便于升级规则版本）**

```bash
cd product/web-front
git submodule add <frontend-rules-repo-url> rules

cd ../web-backend
git submodule add <backend-rules-repo-url> rules
```

> 注意：只有当远端仓库根目录本身就是单端 `rules/` 包时，才能直接 submodule 到业务仓 `rules/`。如果远端是本 `code-rules` 整仓，直接 `git submodule add <code-rules-repo-url> rules` 会得到 `rules/web-front/rules/...` 这类嵌套路径，导致 `rules/codex/AGENTS.md`、`rules/shared/...` 断链。此时应使用 sparse-checkout / subtree / 发布单端 rules 包，或直接复制 `web-front/rules/` 到业务仓 `rules/`。

**方式 2 — 复制目录**

将 `code-rules` 仓库中 `web-front/rules/`、`web-backend/rules/`、`miniapp/rules/` **整目录**复制到对应子工程。

**每个子工程必须执行：**

| 步骤 | 管理端 | 后端 | 小程序 |
|---|---|---|---|
| 1 | 整包 `rules/` 可访问 | 同左 | 同左 |
| 2 | 复制 `rules/codex/AGENTS.md` → `web-front/AGENTS.md` | → `web-backend/AGENTS.md` | → `miniapp/AGENTS.md` |
| 3 | 复制 `rules/cursor/*.mdc` → `web-front/.cursor/rules/` | 同左 | 同左 |
| 4 | 复制 `rules/examples/99-project-local.mdc.sample` → `99-project-local.mdc` 并填写 | 同左 | 同左 |
| 5 | 校验 | `python web-front/rules/scripts/validate-rules-package.py` | 后端/小程序同理 |

### 1.3 Cursor 在 monorepo 中的打开方式

| 方式 | 说明 |
|---|---|
| **多根工作区** | VS Code / Cursor 添加 `web-front`、`web-backend` 为文件夹；各子工程自带 `.cursor/rules/` |
| **只打开子工程** | 日常只开 `web-front/` 时，该目录下须有完整 `rules/` + `AGENTS.md` + `.cursor/rules/` |

**不要**把三端所有 `.mdc` 合并到一个 `.cursor/rules/` 且全部 `alwaysApply: true`。

### 1.4 契约与联调流

```text
1. 改 contracts/openapi.yaml（PR 须 OpenAPI diff）
2. 后端实现 + `mvn verify` / `./gradlew check`
3. 管理端 pnpm api:gen + api:check + 页面
4. 小程序（若有）api:gen + 联调
5. 对齐 traceId、errorCode、分页、权限码
```

字段对照：`web-backend/rules/docs/fullstack-contract.md`。

### 1.5 monorepo CI 建议

**后端构建工具**：规则包对 Maven / Gradle **等价**——门禁目标是「编译 + 单测 +（若配置）ArchUnit / Checkstyle」，对应命令为 `mvn verify` 或 `./gradlew check`（见 `web-backend/rules/shared/23-quality-gates.md`）。`examples/ci/backend-ci-required.yml` 的 verify job **自动识别** `pom.xml` 与 `gradlew` + `build.gradle*`。Gradle 样板见 `web-backend/rules/examples/gradle/`；供应链 `common-governance/examples/ci/supply-chain-required.yml` 含 `gradle-dependency-check`（须 OWASP Gradle 插件）。Optional 的 Flyway 样板按构建工具拆分：Maven 用 `web-backend/rules/examples/ci/backend-ci-optional.yml`，Gradle 用 `web-backend/rules/examples/ci/backend-ci-optional-gradle.yml`（须 Flyway Gradle 插件）。

| Workflow | 路径触发 | 内容 |
|---|---|---|
| `backend-ci-required.yml` | `web-backend/**` | `mvn verify` / `./gradlew check`、OpenAPI diff、secret scan |
| 前端 lint/build | `web-front/**` | `pnpm lint`、`type-check`、`build` |
| `supply-chain-required.yml` | 根 / 各端 lockfile | npm/pnpm audit、Maven/Gradle OWASP、license-checker |
| `artifact-trust-required.yml` | 生产构建产物 | SPDX SBOM、构建 provenance / attestation |
| `rules-package-validate.yml` | `**/rules/**` | 各端 `validate-rules-package.py` |

样板：`web-backend/rules/examples/ci/`、`web-front/rules/examples/ci/`、`common-governance/examples/ci/`。第三方 action 必须固定完整 commit SHA，workflow 顶层默认只读，并由 `validate-workflow-security.py` 校验。

### 1.6 monorepo 验收命令

```bash
# 在 code-rules 仓或已复制 scripts/ 后
python scripts/check-project-adoption.py --repo ./web-front --stack frontend --strict
python scripts/check-project-adoption.py --repo ./web-backend --stack backend --strict   # 接受 pom.xml 或 Gradle wrapper
python scripts/check-project-adoption.py --repo ./miniapp --stack miniapp --strict

# Level 2+：校验三类 PR 工作流及产物信任发布工作流的静态结构；平台状态另行核对
python common-governance/scripts/check-project-adoption.py --repo ./web-front --stack frontend --level 2
```

---

## 2. 前后端分仓

### 2.1 结构示例

```text
# 仓库 1：frontend-repo
frontend-repo/
├─ AGENTS.md
├─ rules/                    # web-front/rules 整包
├─ .cursor/rules/
├─ contracts/openapi.yaml    # 方案甲：契约在前端仓
│  或仅 openapi.generated    # 方案乙：契约仅在后端仓，前端 CI 拉取
├─ package.json
└─ src/

# 仓库 2：backend-repo
backend-repo/
├─ AGENTS.md
├─ rules/                    # web-backend/rules 整包
├─ .cursor/rules/
├─ contracts/openapi.yaml    # 方案乙：契约在后端仓（更常见）
└─ src/main/java/
```

### 2.2 契约 SSOT 两种做法（二选一，写进 README）

| 方案 | SSOT 位置 | 前端如何更新 generated |
|---|---|---|
| **甲：后端仓** | `backend-repo/contracts/openapi.yaml` | CI 从后端仓拉取 yaml → `api:gen` |
| **乙：独立契约仓** | `api-contracts/openapi.yaml` | 两端 submodule / package 同步 |

**禁止**：前后端各维护一份字段定义且长期不同步。

### 2.3 分仓落地步骤

每个仓库**独立**完成：

1. 引入对应端 `rules/` 整包
2. `AGENTS.md` + `.cursor/rules/` + `99-project-local.mdc`
3. 复制 `rules/examples/.github/` → 本仓 `.github/`（PR 模板）
4. 接入本仓 CI（见各端 `rules/examples/ci/`）
5. 在 `AGENTS.md` 或 `99-project-local.mdc` 写明：
   - 契约文件 URL / 相对路径
   - 对端仓库名与联调联系人
   - 采纳 Level

### 2.4 分仓协作约定

| 变更类型 | 谁先改 | 谁后改 |
|---|---|---|
| 新 API | 后端仓 OpenAPI PR | 前端仓 `api:gen` PR |
| 字段重命名 | 后端兼容期 + deprecated | 前端跟进 generated |
| 权限码 / 菜单 | 后端定义 | 前端路由与按钮对齐 |

全栈 PR 可拆两个链接 PR，但须在描述中互相引用；契约变更须双端 Owner Review（见 [`codeowners-matrix.md`](codeowners-matrix.md)）。

### 2.5 分仓验收

对每个仓库分别运行 `check-project-adoption.py`（见 §7.1）。

---

## 3. 单端项目

### 3.1 仅管理端（Vue3 + Element Plus）

```text
admin-portal/
├─ AGENTS.md              ← web-front/rules/codex/AGENTS.md
├─ rules/                 ← web-front/rules 整包
├─ .cursor/rules/
├─ contracts/schema.json  # 或 openapi.yaml，须单一 SSOT
└─ src/
```

**必读**：`web-front/rules/README.md`、`web-front/rules/docs/onboarding-new-project.md`。

**硬门禁（Level 0）**：

```bash
pnpm lint
pnpm type-check
pnpm build
pnpm api:check          # 若已配置
node rules/examples/ci-scan-views-el-tags.mjs   # views 禁 el-*
```

**成熟度**：`web-front/rules/docs/rule-maturity-model.md`（建议首迭代 Level 0，上线前 Level 1–2）。

**若无后端**：契约可来自第三方 OpenAPI；`AGENTS.md` 中写明契约来源与字段谁维护。

---

### 3.2 仅后端（Spring Boot）

```text
api-service/
├─ AGENTS.md              ← web-backend/rules/codex/AGENTS.md
├─ rules/                 ← web-backend/rules 整包
├─ .cursor/rules/
├─ contracts/openapi.yaml
└─ src/main/java/
```

**必读**：`web-backend/rules/docs/onboarding-new-project.md`。

**硬门禁（Level 0）**：

```bash
mvn verify                # Maven：含单测 + ArchUnit（若接入）
# 或
./gradlew check           # Gradle：等价门禁
# CI：OpenAPI diff、gitleaks
```

**成熟度**：`web-backend/rules/docs/rule-maturity-model.md`（Level 0 起；核心域 Level 1–2）。

**样板代码**：

- Maven：`web-backend/rules/examples/scaffold/`、`examples/archunit/`、`examples/pom-dependencies.sample.xml`
- Gradle：`web-backend/rules/examples/gradle/`（`build.gradle.kts.sample` + 同上 ArchUnit / scaffold Java）

---

### 3.3 仅小程序（uni-app）

```text
miniapp-product/
├─ AGENTS.md
├─ rules/                 ← miniapp/rules 整包
├─ .cursor/rules/
├─ .cursor/rules/99-project-local.mdc   # 主包预算、平台、分包路径
├─ contracts/openapi.yaml
└─ src/
```

**必读**：`miniapp/rules/README.md`、`miniapp/rules/docs/onboarding-new-project.md`。

**硬门禁（Level 0–1）**：

```bash
pnpm lint
pnpm type-check
pnpm build:mp-weixin
pnpm api:check
pnpm size:check           # 主包体积
```

**成熟度**：`miniapp/rules/docs/rule-maturity-model.md`（Level 0 基线 → Level 1 上线 → Level 2 支付/多分包）。

**脚手架**：`miniapp/rules/examples/scaffold/*.sample`。

---

### 3.4 单端 + 未来扩展

若当前只有管理端，但计划加后端：

1. 现在就采用 `contracts/openapi.yaml` 作为字段 SSOT（可先手写或 Mock）。
2. `99-project-local.mdc` 预留后端联调路径。
3. 规则包升级时只升 `web-front/rules`，后端接入时再引入 `web-backend/rules`。

---

## 4. 所有形态通用：本地覆盖层

规则包不知道你的真实包名与目录，**必须**补本地配置。

### 4.1 `99-project-local.mdc`（Cursor）

从对应端复制 sample 并修改：

| 端 | Sample 路径 |
|---|---|
| 管理端 | `web-front/rules/examples/99-project-local.mdc.sample` |
| 后端 | `web-backend/rules/examples/99-project-local.mdc.sample` |
| 小程序 | `miniapp/rules/examples/99-project-local.mdc.sample` |

**建议填写**：

- `views` / `modules` / 分包根路径
- Base 组件、request、generated API 路径
- OpenAPI / schema 路径
- `采纳 Level: 0 | 1 | 2`
- 实际 npm / Maven / Gradle 脚本名（如 `mvn verify`、`./gradlew check`）
- 测试治理参数：覆盖率策略、N/N-1 或迁移兼容窗口、flaky 登记与隔离期限、失败证据保留、测试数据隔离/清理、风险专项触发条件

`PROJECT_RULES.md` 与三端 `99-project-local.mdc` 应表达同一组项目事实；可以互相引用，不能一处仍是占位符、另一处却被当作已完成接入。不适用项必须写 `not-applicable` 和原因。

### 4.2 `AGENTS.md` 追加「本项目约定」

```markdown
## 本项目约定

- 仓库形态：全栈 monorepo | 分仓·前端 | 单端·后端
- 契约 SSOT：contracts/openapi.yaml
- 业务模块：src/views/crm/ | modules/crm/
- 成熟后台栈：RuoYi-Vue-Plus 5.x（若适用）
- 采纳 Level：1
- 联调：traceId 头 X-Trace-Id；分页 page/size/total
```

### 4.3 Cursor 配置要点

| 项 | 建议 |
|---|---|
| `alwaysApply: true` | **仅** `00-project-overview.mdc` |
| 其余 `.mdc` | 靠 `globs` 按路径触发 |
| `rules/` 路径 | `.mdc` 内使用 `rules/shared/...`，确保能解析 |

### 4.4 Codex / Agent 提示词模板

```text
任务：新增 {模块} 列表页。
先读 rules/codex/01-before-editing.md 与 rules/shared/00-must-follow.md。
实现按 rules/shared/22-business-module-extension.md（若成熟后台）。
改完按 rules/shared/10-verification-checklist.md 收尾，并说明跑了哪些命令。
```

**不要**：`请阅读 rules/shared 下所有文件`。

---

## 5. 采纳成熟度（Level）与 DoD

不必一次接入全部 shared 文件。按 Level 分阶段：

| Level | 何时 | 摘要 |
|---|---|---|
| **0** | 第 1 个迭代 | 能安全构建：分层、契约、基础鉴权、lint/build |
| **1** | 上线前 | 测试、依赖治理、审计/隐私基线、Smoke evals |
| **2** | 核心域 / 企业客户 | SLO、威胁建模、Full evals、发版清单 |
| **3** | 平台团队 | 云原生、事件契约、成本治理 |

**DoD 与 Level 对照**：[`dod-maturity-mapping.md`](dod-maturity-mapping.md)。
**合并 / 发版标准**：[`definition-of-done.md`](definition-of-done.md)。

各端 Level 细则：

- 后端：`web-backend/rules/docs/rule-maturity-model.md`
- 管理端：`web-front/rules/docs/rule-maturity-model.md`
- 小程序：`miniapp/rules/docs/rule-maturity-model.md`

---

## 6. 通用治理发布包

规则包内是**编码规则**；组织级 DoD、豁免、Owner 的维护 SSOT 在 code-rules 根 `docs/`，可分发副本位于 `common-governance/`。

业务仓应整包引入 `common-governance/`，不要手工挑选并维护第二份文档：

| 文件 | 用途 |
|---|---|
| `project-adoption-guide.md` | 业务项目接入总指南（本文件随包分发） |
| `definition-of-done.md` | 合并 / 发版门禁 |
| `architect-engineering-checklist.md` | 立项、方案和上线评审提问单 |
| `migration-baseline.md` | 目标规则与存量债务基线分离 |
| `release-evidence.md` | 结构化发布证据 |
| `environment-promotion.md` | 多环境晋级与回滚 |
| `branch-protection.md` | 分支保护与 Required Checks |
| `rule-exception-process.md` | 跳过 CI 怎么批 |
| `docs/exceptions/README.md` | 机器可读豁免目录与 CI 接入 |
| `codeowners-matrix.md` | 谁必须 Review |
| `supply-chain-baseline.md` | 依赖 / 许可证策略 |
| `data-classification-matrix.md` | PII 分级 |
| `slo-alerting-template.md` | 管理端 / 小程序 SLO 与告警 |
| `dod-maturity-mapping.md` | Level × DoD |
| `compliance-evidence-log.md` | 等保 / 审计留痕 |
| `git-pr-governance.md` | Commit、PR、本地 hook 与 CI 边界 |
| `examples/SECURITY.md.sample` | 项目漏洞报告与凭据泄露处置入口模板 |
| `examples/adr-template.md` | 项目架构决策记录模板 |
| `examples/rule-exception.yaml` | 豁免记录样板 |
| `examples/migration-baseline.json` | 存量债务基线样板 |
| `examples/ci/credential-scan-required.yml` | 凭据泄露扫描 Required workflow |
| `examples/ci/rules-adoption-required.yml` | 规则采纳 Level 2 Required workflow |
| `examples/ci/supply-chain-required.yml` | 锁文件、依赖漏洞与许可证 Required workflow |
| `examples/ci/artifact-trust-required.yml` | SBOM 与构建 provenance / attestation workflow |
| `examples/ci/debt-baseline-required.yml` | 存量债务不可增长 Required workflow |
| `examples/ci/exceptions-required.yml` | 豁免记录期限与关闭证据 Required workflow |
| `examples/ci/ai-eval-results-required.yml` | AI Tool Safety 结果 YAML 校验（发版 / 高风险 AI；不跑模型） |
| `examples/ai-eval-results.yaml` | AI Tool Safety 结果样板 |
| `examples/governance-adoption.yaml` | 三类 PR Required workflow、产物信任发布工作流、平台控制和 Level 3 证据清单 |
| `examples/governance-platform-evidence.json` | 组织权限、主干保护和生产环境控制快照 |
| `docs/control-catalog.yaml` | SSDF / ASVS / OSPS / SLSA 版本化控制映射 |

维护者运行 `python scripts/sync-common-governance.py` 防止发布副本漂移；业务仓运行 `python common-governance/scripts/validate-package.py` 验证发布文件与 manifest 一致。企业项目推荐 `--level 2`（自动校验完整治理包、版本与 checksum）；仅当 Level < 2 仍要强制校验治理包时，再显式加 `--require-governance`。

---

## 7. 验收与自检

### 7.1 自动化接入检查

```bash
# 在 code-rules 仓执行，或复制 scripts/check-project-adoption.py 后执行
python scripts/check-project-adoption.py --repo /path/to/project --stack frontend
python scripts/check-project-adoption.py --repo /path/to/project --stack backend
python scripts/check-project-adoption.py --repo /path/to/project --stack miniapp

# 严格模式（要求 CODEOWNERS、PR 模板）
python scripts/check-project-adoption.py --repo /path/to/project --stack frontend --strict

# 按成熟度门禁验收
python scripts/check-project-adoption.py --repo /path/to/project --stack frontend --level 1
python common-governance/scripts/check-project-adoption.py --repo /path/to/project --stack frontend --level 2

# 当前 Level 作为 Required；更高目标以报告模式展示真实差距
python common-governance/scripts/check-project-adoption.py --repo /path/to/project --stack frontend --level 3 --report-only

# 存量债务只能持平或下降
python common-governance/scripts/check-debt-baseline.py --config /path/to/project/migration-baseline.json
```

后端 `--stack backend` 接受 **`pom.xml`** 或 **`gradlew` + `build.gradle` / `build.gradle.kts`**，不再强制 Maven。

| Level | 自动检查增量 |
|---|---|
| 0 | 规则入口、基础构建脚本；本地覆盖缺失仅警告 |
| 1 | 强制 `99-project-local.mdc` 且测试治理参数已替换占位符；管理端支持 OpenAPI、JSON Schema 或明确声明的契约源并要求 `api:check`；小程序强制 OpenAPI、`api:check`、`size:check`；后端要求 CI 运行 Maven verify/test 或 Gradle check/test |
| 2 | 自动启用严格 CODEOWNERS / 结构化 PR 模板、完整 `common-governance/`，并核验规则采纳、凭据扫描、供应链三类 PR workflow、产物信任发布 workflow，以及 90 天内的平台控制声明快照 |
| 3 | 在 Level 2 基础上要求 Scorecard 及至少三项带 Owner、状态和证据引用的平台治理控制；仓内校验仍不是平台实时证明 |

生产发布另运行：

```bash
python common-governance/scripts/validate-release-evidence.py --file releases/<version>/release-evidence.yaml --artifact dist/<artifact> --require-artifact
```

### 7.2 人工清单

各端：`<端>/rules/evals/adoption-checklist.md`，按 Level 勾选。

### 7.3 AI 规则回归（evals）

| 场景 | 管理端 | 后端 | 小程序 |
|---|---|---|---|
| 日常 PR | Smoke | Smoke | Smoke |
| 成熟后台新业务 | E32–E40 | B55–B63 | M21–M29 |
| i18n / 实时 / 富文本 | E41–E43 | — | — |
| 金融 / 政务 / 高敏 Web | E44–E49 | — | M39–M44（小程序对应加固） |
| UGC / 恢复 | — | — | M35–M38 |
| 发版 / 规则升级 | Full E01–E50 | Full B01–B67 | Full M01–M52 |

操作：向 AI 发送 `rules/evals/prompts.md` 中固定提示词，对照 `rubric.md` 打分。AI Tool Safety 结果必须写入结构化 YAML，并通过 `validate-ai-eval-results.py` 绑定套件摘要、模型版本和独立评测人。详见各端 `rules/evals/README.md`。

---

## 8. 常见业务场景速查

### 8.1 成熟后台新增 CRUD（RuoYi / Jeecg 二开）

1. 改 `contracts/openapi.yaml`
2. 后端：`shared/43` + `web-backend/rules/docs/business-feature-playbook.md`
3. 前端：`api:gen` + `shared/22` + `web-front/rules/docs/business-feature-playbook-frontend.md`
4. 菜单 / 路由 / 权限码三端一致
5. Evals：B55–B63 + E32–E40

### 8.2 普通接口 + 单页

1. OpenAPI 先行
2. 后端不返回 Entity；前端不手写 generated 类型
3. 列表四态、分页、错误恢复
4. `mvn verify` / `./gradlew check` + `pnpm lint` / `build`

### 8.3 小程序新业务分包

1. OpenAPI → `api:gen`
2. 页面进 `src/subpackages/{domain}/`
3. `miniapp/rules/docs/business-feature-playbook-miniapp.md`
4. Evals：M21–M29

### 8.4 升级规则包版本

1. 更新 submodule 或替换 `rules/` 目录
2. 阅读新版本 `rules/CHANGELOG.md`
3. 运行 `python rules/scripts/validate-rules-package.py`
4. 若改过 `evals/prompts.md` 或 `rubric.md`，同步生成并提交 `evals/topic-manifest.yaml`（monorepo：`python scripts/generate-eval-topic-manifest.py --all`）
5. 规则大版本：跑该端 **Full** evals
6. submodule 接入时，提交中须包含 submodule 指针变化；复制目录接入时，提交中须包含实际 `rules/` 文件变化
7. 升级失败时，回退到上一版 submodule commit 或恢复上一版 `rules/` 目录，并记录失败原因

---

## 9. 常见误用

| 误用 | 后果 | 正确做法 |
|---|---|---|
| 只复制 `AGENTS.md` | AI 幻觉补规则 | 整包 `rules/` |
| 所有 `.mdc` alwaysApply | 上下文爆炸 | 仅概览 alwaysApply |
| 一次读完全部 shared | 慢、漏重点 | 按任务 / glob |
| 不写 `99-project-local` | 路径猜错 | 必填真实路径 |
| 前后端各写字段 | 联调失败 | 契约 SSOT |
| CodeGen 直接上线 | 缺权限/审计 | playbook 补齐 |
| 只 submodule rules 不接治理包 | DoD / 豁免无据 | 引入并验证 `common-governance/` |
| Gradle 仓只复制 Maven optional CI | Flyway / OWASP 门禁失效 | 用 `backend-ci-optional-gradle.yml` + `supply-chain-required.yml` |
| 平台控制只贴截图或链接 | Level 2 证据可过期、不可机器核验 | 生成 90 天内的 `governance-platform-evidence.json` |
| 发布证据只手填产物摘要 | 无法证明摘要对应真实产物 | 校验时传 `--artifact` 和 `--require-artifact` |

---

## 10. 文档索引

| 主题 | 路径 |
|---|---|
| 本说明 | `docs/project-adoption-guide.md` |
| Monorepo 布局 | `docs/monorepo-layout.md` |
| 治理总索引 | `docs/README.md` |
| 通用治理发布包 | `common-governance/README.md` |
| 需求追踪 | `docs/requirements-traceability.md` |
| 业务正确性评审 | `docs/business-correctness-review.md` |
| AI 工具安全 | `docs/ai-tool-security.md` |
| 发布证据 | `docs/release-evidence.md` |
| 根 README | `README.md` |
| 全栈契约 | `web-backend/rules/docs/fullstack-contract.md` |
| 跨包 shared 编号 | 同上 §跨包编号说明 |
| 管理端规则包 | `web-front/rules/README.md` |
| 后端规则包 | `web-backend/rules/README.md` |
| 后端 Gradle 样板 | `web-backend/rules/examples/gradle/` |
| 小程序规则包 | `miniapp/rules/README.md` |

---

## 11. Day 1 最小清单（复制勾选）

**所有形态必做：**

- [ ] 选定部署形态（§0）并写入项目 README
- [ ] 对应端 `rules/` 整包可访问
- [ ] `AGENTS.md` + `.cursor/rules/` + `99-project-local.mdc`
- [ ] Level 1+ 已填写测试治理参数；不适用项有原因，无样板占位符
- [ ] 契约 SSOT 路径已文档化
- [ ] Level 0 CI：lint + build（+ 后端 `mvn verify` / `./gradlew check`）
- [ ] 运行 `check-project-adoption.py` 通过

**全栈额外：**

- [ ] `contracts/openapi.yaml` + baseline 策略
- [ ] 双端（三端）`api:gen` / `api:check` 脚本可用
- [ ] PR 模板含契约与权限自检
- [ ] PR 模板含需求追踪矩阵与业务正确性复核

**企业客户额外：**

- [ ] 引入 `common-governance/` 并运行包一致性校验
- [ ] CODEOWNERS 按 [`codeowners-matrix.md`](codeowners-matrix.md)
- [ ] 接入 `common-governance/examples/ci/supply-chain-required.yml` 到 `.github/workflows/`
- [ ] 接入 `artifact-trust-required.yml`，生成并归档 SBOM 与 attestation
- [ ] 生成 90 天内的平台控制快照，通过 Level 2 静态校验，并核对平台当前设置与 Required check 状态
- [ ] 生产发布使用真实产物参数校验并归档 `release-evidence.yaml`
- [ ] 发版 / 规则包升级 / 高风险 AI 变更时，归档通过校验的 AI Tool Safety 5/5 结果 YAML（日常 L0 采纳不强制）
