# Frontend Engineering Scaffold

这些文件用于补齐新项目的工程基线。复制 `.sample` 后缀文件时先去掉后缀，再按业务仓真实依赖和路径调整。

| 样板 | 用途 |
|---|---|
| `eslint.config.mjs.sample` | ESLint flat config、TypeScript 禁显式 any、views import 门禁 |
| `prettier.config.mjs.sample` | 最小格式化基线 |
| `stylelint.config.mjs.sample` | CSS / SCSS 基线（使用样式文件时接入） |
| `src/api/request-boundary.ts.sample` | transport 注入、稳定错误结构和请求边界 |
| `src/stores/reset-all-stores.ts.sample` | 登出时统一清理 store 的注册机制 |
| `src/views/list-page-state.ts.sample` | 列表页页码、筛选、竞态、六态和删除末页回退的无 UI 状态骨架 |
| `scripts/check-bundle-budget.mjs.sample` | 用项目显式预算检查总量、首屏和单 chunk gzip 体积 |

## 使用顺序

1. 先填写 `99-project-local.mdc` 的真实目录和脚本。
2. 合并 ESLint / Prettier / Stylelint 样板到项目现有配置，不覆盖已有框架插件。
3. request 与 store 样板只定义边界；将 transport、日志、鉴权和具体 Pinia stores 绑定到项目现有实现。
4. 列表状态骨架不声明任何 Base 组件 Props。创建 `.vue` 页面前必须读取实际 Base 组件源码，再绑定 slots、events 和 v-model。
5. 在 CI 至少设置一个 bundle 预算后运行脚本；首屏预算依赖 Vite `build.manifest: true` 生成的 `dist/.vite/manifest.json`，禁止沿用不适合项目的随意阈值。

## 配置依赖

样板不捆绑版本，业务仓应按现有 Vue / TypeScript 工具链选择兼容版本。使用对应配置前确认开发依赖包含：

| 配置 | 必需包 |
|---|---|
| ESLint | `eslint`、`@eslint/js`、`typescript-eslint`、`eslint-plugin-vue` |
| Prettier | `prettier` |
| Stylelint | `stylelint`、`stylelint-config-standard-scss`、`stylelint-config-recommended-vue`、项目使用的 Sass 实现 |

## 最低验证

```bash
pnpm lint
pnpm type-check
pnpm test
pnpm build
pnpm api:check
BUNDLE_TOTAL_BUDGET_KB=512 BUNDLE_INITIAL_BUDGET_KB=256 BUNDLE_CHUNK_BUDGET_KB=128 node scripts/check-bundle-budget.mjs
```

上面的数值只演示参数形状，不是推荐预算。`BUNDLE_BUDGET_KB` 仍作为总量预算兼容别名；真实阈值必须由项目 Owner 基于现有构建基线确认。
