# Evals 套件索引（非独立提示词）

> 正文均在 `prompts.md`；本文件仅定义**套件范围**与**门槛**，避免复制导致 drift。
>
> **维护说明**：本文件是**索引**，不要用 `### Exx` 标题（否则自动计数脚本会误判为提示词正文）。
> 发版校验时：只检查此处引用的 **E 编号是否都在 `prompts.md` 存在**，**不计入**提示词条数。
> 自动化：`python scripts/validate-rules-package.py`（见 `docs/contributing-rules-package.md`）。

## Smoke（日常）

| ID | 章节 |
|---|---|
| E01–E08 | P0 全量 |
| E09 | 新依赖 |
| E13 | 不可信外部指令 + 真实验证 |
| E15 | useTable + error |
| E16 | ci-scan 组合 |
| E17 | ElButton denylist |
| E18 | 日志脱敏 |
| E22 | 大表格分页/虚拟滚动 |
| E24 | Excel/CSV 导入 |
| E27 | 高风险导入 |
| E28 | 命名 |
| E29 | 依赖治理 |
| E30 | chunk 失败恢复 |

**门槛**：P0 **8/8**；上表 P1 **≥10/12** Pass。

## Security（安全 / 隐私 / 导入导出 PR）

E12、E18、E25、E27

**门槛**：建议 **4/4** Pass。

## Contract（Schema / API / 字段 PR）

E03、E04、E05、E26

**门槛**：建议 **4/4** Pass。

## Business Extension（成熟后台业务扩展 PR）

E32、E33、E34、E35、E36、E37、E38、E39、E40

**门槛**：建议 **9/9** Pass。

## Platform Extension（i18n / 实时 / 富文本 PR）

E41、E42、E43

**门槛**：建议 **3/3** Pass。

## Enterprise Hardening（金融 / 政务 / 高敏 Web PR）

E44、E45、E46、E47、E48、E49

**门槛**：建议 **6/6** Pass。

## Testing Governance（测试稳定性 / 竞态 / 兼容 PR）

E31、E50

**门槛**：建议 **2/2** Pass。

## Full（发版 / 规则包升级）

E01–E50，见 `prompts.md` 全文。

**门槛**：P0 **8/8**；P1 **≥39/42**（见 `rubric.md`）。
