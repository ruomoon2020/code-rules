# 分支保护与 Required Checks 实施指南

> 目标：让 `main` 的合并必须“有证据、有审批、有回滚”，并把 CI Required 门禁与豁免流程串起来，避免“Required 被绕过但没有审计记录”。

---

## 适用范围
- 组织仓/业务仓的默认发布分支：`main`（或你们的主干分支等价项）
- 使用本仓规则包后：业务仓必须把规则包治理校验脚本接入 CI，并把对应校验设置为 Required Checks。

---

## 概念约定
### Required Checks
指 GitHub/GitLab 分支保护规则里“合并前必须全绿”的状态检查（status checks）。

code-rules 源仓提供的 Required Checks 参考实现位于 `.github/workflows/validate-rules-packages.yml`；发布包不复制该 monorepo 专用 workflow。

### 绕过（Bypass）
指在分支保护 Required Checks 未通过的情况下由特定权限人允许合并。

本指南要求：绕过必须有“时间盒豁免单 + 风险接收”，并在 PR 中可追溯。

### 豁免/例外（Exception/Waiver）
绕过或跳过 Required 门禁时，必须走豁免流程并链到记录：
[`docs/rule-exception-process.md`](rule-exception-process.md)

---

## main 必须配置项（GitHub UI）
在 GitHub 仓库：`Settings -> Branches -> Branch protection rules` 配置 `main`，建议至少开启：

1. **Require a pull request before merging**
   - 禁止直推（no direct push）。
2. **Require status checks to pass before merging**
   - 选择本仓提供的规则校验 workflow 的 Required checks。
3. **Require review from Code Owners**
   - 与 [`docs/codeowners-matrix.md`](codeowners-matrix.md) 对齐，避免“安全/契约/CI/规则包”无人审。
4. （可选但建议）**Restrict who can push to matching branches**
   - 仅允许 Maintainers/DevOps/Release 角色推送；普通开发仅 PR。

## Level 2+ 组织与生产环境控制

以下配置不能仅写在制度文档中，必须从代码托管平台接口、基础设施状态或平台导出结果生成结构化快照：

- 组织强制 MFA；仓库默认权限为 `read` 或 `none`；CI 内置身份默认只读。
- 主干至少 1 名审批人，要求 CODEOWNERS、驳回过期审批、至少 1 名非作者审批，禁止强制推送和删除。
- 生产环境至少 1 名 Reviewer，并启用禁止自审或平台等价控制。
- 主干 PR Required Checks 至少覆盖 `rules-adoption`、`credential-scan`、`supply-chain`；生产发布另以 `artifact-trust` 为发布门禁。仅在发布标签触发的 job 不应登记为 PR Required Check。

证据使用 `examples/governance-platform-evidence.json` 的 schema；`captured_at` 必须带时区且不早于验收日 90 天。业务仓在 `governance-adoption.yaml` 的 `branch_protection.evidence` 引用该快照。Level 2 接入脚本只检查仓内快照与工作流的结构，不能证明平台当前设置、Required Checks 状态或工作流实际执行；发布负责人须核对平台导出/API 结果，并在 PR 或发布证据中记录核对时间与来源。截图可作为附件，但不能替代结构化快照。

---

## Recommended: Required Checks 清单
你们应在业务仓 CI 中确保存在对应 workflow/job（job 名按本仓一致即可），然后在分支保护里选择这些 checks 为 Required。不要机械要求单端业务仓具备三端全部 job，应按仓库形态选择。

### 全栈 monorepo
适用于同一仓库同时维护后端、管理端、小程序或跨端规则包：

- 规则包 / 治理脚本：`validate-rules-packages / validate-backend-rules`、`validate-frontend-rules`、`validate-miniapp-rules`、`validate-governance-scripts`
- 规则采纳：`rules-adoption`（Level 2+ Required）
- 凭据扫描：`credential-scan`
- 供应链：`supply-chain`
- 发布产物信任：`artifact-trust`（SBOM + provenance / attestation，发布门禁）
- 有存量债务时追加：`debt-baseline`；有开放豁免时追加：`exceptions`

### 后端单仓
适用于只接入 `web-backend/rules/` 的业务仓：

- 后端构建门禁：`mvn verify` 或 `./gradlew check`
- 契约门禁：固定版本 `oasdiff breaking --fail-on WARN`（若改 API）；相对目标分支已接受的契约基线执行，首次 baseline 须有 Owner 标签并满足基线相等性要求，禁止用 PR 说明跳过
- 规则采纳：`rules-adoption`（Level 2+）
- 凭据扫描：`credential-scan`
- 供应链门禁：`supply-chain-required`（按 [`supply-chain-baseline.md`](supply-chain-baseline.md)）
- 产物信任门禁：`artifact-trust`（生产发布）
- 规则接入门禁：`python common-governance/scripts/check-project-adoption.py --repo . --stack backend --level 2`

### 前端单仓
适用于只接入 `web-front/rules/` 的业务仓：

- 前端构建门禁：`pnpm lint`、`pnpm type-check`、`pnpm build`
- 契约门禁：`api:gen` / `api:check`（若消费 OpenAPI）
- 规则采纳：`rules-adoption`（Level 2+）
- 凭据扫描：`credential-scan`
- 供应链门禁：`supply-chain-required`
- 产物信任门禁：`artifact-trust`（生产发布）
- 规则接入门禁：`python common-governance/scripts/check-project-adoption.py --repo . --stack frontend --level 2`

### 小程序单仓
适用于只接入 `miniapp/rules/` 的业务仓：

- 小程序构建门禁：`pnpm lint`、`pnpm type-check`、`pnpm build:mp-weixin`
- 契约门禁：`api:check`
- 规则采纳：`rules-adoption`（Level 2+）
- 凭据扫描：`credential-scan`
- 供应链门禁：`supply-chain-required`
- 产物信任门禁：`artifact-trust`（生产发布）
- 规则接入门禁：`python common-governance/scripts/check-project-adoption.py --repo . --stack miniapp --level 2`

说明：
- GitHub UI 中显示的 check context 名称可能略有差异（例如 provider 将其显示为 `validate-backend-rules` 或带 workflow 前缀）。以 UI 中的实际名称为准。
- 若你们业务仓拆分/合并 workflow，请仍保持“本仓形态对应的构建、契约、安全、供应链、规则接入”五类校验 Required。

---

## 绕过策略（Bypass Policy）与审计要求

### 规则（必须落地）
1. **绕过 Required Checks 必须有豁免单 ID**
   - 在 PR 中显式写明 `EXC-YYYY-NNN`（或你们工单系统同等 ID），并引用到 [`docs/rule-exception-process.md`](rule-exception-process.md)。
2. **绕过需时间盒**
   - 豁免默认有效期不得长期化（参照豁免流程，默认 ≤ 90 天；到期必须复查/续期）。
3. **安全 Critical 类门禁原则上不允许“无补偿绕过”**
   - Critical 安全绕过必须同时附补偿控制（例如 WAF/限流/审计/feature flag/额外测试或威胁建模）。
4. **绕过必须由风险接收人承担责任**
   - Risk Acceptance 与最低审批矩阵参照 [`docs/rule-exception-process.md`](rule-exception-process.md) 的审批要求。

### 谁可以绕过（建议）
- 技术/治理类 Required checks 的绕过：Rules/DevOps/Architecture 负责人（可按 CODEOWNERS/团队映射）
- 安全/PII/供应链相关 Required checks 的绕过：Security Owner（或安全团队）+ 领域 Owner

你们可用 CODEOWNERS/团队别名替换示例账号（例如安全团队 `@security-team`、DevOps `@devops-team`），并确保 PR 模板要求 Owner/豁免链路。

---

## 代码片段：可选 IaC 样板（Terraform 示例）
> 说明：不同 Terraform GitHub Provider 版本字段名可能不同。本段提供“可落地思路”，以你们 provider 的实际 schema 为准。

```hcl
# 仅示意：required status checks 需要填你们 GitHub UI 实际显示的 check context
resource "github_branch_protection" "main" {
  repository_id = var.repository_id
  pattern       = "main"

  required_pull_request_reviews {
    required_approving_review_count = 1
    # require_code_owner_reviews = true  # 视 provider 支持
  }

  required_status_checks {
    strict   = true
    contexts = [
      "validate-rules-packages/validate-backend-rules",
      "validate-rules-packages/validate-frontend-rules",
      "validate-rules-packages/validate-miniapp-rules",
      "validate-rules-packages/validate-governance-scripts",
    ]
  }

  # 禁止直推：provider 支持时可配 restrict push（或在 settings 中手工配置）
}
```

---

## 与 PR 模板的联动要求
建议在根级 PR 模板中强化：
- 当 Required checks 未全绿时，必须填豁免单 ID（见 PR 模板“豁免单链路”）
- 当涉及安全 Critical/PII/供应链时，Owner/风险等级更严格并要求安全 Owner 签字

根级 PR 模板存在于：`.github/pull_request_template.md`（本仓提供的组织级入口）。
