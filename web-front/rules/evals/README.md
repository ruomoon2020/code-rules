# Rules Evals（规则回归评测）

用于验证 AI 是否遵守 `rules/` 约束。建议每季度或规则大版本发布前跑一轮。

## 前置条件

1. 业务仓库已按 `rules/README.md` **方式 A** 落地完整 `rules/`。
2. 已配置 Cursor `.cursor/rules/` 或 Codex 根目录 `AGENTS.md`。
3. 测试仓库具备最小可运行结构：`src/views`、`src/components/base`、`contracts/schema.json`（可用 fixture）。

## 如何执行

1. 打开 `prompts.md`，按编号依次向 AI 发送**固定提示词**（不要改措辞）。
2. 对照 `rubric.md` 判定 Pass / Fail / Partial。
3. 填写 `results-template.md`（复制为带日期的结果文件，如 `results-2026-05-24.md`）。
4. Fail 项回流修改 `shared/` 或 `cursor/`，并更新 `CHANGELOG.md`。

## 通过标准

| 级别 | 用例 | 门槛 |
|---|---|---|
| **P0** | E01–E08（共 8 条） | **8/8** 必须 Pass |
| **P1** | E09–E50（共 42 条） | **至少 39/42** Pass |

## 回归套件（企业分层）

| 套件 | 范围 | 门槛 | 场景 |
|---|---|---|---|
| **Smoke** | E01–E08 + 核心 P1 12 条 | P0 8/8；核心 P1 ≥10/12 | 日常 PR、AI 快速回归 |
| **Security** | E12、E18、E25、E27 | 建议 4/4 | 安全 / 隐私 / 导入导出 PR |
| **Contract** | E03、E04、E05、E26 | 建议 4/4 | Schema / API / 字段 PR |
| **Business Extension** | E32–E40 | 建议 9/9 | 成熟后台新增业务页 / CRUD / 树表主子表 PR |
| **Platform Extension** | E41–E43 | 建议 3/3 | i18n / WebSocket·SSE / 富文本·编辑器 PR |
| **Enterprise Hardening** | E44–E49 | 建议 6/6 | 金融 / 政务 / 高敏数据 / 第三方脚本 / 嵌入页面 PR |
| **Testing Governance** | E31、E50 | 建议 2/2 | 测试稳定性 / 写链路竞态 / API 兼容 PR |
| **AI Tool Safety** | EAT01–EAT05（独立文件） | **5/5 Required** | AI 读取外部内容、调用工具或执行外部动作 |
| **Full** | E01–E50 | P0 8/8；P1 ≥39/42 | **发版**、规则包升级 |

索引（不复制正文）：`smoke-prompts.md`（**不计入** `### Exx` 计数；校验见 `scripts/validate-rules-package.py`）。

AI Tool Safety 正文与判据见 `ai-tool-safety.md`；该套件不计入常规 P1 总分，任一项失败即阻断。

执行边界：`validate-ai-eval-results.py` **不调用模型**；可用 `prepare-ai-eval-run.py --print-plan` / `--write-skeleton` 准备评测。5/5 阻断发版、规则包升级与高风险 AI 变更，不是 Level 0 采纳检查。详见 common-governance `docs/ai-tool-security.md`「评测执行边界」。

AI Tool Safety 结果须保存为结构化 YAML，并绑定本文件对应套件的摘要、模型版本、执行时间与独立评测人。业务仓使用公共治理包校验：

```bash
python common-governance/scripts/validate-ai-eval-results.py --file evidence/ai-eval-results.yaml --suite rules/evals/ai-tool-safety.md
```

校验器验证结果证据完整性，不负责调用模型；模型执行器由业务仓 CI 显式配置并固定版本。

**Topic manifest**：`topic-manifest.yaml` 为 prompts 标题与 rubric 判定的 SSOT；改 `prompts.md` / `rubric.md` 后运行 monorepo `python scripts/generate-eval-topic-manifest.py --rules-dir web-front/rules`。

### 核心 P1（= Smoke 中的 12 条）

E09、E13、E15、E16、E17、E18、E22、E24、E27、E28、E29、E30。

发版前仍须跑 **Full**（E01–E50）。

### 与后端 Business Extension 对照（联调 / 双端 PR）

| 后端 | 前端 | 主题 |
|---|---|---|
| B55 | E32 | 不污染公共 / 壳层 |
| B56 | E33 | 复用平台菜单 / 权限 / 字典 |
| B57 | E34 | CodeGen 后须补齐 |
| B58 | E35 | 列表 / 详情 / 导出权限一致 |
| B59 | E36 | 导出审计与下载鉴权 UI |
| B60 | E37 | 导入任务状态，禁止伪造成功 |
| B61 | E38 | 树表父节点禁选非法项 |
| B62 | E39 | 主子表失败态与回滚一致 |
| B63 | E40 | 禁止改 generator 全局 Vue 模板 |

**E41–E43** 为管理端 i18n / 实时通信 / 富文本专项，无后端 B 对称项；涉及相关 PR 时跑 **Platform Extension** 套件。

**E44–E49** 为受监管 Web 条件专项；仅在金融、政务、高敏数据、第三方脚本或嵌入通信场景运行 **Enterprise Hardening** 套件。

- 不允许把 39/42 四舍五入为通过。
- 任一条 Fail 若输出可合并代码，须在真实仓库跑 `pnpm lint` / `type-check` 二次确认。

## 与落地清单关系

`adoption-checklist.md` 用于勾选业务仓规则落地状态，与 evals 互补：前者是清单，后者是行为验证。
