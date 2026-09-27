# 新项目接入（前端）

> 适用于 Vue 3 + TypeScript + Element Plus 管理端。接入目标是“规则可触发、命令可运行、证据可复查”，不是只复制 Markdown。

## 0. 声明项目基线

在项目 README、根 `AGENTS.md` 或 `99-project-local.mdc` 写明：

- Node.js 与 pnpm 版本、包管理器锁文件
- views、Base 组件、request wrapper、store、generated API、schema 和 layout 路径
- OpenAPI / schema 唯一来源及同步方式
- 当前采纳 Level、目标 Level、Owner 和计划迭代
- 实际存在的 lint、type-check、test、build、api check、E2E 和发布命令

## 1. 复制规则与入口

1. 整包复制或发布 `rules/`，不要只复制 `.mdc`。
2. 复制 `rules/codex/AGENTS.md` 到业务仓根 `AGENTS.md`，追加本项目约定。
3. 复制 `rules/cursor/*.mdc` 到 `.cursor/rules/`；仅概览规则设为 `alwaysApply: true`。
4. 复制 `rules/examples/99-project-local.mdc.sample` 为 `.cursor/rules/99-project-local.mdc` 并填写真实路径。
5. 企业项目引入 `common-governance/`；至少接入 DoD、豁免、CODEOWNERS、供应链和数据分级。

## 2. 固定工具链

1. 使用项目认可的 Node.js LTS 与 pnpm 版本，并在 `packageManager`、Corepack 或 CI 中固定。
2. 提交 lockfile；CI 使用 frozen lockfile 安装。
3. 接入 ESLint flat config、Prettier；使用 CSS / SCSS 时按团队基线接入 Stylelint。
4. 可从 `examples/scaffold/` 复制工程样板，再按项目插件和目录调整。

## 3. 契约与组件上下文

1. 设置 OpenAPI / schema 的唯一来源，接入 `schema:sync`、`api:gen`、`api:check` 或等价命令。
2. generated 目录只由生成器更新，禁止手改或维护重复 DTO。
3. 首个页面实现前读取真实 Base 组件源码，记录 props、events、slots、loading / empty / error 行为。
4. 确认菜单、路由、按钮权限、字典和后端鉴权的映射；前端权限只改善体验。

## 4. CI 顺序

推荐 PR 顺序：

```text
install (frozen lockfile)
  -> lint
  -> type-check
  -> api:check
  -> unit/component test
  -> build
  -> bundle budget
  -> E2E / a11y（按 Level）
```

缺少某脚本时记录“未配置”，不得声称通过。`examples/package-scripts.sample.json` 只提供名称约定，脚本实现必须随业务仓提交。

## 5. 按 Level 验收

| Level | 首次接入必须通过 |
|---|---|
| 0 | lint、type-check、build、rules validator、views 禁 Element Plus 扫描、P0 8/8 |
| 1 | api check、核心测试、依赖与包体积检查、Smoke、发布 / 回滚清单 |
| 2 | 关键 E2E / a11y、数据分级、性能预算、Full（P0 8/8，P1 ≥39/42）、治理文档与 Owner |
| 3 | 组件兼容策略、视觉回归、SLO 看板与演练记录 |

成熟后台新增业务页追加 Business Extension E32–E40；i18n、实时、富文本追加 Platform Extension E41–E43；受监管 Web 追加 Enterprise Hardening E44–E49。

## 6. 最终验收

1. 运行 `python rules/scripts/validate-rules-package.py`。
2. 运行项目实际存在的 lint、type-check、test、build、api check。
3. 在 code-rules 仓或复制验收脚本后运行：

```bash
python scripts/check-project-adoption.py --repo /path/to/frontend --stack frontend --strict
```

4. PR 中附命令结果、跳过项、残余风险、回滚方式和 Owner。

全栈字段与发布顺序见 `docs/fullstack-contract.md`；业务扩展见 `docs/business-feature-playbook-frontend.md`；发布见 `docs/release-checklist.md`。
