# 质量门禁规则

用于测试、CI、监控、发布和灰度。

## 本地与 CI

优先运行项目实际存在的 scripts：

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build
pnpm api:check
```

如果脚本不存在，记录“项目未配置该门禁”，不要编造执行结果。

## 规则到工具映射

| 规则域 | 工具 / 门禁 | 阻断级别 |
|---|---|---|
| TypeScript 类型 | `vue-tsc --noEmit` / `pnpm type-check` | PR 必须阻断 |
| ESLint 代码规范 | `pnpm lint` | PR 必须阻断 |
| views 禁原生 Element Plus import | `eslint-views-ban-el.mjs` | PR 必须阻断 |
| views 禁 `<el-*>` / EP PascalCase | `ci-scan-views-el-tags.mjs` | PR 必须阻断 |
| Schema / generated 一致性 | `pnpm api:check` 或等价脚本 | API 变更必须阻断 |
| 单元 / 组件测试 | `pnpm test:unit` / `pnpm test` | 核心逻辑必须阻断 |
| E2E 核心链路 | `pnpm test:e2e` | 发布分支必须阻断 |
| a11y 关键页 | axe / Playwright / 项目等价检查 | 新增关键交互建议阻断 |
| 依赖安全 / 许可证 | audit / license check / lockfile review | 高危漏洞必须阻断 |
| Bundle 体积 | bundle analyzer / size-limit / CI 体积对比 | 超预算须说明或阻断 |
| 敏感信息 | secret scan / CI 扫描 | PR 必须阻断 |

缺失门禁时，在 PR / Codex 最终回复中记录“项目未配置”，不得声称已通过。

## views 硬门禁（若已接入）

须**组合** ESLint import 禁令与模板扫描（见 `00-must-follow` §33、`rules/examples/README.md`）：

- `eslint-views-ban-el.mjs`：`element-plus` / `element-plus/*` import
- `ci-scan-views-el-tags.mjs`：`<el-*>`、动态 `is`、`element-plus-pascal-denylist.mjs` 内 PascalCase

业务仓 `lint:views-el` 应进入 PR 必跑链路；CI 勿对 ci-scan 使用 `--allow-empty`。

## 测试

1. 工具函数、composable、复杂组件应有单测。
2. 核心流程需要 E2E 或最小回归用例。
3. API / schema 改动必须通过类型与契约检查。
4. UI 组件、Token、主题变更建议做视觉回归。
5. 测试分层与 a11y 自动化见 `15-testing.md`。
6. Required 测试不得靠无限重试洗绿；临时隔离 flaky test 须有 Owner、到期日和补跑计划。
7. API 变更须验证生成代码与 N/N-1 兼容窗口；高风险写链路须覆盖重复提交、竞态和失败恢复。
8. 测试失败须归档可诊断且脱敏的报告、traceId、日志或端侧证据。

## 规则回归（evals）

发版或大改 `shared/` 时，在测试仓库按场景跑 evals（见 `evals/README.md`、`evals/smoke-prompts.md`）：

| 场景 | 套件 |
|---|---|
| 日常 PR | Smoke（P0 8/8；核心 P1 ≥10/12） |
| 成熟后台业务页 | Business Extension E32–E40（建议 9/9） |
| i18n / 实时 / 富文本 | Platform Extension E41–E43（建议 3/3） |
| 受监管 Web | Enterprise Hardening E44–E49（建议 6/6） |
| 测试治理变更 | Testing Governance E31、E50（建议 2/2） |
| 发版 / 规则大改 | Full E01–E50（P1 ≥39/42） |

## 监控

1. 错误上报须符合 `shared/18-logging-observability.md` 字段契约。
2. 禁止上报未脱敏敏感信息。
3. 关键流程失败应有业务埋点。
4. 发布后观察 JS 错误率、白屏率、API 失败率、LCP、INP。

## 发布

1. 生产构建使用锁定依赖。
2. 静态资源带 hash，入口 HTML 短缓存。
3. 每次发布必须有关联 release、Git commit、sourcemap。
4. 发布前确认回滚方式。
5. 高峰期、结算窗口、重大活动期间冻结非紧急发布。
6. Feature Flag、灰度和实验配置必须通过 `common-governance/docs/environment-promotion.md` 的统一生命周期清单；前端必须实现已登记的安全失败值和回滚路径。
7. 发布前确认错误恢复与白屏监控策略，见 `21-error-recovery.md`。
