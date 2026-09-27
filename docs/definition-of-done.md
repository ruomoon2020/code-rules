# 全栈 Definition of Done（DoD）

> 业务 PR **合并**与**发布**的统一完成标准。各端细则见对应 `shared/10` / `16` / `23`；本文是跨端 SSOT。

## 适用

| 场景 | 必过门禁 |
|---|---|
| 日常功能 PR | 代码 + 契约（若改 API） |
| 安全 / 依赖 / 权限 PR | 上述 + 安全 + 供应链 |
| 含 DB 变更 PR | 上述 + 数据 |
| 发版 / 灰度 | 全部 + 可观测 + 发布 |

所有业务行为变更还须按 [`requirements-traceability.md`](requirements-traceability.md) 建立需求、验收条件、实现与验证证据链，并按 [`business-correctness-review.md`](business-correctness-review.md) 完成人工业务评审。

豁免见 [`rule-exception-process.md`](rule-exception-process.md)。

---

## 1. 代码门禁

| 检查项 | 后端 | 管理端 | 小程序 |
|---|---|---|---|
| Lint | `mvn verify` / `./gradlew check`、Checkstyle | `pnpm lint` | `pnpm lint` |
| 类型 / 编译 | `mvn compile` / `./gradlew compileJava` | `pnpm type-check` | `pnpm type-check` |
| 单元 / 集成测试（Level 1+） | `mvn test` / `./gradlew test`（含 ArchUnit 若接入） | 项目约定 Vitest | 项目约定单测 |
| 测试稳定性（Level 1+） | 固定时钟/随机/依赖；flaky 有期限治理 | 固定浏览器/网络/数据；保留失败证据 | 固定平台/网络/数据；保留失败证据 |
| 并发 / 幂等（Level 2+ 或命中写链路） | 重复提交、并发更新、消息重放、任务防重 | 重复点击、竞态、旧响应覆盖 | 重复点击、支付/回调重放、页面重复进入 |
| 兼容 / 迁移（Level 2+ 或命中契约/迁移） | N/N-1、事件与数据库迁移 | generated 与旧服务端响应 | generated、旧服务端与平台版本 |
| 构建 | 可部署产物 | `pnpm build` | `pnpm build:mp-weixin` |
| 分层 / 架构 | ArchUnit（推荐） | views 禁 EP 扫描 | 分包 / request 封装 |

**未通过**：Required CI 红灯时禁止合并。带 Level 或场景条件的条目按 [`dod-maturity-mapping.md`](dod-maturity-mapping.md) 和本次变更范围启用；未命中时不得伪装成已执行。

---

## 2. 契约门禁

| 检查项 | 说明 |
|---|---|
| OpenAPI SSOT | 字段 / 错误码 / 分页先于实现 |
| OpenAPI diff | 相对 `openapi.baseline.yaml` 无未说明 breaking |
| 前端 / 小程序生成 | `api:gen` + `api:check`；禁止手改 `generated/**` |
| 联调字段 | `traceId`、`errorCode`、权限码、分页与 `fullstack-contract` 一致 |

**Owner**：API 变更须后端 + 消费端 Owner 双签（见 [`codeowners-matrix.md`](codeowners-matrix.md)）。

---

## 3. 安全门禁

| 检查项 | 工具示例 | 策略 |
|---|---|---|
| Secret scan | gitleaks / trufflehog | Required：发现即阻断 |
| 依赖漏洞 | OWASP DC / Dependabot / Snyk | Critical/High 按 SLA（见 [`supply-chain-baseline.md`](supply-chain-baseline.md)） |
| 许可证 | license-check / FOSSA | GPL/AGPL/未知须评审 |
| 鉴权回归 | 越权 / BOLA 测试 | 高风险接口必测 |
| 隐私 / PII | 对照 [`data-classification-matrix.md`](data-classification-matrix.md) | 日志 / 缓存 / 导出脱敏 |

---

## 4. 数据门禁

| 检查项 | 说明 |
|---|---|
| Migration | Flyway/Liquibase 在目标方言 validate |
| Dry-run | 生产向脚本须 dry-run + 影响行数 |
| 回滚 | 可执行回滚脚本或逆向 migration |
| 生产数据 | 手工 SQL 须工单 + DBA/数据 Owner（`31-production-data-ops`） |
| 测试数据 | 禁止生产 PII 进 fixture / 非生产库 |

---

## 5. 可观测门禁

| 检查项 | 后端 | 管理端 | 小程序 |
|---|---|---|---|
| traceId | 全链路传递 | 请求头携带 | 请求头携带 |
| 诊断主事件 | 失败响应的 traceId 能检索到一条诊断事件 | 错误上报带同一 traceId | 错误上报带同一 traceId |
| 结构化日志 | 无 Token/PII 明文 | 同左 | 同左 |
| 指标 / SLO | `32-service-reliability` | [`slo-alerting-template.md`](slo-alerting-template.md) §管理端 | 同文档 §小程序 |
| 告警 Owner | Oncall 轮值表 | 前端 Owner | 小程序 Owner |
| 错误恢复 | 降级 errorCode | chunk / 白屏恢复 | 弱网 / 分包失败 |

发版后 **24h** 内观察核心 SLO；异常须可回滚。

---

## 6. 发布门禁

| 检查项 | 说明 |
|---|---|
| 变更说明 | PR / Release Note：范围、风险、回滚步骤 |
| 灰度 | 核心域须灰度或金丝雀（按项目） |
| 回滚 | 上一版本镜像 / 配置可一键回退 |
| Owner 签字 | 发布清单 `release-checklist`（后端）+ 各端 smoke |
| Evals（规则驱动团队） | 发版前跑 Full / Smoke（见各包 `evals/README.md`） |
| AI 工具安全证据 | 使用 AI 时遵守 [`ai-tool-security.md`](ai-tool-security.md)；**发版 / 规则包升级 / 高风险 AI 变更**须归档 AI Tool Safety 5/5 YAML（绑定套件摘要、模型版本、评测人）。日常 Level 0 采纳检查不要求 5/5 |
| 发布证据 | 按 [`release-evidence.md`](release-evidence.md) 生成并校验 `release-evidence.yaml` |
| 产物信任 | Level 2+ 生产产物生成 SBOM、provenance / attestation，并在发布证据中记录验证命令 |
| 环境晋级 | 同一不可变产物按 [`environment-promotion.md`](environment-promotion.md) 晋级，配置漂移、灰度与回滚有证据 |
| 事故准备 | 值班、升级和证据路径明确；高风险发布可按 [`incident-response.md`](incident-response.md) 响应并使用复盘模板 |

---

## PR 自检（最小）

复制到业务仓 PR 描述或链接本文件：

- [ ] 代码门禁 CI 全绿
- [ ] 若改 API：OpenAPI 已更新 + diff 已审 + 消费端已 gen
- [ ] 若改依赖：供应链基线已对照
- [ ] 若改 DB：migration + 回滚已附
- [ ] 若改写链路 / API / 事件：并发幂等、N/N-1 或迁移兼容用例已运行
- [ ] 测试失败证据可定位；无靠重试洗绿或无期限隔离的 flaky test
- [ ] traceId / 关键指标 / 告警已确认
- [ ] 回滚方案与 Owner 已写明
- [ ] 需求追踪矩阵完整，关键业务场景已完成人工评审
- [ ] `release-evidence.yaml` 已通过校验（生产发布）
- [ ] Level 2+ 的平台快照与产物信任通过机器校验；若本变更使用 AI 且属发版 / 高风险 AI 场景，AI Tool Safety 5/5 YAML 已通过校验

## 相关文档

| 文档 | 用途 |
|---|---|
| [`requirements-traceability.md`](requirements-traceability.md) | 需求与验收证据链 |
| [`business-correctness-review.md`](business-correctness-review.md) | 业务正确性评审 |
| [`release-evidence.md`](release-evidence.md) | 结构化发布证据 |
| [`environment-promotion.md`](environment-promotion.md) | 环境晋级与生产变更 |
| [`incident-response.md`](incident-response.md) | 事故响应 |
| [`incident-postmortem-template.md`](incident-postmortem-template.md) | 事故复盘模板 |
| [`rule-exception-process.md`](rule-exception-process.md) | 豁免流程 |
| [`codeowners-matrix.md`](codeowners-matrix.md) | Review 矩阵 |
| [`supply-chain-baseline.md`](supply-chain-baseline.md) | 依赖强制基线 |
| [`data-classification-matrix.md`](data-classification-matrix.md) | 数据分级 |
| [`slo-alerting-template.md`](slo-alerting-template.md) | SLO 与告警 |
| [`dod-maturity-mapping.md`](dod-maturity-mapping.md) | DoD × Level 对照 |
| [`control-catalog.yaml`](control-catalog.yaml) | 版本化控制与外部标准映射 |
| `web-backend/rules/docs/release-checklist.md` | 后端发版清单 |
