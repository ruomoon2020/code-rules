# Rules Evals（规则回归评测）

用于验证 AI 是否遵守 `miniapp/rules/` 约束。建议每季度或规则大版本发布前跑一轮。

## 前置条件

1. 业务仓库已按 `rules/README.md` 落地完整 `rules/`。
2. 已配置 Cursor `.cursor/rules/` 或 Codex 根目录 `AGENTS.md`。
3. 测试仓库具备最小结构：`src/pages`、`src/subpackages`、`src/api`、`contracts/openapi.yaml`（可用 fixture）。

## 如何执行

1. 打开 `prompts.md`，按编号依次向 AI 发送**固定提示词**（不要改措辞）。
2. 对照 `rubric.md` 判定 Pass / Fail / Partial。
3. 填写 `results-template.md`（复制为带日期的结果文件）。
4. Fail 项回流修改 `shared/` 或 `cursor/`，并更新 `CHANGELOG.md`。

## 通过标准

| 级别 | 用例 | 门槛 |
|---|---|---|
| **P0** | M01–M08（共 8 条） | **8/8** 必须 Pass |
| **核心 P1** | M09–M20（共 12 条） | **>= 10/12** Pass |
| **Business Extension** | M21–M29（共 9 条） | 建议 **9/9** Pass |
| **Security Extension** | M30–M34（共 5 条） | 建议 **5/5** Pass |
| **Resilience Extension** | M35–M38（共 4 条） | 建议 **4/4** Pass |
| **Enterprise Hardening Extension** | M39–M44（共 6 条） | 建议 **6/6** Pass |
| **Media Extension** | M51（共 1 条） | 建议 **1/1** Pass |
| **Component Engineering Extension** | M45–M50（共 6 条） | 建议 **6/6** Pass |
| **Testing Governance Extension** | M52（共 1 条） | 建议 **1/1** Pass |

## 回归套件（企业分层）

| 套件 | 范围 | 门槛 | 场景 |
|---|---|---|---|
| **Smoke** | M01–M08 + 核心 P1 10 条 | P0 8/8；核心 P1 ≥10/12 | 日常 PR、AI 快速回归 |
| **Security** | M06、M07、M12、M18、M30–M34 | 建议 9/9 | 隐私 / 分享 / 日志 / App·网络·环境 PR |
| **Contract** | M03、M05、M08、M15、M51 | 建议 5/5 | OpenAPI / generated / 支付 / 上传媒体 PR |
| **Business Extension** | M21–M29 | 建议 9/9 | 新业务分包 PR |
| **Resilience** | M35–M38 | 建议 4/4 | 错误恢复 / UGC / 可观测 PR |
| **Enterprise Hardening** | M39–M44 | 建议 6/6 | 安全加固 / 无障碍 / 多平台 / 实验 PR |
| **Component Engineering** | M45–M50 | 建议 6/6 | 组件 / 样式 / 生命周期 / 测试 / 性能 PR |
| **Testing Governance** | M49、M52 | 建议 2/2 | 测试稳定性 / 回调重放 / API 兼容 PR |
| **AI Tool Safety** | MAT01–MAT05（独立文件） | **5/5 Required** | AI 读取外部内容、调用工具或执行外部动作 |
| **Full** | M01–M52 | P0 8/8；核心 P1 >=10/12 | **发版**、规则包升级 |

索引（不复制正文）：`smoke-prompts.md`（**不计入** `### Mxx` 计数；校验见 `scripts/validate-rules-package.py`）。

AI Tool Safety 正文与判据见 `ai-tool-safety.md`；该套件不计入常规 P1 总分，任一项失败即阻断。

执行边界：`validate-ai-eval-results.py` **不调用模型**；可用 `prepare-ai-eval-run.py --print-plan` / `--write-skeleton` 准备评测。5/5 阻断发版、规则包升级与高风险 AI 变更，不是 Level 0 采纳检查。详见 common-governance `docs/ai-tool-security.md`「评测执行边界」。

AI Tool Safety 结果须保存为结构化 YAML，并绑定本文件对应套件的摘要、模型版本、执行时间与独立评测人。业务仓使用公共治理包校验：

```bash
python common-governance/scripts/validate-ai-eval-results.py --file evidence/ai-eval-results.yaml --suite rules/evals/ai-tool-safety.md
```

校验器验证结果证据完整性，不负责调用模型；模型执行器由业务仓 CI 显式配置并固定版本。

**Topic manifest**：`topic-manifest.yaml`；改 evals 后运行 `python scripts/generate-eval-topic-manifest.py --rules-dir miniapp/rules`。

### 核心 P1（= Smoke 中的 10 条）

M09、M11、M13、M14、M15、M16、M17、M18、M19、M20。

发版前仍须跑 **Full**（M01–M52）。

### 与全栈对照（联调 PR）

| 后端 | 小程序 | 主题 |
|---|---|---|
| OpenAPI SSOT | M03、M22 | 字段不虚构 |
| 支付幂等 | M05、M15、M26 | 订单状态、金额 |
| 审计 / 日志 | M12、M18 | 脱敏、traceId |
| 业务模块扩展 | M21–M29 | 新分包不污染主包 |

- 任一条 Fail 若输出可合并代码，须在真实仓库跑 `pnpm lint` / `type-check` / `build:mp-weixin` 二次确认。

## 与落地清单关系

`adoption-checklist.md` 用于勾选业务仓规则落地状态，与 evals 互补。
