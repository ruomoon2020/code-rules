# 跨端治理 CI 样板

本目录提供可复制到业务仓 `.github/workflows/` 的治理工作流。它们负责把规则采纳、供应链、存量债务、豁免和发布证据变成可重复执行的门禁，不替代前后端自身的编译、测试和业务验收。

## 选择与落地

1. 先按项目风险和采纳 Level 选择工作流，不要无差别全部复制。
2. 复制到业务仓后，修改路径、包管理器、构建命令和证据文件位置。
3. 在测试分支触发一次，确认工作流确实执行而不是被条件表达式跳过。
4. 再将通过且稳定的 job 配置为 Required Check，并记录 Owner 和豁免流程。

| 文件 | 复制目标 | 用途 |
|---|---|---|
| [`supply-chain-required.yml`](supply-chain-required.yml) | `.github/workflows/supply-chain-required.yml` | 单锁文件校验 + audit + 固定版本 OWASP / license-checker |
| [`rules-adoption-required.yml`](rules-adoption-required.yml) | `.github/workflows/rules-adoption-required.yml` | 规则采纳 Level 2 Required |
| [`debt-baseline-required.yml`](debt-baseline-required.yml) | `.github/workflows/debt-baseline-required.yml` | 存量债务不可增长 Required |
| [`artifact-trust-required.yml`](artifact-trust-required.yml) | `.github/workflows/artifact-trust-required.yml` | 可复用的 SBOM 与构建 provenance / attestation 步骤；须由自动触发的发布工作流调用 |
| [`exceptions-required.yml`](exceptions-required.yml) | `.github/workflows/exceptions-required.yml` | 豁免期限、审批与关闭证据 Required |
| [`ai-eval-results-required.yml`](ai-eval-results-required.yml) | `.github/workflows/ai-eval-results-required.yml` | AI Tool Safety 结果 YAML 校验（不跑模型；发版 / 高风险 AI） |
| [`../../common-governance/examples/ci/credential-scan-required.yml`](../../common-governance/examples/ci/credential-scan-required.yml) | `.github/workflows/credential-scan-required.yml` | 凭据泄露扫描（Required） |

## 使用边界

发布时，供应链、采纳、债务、产物信任、豁免与 AI 结果样板会同步到 `common-governance/examples/ci/`；前端、后端和小程序的编译测试样板分别位于各自 `rules/examples/ci/`。

`governance-adoption.yaml` 的 `artifact_trust.evidence` 应指向自动触发的发布工作流。仅复制可复用 workflow 而没有发布调用方，不构成产物信任证据。

验收时同时核对 [`docs/supply-chain-baseline.md`](../../docs/supply-chain-baseline.md)、[`docs/branch-protection.md`](../../docs/branch-protection.md)、[`docs/rule-exception-process.md`](../../docs/rule-exception-process.md) 和 [`docs/ai-tool-security.md`](../../docs/ai-tool-security.md)。工作流绿色只能证明对应工具执行成功，不能替代业务正确性评审。
