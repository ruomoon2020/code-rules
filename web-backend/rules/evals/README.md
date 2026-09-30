# 后端 AI 规则回归评测

本目录用固定提示词和判定标准验证 AI 是否遵守后端规则，适用于规则维护、重大架构调整和规则包发布。评测通过只能说明 AI 输出满足当前 rubric，不能证明接口、事务、权限、数据范围或迁移脚本在真实业务中正确。

## 什么时候运行

| 变更场景 | 最小套件 |
|---|---|
| 日常规则或路由调整 | Smoke |
| 鉴权、契约、架构或业务模块扩展 | 对应专项套件 + Smoke |
| 规则包发布或大版本升级 | Full + AI Tool Safety |

## 前置条件

1. 业务仓已落地完整 `rules/`。
2. 具备 Spring Boot 最小结构：`modules/*/api`、`application`、`mapper`。
3. 有 `contracts/openapi.yaml`（可用 fixture）。

## 执行流程

1. 从 `prompts.md` 复制固定提示词，不改措辞或补充隐含条件。
2. 使用相同模型配置执行选定套件。
3. 按 `rubric.md` 判定 Pass / Fail / Partial，并保存原始输出。
4. 用 `results-template.md` 记录模型、时间、评测人和失败证据。
5. 修复规则或路由后重跑失败项与相关套件；生成的代码还须进入真实项目的构建、测试和业务评审。

## 门槛

| 级别 | 范围 | 门槛 |
|---|---|---|
| P0 | B01–B08 | **8/8** |
| P1 | B09–B71 | **至少 57/63** |

## 回归套件（企业分层）

| 套件 | 范围 | 门槛 | 场景 |
|---|---|---|---|
| **Smoke** | B01–B08 + 核心 P1 21 条 | P0 8/8；核心 P1 ≥18/21 | 日常 PR、AI 快速回归 |
| **Security** | B06、B21、B26、B31、B34、B39、B40、B43、B44、B45、B52、B53 | 建议 12/12 | 鉴权 / 安全 / 隐私 / 外部集成 PR |
| **Contract** | B03、B11、B25、B47、B51、B65 | 建议 6/6 | OpenAPI / 事件契约 / 幂等头 / 多范式 API PR |
| **Architecture** | B01、B10、B55、B67、B68、B69 | 建议 6/6 | 默认轻量分层、按场景升级、模块边界、表的写入方、事务和公共层 PR |
| **Business Extension** | B55–B63 | 建议 9/9 | 成熟后台新增业务 / CRUD / 树表主子表 / CodeGen PR |
| **Testing Governance** | B29、B42 | 建议 2/2 | 测试基础设施、稳定性、兼容性或故障演练规则变更 |
| **AI Tool Safety** | BAT01–BAT05（独立文件） | **5/5 Required** | AI 读取外部内容、调用工具或执行外部动作 |
| **Full** | B01–B71 | P0 8/8；P1 ≥57/63 | **发版**、规则包升级、大版本 |

索引（不复制正文）：`smoke-prompts.md`（**不计入** `### Bxx` 提示词计数；校验见 `scripts/validate-rules-package.py`）。

AI Tool Safety 正文与判据见 `ai-tool-safety.md`；该套件不计入常规 P1 总分，任一项失败即阻断。

执行边界：`validate-ai-eval-results.py` **不调用模型**；可用 `prepare-ai-eval-run.py --print-plan` / `--write-skeleton` 准备评测。5/5 阻断发版、规则包升级与高风险 AI 变更，不是 Level 0 采纳检查。详见 common-governance `docs/ai-tool-security.md`「评测执行边界」。

AI Tool Safety 结果须保存为结构化 YAML，并绑定本文件对应套件的摘要、模型版本、执行时间与独立评测人。业务仓使用公共治理包校验：

```bash
python common-governance/scripts/validate-ai-eval-results.py --file evidence/ai-eval-results.yaml --suite rules/evals/ai-tool-safety.md
```

校验器验证结果证据完整性，不负责调用模型；模型执行器由业务仓 CI 显式配置并固定版本。

**Topic manifest**：`topic-manifest.yaml` 为 prompts 标题与 rubric 判定的 SSOT；改 evals 后运行 `python scripts/generate-eval-topic-manifest.py --rules-dir web-backend/rules`。

### 核心 P1（= Smoke 中的 21 条）

B09、B11、B12、B21、B25、B27、B28、B29、B31、B34、B36、B39、B40、B43、B44、B45、B48、B51、B52、B55、B58。

发版前仍须跑 **Full**（B01–B71）。

### 与前端 Business Extension 对照（联调 / 双端 PR）

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

**E41–E43** 为管理端 i18n / 实时通信 / 富文本专项（`web-front/rules/evals`），无后端 B 对称项；双端 PR 仍以 Business Extension B55–B63 ↔ E32–E40 为主。

双端新增业务、树表、主子表、导入导出或 CodeGen PR 必须同时跑 B55–B63 与 E32–E40；仅 Smoke 不代表该场景已回归。

## 用例说明（部分重叠）

| 用例 | 侧重点 |
|---|---|
| B28 vs B36 | B28：事务内同步外部调用；B36：Feign/HTTP 超时与重试边界 |
| B18 并发 vs B38 | B18：方言/SQL 登记；B38：分布式锁释放须校验 owner token |
| B29 vs B31 | B29：测试环境隔离、确定性、失败证据及幂等/兼容测试；B31：fixture PII、缓存 key 明文等隐私生命周期 |
| B43 vs B45 | B43：高风险入口威胁建模；B45：服务调用要证明调用方身份 |
| B44 vs B37 | B44：密码/Token/密钥；B37：普通配置外部化 |
| B27 vs B52 | B27：审计字段；B52：对象级授权（BOLA/IDOR） |
| B28 vs B53 | B28：事务内外部调用；B53：用户可控 URL 出站（SSRF） |
| B39 vs B54 | B39：限流；B54：metric 高基数 label |
| B55 vs B32 | B55：业务模块污染公共层；B32：公共架构变更治理 |
| B57 vs B11 | B57：CodeGen 后补齐平台能力；B11：OpenAPI 先行 |
| B61 vs B21 | B61：树表父子租户 / 数据权限；B21：列表多租户条件 |
| B62 vs B05 | B62：主子表事务与孤儿数据；B05：写操作事务边界 |
| B63 vs B32 | B63：generator 全局模板；B32：公共架构变更治理 |
