# Examples

可复制的工程门禁样板。`00-must-follow.md` §33 要求 views 拦截 **import**、**`<el-*>`** 与 **Element Plus PascalCase（denylist）**。

| 文件 | 说明 |
|---|---|
| `eslint-views-ban-el.mjs` | 禁 `element-plus` / `element-plus/*` import |
| `ci-scan-views-el-tags.mjs` | 扫 template：`<el-*>`、`<ElButton>` 等 denylist、动态 `is` |
| `element-plus-pascal-denylist.mjs` | EP PascalCase 组件名列表（可随 EP 版本扩展） |
| `run-ci-scan-fixtures.mjs` | 脚本回归测试 |
| `package-scripts.sample.json` | 业务仓 scripts 示例 |
| `ci/rules-package-validate.yml` | 嵌入 `rules/` 时 PR 校验规则包一致性（复制到 `.github/workflows/`） |
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
