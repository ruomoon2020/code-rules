# 前端工程与 CI 样板

本目录提供可复制的前端门禁、脚本和工程骨架，帮助业务仓把规则从文档要求落实为自动检查。样板必须按项目目录和工具链调整，不能仅复制文件就声称已接入。

其中 views 扫描对应 `00-must-follow.md` §33：业务页面需要拦截 Element Plus 的直接 **import**、**`<el-*>`** 标签和 denylist 中的 PascalCase 组件；该限制不等于整个项目禁用 Element Plus。

## 推荐使用顺序

1. 先复制 `99-project-local.mdc.sample`，填写真实目录、Base 组件路径和脚本名。
2. 按业务仓结构接入 ESLint 和 views 扫描，不放宽扫描范围来适配存量问题。
3. 按需采用 `scaffold/` 中的 request、store、列表状态和构建预算样板。
4. 在本地跑 fixture，再将同一命令加入 PR Required Check。

| 文件 | 说明 |
|---|---|
| `eslint-views-ban-el.mjs` | 禁 `element-plus` / `element-plus/*` import |
| `ci-scan-views-el-tags.mjs` | 扫 template：`<el-*>`、`<ElButton>` 等 denylist、动态 `is` |
| `element-plus-pascal-denylist.mjs` | EP PascalCase 组件名列表（可随 EP 版本扩展） |
| `run-ci-scan-fixtures.mjs` | 脚本回归测试 |
| `package-scripts.sample.json` | 业务仓 scripts 示例 |
| `ci/rules-package-validate.yml` | 嵌入 `rules/` 时 PR 校验规则包一致性（复制到 `.github/workflows/`） |
| `.github/pull_request_template.md` | 前端 PR 模板（复制到业务仓根 `.github/pull_request_template.md`） |
| `scaffold/` | ESLint / Prettier / Stylelint、request、store 清理、列表状态与 bundle budget 工程样板 |

## 规则包一致性（维护者 / 嵌入 rules/ 的业务仓）

```bash
python rules/scripts/validate-rules-package.py --rules-dir rules
```

Monorepo 见仓库根 `.github/workflows/validate-rules-packages.yml`。

## 业务仓（PR 必跑）

```json
{
  "scripts": {
    "lint": "eslint . && pnpm lint:views-el",
    "lint:views-el": "node ./rules/examples/ci-scan-views-el-tags.mjs"
  }
}
```

- 在仓库根执行；子应用 `--root ./apps/admin`；非标准 views：`--include`（支持绝对路径）。
- **`lint:views-el` 须为 PR 必跑**（与 `lint` 串联或同级 required check）。
- **不要**加 `--allow-empty`。

## 规则包仓库（无 src/views）

```json
"lint:views-el": "node ./rules/examples/ci-scan-views-el-tags.mjs --allow-empty"
```

## 发版前自测

```bash
node rules/examples/run-ci-scan-fixtures.mjs
```

自测通过后，还应在业务仓准备至少一个真实违规文件验证 CI 会失败，再移除该文件。这样可以证明门禁确实被触发，而不是因路径或条件配置错误而空跑。

## ci-scan 检测清单

| 写法 | 检测 |
|---|---|
| `<el-button>` | ✅ |
| `<ElButton>`（denylist 内） | ✅ |
| `<EligibilityCard>`（非 EP 自有组件） | ❌ 不报错 |
| `<component :is="'el-button'" />` | ✅ |
| `<component :is="'ElButton'" />` | ✅ |
| `<component is="el-button" />` | ✅ |
| `<!-- <el-button> -->` 注释内 | ❌ 不报错 |
| `src/components` 下 `<el-*>` | ❌ 不扫描 |
| 同文件多处违规 | ✅ 全部列出，含 `file:line:column` |
| 运行时 `:is="variable"` | ❌ 不检测 |

违规输出示例：

```text
src/views/user/index.vue:23:5 [static-tag] <el-button
```
