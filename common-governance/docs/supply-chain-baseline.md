# 跨端供应链强制基线

> 汇总 `web-backend/rules/shared/20`、`web-front/rules/shared/20`、`miniapp/rules/shared/25`。业务仓 CI **Required** 须满足本基线；Optional 项见各包 `examples/ci/`。

## 许可证

| 策略 | 要求 |
|---|---|
| 白名单 | Apache-2.0、MIT、BSD、ISC 等（法务可扩） |
| **禁止未评审** | **GPL / AGPL** 传染、未知许可证、自定义「禁止商用」 |
| PR 说明 | 新许可证须写合规结论 |
| Abandonware | 核心依赖禁止长期无维护包；无法替代 → ADR + 豁免单 |

## 漏洞 SLA

| 严重级别 | 修复时限 | 无法修复 |
|---|---|---|
| Critical | **7 天** | 风险登记 + 补偿控制 + 安全签字 |
| High | **30 天** | 同上 |
| Medium | 90 天或下季度 | 跟踪单 |
| Low | 按计划 | — |

**阻断**：`mvn verify` / `./gradlew check` / CI Required 在 Critical 未缓解时不得绿。

## 锁版本与来源

| 端 | 要求 |
|---|---|
| 后端 | BOM（Maven）或 version catalog（Gradle）；禁止随意 major 升级无回归 |
| 管理端 | `pnpm-lock.yaml` / `package-lock.json` 入库；禁止仅 `^` 漂移上线 |
| 小程序 | 同左；第三方 SDK 须平台兼容说明 |
| 私服 | npm / Maven 仅允许公司私服 + 官方源白名单；禁止随意 `registry` 指向未知 URL |

## SBOM 与镜像

| 产物 | 要求 |
|---|---|
| Java | CycloneDX / SPDX（`mvn` 插件、`./gradlew` 任务或 CI 步骤） |
| Node | `npm sbom` / CycloneDX 或 Dependabot 导出 |
| 发布分支 | 保留 SBOM 产物或构建链接 |
| 容器 | 镜像扫描（Trivy / 云厂商）；禁止 `latest` 上生产；非 root 运行 |

## CI 映射（Required vs Optional）

| 门禁 | 后端 | 管理端 | 小程序 | 级别 |
|---|---|---|---|---|
| 依赖 audit | OWASP DC（Maven / Gradle，见 `supply-chain-required.yml`）/ Dependabot | `pnpm audit` / Snyk | 同左 | **Required** |
| 许可证 | license-check | license-check | 同左 | **Required**（金融政务） |
| SBOM | 发版分支生成 | 发版分支生成 | 发版分支生成 | Level 2+ / 核心域 Required |
| Provenance / 签名 | 产物与 commit、builder、SBOM 绑定并可验签 | 同左 | 同左 | Level 2+ / 生产 Required |
| 容器扫描 | 有镜像则 Required | N/A | Required |
| 包体积 | N/A | bundle 预算 | 主包 / 分包预算 | **Required** |
| **许可证（Node）** | — | `license-checker`（见 `supply-chain-required.yml`） | 同左 | **Required**（金融政务） |

GitHub Actions 样板见 `examples/ci/artifact-trust-required.yml`：调用方先上传唯一命名的构建产物，再调用该 reusable workflow 生成 SPDX SBOM、build provenance 和 SBOM attestation。所有外部 Action 必须固定到 40 位 commit SHA。
`governance-adoption.yaml` 的产物信任证据应指向自动触发的发布调用方；单独存在的 reusable workflow 只说明具备步骤，不能证明发布流程会运行它。

样板：`common-governance/examples/ci/supply-chain-required.yml`（发布包内路径；源码位于 monorepo 根 `examples/ci/`）。Node 样板要求恰好一个 pnpm/npm 锁文件；Yarn 项目须提供组织批准的等价 workflow，禁止静默退化。后端另见 `web-backend/rules/examples/ci/backend-ci-required.yml`。

## AI 生成约束

1. 不得随意添加未在 BOM / lockfile 治理下的依赖。
2. 用户要求 GPL、来源不明、废弃库 → **拒绝**并给替代方案（evals B41 / E29 / M 等价项）。

## 豁免

无法满足时走 [`rule-exception-process.md`](rule-exception-process.md)，**安全类禁止无期限豁免**。

## 相关

- [`definition-of-done.md`](definition-of-done.md) §安全门禁
- `web-backend/rules/shared/23-quality-gates.md`
