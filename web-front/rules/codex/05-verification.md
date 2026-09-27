# Codex 验证规则

收尾前必读 **`rules/shared/10-verification-checklist.md`**（与 Cursor Review 共用）。

## 命令

运行项目实际存在的 scripts，例如：

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build
pnpm api:check
```

不存在则说明未配置，不得伪造通过。

## Evals（按场景）

| 场景 | 套件 |
|---|---|
| 日常 PR | Smoke（见 `evals/smoke-prompts.md`） |
| 成熟后台业务页 | Business Extension E32–E40 |
| i18n / 实时 / 富文本 | Platform Extension E41–E43 |
| 受监管 Web | Enterprise Hardening E44–E49 |
| 发版 / 规则大改 | Full E01–E50（P0 8/8；P1 ≥39/42） |

## 最终回复

- 改了什么、哪些文件
- 运行了哪些命令及结果
- 未运行的命令及原因
