# Evals 套件索引（非独立提示词）

> 正文均在 `prompts.md`；本文件仅定义**套件范围**与**门槛**，避免复制导致 drift。
>
> **维护说明**：本文件是**索引**，不要用 `### Bxx` 标题（否则自动计数脚本会误判为提示词正文）。
> 发版校验时：只检查此处引用的 **B 编号是否都在 `prompts.md` 存在**，**不计入**提示词条数；条数仅以 `prompts.md` / `rubric.md` / `results-template.md` 为准。
> 自动化：`python scripts/validate-rules-package.py`（见 `contributing-rules-package.md`）。

执行时打开 `prompts.md` 对应章节。

## Smoke（日常）

| ID | 章节 |
|---|---|
| B01–B08 | P0 全量 |
| B09 | 新依赖 |
| B11 | OpenAPI 先行 |
| B12 | 异常可观测与校验 4xx |
| B21 | 数据权限 |
| B25 | 契约 breaking |
| B27 | 审计 |
| B28 | 事务内外部调用 |
| B29 | 隔离环境、稳定性、失败证据、幂等与兼容测试 |
| B31 | PII fixture |
| B34 | 越权 |
| B36 | Feign 超时 |
| B39 | CORS |
| B40 | Swagger/Actuator |
| B43 | 威胁建模 |
| B44 | 弱加密 |
| B45 | 内部接口认证 |
| B48 | 金额时间 |
| B51 | Idempotency-Key |
| B52 | BOLA/IDOR |
| B55 | 业务模块边界 |
| B58 | 业务数据权限一致性 |

**门槛**：P0 **8/8**；上表 P1 **≥18/21** Pass。

## Security（安全 / 隐私 PR）

B06、B21、B26、B31、B34、B39、B40、B43、B44、B45、B52、B53

**门槛**：建议 **12/12** Pass。

## Contract（契约 / 事件 / 多范式 API PR）

B03、B11、B25、B47、B51、B65

**门槛**：建议 **6/6** Pass。

## Architecture（默认轻量分层 / 按场景升级 / 模块边界 / 聚合 PR）

B01、B10、B55、B67、B68、B69

**门槛**：建议 **6/6** Pass。

## Business Extension（成熟后台业务扩展 PR）

B55、B56、B57、B58、B59、B60、B61、B62、B63

**门槛**：建议 **9/9** Pass。

## Testing Governance（测试治理 / 可靠性规则变更）

B29、B42

**门槛**：建议 **2/2** Pass。

## Full（发版 / 规则包升级）

B01–B71，见 `prompts.md` 全文。

**门槛**：P0 **8/8**；P1 **≥57/63**（见 `rubric.md`）。
