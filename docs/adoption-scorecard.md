# 规则体系采纳评分卡（Adoption Scorecard）

> 用途：对业务团队的规则包采纳情况做“证据化体检”，把 Level 0-3 的目标落到可追溯字段（Evidence）与 Owner。

---

## 设计原则
- 评分维度严格对齐根级 DoD（代码/契约/安全/数据/可观测/发布）：[`docs/definition-of-done.md`](definition-of-done.md)
- DoD 与 Level 对照以：[`docs/dod-maturity-mapping.md`](dod-maturity-mapping.md) 为准
- 必须 Required 的项：不满足就不建议评定该 Level 可合并/可发版
- 豁免/例外：仅允许走 [`docs/rule-exception-process.md`](rule-exception-process.md)，并且必须限时、可复查

---

## 打分输出格式（团队建议填表）

建议对每个 Evidence 行都填写：
- `Owner`：负责人/团队（需与 `docs/codeowners-matrix.md` 可映射）
- `Evidence`：链接（PR 链接、CI 链接、文档路径、报告编号）
- `Target`：目标 Level（0/1/2/3）
- `Status`：未就绪/进行中/已完成
- `Due/Review`：到期时间或复查日期（适用于 Required 且走豁免的情况）

示例行：
- 项目：`OpenAPI diff` evidence
- Target：Level 1
- Required：是
- Evidence：PR #123 + CI #456 链接
- Owner：@api-owner

---

## 评分维度（按 DoD 门禁拆分）

### 0. 需求与业务评审（所有业务变更）

| 项目 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| 需求 / Issue 与验收条件可追溯 | Required | Required | Required | Required |
| 工作流、数据、权限、契约和回归人工复核 | Required（按业务变更） | Required | Required | Required |
| AI 外部内容与工具安全边界 | Required（使用 AI 时） | Required | Required | Required |
| AI Tool Safety 5/5 套件 | Optional（行为仍须遵守） | Optional（高风险 AI 变更建议） | Required（发版 / 规则包升级 / 高风险 AI 变更） | Required |

证据字段建议：PR 需求追踪矩阵、关键业务测试名、Reviewer 结论、外部写入 / 数据出站审批（若有）。触发 5/5 套件时另附绑定套件摘要、模型版本和独立评测人的 AI 结果 YAML。`check-project-adoption.py` 不验收 5/5；见 [`ai-tool-security.md`](ai-tool-security.md)「评测执行边界」。

### A. 代码门禁（DoD 第 1 道）
| 项目 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| Lint/Build/编译可通过 | Required | Required | Required | Required |
| 单测/验证增强 | Optional | Required | Required | Required |
| 分层/架构扫描（如适用） | Optional | Required（推荐） | Required | Required |

证据字段建议（按端选择）：
- 后端：`mvn verify` / `./gradlew check` +（如启用）ArchUnit/Checkstyle 证据
- 前端：`pnpm lint/type-check/build` 证据
- 小程序：`pnpm lint/type-check/build:mp-weixin` +（如启用）views 约束证据

---

### B. 契约门禁（DoD 第 2 道）
| 项目 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| 契约 SSOT 可追溯（OpenAPI） | Required | Required | Required | Required |
| OpenAPI diff（breaking 标识） | Required（按改 API 触发） | Required | Required | Required |
| 生成/校验一致（api:gen/api:check） | Optional | Required | Required | Required |

证据字段建议：
- 契约变更 PR：contracts/openapi.yaml（或项目约定路径）+ diff/报告
- 消费端生成证据：api:gen + api:check 输出
- “禁止手改 generated”的约束证据（PR 审查要点）

---

### C. 安全门禁（DoD 第 3 道）
| 项目 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| Secret scan（发现阻断） | Required | Required | Required | Required |
| 依赖漏洞审计与 SLA | Required（基础） | Required | Required | Required |
| PII/隐私日志脱敏 | Optional | Required（按 PII 触发） | Required | Required |
| 威胁建模/越权回归（高风险时） | Optional | Optional（推荐） | Required（按高风险） | Required |
| 组织 MFA / 最小默认权限 / 生产非自审 | Optional | Optional | Required | Required |

证据字段建议：
- 依赖/许可证/漏洞扫描报告（CI 链接）
- 高风险接口的安全测试/威胁建模记录或 PR 说明
- PII 字段对照与脱敏证明（对应文档/PR）

---

### D. 数据门禁（DoD 第 4 道）
| 项目 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| DB migration validate | Required（改库时） | Required | Required | Required |
| Dry-run/影响行数 | Optional | Required（生产数据修复时） | Required | Required |
| 回滚或逆向 migration 可执行 | Required（改库时） | Required | Required | Required |
| 备份演练/归档策略 | Optional | Optional | Required | Required |

证据字段建议：
- migration 脚本 + validate 结果
- 回滚脚本/逆向 migration
- 生产数据变更工单/审批链路（如适用）

---

### E. 可观测门禁（DoD 第 5 道）
| 项目 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| traceId 贯通 | Required | Required | Required | Required |
| 结构化日志不含敏感明文 | Required | Required | Required | Required |
| SLO/告警 Owner | Optional | Required（按端能力） | Required | Required |
| 降级/恢复与可观测验证 | Optional | Optional | Required（按风险） | Required |

证据字段建议：
- traceId 传递说明或回归证据
- SLO/告警配置证据（链接 [`docs/slo-alerting-template.md`](slo-alerting-template.md) 的实际配置或 PR）

---

### F. 发布门禁（DoD 第 6 道）
| 项目 | Level 0 | Level 1 | Level 2 | Level 3 |
|---|---|---|---|---|
| 发版说明/范围/回滚步骤 | Required | Required | Required | Required |
| 回滚机制可用（至少一键可回退） | Required | Required | Required | Required |
| 灰度/金丝雀（按风险域） | Optional | Required（按项目） | Required | Required |
| 发版后 24h 观察与复盘链路 | Optional | Required（按端） | Required | Required |
| 结构化 `release-evidence.yaml` | Optional | Optional | Required | Required |
| 不可变产物与环境晋级证据 | Optional | Optional | Required（生产） | Required |
| SBOM + provenance / attestation 验证 | Optional | Optional | Required（生产） | Required |
| 事故响应演练与行动项闭环 | Optional | Optional | Required（高风险系统） | Required |

证据字段建议：
- 发布清单/Release Note + 回滚步骤
- 灰度策略与验证证据
- 发版观察记录（至少 24h）
- `validate-release-evidence.py` 通过记录与归档文件
- 90 天内的 `governance-platform-evidence.json` 与 Level 2 接入校验通过记录

---

## 体检流程（建议 30-60 分钟）
1. 从最近 3-5 个代表性 PR/发版挑选 Evidence（覆盖代码/契约/安全/数据/可观测/发布）
2. 对照每个维度的 Target Level：标注 Evidence 是否满足 Required
3. 对缺失项：
   - 能补：给出 Owner + 截止时间
   - 必须跳过：创建豁免单，填到 [`docs/rule-exception-process.md`](rule-exception-process.md)
4. 输出评分卡 PDF/链接（可直接作为业务接入推进材料）
