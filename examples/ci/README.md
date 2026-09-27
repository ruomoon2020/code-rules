# CI 样板（monorepo 根）

| 文件 | 复制目标 | 用途 |
|---|---|---|
| [`supply-chain-required.yml`](supply-chain-required.yml) | `.github/workflows/supply-chain-required.yml` | 单锁文件校验 + audit + 固定版本 OWASP / license-checker |
| [`rules-adoption-required.yml`](rules-adoption-required.yml) | `.github/workflows/rules-adoption-required.yml` | 规则采纳 Level 2 Required |
| [`debt-baseline-required.yml`](debt-baseline-required.yml) | `.github/workflows/debt-baseline-required.yml` | 存量债务不可增长 Required |
| [`artifact-trust-required.yml`](artifact-trust-required.yml) | `.github/workflows/artifact-trust-required.yml` | 可复用的 SBOM 与构建 provenance / attestation 步骤；须由自动触发的发布工作流调用 |
| [`exceptions-required.yml`](exceptions-required.yml) | `.github/workflows/exceptions-required.yml` | 豁免期限、审批与关闭证据 Required |
| [`ai-eval-results-required.yml`](ai-eval-results-required.yml) | `.github/workflows/ai-eval-results-required.yml` | AI Tool Safety 结果 YAML 校验（不跑模型；发版 / 高风险 AI） |
| [`../../common-governance/examples/ci/credential-scan-required.yml`](../../common-governance/examples/ci/credential-scan-required.yml) | `.github/workflows/credential-scan-required.yml` | 凭据泄露扫描（Required） |

发布时供应链、采纳、债务、产物信任、豁免与 AI 结果样板同步到 `common-governance/examples/ci/`；各端规则包另有 `web-*/rules/examples/ci/` 与 `miniapp/rules/examples/ci/`。

`governance-adoption.yaml` 的 `artifact_trust.evidence` 应指向自动触发的发布工作流。仅复制可复用 workflow 而没有发布调用方，不构成产物信任证据。

详见 [`docs/supply-chain-baseline.md`](../../docs/supply-chain-baseline.md)、[`docs/branch-protection.md`](../../docs/branch-protection.md)、[`docs/rule-exception-process.md`](../../docs/rule-exception-process.md)、[`docs/ai-tool-security.md`](../../docs/ai-tool-security.md)。
